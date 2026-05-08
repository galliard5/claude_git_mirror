#!/usr/bin/env python3
"""
Consolidated directory index builder for the Aethelmark/Gallihammer project.

Single tree walk produces TWO output files:
  - directory_index.md             - Compressed directories only (YAML + tree)
  - directory_index_with_files.md  - Compressed dirs + files (YAML + startup logic + tree)

The human-readable section that previously appeared in directory_index.md has
been dropped (never used). Both index files contain only the YAML header and
the compressed Claude-section tree, so the Claude-section read range
(head=claude_section_end) covers the entire useful content.

YAML frontmatter on each file includes claude_section_end so Claude can read
only the relevant range via head=. All timestamps use UTC for consistent
freshness checks.

Replaces: map_directory.py + map_directory_with_files.py (consolidation 2026-05).

Usage:
    python build_directory_indexes.py                           # Defaults
    python build_directory_indexes.py --root C:\\Projects        # Custom root
    python build_directory_indexes.py --output-dir D:\\out       # Custom output dir
    python build_directory_indexes.py --depth 4                 # Limit tree depth
    python build_directory_indexes.py --console                 # Print to console only
    python build_directory_indexes.py --no-pause                # Unattended run
"""

import argparse
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set, Optional, Dict


# --- Configuration ---

DEFAULT_ROOT = r"D:\Claude_MCP_folder"
OUTPUT_DIRS_ONLY = "directory_index.md"
OUTPUT_WITH_FILES = "directory_index_with_files.md"

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".obsidian",
    "__pycache__",
    "node_modules",
    "Trash",
}


# --- Walker ---

