#!/usr/bin/env python3
# name: validate_naming.py
# keywords: [naming, validation, corpus, maintenance, rename]
# description: Scans a directory tree for Snake_Case naming violations (spaces, ampersands, apostrophes) and renames files/folders after confirmation.
#
# Modification script. Checks files and folders for compliance with the corpus naming
# convention (Snake_Case_With_Capitals). Reports issues grouped by type, previews all
# proposed renames, then asks for confirmation before touching anything.
# Run from any directory; defaults to current directory if no --root is given.
#
# Command line arguments:
#   --root [path]  - Directory to scan (default: prompted interactively)
#   --dry-run      - Show report and preview without renaming anything
#
# changed 2026-05-19: added standard header, --dry-run flag, --root argument, confirmation changed to [y/N] default NO

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict
from enum import Enum


class IssueType(Enum):
    SPACE_IN_NAME = "Contains spaces"
    AMPERSAND = "Contains '&' (should be '_and_')"
    APOSTROPHE = "Contains apostrophes"
    # INCONSISTENT_CAPS is defined but not currently checked in check_name().
    # Left here as a placeholder if cap-consistency checking is added later.
    INCONSISTENT_CAPS = "Inconsistent capitalization"


class NamingValidator:
    def __init__(self, root_dir: str = None):
        if root_dir:
            self.root_dir = Path(root_dir).absolute()
        else:
            self.root_dir = Path.cwd()
        
        if not self.root_dir.is_dir():
            raise ValueError(f"Invalid directory: {self.root_dir}")
        
        self.issues: Dict[str, List[Tuple[IssueType, str]]] = {}
        self.renames: List[Tuple[str, str]] = []
    
    def check_name(self, name: str) -> List[Tuple[IssueType, str]]:
        """
        Check a filename/folder name against naming rules.
        Returns list of issues found.
        """
        issues = []
        original_name = name
        
        # Don't check hidden files or system files
        if name.startswith('.'):
            return issues
        
        # Check for spaces
        if ' ' in name:
            issues.append((IssueType.SPACE_IN_NAME, f"'{name}' → '{name.replace(' ', '_')}'"))
        
        # Check for ampersands
        if ' & ' in name:
            fixed = name.replace(' & ', '_and_')
            issues.append((IssueType.AMPERSAND, f"'{name}' → '{fixed}'"))
        elif '&' in name:
            fixed = name.replace('&', '_and_')
            issues.append((IssueType.AMPERSAND, f"'{name}' → '{fixed}'"))
        
        # Check for apostrophes
        if "'" in name:
            fixed = name.replace("'", "")
            issues.append((IssueType.APOSTROPHE, f"'{name}' → '{fixed}'"))
        
        return issues
    
    def normalize_name(self, name: str) -> str:
        """
        Apply all normalization rules to a name.
        Preserves file extensions.
        """
        # Split into name and extension
        if '.' in name and not name.startswith('.'):
            # Find the last dot to handle multi-dot extensions
            parts = name.rsplit('.', 1)
            base_name = parts[0]
            extension = '.' + parts[1]
        else:
            base_name = name
            extension = ''
        
        # Apply transformations
        normalized = base_name
        
        # Fix ampersands first (before space replacement)
        normalized = normalized.replace(' & ', '_and_')
        normalized = normalized.replace('&', '_and_')
        
        # Remove apostrophes
        normalized = normalized.replace("'", "")
        
        # Replace spaces with underscores
        normalized = normalized.replace(" ", "_")
        
        # Remove consecutive underscores
        normalized = re.sub(r'_+', '_', normalized)
        
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        
        return normalized + extension
    
    def scan_directory(self, directory: Path = None) -> None:
        """Recursively scan directory and find naming issues."""
        if directory is None:
            directory = self.root_dir
        
        try:
            for item in sorted(directory.iterdir()):
                item_type = "folder" if item.is_dir() else "file"
                rel_path = item.relative_to(self.root_dir)
                
                # Check the name
                issues = self.check_name(item.name)
                
                if issues:
                    self.issues[str(rel_path)] = issues
                    # Calculate the normalized name
                    normalized = self.normalize_name(item.name)
                    if normalized != item.name:
                        old_path = str(item)
                        new_path = str(item.parent / normalized)
                        self.renames.append((old_path, new_path))
                
                # Recurse into directories
                if item.is_dir():
                    self.scan_directory(item)
        
        except PermissionError as e:
            print(f"⚠️  Permission denied: {directory}")
    
    def print_report(self) -> None:
        """Print a detailed report of all issues found."""
        if not self.issues:
            print("\n✅ All files and folders are compliant with naming rules!")
            return
        
        print(f"\n{'='*80}")
        print(f"NAMING COMPLIANCE REPORT")
        print(f"{'='*80}\n")
        
        print(f"📊 Found {len(self.issues)} items with naming issues:\n")
        
        # Group by issue type
        by_type: Dict[IssueType, List[str]] = {}
        for path, issues_list in sorted(self.issues.items()):
            for issue_type, description in issues_list:
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(f"{path}\n    {description}")
        
        for issue_type in sorted(by_type.keys(), key=lambda x: x.value):
            print(f"⚠️  {issue_type.value}")
            print("-" * 80)
            for item in by_type[issue_type]:
                print(f"  {item}")
            print()
    
    def preview_fixes(self) -> None:
        """Show preview of all planned fixes."""
        if not self.renames:
            return
        
        print(f"\n{'='*80}")
        print(f"PREVIEW: {len(self.renames)} ITEMS WILL BE RENAMED")
        print(f"{'='*80}\n")
        
        # Group by directory
        by_dir: Dict[str, List[Tuple[str, str]]] = {}
        for old_path, new_path in self.renames:
            directory = os.path.dirname(old_path)
            if directory not in by_dir:
                by_dir[directory] = []
            
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)
            by_dir[directory].append((old_name, new_name))
        
        for directory in sorted(by_dir.keys()):
            rel_dir = os.path.relpath(directory, self.root_dir)
            print(f"📁 {rel_dir}")
            print("-" * 80)
            for old_name, new_name in by_dir[directory]:
                print(f"  {old_name:<55} → {new_name}")
            print()
    
    def execute_fixes(self) -> int:
        """Execute all rename operations."""
        if not self.renames:
            return 0
        
        print(f"\n{'='*80}")
        print(f"EXECUTING {len(self.renames)} RENAMES")
        print(f"{'='*80}\n")
        
        success_count = 0
        error_count = 0
        
        for old_path, new_path in self.renames:
            try:
                os.rename(old_path, new_path)
                old_name = os.path.basename(old_path)
                new_name = os.path.basename(new_path)
                print(f"✅ {old_name:<55} → {new_name}")
                success_count += 1
            except Exception as e:
                old_name = os.path.basename(old_path)
                print(f"❌ FAILED: {old_name}")
                print(f"   Error: {str(e)}")
                error_count += 1
        
        print(f"\n{'='*80}")
        print(f"RESULTS: {success_count} successful, {error_count} failed")
        print(f"{'='*80}\n")
        
        return error_count


