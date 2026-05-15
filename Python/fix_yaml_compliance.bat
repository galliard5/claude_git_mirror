@echo off
REM Batch YAML compliance fixer for World_Building/
REM Run this from D:\claude\filesystem\ to fix all missing type fields

python3 << EOF
import os
import re
from pathlib import Path

WORLD_BUILDING = Path(r"D:\claude\filesystem\World_Building")

TYPE_RULES = {
    "Character_Pool": "character",
    "Characters": "character",
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
    "Equipment": "rules-reference",
    "Dead_Terra": "setting-document",
    "Gallihammer": "setting-document",
    "Archaeos": "setting-document",
}

def infer_type(file_path):
    parts = str(file_path).split("\\")
    for part in parts:
        for rule_key, rule_type in TYPE_RULES.items():
            if rule_key in part:
                return rule_type
    return "setting-document"

def extract_name(file_path):
    name = file_path.stem
    name = name.replace("_", " ")
    return name

def has_yaml_frontmatter(content):
    return content.startswith("---\n") or content.startswith("---\r\n")

def has_type_field(content):
    if not has_yaml_frontmatter(content):
        return False
    lines = content.split("\n", 10)
    for line in lines:
        if line.startswith("type:"):
            return True
        if line == "---":
            return False
    return False

def add_type_to_yaml(content, file_path):
    lines = content.split("\n")
    result = []
    type_added = False
    
    for i, line in enumerate(lines):
        result.append(line)
        if not type_added and line.startswith("name:"):
            inferred_type = infer_type(file_path)
            result.append(f"type: {inferred_type}")
            type_added = True
    
    return "\n".join(result)

def add_full_yaml(file_path, content):
    name = extract_name(file_path)
    doc_type = infer_type(file_path)
    
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
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not has_yaml_frontmatter(content):
            fixed = add_full_yaml(file_path, content)
            file_path.write_text(fixed, encoding='utf-8')
            return "added_frontmatter"
        elif not has_type_field(content):
            fixed = add_type_to_yaml(content, file_path)
            file_path.write_text(fixed, encoding='utf-8')
            return "added_type"
        else:
            return "already_compliant"
    except Exception as e:
        return f"error: {e}"

stats = {
    "total": 0,
    "added_frontmatter": 0,
    "added_type": 0,
    "already_compliant": 0,
    "errors": 0,
}

for md_file in WORLD_BUILDING.rglob("*.md"):
    result = process_file(md_file)
    stats["total"] += 1
    
    if result == "added_frontmatter":
        stats["added_frontmatter"] += 1
        print(f"✓ Added frontmatter: {md_file.relative_to(WORLD_BUILDING.parent)}")
    elif result == "added_type":
        stats["added_type"] += 1
    elif result == "already_compliant":
        stats["already_compliant"] += 1
    else:
        stats["errors"] += 1
        print(f"✗ Error: {md_file.relative_to(WORLD_BUILDING.parent)} — {result}")

print("\n" + "="*60)
print("YAML Compliance Fix Summary")
print("="*60)
print(f"Total files processed:     {stats['total']}")
print(f"Added full frontmatter:    {stats['added_frontmatter']}")
print(f"Added type field:          {stats['added_type']}")
print(f"Already compliant:         {stats['already_compliant']}")
print(f"Errors:                    {stats['errors']}")
print("="*60)

EOF
pause
