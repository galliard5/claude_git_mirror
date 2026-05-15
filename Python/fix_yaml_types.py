#!/usr/bin/env python3
"""
YAML Type Field Fixer — Apply to all World_Building markdown files
Adds missing 'type:' field to YAML frontmatter based on file path heuristics

USAGE:
  python3 fix_yaml_types.py

REQUIREMENTS:
  - Run from D:\claude\filesystem\ or adjust WORLD_BUILDING path below
  - Python 3.7+

WHAT IT DOES:
  1. Scans all .md files in World_Building/ recursively
  2. For each file with YAML frontmatter but no 'type:' field:
     - Infers type from file path
     - Inserts 'type: <inferred>' after 'name:' line
     - Writes updated file back to disk
  3. Reports progress and summary
"""

import os
from pathlib import Path
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

WORLD_BUILDING = Path(r"D:\claude\filesystem\World_Building")
if not WORLD_BUILDING.exists():
    # Fallback for other environments
    WORLD_BUILDING = Path("World_Building")

# Type inference rules: if path contains KEY, assign TYPE
TYPE_RULES = {
    "Character_Pool": "character",
    "Characters": "character",
    "Region": "location",
    "Town": "location",
    "Cendrel": "location",
    "Maruvec": "location",
    "Vauclair": "location",
    "Camp_Rochevaux": "location",
    "Factions": "faction",
    "Guilds": "faction",
    "Noble_Houses": "faction",
    "Merchant_Families": "faction",
    "Scenarios": "scenario",
    "Session": "session-summary",
    "Summary": "session-summary",
    "Briefing": "scenario",
    "Equipment": "rules-reference",
    "Dead_Terra": "setting-document",
    "Gallihammer": "setting-document",
    "Archaeos": "setting-document",
    "Rogue_Trader": "setting-document",
    "Overview": "setting-document",
}

def infer_type(file_path):
    """Infer type from file path components."""
    path_str = str(file_path)
    
    # Check path components in order of precedence
    for rule_key, rule_type in TYPE_RULES.items():
        if rule_key in path_str:
            return rule_type
    
    # Default fallback
    return "setting-document"

def has_yaml_frontmatter(content):
    """Check if file starts with YAML."""
    return content.startswith("---\n") or content.startswith("---\r\n")

def has_type_field(content):
    """Check if YAML already has type field."""
    if not has_yaml_frontmatter(content):
        return False
    
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("type:"):
            return True
        # Stop checking after the closing ---
        if i > 0 and line.strip() == "---":
            break
    
    return False

def add_type_field(content, file_path):
    """Add type field after name field in YAML."""
    lines = content.split("\n")
    result = []
    type_added = False
    in_frontmatter = False
    
    for i, line in enumerate(lines):
        # Start of frontmatter
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
        
        result.append(line)
        
        # Add type after name (within frontmatter)
        if in_frontmatter and not type_added and line.startswith("name:"):
            inferred_type = infer_type(file_path)
            result.append(f"type: {inferred_type}")
            type_added = True
        
        # End of frontmatter
        if in_frontmatter and i > 0 and line.strip() == "---":
            in_frontmatter = False
    
    return "\n".join(result)

def process_file(file_path):
    """Process a single file. Returns (status, message)."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not has_yaml_frontmatter(content):
            return ("skip", "No YAML frontmatter")
        
        if has_type_field(content):
            return ("skip", "Already has type field")
        
        # Add type field
        fixed_content = add_type_field(content, file_path)
        file_path.write_text(fixed_content, encoding='utf-8')
        
        return ("fixed", infer_type(file_path))
    
    except Exception as e:
        return ("error", str(e))

def main():
    """Main entry point."""
    if not WORLD_BUILDING.exists():
        print(f"ERROR: World_Building not found at {WORLD_BUILDING}")
        print(f"       Please adjust WORLD_BUILDING path or run from D:\\claude\\filesystem\\")
        return
    
    print("=" * 70)
    print("YAML Type Field Fixer")
    print("=" * 70)
    print(f"Scanning: {WORLD_BUILDING}")
    print()
    
    stats = {
        "total": 0,
        "fixed": {},
        "skipped": 0,
        "errors": [],
    }
    
    # Find all .md files
    md_files = sorted(WORLD_BUILDING.rglob("*.md"))
    
    print(f"Found {len(md_files)} markdown files")
    print()
    
    # Process each file
    for i, md_file in enumerate(md_files, 1):
        rel_path = md_file.relative_to(WORLD_BUILDING.parent)
        status, detail = process_file(md_file)
        stats["total"] += 1
        
        if status == "fixed":
            if detail not in stats["fixed"]:
                stats["fixed"][detail] = 0
            stats["fixed"][detail] += 1
            print(f"  [{i:3d}] ✓ Fixed ({detail:20s}) {rel_path}")
        elif status == "skip":
            stats["skipped"] += 1
        elif status == "error":
            stats["errors"].append((rel_path, detail))
            print(f"  [{i:3d}] ✗ ERROR: {rel_path}")
            print(f"         {detail}")
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total files scanned:        {stats['total']}")
    print(f"Files fixed:                {sum(stats['fixed'].values())}")
    if stats['fixed']:
        for type_val, count in sorted(stats['fixed'].items()):
            print(f"  - {type_val:20s}: {count}")
    print(f"Files skipped:              {stats['skipped']}")
    print(f"Errors:                     {len(stats['errors'])}")
    if stats['errors']:
        print()
        for path, error in stats['errors'][:10]:  # Show first 10
            print(f"  - {path}: {error}")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Rebuild search index: python3 Python/build_indexes.py")
    print("  2. Commit changes: git add . && git commit -m '...'")
    print()

if __name__ == "__main__":
    main()
