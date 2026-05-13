#!/usr/bin/env python3
"""
build_indexes.py — Unified index builder.

Single os.walk produces three outputs:
  1. directory_index.md              — compressed directory tree (YAML + dirs only)
  2. directory_index_with_files.md   — compressed directory + file tree (YAML + startup + tree)
  3. Python/search_index.db          — SQLite FTS5 full-text search index

All behaviour is driven by indexer.cfg via cfg_loader.py.
Both files must be in the same directory as this script.

Replaces: build_directory_indexes.py + build_search_index.py

Usage:
    python build_indexes.py                   # reads indexer.cfg, writes all outputs
    python build_indexes.py --cfg other.cfg   # use a different cfg file
    python build_indexes.py --console         # print trees to console, skip file writes
    python build_indexes.py --no-pause        # unattended run (used by refresh_indexes.bat)
"""

import argparse
import fnmatch
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

# cfg_loader.py lives alongside this script
sys.path.insert(0, str(Path(__file__).parent))
from cfg_loader import load_cfg


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CFG     = Path(__file__).parent / "indexer.cfg"
OUTPUT_DIRS_ONLY  = "directory_index.md"
OUTPUT_WITH_FILES = "directory_index_with_files.md"

# search_index.db lives in Python/ alongside the MCP server that reads it.
# Update search_mcp_server.py if this path changes.
DB_REL_PATH = Path("Python") / "search_index.db"


# ---------------------------------------------------------------------------
# Cfg interpretation
# ---------------------------------------------------------------------------

def resolve_paths(cfg: dict) -> tuple[Path, Path]:
    """
    Determine root and index_dir.

    Priority for root:
        1. CORPUS_ROOT env var — allows Docker to override without editing cfg
        2. root_directory in [paths] cfg section

    index_directory resolution (always relative to root):
        blank              -> root_directory (current behaviour)
        starts with / or \ -> root-relative  (/index/ -> root/index/)
        anything else      -> treat as absolute path
    """
    # 1. Env var override
    env_root = os.environ.get("CORPUS_ROOT", "").strip()
    if env_root:
        root      = Path(env_root)
        index_dir = root   # when running via env var, index output goes to root
        return root, index_dir

    # 2. cfg fallback
    settings = cfg.get("paths", {}).get("settings", {})
    raw_root = str(settings.get("root_directory", "")).strip()
    if not raw_root:
        raise ValueError("[paths] root_directory is required but not set in cfg")
    root = Path(raw_root)

    raw_index = str(settings.get("index_directory", "")).strip()
    if not raw_index:
        index_dir = root
    elif raw_index[0] in ("/", "\\"):
        index_dir = root / raw_index.lstrip("/\\")
    else:
        index_dir = Path(raw_index)

    return root, index_dir


def parse_dir_patterns(cfg: dict) -> tuple[str, set, set]:
    """
    Parse [directory_index] section.

    Pattern syntax (after comment stripping):
        dirname/      -> fully excluded from all outputs
        dirname/*.*   -> shallow: directory visible in tree, contents suppressed

    Returns:
        mode          'blacklist' | 'whitelist'
        dir_excluded  set of directory names
        dir_shallow   set of directory names
    """
    section  = cfg.get("directory_index", {})
    mode     = str(section.get("settings", {}).get("mode", "blacklist")).strip().lower()

    dir_excluded: set[str] = set()
    dir_shallow:  set[str] = set()

    for pattern in section.get("patterns", []):
        p = pattern.strip()
        if not p:
            continue
        if p.endswith("/*.*"):
            dir_shallow.add(p[:-4].strip("/\\"))    # 'Trash/*.*'  -> 'Trash'
        elif p.endswith("/") or p.endswith("\\"):
            dir_excluded.add(p.rstrip("/\\"))        # '.obsidian/' -> '.obsidian'
        else:
            dir_excluded.add(p)                      # bare name, full exclude

    return mode, dir_excluded, dir_shallow


def parse_search_excluded(cfg: dict) -> set:
    """
    Parse [search_index] patterns.
    Returns the set of directory names excluded from search_index.db.
    Always additive on top of dir_excluded.
    """
    patterns = cfg.get("search_index", {}).get("patterns", [])
    return {p.strip().rstrip("/\\") for p in patterns if p.strip()}


