#!/usr/bin/env python3
"""
Clean up legacy metadata tags from .md files
Removes: [TEXT], [LABEL], [NUMBER], and similar bracket tags
"""

import os
import re
from pathlib import Path

ROOT_DIR = r"D:\Claude_MCP_folder"
EXCLUDE_DIRS = {".obsidian", "Stories"}

def clean_file(file_path):
    """Remove legacy bracket tags from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Remove [TEXT] tags - keeping the content after them
        content = re.sub(r'\[TEXT\]\s*', '', content)
        
        # Remove [LABEL] tags - keeping the content after them
        content = re.sub(r'\[LABEL\]\s*', '', content)
        
        # Remove [NUMBER] tags - keeping the content after them
        content = re.sub(r'\[NUMBER\]\s*', '', content)
        
        # Remove any other similar bracket tags (generic cleanup)
        content = re.sub(r'\[A-Z_]+\]\s*', '', content)
        
        # Clean up any double blank lines that might have been created
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, len(original) - len(content)
        return False, 0
        
    except Exception as e:
        return None, str(e)

def main():
    print("\n" + "="*70)
    print("LEGACY TAG CLEANUP TOOL")
    print("="*70 + "\n")
    
    # Find all .md files
    md_files = []
    for root, dirs, files in os.walk(ROOT_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    
    md_files.sort()
    
    print(f"Found {len(md_files)} .md files to process\n")
    
    cleaned = 0
    skipped = 0
    errors = 0
    total_chars_removed = 0
    
    for md_file in md_files:
        relative_path = md_file.relative_to(ROOT_DIR)
        success, result = clean_file(md_file)
        
        if success is True:
            cleaned += 1
            total_chars_removed += result
            print(f"✓ {relative_path} ({result} chars removed)")
        elif success is False:
            skipped += 1
            print(f"- {relative_path} (no tags found)")
        else:
            errors += 1
            print(f"✗ {relative_path} (error: {result})")
    
    print("\n" + "="*70)
    print("CLEANUP SUMMARY")
    print("="*70)
    print(f"Files processed:  {len(md_files)}")
    print(f"Files cleaned:    {cleaned}")
    print(f"Files unchanged:  {skipped}")
    print(f"Errors:           {errors}")
    print(f"Total chars removed: {total_chars_removed}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()