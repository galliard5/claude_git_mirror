#!/usr/bin/env python3
"""
Enhanced directory tree mapper for the Aethelmark project.
Generates compressed directory index with FILES listed.
Output: compressed Claude-only section (single-space indent, files indented under dirs).

YAML frontmatter includes claude_section_end so Claude can read
only the compressed section via head= parameter.

All timestamps use UTC for consistent freshness checks.

Usage:
    python map_directory_with_files.py                     # Defaults
    python map_directory_with_files.py --root C:\Projects  # Custom root
    python map_directory_with_files.py --output my_tree.md # Custom output path
    python map_directory_with_files.py --depth 4           # Limit tree depth
    python map_directory_with_files.py --console           # Print to console only
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Set, Optional


# --- Configuration ---

DEFAULT_ROOT = r"D:\Claude_MCP_folder"
DEFAULT_OUTPUT = "directory_index_with_files.md"

EXCLUDED_DIRS: Set[str] = {
    ".git",
    ".obsidian",
    "__pycache__",
    "node_modules",
    "Trash",
}


# --- Tree Builders ---

class DirectoryMapperWithFiles:
    """Walks a root directory and produces directory trees with files listed."""

    def __init__(self, root: str, excluded: Set[str] = None, max_depth: Optional[int] = None):
        self.root = Path(root).resolve()
        self.excluded = excluded or EXCLUDED_DIRS
        self.max_depth = max_depth

        if not self.root.is_dir():
            raise ValueError(f"Root is not a valid directory: {self.root}")

    def build_compressed(self) -> List[str]:
        """
        Compressed tree for Claude consumption.
        Single space per depth level, files indented under dirs.
        Optimised for minimum token count.
        """
        lines: List[str] = [self.root.name]
        self._walk_compressed(self.root, depth=1, lines=lines)
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

    def _get_files(self, current: Path) -> List[Path]:
        """Get sorted files in directory."""
        try:
            return sorted(
                [e for e in current.iterdir() if e.is_file()],
                key=lambda p: p.name.lower()
            )
        except PermissionError:
            return []

    def _walk_compressed(self, current: Path, depth: int, lines: List[str]):
        """Recurse for compressed format: single space per depth level, files listed."""
        if self.max_depth is not None and depth > self.max_depth:
            return

        subdirs = self._get_subdirs(current)
        files = self._get_files(current)

        # Add directories
        for entry in subdirs:
            lines.append(f"{' ' * depth}{entry.name}/")
            self._walk_compressed(entry, depth + 1, lines)

        # Add files at this level (indented one level deeper than directory name)
        if files:
            for file in files:
                lines.append(f"{' ' * (depth + 1)}{file.name}")


# --- Output ---

def build_output(root_name: str, compressed: List[str]) -> str:
    """
    Assemble the final file with YAML header and compressed section only.

    File layout:
        Lines 1-N:   YAML frontmatter (includes claude_section_end)
        Lines N+1-M: Compressed Claude-only tree with files
    """
    now_utc = datetime.now(timezone.utc)
    now_local = datetime.now().astimezone()

    # YAML is 8 lines (--- through ---)
    # Compressed section starts at line 9
    yaml_lines = 8
    claude_end = yaml_lines + len(compressed)

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

    compressed_block = "\n".join(compressed) + "\n"

    return yaml_block + compressed_block


# --- CLI ---

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a compressed directory index with files listed."
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

    # Build compressed tree
    mapper = DirectoryMapperWithFiles(root=args.root, excluded=excluded, max_depth=args.depth)
    compressed = mapper.build_compressed()

    # Assemble output
    content = build_output(mapper.root.name, compressed)

    # File output
    if not args.console:
        output_path = args.output or str(Path(args.root) / DEFAULT_OUTPUT)
        Path(output_path).write_text(content, encoding="utf-8")

    # --- Summary ---
    # Count dirs (lines that end with /)
    dir_count = sum(1 for line in compressed if line.endswith('/'))
    file_count = sum(1 for line in compressed if not line.endswith('/') and line != mapper.root.name)
    
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    now_local = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    yaml_lines = 8
    claude_end = yaml_lines + len(compressed)

    print()
    print("=" * 50)
    print("  DIRECTORY SCAN COMPLETE")
    print("=" * 50)
    print(f"  Root:             {args.root}")
    print(f"  Directories:      {dir_count}")
    print(f"  Files:            {file_count}")
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