def parse_file_types(cfg: dict) -> tuple[str, list[str]]:
    """
    Parse [file_types].
    Returns (mode, [fnmatch_patterns]) e.g. ('whitelist', ['*.md', '*.txt']).
    """
    section  = cfg.get("file_types", {})
    mode     = str(section.get("settings", {}).get("mode", "whitelist")).strip().lower()
    patterns = [p.strip() for p in section.get("patterns", []) if p.strip()]
    return mode, patterns


def parse_context_limits(cfg: dict) -> tuple[int, list[tuple[str, object]]]:
    """
    Parse [context_limits].

    Returns:
        default_limit   int (−1 = full file, 0 = no content, N = first N lines)
        limits          [(fnmatch_pattern, value), ...] in cfg order

    When matching a file, iterate limits in order and keep overwriting —
    last match wins — so general patterns should precede specific ones in the cfg.
    Values are int or ('line', N) tuple as produced by cfg_loader.
    """
    settings = cfg.get("context_limits", {}).get("settings", {})

    raw_default = settings.get("default", -1)
    default = raw_default if isinstance(raw_default, int) else -1

    limits = [
        (key, value)
        for key, value in settings.items()
        if key != "default"
    ]
    return default, limits


# ---------------------------------------------------------------------------
# File type matching
# ---------------------------------------------------------------------------

def matches_file_type(filename: str, mode: str, patterns: list[str]) -> bool:
    """True if filename should be included given mode and fnmatch patterns."""
    fname   = filename.lower()
    matched = any(fnmatch.fnmatch(fname, p.lower()) for p in patterns)
    return matched if mode == "whitelist" else not matched


# ---------------------------------------------------------------------------
# Context limit resolution and file reading
# ---------------------------------------------------------------------------

def _read_line_limit(path: Path, line_num: int) -> int:
    """
    Read line line_num (1-based) from path and return the first integer found.
    Returns -1 (full file) if the line is missing or contains no integer.
    Used to resolve ('line', N) context limit sentinels.
    """
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                if i == line_num:
                    m = re.search(r"\d+", line)
                    return int(m.group()) if m else -1
    except Exception:
        pass
    return -1


def resolve_limit(filename: str, default: int, limits: list) -> object:
    """
    Determine the effective context limit for a file.
    Iterates limits in cfg order; last fnmatch hit wins.
    Returns the raw value (int or ('line', N) tuple) for read_file_content to act on.
    """
    effective = default
    for pattern, value in limits:
        if fnmatch.fnmatch(filename.lower(), pattern.lower()):
            effective = value
    return effective


def read_file_content(path: Path, limit: object) -> str:
    """
    Read file content up to the configured limit.

        limit == 0             -> return '' (path/name only, no content stored)
        limit == -1            -> return full file
        limit == ('line', N)   -> read line N of the file to get actual int limit, then apply
        limit == N (int > 0)   -> return first N lines

    Tries UTF-8 then latin-1; returns '' if both fail.
    """
    if limit == 0:
        return ""

    if isinstance(limit, tuple) and limit[0] == "line":
        limit = _read_line_limit(path, limit[1])

    for encoding in ("utf-8", "latin-1"):
        try:
            if limit == -1:
                return path.read_text(encoding=encoding)
            lines = []
            with path.open(encoding=encoding) as f:
                for i, line in enumerate(f):
                    if i >= limit:
                        break
                    lines.append(line)
            return "".join(lines)
        except UnicodeDecodeError:
            continue
        except Exception:
            return ""

    return ""


# ---------------------------------------------------------------------------
# Single unified walk
# ---------------------------------------------------------------------------