def get_directory_input() -> Path:
    """Prompt user for directory path interactively (used when --root is not supplied)."""
    print("\n" + "="*80)
    print("NAMING VALIDATOR & FIXER")
    print("="*80 + "\n")

    while True:
        user_input = input("Enter directory path (or press Enter for current directory): ").strip()

        if not user_input:
            return Path.cwd()

        directory = Path(user_input).absolute()

        if directory.is_dir():
            print(f"\n✓ Using: {directory}\n")
            return directory
        else:
            print(f"❌ Directory not found: {directory}")
            print("   Please try again.\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan a directory for corpus naming violations and rename after confirmation."
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Directory to scan (default: prompted interactively)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show report and preview renames without applying any changes",
    )
    args = parser.parse_args()

    try:
        if args.dry_run:
            print("[DRY RUN] No files will be renamed.")

        root_dir = Path(args.root).absolute() if args.root else get_directory_input()

        if not root_dir.is_dir():
            print(f"❌ Directory not found: {root_dir}")
            return 1

        print("🔍 Scanning directory structure...\n")
        validator = NamingValidator(str(root_dir))
        validator.scan_directory()

        validator.print_report()

        if not validator.issues:
            return 0

        validator.preview_fixes()

        print(f"\n{len(validator.renames)} rename(s) proposed.")

        if args.dry_run:
            print("[DRY RUN] No changes made.")
            return 0

        response = input("Apply changes? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            return 0

        error_count = validator.execute_fixes()
        return error_count

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
