#!/usr/bin/env python3
"""
search_mcp_server.py — MCP server exposing FTS5 search over the corpus.

Provides two tools:
    search_corpus(query, limit, category_filter) -> formatted ranked results
    index_status() -> diagnostic info about the index

The database path is hardcoded and opened read-only. The server has no
SQL passthrough and no path arguments — the only thing reachable through
this interface is ranked search over the pre-built corpus_fts table.

Launched by Claude Desktop as a stdio subprocess via claude_desktop_config.json.
Not intended to be run manually.
"""

import datetime
import os
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# CORPUS_ROOT env var allows Docker to override the path without editing this file.
# Falls back to the local Windows path when not set.
# DB_PATH must stay in lockstep with build_indexes.py and indexer.cfg index_directory.
_CORPUS_ROOT = Path(os.environ.get("CORPUS_ROOT", r"D:\claude\filesystem"))
DB_PATH = _CORPUS_ROOT / "index" / "search_index.db"

mcp = FastMCP(
    "corpus-search",
    host=os.environ.get("MCP_HOST", "127.0.0.1"),
    port=int(os.environ.get("MCP_PORT", "8000")),
)


def _open_readonly() -> sqlite3.Connection:
    """Open the database in read-only mode using a SQLite URI."""
    uri = f"{DB_PATH.as_uri()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def _wrap_query(query: str) -> str:
    """Wrap a user query for FTS5 MATCH safely. Escapes embedded double quotes
    and wraps the whole thing in parens for predictable operator precedence."""
    cleaned = query.strip().replace('"', '""')
    return f"({cleaned})"