def walk_and_collect(
    root:            Path,
    dir_excluded:    set,
    dir_shallow:     set,
    search_excluded: set,
    file_mode:       str,
    file_patterns:   list,
) -> tuple[list, list]:
    """
    Walk the corpus once with os.walk, building all three output datasets.

    Directory ordering per iteration:
        1. Directory entry added to dir_entries first.
        2. Files in that directory processed for search_files second.
    If a directory is blocked (excluded or shallow), its files are never seen.

    Returns:
        dir_entries   [(depth, name, [filenames]), ...]
                      depth 0 = root itself; shallow dirs have empty filename list.
        search_files  [Path, ...]  files to index in search_index.db
    """
    dir_entries:  list[tuple[int, str, list]] = []
    search_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):

        rel      = Path(dirpath).relative_to(root)   # Path('.') at root
        depth    = len(rel.parts)                     # 0 at root
        dir_name = Path(dirpath).name

        # ----------------------------------------------------------------
        # 1. Shallow dir: add to tree as a leaf, suppress all contents
        # ----------------------------------------------------------------
        if dir_name in dir_shallow:
            dirnames[:] = []                              # prevent descent
            dir_entries.append((depth, dir_name, []))    # no files listed
            continue

        # ----------------------------------------------------------------
        # 2. Prune dirs fully excluded from the directory index.
        #    Sorting here gives alphabetical output for free.
        # ----------------------------------------------------------------
        dirnames[:] = sorted(
            (d for d in dirnames if d not in dir_excluded),
            key=str.lower,
        )

        # ----------------------------------------------------------------
        # 3. Directory entry — always added (for both directory index outputs)
        # ----------------------------------------------------------------
        sorted_files = sorted(filenames, key=str.lower)
        dir_entries.append((depth, dir_name, sorted_files))

        # ----------------------------------------------------------------
        # 4. Files — only queued for search if this dir isn't search-excluded.
        #    Checking rel.parts catches both the excluded dir itself and any
        #    descendant that slipped past the pruning step.
        # ----------------------------------------------------------------
        if any(part in search_excluded for part in rel.parts):
            continue

        for filename in sorted_files:
            if matches_file_type(filename, file_mode, file_patterns):
                search_files.append(Path(dirpath) / filename)

    return dir_entries, search_files


# ---------------------------------------------------------------------------
# Directory index rendering
# ---------------------------------------------------------------------------

def render_dirs_only(dir_entries: list) -> list[str]:
    """
    Compressed directory-only tree.
    One space per depth level, no decorators.
    """
    lines = []
    for depth, name, _files in dir_entries:
        lines.append(" " * depth + name)
    return lines


def render_with_files(dir_entries: list) -> list[str]:
    """
    Compressed tree including files.
    Directories end with '/'; files indented one level deeper.
    Shallow dirs (empty file list) appear as childless leaf nodes.
    """
    lines = []
    for depth, name, files in dir_entries:
        lines.append(" " * depth + name + ("/" if depth > 0 else ""))
        for filename in files:
            lines.append(" " * (depth + 1) + filename)
    return lines


# ---------------------------------------------------------------------------
# Directory index file assembly
# ---------------------------------------------------------------------------

_YAML_LINE_COUNT    = 8
_STARTUP_LINE_COUNT = 15

_STARTUP_BLOCK = (
    "## STARTUP PROCEDURE FOR CLAUDE\n"
    "\n"
    "CHECK 1: Is directory_index.md loaded in this session?\n"
    "  - NO: Skip remaining checks. Use this file normally.\n"
    "  - YES: Proceed to CHECK 2.\n"
    "\n"
    "CHECK 2: Compare scan_utc timestamps (YAML header).\n"
    "  - This file NEWER: Discard directory_index.md. Use this file only.\n"
    "  - directory_index.md NEWER: Proceed to CHECK 3.\n"
    "\n"
    "CHECK 3: Compare compressed sections for structural differences.\n"
    "  - IDENTICAL directories: Discard directory_index.md. Use this file only.\n"
    "  - DIFFERENT directories: Keep both loaded.\n"
    "    \u26a0\ufe0f Directory structures may be inconsistent (one file is stale).\n"
    "    ACTION: Recommend user run: python build_indexes.py\n"
    "\n"
)


def _yaml_block(name: str, description: str,
                now_utc: datetime, now_local: datetime,
                claude_section_end: int) -> str:
    return (
        "---\n"
        f"name: {name}\n"
        "keywords: [index, directory, structure, map]\n"
        f"description: {description}\n"
        f"scan_utc: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"scan_local: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"claude_section_end: {claude_section_end}\n"
        "---\n"
    )


