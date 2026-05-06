#!/usr/bin/env python3
"""
Directory tree mapper for the Aethelmark project.
Generates a dual-format directory index:
  1. Compressed Claude-only section (single-space indent, no decorators)
  2. Human-readable section (box-drawing tree connectors)

YAML frontmatter includes claude_section_end so Claude can read
only the compressed section via head= parameter.

All timestamps use UTC for consistent freshness checks.

Usage:
    python map_directory.py                     # Defaults
    python map_directory.py --root C:\Projects  # Custom root
    python map_directory.py --output my_tree.md # Custom output path
    python map_directory.py --depth 4           # Limit tree depth
    python map_directory.py --console           # Print to console only
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set, Optional


# --- Configuration ---

DEFAULT_ROOT = r"D:\Claude_MCP_folder"
DEFAULT_OUTPUT = "directory_index.md"

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".obsidian",
    "__pycache__",
    "node_modules",
    "Trash",
}


# --- Tree Builders ---

class DirectoryMapper:
    """Walks a root directory and produces directory trees in two formats."""

    def __init__(self, root: str, excluded: Set[str] = None, max_depth: Optional[int] = None):
        self.root = Path(root).resolve()
        self.excluded = excluded or EXCLUDED_DIRS
        self.max_depth = max_depth

        if not self.root.is_dir():
            raise ValueError(f"Root is not a valid directory: {self.root}")

    def build_compressed(self) -> List[str]:
        """
        Compressed tree for Claude consumption.
        Single space per depth level, no connectors, no slashes.
        Optimised for minimum token count.
        """
        lines: List[str] = [self.root.name]
        self._walk_compressed(self.root, depth=1, lines=lines)
        return lines

    def build_readable(self) -> List[str]:
        """
        Human-readable tree with box-drawing connectors.
        """
        lines: List[str] = [f"{self.root.name}/"]
        self._walk_readable(self.root, prefix="", lines=lines, depth=0)
        return lines

    def _get_subdirs(self, current: Path) -> List[Path]:
        """Get sorted, filtered subdirectories."""
        try:
            return sorted(
                [e for e in current.iterdir() if e.is_dir() and e.name not in self.excluded],
                key=lambda p: p.name.lower()
            )
        except PermissionError:
            return []

    def _walk_compressed(self, current: Path, depth: int, lines: List[str]):
        """Recurse for compressed format: single space per depth level."""
        if self.max_depth is not None and depth > self.max_depth:
            return

        for entry in self._get_subdirs(current):
            lines.append(f"{' ' * depth}{entry.name}")
            self._walk_compressed(entry, depth + 1, lines)

    def _walk_readable(self, current: Path, prefix: str, lines: List[str], depth: int):
        """Recurse for human-readable format: box-drawing connectors."""
        if self.max_depth is not None and depth >= self.max_depth:
            return

        entries = self._get_subdirs(current)
        if not entries and prefix:
            return

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{entry.name}/")

            extension = "    " if is_last else "│   "
            self._walk_readable(entry, prefix + extension, lines, depth + 1)


# --- Output ---

def build_output(root_name: str, compressed: List[str], readable: List[str]) -> str:
    """
    Assemble the final file with YAML header, compressed section, note, and readable section.

    File layout:
        Lines 1-N:    YAML frontmatter (includes claude_section_end)
        Lines N+1-M:  Compressed Claude-only tree
        Lines M+1-K:  Note about directory_index_with_files.md
        Lines K+1-?: Human-readable tree
    """
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now().astimezone()

    # YAML is 8 lines (--- through ---)
    # Compressed section starts at line 9
    # Note is ~4 lines
    yaml_lines = 8
    note_lines = 4
    claude_end = yaml_lines + len(compressed) + note_lines

    yaml_block = (
        "---\n"
        "name: Directory Index\n"
        "keywords: [index, directory, structure, map]\n"
        "description: Auto-generated directory tree snapshot\n"
        f"scan_utc: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"scan_local: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
        f"claude_section_end: {claude_end}\n"
        "---\n"
    )

    compressed_block = "\n".join(compressed) + "\n"

    note_block = (
        "\n"
        "---\n"
        "NOTE: For filesystem-intensive sessions, use `directory_index_with_files.md` which lists all files.\n"
        "Run: python D:\\Claude_MCP_folder\\Python\\map_directory_with_files.py\n"
        "---\n"
    )

    readable_block = (
        "\n"
        "# Human-Readable Directory Tree\n"
        "\n"
        f"Scanned: {now_local.strftime('%Y-%m-%d %H:%M:%S %Z')} "
        f"(UTC: {now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')})\n"
        f"Excluded: {', '.join(sorted(EXCLUDED_DIRS))}\n"
        "\n"
        "```\n"
        + "\n".join(readable)
        + "\n```\n"
    )

    return yaml_block + compressed_block + note_block + readable_block


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a dual-format directory index with UTC timestamps."
    )
    parser.add_argument(
        "--root", type=str, default=DEFAULT_ROOT,
        help=f"Root directory to scan (default: {DEFAULT_ROOT})"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help=f"Output file path (default: <root>/{DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "--depth", type=int, default=None,
        help="Maximum directory depth (default: unlimited)"
    )
    parser.add_argument(
        "--console", action="store_true",
        help="Print to console only; do not write a file"
    )
    parser.add_argument(
        "--exclude", type=str, nargs="*", default=None,
        help=f"Additional dirs to exclude (always excludes: {', '.join(sorted(EXCLUDED_DIRS))})"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    excluded = set(EXCLUDED_DIRS)
    if args.exclude:
        excluded.update(args.exclude)

    # Build both trees
    mapper = DirectoryMapper(root=args.root, excluded=excluded, max_depth=args.depth)
    compressed = mapper.build_compressed()
    readable = mapper.build_readable()

    # Assemble output
    content = build_output(mapper.root.name, compressed, readable)

    # Console: show human-readable only (compressed is for Claude)
    print("```")
    print("\n".join(readable))
    print("```")

    # File output
    if not args.console:
        output_path = args.output or str(Path(args.root) / DEFAULT_OUTPUT)
        Path(output_path).write_text(content, encoding="utf-8")

    # --- Summary ---
    dir_count = len(compressed) - 1  # -1 for root line
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    now_local = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    yaml_lines = 8
    note_lines = 4
    claude_end = yaml_lines + len(compressed) + note_lines

    print()
    print("=" * 50)
    print("  DIRECTORY SCAN COMPLETE")
    print("=" * 50)
    print(f"  Root:             {args.root}")
    print(f"  Directories:      {dir_count}")
    print(f"  Claude section:   lines 1–{claude_end}")
    if args.depth is not None:
        print(f"  Depth limit:      {args.depth}")
    if args.exclude:
        print(f"  Extra excluded:   {', '.join(args.exclude)}")
    print(f"  Timestamp (UTC):  {now_utc}")
    print(f"  Local time:       {now_local}")
    if not args.console:
        print(f"  Output:           {output_path}")
    else:
        print("  Output:           console only (no file written)")
    print("=" * 50)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
