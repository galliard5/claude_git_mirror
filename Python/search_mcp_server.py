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
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(r"D:\Claude_MCP_folder\Python\search_index.db")

mcp = FastMCP("corpus-search")


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
) -> str:
    """Full-text ranked search over the worldbuilding corpus.

    Searches markdown content, frontmatter (name, keywords, description),
    and path-derived category across all indexed files. Results are ranked
    by BM25 with name and keywords weighted highest.

    Query syntax (FTS5):
        Vogt                       - single term (matches Vogt, Vogts, etc via porter stem)
        Vogt security              - both words present (implicit AND)
        Vogt OR Sable              - either term
        "Reshaping Cascade"        - exact phrase (escape inner quotes by doubling)
        petition NOT rejected      - boolean exclusion
        transform*                 - prefix match (matches transformed, transformation, etc)

    Args:
        query: FTS5 search expression. Multi-word queries default to AND.
        limit: Max results to return. Default 10.
        category_filter: Optional path-segment filter (e.g. "Aethelmark",
            "Manor", "Cendrel", "Senior_Staff"). Matches against the indexed
            category column derived from the file's directory path.

    Returns:
        Formatted ranked results: each entry shows score, relative path, name,
        keywords, description, and a snippet showing the matched context with
        ** ** marks around hit terms. Returns a "no results" message if the
        query matches nothing, or an error message if the query is malformed.
    """
    if not DB_PATH.exists():
        rebuild_path = DB_PATH.parent / "build_search_index.py"
        return (
            f"[!] Search index not found at {DB_PATH}.\n"
            f"Run: python {rebuild_path}"
        )

    if category_filter:
        cat_clean = category_filter.strip().replace('"', '""')
        match_expr = f'category:"{cat_clean}" AND {_wrap_query(query)}'
    else:
        match_expr = _wrap_query(query)

    try:
        conn = _open_readonly()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                path,
                name,
                keywords,
                description,
                category,
                snippet(corpus_fts, 5, '**', '**', '...', 24) AS preview,
                bm25(corpus_fts, 0.0, 10.0, 5.0, 3.0, 0.0, 1.0) AS rank
            FROM corpus_fts
            WHERE corpus_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (match_expr, limit),
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
        suffix = f" [filter: {category_filter}]" if category_filter else ""
        return f"No results for: {query}{suffix}"

    lines = [f"Found {len(rows)} result(s) for: {query}"]
    if category_filter:
        lines[0] += f" [filter: {category_filter}]"
    lines.append("")

    for i, (path, name, keywords, description, category, preview, rank) in enumerate(rows, 1):
        # bm25 returns negative values; magnitude indicates relevance
        score = abs(rank)
        lines.append(f"{i}. [score: {score:.2f}] {path}")
        if name:
            lines.append(f"   Name: {name}")
        if keywords:
            lines.append(f"   Keywords: {keywords}")
        if description:
            lines.append(f"   Description: {description}")
        if preview:
            preview_clean = " ".join(preview.split())
            lines.append(f"   Match: {preview_clean}")
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
    mcp.run()