def assemble_dirs_only(compressed: list[str],
                       now_utc: datetime, now_local: datetime) -> tuple[str, int]:
    """Returns (file_content, claude_section_end)."""
    claude_end = _YAML_LINE_COUNT + len(compressed)
    yaml = _yaml_block(
        "Directory Index",
        "Auto-generated directory tree snapshot (directories only)",
        now_utc, now_local, claude_end,
    )
    return yaml + "\n".join(compressed) + "\n", claude_end


def assemble_with_files(compressed: list[str],
                        now_utc: datetime, now_local: datetime) -> tuple[str, int]:
    """Returns (file_content, claude_section_end)."""
    claude_end = _YAML_LINE_COUNT + _STARTUP_LINE_COUNT + len(compressed)
    yaml = _yaml_block(
        "Directory Index with Files",
        "Auto-generated directory tree snapshot including files",
        now_utc, now_local, claude_end,
    )
    return yaml + _STARTUP_BLOCK + "\n".join(compressed) + "\n", claude_end


# ---------------------------------------------------------------------------
# Search index (SQLite FTS5)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """
    Extract YAML frontmatter from markdown. Returns (metadata, body).
    Falls back gracefully on missing or malformed frontmatter.
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        meta = yaml.safe_load(parts[1]) or {}
        if not isinstance(meta, dict):
            meta = {}
        return meta, parts[2].lstrip("\n")
    except yaml.YAMLError:
        return {}, text


def _keywords_str(kw) -> str:
    if isinstance(kw, list):
        return " ".join(str(k) for k in kw)
    return str(kw) if kw else ""


