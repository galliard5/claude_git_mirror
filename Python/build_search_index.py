#!/usr/bin/env python3
"""
build_search_index.py — Builds an FTS5 search index over the corpus.

Walks D:\\Claude_MCP_folder for .md files, extracts YAML frontmatter,
and inserts everything into a SQLite FTS5 virtual table for full-text search.

Run whenever the corpus has drifted. Takes ~1 second for ~200 files.
Drops and rebuilds the table from scratch each time — no incremental logic.

Usage:
    cd D:\\Claude_MCP_folder\\Python
    python build_search_index.py
"""

import sqlite3
import sys
from pathlib import Path

import yaml

ROOT = Path(r"D:\Claude_MCP_folder")
DB_PATH = ROOT / "Python" / "search_index.db"

EXCLUDED_DIRS = {
    "Trash",
    "Python",
    "Perchance_prompts",
    "Sheet_Import",
    "Miscelanious_rpg_material",
    ".git",
    ".github",
    ".vscode",
    "node_modules",
    "__pycache__",
}

INCLUDED_EXTENSIONS = {".md"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from a markdown file. Returns (metadata_dict, body_text).
    Falls back gracefully on missing or malformed frontmatter."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    try:
        metadata = yaml.safe_load(parts[1]) or {}
        if not isinstance(metadata, dict):
            metadata = {}
        body = parts[2].lstrip("\n")
        return metadata, body
    except yaml.YAMLError:
        return {}, text


def is_excluded(rel_path: Path) -> bool:
    """Check if any directory in the relative path is excluded."""
    return any(part in EXCLUDED_DIRS for part in rel_path.parts)


def walk_corpus():
    """Yield every .md file under ROOT that isn't in an excluded directory."""
    for path in ROOT.rglob("*.md"):
        if path.suffix.lower() not in INCLUDED_EXTENSIONS:
            continue
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if is_excluded(rel):
            continue
        yield path


def make_category(rel_path: Path) -> str:
    """Build a category string from the directory portion of the relative path."""
    parts = rel_path.parts[:-1]  # exclude filename
    return "/".join(parts)


def keywords_to_string(kw) -> str:
    """Normalize the YAML keywords field (which may be a list or string) into
    a single space-separated string for FTS indexing."""
    if isinstance(kw, list):
        return " ".join(str(k) for k in kw)
    if isinstance(kw, str):
        return kw
    return ""


def build_index() -> None:
    """Drop and rebuild the FTS5 index from scratch."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS corpus_fts")
    cur.execute(
        """
        CREATE VIRTUAL TABLE corpus_fts USING fts5(
            path UNINDEXED,
            name,
            keywords,
            description,
            category,
            content,
            tokenize = 'porter unicode61'
        )
        """
    )

    indexed = 0
    skipped = 0
    errors: list[tuple[str, str]] = []

    for full_path in walk_corpus():
        try:
            rel_path = full_path.relative_to(ROOT)
        except ValueError:
            continue

        try:
            text = full_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = full_path.read_text(encoding="latin-1")
            except Exception as e:
                errors.append((str(rel_path), f"Read error: {e}"))
                skipped += 1
                continue
        except Exception as e:
            errors.append((str(rel_path), f"Read error: {e}"))
            skipped += 1
            continue

        metadata, body = parse_frontmatter(text)

        name = str(metadata.get("name") or full_path.stem)
        keywords = keywords_to_string(metadata.get("keywords"))
        description = str(metadata.get("description") or "")
        category = make_category(rel_path)
        path_str = str(rel_path).replace("\\", "/")

        cur.execute(
            "INSERT INTO corpus_fts(path, name, keywords, description, category, content) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (path_str, name, keywords, description, category, body),
        )
        indexed += 1

    conn.commit()
    conn.close()

    print(f"\n[OK] Indexed {indexed} files")
    if skipped:
        print(f"[!]  Skipped {skipped} files due to errors:")
        for path, err in errors:
            print(f"     {path}: {err}")
    print(f"\nDatabase: {DB_PATH}")


if __name__ == "__main__":
    try:
        build_index()
    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)