@mcp.tool()
def search_corpus(
    query: str,
    limit: int = 10,
    category_filter: str | None = None,
    type_filter: str | None = None,
    missing_filter: str | None = None,
) -> str:
    """Full-text ranked search over the worldbuilding corpus.

    FTS5 handles full-text ranking. Structured field filters (type, missing)
    use SQL equality against a companion table joined at query time, so
    hyphenated type values like 'setting-document' work correctly.

    Query syntax (FTS5):
        Vogt                       - single term (porter stem: Vogt, Vogts, etc)
        Vogt security              - both words present (implicit AND)
        Vogt OR Sable              - either term
        "Reshaping Cascade"        - exact phrase (escape inner quotes by doubling)
        petition NOT rejected      - boolean exclusion
        transform*                 - prefix match (transformed, transformation, etc)

    Args:
        query: FTS5 search expression. Multi-word queries default to AND.
        limit: Max results to return. Default 10.
        category_filter: Path-segment filter (e.g. "Manor", "Cendrel",
            "Senior_Staff"). Matched against the directory portion of the
            file path via FTS5 column filter.
        type_filter: Exact match against the type: frontmatter field
            (e.g. "setting-document", "character", "session"). SQL equality —
            hyphenated values work correctly here.
        missing_filter: Find files where a frontmatter field is absent or empty.
            One of: name, keywords, description, type.

    Returns:
        Formatted ranked results: path, name, keywords, description, type,
        missing fields, and a snippet with ** ** around matched terms.
        Returns a 'no results' message or error string on failure.
    """
    if not DB_PATH.exists():
        rebuild_path = DB_PATH.parent / "build_search_index.py"
        return (
            f"[!] Search index not found at {DB_PATH}.\n"
            f"Run: python {rebuild_path}"
        )

    # Validate missing_filter before touching the DB
    _valid_missing = {"name", "keywords", "description", "type"}
    if missing_filter:
        _field = missing_filter.lower().strip()
        if _field not in _valid_missing:
            return (
                f"[!] Invalid missing_filter: '{missing_filter}'. "
                f"Valid values: {', '.join(sorted(_valid_missing))}"
            )

    # FTS5 MATCH expression — category stays here; type/missing use SQL below
    conditions = []
    if category_filter:
        cat_clean = category_filter.strip().replace('"', '""')
        conditions.append(f'category:"{cat_clean}"')
    conditions.append(_wrap_query(query))
    match_expr = " AND ".join(conditions)

    # SQL WHERE extensions for structured field filters — use IN subqueries
    # against corpus_meta rather than JOIN conditions, to avoid FTS5's known
    # quirk of silently ignoring non-MATCH WHERE clauses on joined tables.
    subquery_filters: list[str] = []
    subquery_params: list = []
    if type_filter:
        subquery_filters.append(
            "f.path IN (SELECT path FROM corpus_meta WHERE doc_type = ?)"
        )
        subquery_params.append(type_filter.strip())
    if missing_filter:
        field = missing_filter.lower().strip()
        subquery_filters.append(
            f"f.path IN (SELECT path FROM corpus_meta WHERE missing_{field} = 1)"
        )

    where_clause = "WHERE corpus_fts MATCH ?"
    if subquery_filters:
        where_clause += "\n  AND " + "\n  AND ".join(subquery_filters)

    try:
        conn = _open_readonly()
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT
                f.path,
                f.name,
                f.keywords,
                f.description,
                f.category,
                COALESCE(m.doc_type, '') AS doc_type,
                COALESCE(m.missing_name, 0) AS missing_name,
                COALESCE(m.missing_keywords, 0) AS missing_keywords,
                COALESCE(m.missing_description, 0) AS missing_description,
                COALESCE(m.missing_type, 0) AS missing_type,
                snippet(corpus_fts, 5, '**', '**', '...', 24) AS preview,
                bm25(corpus_fts, 0.0, 10.0, 5.0, 3.0, 0.0, 1.0) AS rank
            FROM corpus_fts f
            LEFT JOIN corpus_meta m ON f.path = m.path
            {where_clause}
            ORDER BY rank
            LIMIT ?
            """,
            [match_expr] + subquery_params + [limit],
        )
        rows = cur.fetchall()
        conn.close()
    except sqlite3.OperationalError as e:
        return (
            f"[!] Search error: {e}\n\n"
            "Hint: FTS5 has special syntax. Wrap problematic terms in double "
            'quotes (e.g. "Vogt\'s") or use prefix matching (Vogt*).'
        )
    except Exception as e:
        return f"[!] Unexpected error: {e}"

    if not rows:
        suffixes = []
        if category_filter:
            suffixes.append(f"category: {category_filter}")
        if type_filter:
            suffixes.append(f"type: {type_filter}")
        if missing_filter:
            suffixes.append(f"missing: {missing_filter}")
        suffix = f" [{', '.join(suffixes)}]" if suffixes else ""
        return f"No results for: {query}{suffix}"

    lines = [f"Found {len(rows)} result(s) for: {query}"]
    if category_filter:
        lines[0] += f" [category: {category_filter}]"
    if type_filter:
        lines[0] += f" [type: {type_filter}]"
    if missing_filter:
        lines[0] += f" [missing: {missing_filter}]"
    lines.append("")

    for i, (
        path, name, keywords, description, category,
        doc_type, miss_name, miss_kw, miss_desc, miss_type,
        preview, rank,
    ) in enumerate(rows, 1):
        score = abs(rank)  # bm25 returns negative; magnitude = relevance
        lines.append(f"{i}. [score: {score:.2f}] {path}")
        if name:
            lines.append(f"   Name: {name}")
        if keywords:
            lines.append(f"   Keywords: {keywords}")
        if description:
            lines.append(f"   Description: {description}")
        if doc_type:
            lines.append(f"   Type: {doc_type}")
        missing_parts = []
        if miss_name: missing_parts.append("name")
        if miss_kw:   missing_parts.append("keywords")
        if miss_desc: missing_parts.append("description")
        if miss_type: missing_parts.append("type")
        if missing_parts:
            lines.append(f"   Missing: {', '.join(missing_parts)}")
        if preview:
            lines.append(f"   Match: {' '.join(preview.split())}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def index_status() -> str:
    """Report the current state of the search index.

    Returns the database path, total indexed files, and last-built timestamp.
    Useful for checking whether the index is stale before relying on results.
    """
    if not DB_PATH.exists():
        rebuild_path = DB_PATH.parent / "build_search_index.py"
        return (
            f"[!] Index not built yet.\n"
            f"Run: python {rebuild_path}"
        )

    try:
        conn = _open_readonly()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM corpus_fts")
        count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        return f"[!] Could not read index: {e}"

    mtime = datetime.datetime.fromtimestamp(DB_PATH.stat().st_mtime)
    age = datetime.datetime.now() - mtime
    age_str = (
        f"{age.days}d ago" if age.days >= 1
        else f"{age.seconds // 3600}h ago" if age.seconds >= 3600
        else f"{age.seconds // 60}m ago"
    )

    return (
        "Search index status:\n"
        f"  Path: {DB_PATH}\n"
        f"  Files indexed: {count}\n"
        f"  Last built: {mtime.strftime('%Y-%m-%d %H:%M:%S')} ({age_str})"
    )


if __name__ == "__main__":
    mcp.run(transport=os.environ.get("MCP_TRANSPORT", "stdio"))