def build_search_db(
    search_files:    list[Path],
    root:            Path,
    db_path:         Path,
    context_default: int,
    context_limits:  list,
) -> tuple[int, int, list]:
    """
    Drop and rebuild the FTS5 search index from scratch.

    Parameterised SQL throughout — safe against crafted YAML frontmatter.
    path column is UNINDEXED so folder names don't inflate match scores.
    category IS indexed for location-aware search (e.g. category_filter).

    Returns (indexed, skipped, errors).
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS corpus_meta")
    cur.execute(
        """
        CREATE TABLE corpus_meta (
            path                TEXT    PRIMARY KEY,
            doc_type            TEXT    NOT NULL DEFAULT '',
            missing_name        INTEGER NOT NULL DEFAULT 0,
            missing_keywords    INTEGER NOT NULL DEFAULT 0,
            missing_description INTEGER NOT NULL DEFAULT 0,
            missing_type        INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    cur.execute("DROP TABLE IF EXISTS corpus_fts")
    cur.execute(
        """
        CREATE VIRTUAL TABLE corpus_fts USING fts5(
            path        UNINDEXED,
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

    for full_path in search_files:
        try:
            rel_path = full_path.relative_to(root)
        except ValueError:
            continue

        filename = full_path.name
        limit    = resolve_limit(filename, context_default, context_limits)

        try:
            raw = read_file_content(full_path, limit)
        except Exception as e:
            errors.append((str(rel_path), f"Read error: {e}"))
            skipped += 1
            continue

        # Frontmatter only meaningful for markdown
        if full_path.suffix.lower() == ".md":
            meta, body = _parse_frontmatter(raw)
        else:
            meta, body = {}, raw

        name        = str(meta.get("name") or full_path.stem)
        keywords    = _keywords_str(meta.get("keywords"))
        description = str(meta.get("description") or "")
        category    = "/".join(rel_path.parts[:-1])
        path_str    = str(rel_path).replace("\\", "/")

        is_md            = full_path.suffix.lower() == ".md"
        doc_type         = str(meta.get("type") or "") if is_md else ""
        missing_name     = int(is_md and not meta.get("name"))
        missing_keywords = int(is_md and not meta.get("keywords"))
        missing_desc     = int(is_md and not meta.get("description"))
        missing_type     = int(is_md and not meta.get("type"))

        try:
            cur.execute(
                "INSERT INTO corpus_meta(path, doc_type, missing_name, missing_keywords, missing_description, missing_type) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (path_str, doc_type, missing_name, missing_keywords, missing_desc, missing_type),
            )
            cur.execute(
                "INSERT INTO corpus_fts(path, name, keywords, description, category, content) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (path_str, name, keywords, description, category, body),
            )
            indexed += 1
        except sqlite3.Error as e:
            errors.append((str(rel_path), f"DB insert error: {e}"))
            skipped += 1

    conn.commit()
    conn.close()
    return indexed, skipped, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Unified index builder — directory trees and search index."
    )
    parser.add_argument(
        "--cfg", default=str(DEFAULT_CFG),
        help=f"Path to cfg file (default: {DEFAULT_CFG.name})"
    )
    parser.add_argument(
        "--console", action="store_true",
        help="Print directory trees to console; skip writing index files"
    )
    parser.add_argument(
        "--no-pause", action="store_true",
        help="Skip end-of-run pause prompt (used by refresh_indexes.bat)"
    )
    return parser.parse_args()


def main() -> int:
    args  = parse_args()
    start = time.perf_counter()

    # --- Load cfg ---
    try:
        cfg = load_cfg(args.cfg)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        if not args.no_pause:
            input("\nPress Enter to exit...")
        return 1

    try:
        root, index_dir = resolve_paths(cfg)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    _mode_dir, dir_excluded, dir_shallow = parse_dir_patterns(cfg)
    search_excluded                       = parse_search_excluded(cfg)
    file_mode, file_patterns              = parse_file_types(cfg)
    context_default, context_limits       = parse_context_limits(cfg)

    db_path = root / DB_REL_PATH

    # --- Walk (single pass) ---
    dir_entries, search_files = walk_and_collect(
        root, dir_excluded, dir_shallow,
        search_excluded, file_mode, file_patterns,
    )

    now_utc   = datetime.now(timezone.utc)
    now_local = datetime.now().astimezone()

    # --- Directory index outputs ---
    dirs_only_lines  = render_dirs_only(dir_entries)
    with_files_lines = render_with_files(dir_entries)

    dirs_only_content,  dirs_only_end  = assemble_dirs_only(dirs_only_lines,  now_utc, now_local)
    with_files_content, with_files_end = assemble_with_files(with_files_lines, now_utc, now_local)

    if args.console:
        print("=" * 50 + "\n  directory_index.md\n" + "=" * 50)
        print("\n".join(dirs_only_lines))
        print("\n" + "=" * 50 + "\n  directory_index_with_files.md\n" + "=" * 50)
        print("\n".join(with_files_lines))
        dirs_only_out  = "console only"
        with_files_out = "console only"
    else:
        index_dir.mkdir(parents=True, exist_ok=True)
        dirs_only_path  = index_dir / OUTPUT_DIRS_ONLY
        with_files_path = index_dir / OUTPUT_WITH_FILES
        dirs_only_path.write_text(dirs_only_content,  encoding="utf-8")
        with_files_path.write_text(with_files_content, encoding="utf-8")
        dirs_only_out  = str(dirs_only_path)
        with_files_out = str(with_files_path)

    # --- Search index ---
    indexed, skipped, errors = build_search_db(
        search_files, root, db_path, context_default, context_limits,
    )

    # --- Summary ---
    elapsed    = time.perf_counter() - start
    dir_count  = max(0, len(dir_entries) - 1)   # exclude root itself
    file_count = sum(len(f) for _, _, f in dir_entries)

    print()
    print("=" * 50)
    print("  INDEX BUILD COMPLETE")
    print("=" * 50)
    print(f"  Root:               {root}")
    print(f"  Cfg:                {args.cfg}")
    print()
    print(f"  Directories:        {dir_count}")
    print(f"  Files (tree):       {file_count}")
    print()
    print(f"  Output (dirs):      {dirs_only_out}")
    print(f"    claude_section_end:  {dirs_only_end}")
    print(f"  Output (w/files):   {with_files_out}")
    print(f"    claude_section_end:  {with_files_end}")
    print()
    print(f"  Search DB:          {db_path}")
    print(f"  Files indexed:      {indexed}")
    if skipped:
        print(f"  Files skipped:      {skipped}")
        for path, err in errors:
            print(f"    {path}: {err}")
    print()
    print(f"  Runtime:            {elapsed:.3f}s")
    print("=" * 50)

    if not args.no_pause:
        input("\nPress Enter to exit...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
