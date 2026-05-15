#!/usr/bin/env python3
"""
Batch fix YAML frontmatter compliance across World_Building/
- Add missing type field to files with partial frontmatter
- Add full frontmatter to files with none
"""

import os
import re
from pathlib import Path

CORPUS_ROOT = Path("/corpus")
WORLD_BUILDING = CORPUS_ROOT / "World_Building"

# Type inference rules based on path
TYPE_RULES = {
    "Character_Pool": "character",
    "Characters": "character",
    "Locations": "location",
    "Region": "location",
    "Town": "location",
    "Factions": "faction",
    "Guilds": "faction",
    "Noble_Houses": "faction",
    "Merchant_Families": "faction",
    "Scenarios": "scenario",
    "Session": "session-summary",
    "Summary": "session-summary",
    "Briefing": "scenario",
    "Overview": "setting-document",
    "Equipment": "rules-reference",
    "Dead_Terra": "setting-document",
    "Gallihammer": "setting-document",
    "Archaeos": "setting-document",
}

def infer_type(file_path):
    """Infer type from file path."""
    parts = str(file_path).split("/")
    for part in parts:
        for rule_key, rule_type in TYPE_RULES.items():
            if rule_key in part:
                return rule_type
    # Default fallback based on content patterns
    return "setting-document"

def extract_name(file_path):
    """Extract name from filename (remove .md, replace _ with spaces)."""
    name = file_path.stem
    name = name.replace("_", " ")
    return name

def has_yaml_frontmatter(content):
    """Check if file starts with YAML frontmatter."""
    return content.startswith("---\n") or content.startswith("---\r\n")

def has_type_field(content):
    """Check if YAML frontmatter includes type field."""
    if not has_yaml_frontmatter(content):
        return False
    lines = content.split("\n", 10)  # Check first 10 lines
    for line in lines:
        if line.startswith("type:"):
            return True
        if line == "---":  # End of frontmatter
            return False
    return False

def add_type_to_yaml(content, file_path):
    """Add type field after name in existing YAML frontmatter."""
    lines = content.split("\n")
    result = []
    type_added = False
    
    for i, line in enumerate(lines):
        result.append(line)
        # Add type after name field
        if not type_added and line.startswith("name:"):
            inferred_type = infer_type(file_path)
            result.append(f"type: {inferred_type}")
            type_added = True
    
    return "\n".join(result)

def add_full_yaml(file_path, content):
    """Add full YAML frontmatter to file with none."""
    name = extract_name(file_path)
    doc_type = infer_type(file_path)
    
    # Extract first heading or first substantive text as description
    lines = content.split("\n")
    description = name
    for line in lines[:20]:
        if line.startswith("#") and not line.startswith("##"):
            description = line.lstrip("# ").strip()
            break
        elif line.strip() and not line.startswith("["):
            description = line.strip()[:100]
            break
    
    yaml_frontmatter = f"""---
name: {name}
type: {doc_type}
keywords: [{doc_type}]
description: {description}
---

"""
    return yaml_frontmatter + content

def process_file(file_path):
    """Process a single markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not has_yaml_frontmatter(content):
            # Add full frontmatter
            fixed = add_full_yaml(file_path, content)
            file_path.write_text(fixed, encoding='utf-8')
            return "added_frontmatter"
        elif not has_type_field(content):
            # Add type field only
            fixed = add_type_to_yaml(content, file_path)
            file_path.write_text(fixed, encoding='utf-8')
            return "added_type"
        else:
            return "already_compliant"
    except Exception as e:
        return f"error: {e}"

def main():
    """Process all markdown files in World_Building."""
    stats = {
        "total": 0,
        "added_frontmatter": 0,
        "added_type": 0,
        "already_compliant": 0,
        "errors": 0,
    }
    
    # Iterate all .md files recursively
    for md_file in WORLD_BUILDING.rglob("*.md"):
        result = process_file(md_file)
        stats["total"] += 1
        
        if result == "added_frontmatter":
            stats["added_frontmatter"] += 1
            print(f"✓ Added frontmatter: {md_file.relative_to(CORPUS_ROOT)}")
        elif result == "added_type":
            stats["added_type"] += 1
        elif result == "already_compliant":
            stats["already_compliant"] += 1
        else:
            stats["errors"] += 1
            print(f"✗ Error: {md_file.relative_to(CORPUS_ROOT)} — {result}")
    
    # Summary
    print("\n" + "="*60)
    print("YAML Compliance Fix Summary")
    print("="*60)
    print(f"Total files processed:     {stats['total']}")
    print(f"Added full frontmatter:    {stats['added_frontmatter']}")
    print(f"Added type field:          {stats['added_type']}")
    print(f"Already compliant:         {stats['already_compliant']}")
    print(f"Errors:                    {stats['errors']}")
    print("="*60)

if __name__ == "__main__":
    main()