class DirectoryWalker:
    """
    Walks the corpus once, accumulating per-directory data for both output formats.

    For each directory encountered (post-exclusion), we record:
      - depth (int)
      - name (str)
      - sorted list of contained file names

    From this single walk, both output files can be assembled without re-walking.
    """

    def __init__(self, root: str, excluded: Set[str], max_depth: Optional[int]):
        self.root = Path(root).resolve()
        self.excluded = excluded
        self.max_depth = max_depth

        if not self.root.is_dir():
            raise ValueError(f"Root is not a valid directory: {self.root}")

        # Each entry: (depth, dir_name, [file_names])
        # depth=0 is the root itself; depth=1 is immediate children, etc.
        self.entries: List[tuple] = []

    def walk(self) -> None:
        """Perform the single tree walk and populate self.entries in DFS order."""
        self.entries = []
        # Root entry first (depth 0)
        root_files = self._get_files(self.root)
        self.entries.append((0, self.root.name, root_files))
        self._recurse(self.root, depth=1)

    def _recurse(self, current: Path, depth: int) -> None:
        if self.max_depth is not None and depth > self.max_depth:
            return
        for sub in self._get_subdirs(current):
            files = self._get_files(sub)
            self.entries.append((depth, sub.name, files))
            self._recurse(sub, depth + 1)

    def _get_subdirs(self, current: Path) -> List[Path]:
        try:
            return sorted(
                (e for e in current.iterdir() if e.is_dir() and e.name not in self.excluded),
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            return []

    def _get_files(self, current: Path) -> List[str]:
        try:
            return sorted(
                (e.name for e in current.iterdir() if e.is_file()),
                key=str.lower,
            )
        except PermissionError:
            return []

    # --- Output renderers ---

    def render_dirs_only(self) -> List[str]:
        """
        Compressed directory-only tree. Single space per depth level, no
        decorators, no slashes. Matches legacy map_directory.py format.
        """
        lines: List[str] = []
        for depth, name, _files in self.entries:
            if depth == 0:
                lines.append(name)
            else:
                lines.append(f"{' ' * depth}{name}")
        return lines

    def render_with_files(self) -> List[str]:
        """
        Compressed tree with directories AND files. Directories end with `/`,
        files are indented one level deeper than the directory they belong to.
        Matches legacy map_directory_with_files.py format.
        """
        lines: List[str] = []
        for depth, name, files in self.entries:
            if depth == 0:
                lines.append(name)
            else:
                lines.append(f"{' ' * depth}{name}/")
            # Files indented one level deeper than this directory
            for filename in files:
                lines.append(f"{' ' * (depth + 1)}{filename}")
        return lines

    def stats(self) -> Dict[str, int]:
        """Return summary counts derived from the single walk."""
        dir_count = max(0, len(self.entries) - 1)  # -1 for root
        file_count = sum(len(files) for _depth, _name, files in self.entries)
        return {"directories": dir_count, "files": file_count}


# --- Output assembly ---

def build_dirs_only_content(compressed: List[str], now_utc: datetime, now_local: datetime) -> tuple:
    """
    Assemble directory_index.md content.

    Layout:
        Lines 1-8:  YAML frontmatter (claude_section_end = full file length)
        Lines 9+:   Compressed directory tree

    Returns (content_string, claude_section_end).
    """
    yaml_lines = 8
    claude_end = yaml_lines + len(compressed)

    yaml_block = (
        "---\n"
        "name: Directory Index\n"
        "keywords: [index, directory, structure, map]\n"
        "description: Auto-generated directory tree snapshot (directories only)\n"
        f"scan_utc: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"scan_local: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"claude_section_end: {claude_end}\n"
        "---\n"
    )
    compressed_block = "\n".join(compressed) + "\n"
    return yaml_block + compressed_block, claude_end


def build_with_files_content(compressed: List[str], now_utc: datetime, now_local: datetime) -> tuple:
    """
    Assemble directory_index_with_files.md content.

    Layout:
        Lines 1-8:    YAML frontmatter (claude_section_end covers full tree)
        Lines 9-23:   Claude startup procedure (15 lines)
        Lines 24+:    Compressed tree with files

    Returns (content_string, claude_section_end).
    """
    yaml_lines = 8
    startup_lines = 15
    claude_start = yaml_lines + startup_lines
    claude_end = claude_start + len(compressed)

    yaml_block = (
        "---\n"
        "name: Directory Index with Files\n"
        "keywords: [index, directory, structure, map, files]\n"
        "description: Auto-generated directory tree snapshot including files\n"
        f"scan_utc: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"scan_local: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"claude_section_end: {claude_end}\n"
        "---\n"
    )

    startup_block = (
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
        "    ACTION: Recommend user run: python D:\\Claude_MCP_folder\\Python\\build_directory_indexes.py\n"
        "\n"
    )

    compressed_block = "\n".join(compressed) + "\n"
    return yaml_block + startup_block + compressed_block, claude_end


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build both directory index files from a single tree walk."
    )
    parser.add_argument(
        "--root", type=str, default=DEFAULT_ROOT,
        help=f"Root directory to scan (default: {DEFAULT_ROOT})"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Directory to write index files into (default: same as --root)"
    )
    parser.add_argument(
        "--depth", type=int, default=None,
        help="Maximum directory depth (default: unlimited)"
    )
    parser.add_argument(
        "--console", action="store_true",
        help="Print compressed trees to console; do not write files"
    )
    parser.add_argument(
        "--exclude", type=str, nargs="*", default=None,
        help=f"Additional dirs to exclude (always excludes: {', '.join(sorted(EXCLUDED_DIRS))})"
    )
    parser.add_argument(
        "--no-pause", action="store_true",
        help="Skip the 'Press Enter to exit' prompt at the end (used by refresh_indexes.bat)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    start = time.perf_counter()

    excluded = set(EXCLUDED_DIRS)
    if args.exclude:
        excluded.update(args.exclude)

    # Single tree walk
    walker = DirectoryWalker(root=args.root, excluded=excluded, max_depth=args.depth)
    walker.walk()

    # Render both formats from the same walk data
    dirs_only_lines = walker.render_dirs_only()
    with_files_lines = walker.render_with_files()

    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now().astimezone()

    dirs_only_content, dirs_only_end = build_dirs_only_content(dirs_only_lines, now_utc, now_local)
    with_files_content, with_files_end = build_with_files_content(with_files_lines, now_utc, now_local)

    # Output
    output_dir = Path(args.output_dir) if args.output_dir else Path(args.root)

    if args.console:
        print("=" * 50)
        print("  directory_index.md (dirs only)")
        print("=" * 50)
        print("\n".join(dirs_only_lines))
        print()
        print("=" * 50)
        print("  directory_index_with_files.md (with files)")
        print("=" * 50)
        print("\n".join(with_files_lines))
        dirs_only_path = "console only"
        with_files_path = "console only"
    else:
        dirs_only_path = output_dir / OUTPUT_DIRS_ONLY
        with_files_path = output_dir / OUTPUT_WITH_FILES
        dirs_only_path.write_text(dirs_only_content, encoding="utf-8")
        with_files_path.write_text(with_files_content, encoding="utf-8")

    # Summary
    stats = walker.stats()
    elapsed = time.perf_counter() - start

    print()
    print("=" * 50)
    print("  DIRECTORY INDEX BUILD COMPLETE")
    print("=" * 50)
    print(f"  Root:             {args.root}")
    print(f"  Directories:      {stats['directories']}")
    print(f"  Files:            {stats['files']}")
    if args.depth is not None:
        print(f"  Depth limit:      {args.depth}")
    if args.exclude:
        print(f"  Extra excluded:   {', '.join(args.exclude)}")
    print(f"  Timestamp (UTC):  {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"  Local time:       {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    print(f"  Output 1:         {dirs_only_path}")
    print(f"    claude_section_end: {dirs_only_end}")
    print(f"  Output 2:         {with_files_path}")
    print(f"    claude_section_end: {with_files_end}")
    print()
    print(f"  Runtime:          {elapsed:.3f}s")
    print("=" * 50)

    if not args.no_pause:
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
