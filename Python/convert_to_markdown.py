#!/usr/bin/env python3
"""
Batch converter: .txt to .md with meta tag → YAML frontmatter conversion
"""

import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

ROOT_DIR = r"D:\Claude_MCP_folder"
EXCLUDE_DIRS = {".obsidian", "Stories"}
BACKUP_DIR = os.path.join(ROOT_DIR, "BACKUP_TXT_ORIGINALS")

class MetaTagConverter:
    def __init__(self, root_dir, dry_run=False, keep_txt=True, no_backup=False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.keep_txt = keep_txt
        self.no_backup = no_backup
        self.backup_dir = Path(BACKUP_DIR) if not no_backup else None
        self.log = []
        self.stats = {"files_found": 0, "files_converted": 0, "files_failed": 0}
        self.errors = []
    
    def log_message(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log.append(log_entry)
        print(log_entry)
    
    def find_txt_files(self):
        txt_files = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if file.endswith(".txt"):
                    full_path = Path(root) / file
                    txt_files.append(full_path)
        return sorted(txt_files)
    
    def parse_meta_tag(self, content):
        match = re.match(r'^<meta>(.*?)</meta>', content.strip())
        if not match:
            return None, None, None
        meta_content = match.group(1)
        parts = [p.strip() for p in meta_content.split(",")]
        if len(parts) < 2:
            return None, None, None
        name = parts[0]
        keywords = parts[1:-1] if len(parts) > 2 else []
        description = parts[-1]
        return name, keywords, description
    
    def create_yaml_frontmatter(self, name, keywords, description):
        if keywords:
            keywords_yaml = "[" + ", ".join(keywords) + "]"
        else:
            keywords_yaml = "[]"
        yaml = f"""---
name: {name}
keywords: {keywords_yaml}
description: {description}
---
"""
        return yaml
    
    def convert_file(self, txt_path):
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.split('\n')
            first_line = lines[0] if lines else ""
            name, keywords, description = self.parse_meta_tag(first_line)
            if name is None:
                return False, None, "No valid meta tag found in first line"
            remaining_content = '\n'.join(lines[1:]).strip()
            yaml_frontmatter = self.create_yaml_frontmatter(name, keywords, description)
            md_content = yaml_frontmatter
            if remaining_content:
                md_content += "\n" + remaining_content + "\n"
            else:
                md_content += "\n"
            md_path = txt_path.with_suffix('.md')
            if not self.dry_run:
                if self.backup_dir and not self.no_backup:
                    backup_dir = self.backup_dir / txt_path.relative_to(self.root_dir).parent
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    backup_path = backup_dir / txt_path.name
                    shutil.copy2(txt_path, backup_path)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                if not self.keep_txt:
                    os.remove(txt_path)
            return True, md_path, None
        except Exception as e:
            return False, None, str(e)
    
    def run(self):
        print("\n" + "="*70)
        print("TXT → MD CONVERSION TOOL")
        print("="*70)
        if self.dry_run:
            print("⚠️  DRY RUN MODE - No files will be modified\n")
        print(f"Root directory: {self.root_dir}")
        print(f"Backup directory: {self.backup_dir if not self.no_backup else 'DISABLED'}")
        print(f"Keep original .txt files: {self.keep_txt}\n")
        print("Scanning for .txt files...")
        txt_files = self.find_txt_files()
        self.stats["files_found"] = len(txt_files)
        print(f"Found {len(txt_files)} .txt files to convert\n")
        if len(txt_files) == 0:
            print("No .txt files found. Exiting.")
            return
        print("Files to process:")
        for i, txt_path in enumerate(txt_files, 1):
            relative_path = txt_path.relative_to(self.root_dir)
            print(f"  {i:3d}. {relative_path}")
        if not self.dry_run:
            print("\n" + "="*70)
            response = input("Proceed with conversion? (yes/no): ").strip().lower()
            if response not in ["yes", "y"]:
                print("Conversion cancelled.")
                return
        print("\n" + "="*70)
        print("CONVERTING FILES...")
        print("="*70 + "\n")
        for txt_path in txt_files:
            relative_path = txt_path.relative_to(self.root_dir)
            success, md_path, error = self.convert_file(txt_path)
            if success:
                self.stats["files_converted"] += 1
                md_relative = md_path.relative_to(self.root_dir)
                if self.dry_run:
                    self.log_message("PREVIEW", f"Would convert: {relative_path} → {md_relative}")
                else:
                    action = "Created" if self.keep_txt else "Converted"
                    self.log_message("SUCCESS", f"{action}: {relative_path} → {md_relative}")
            else:
                self.stats["files_failed"] += 1
                self.log_message("ERROR", f"Failed to convert {relative_path}: {error}")
                self.errors.append((relative_path, error))
        print("\n" + "="*70)
        print("CONVERSION SUMMARY")
        print("="*70)
        print(f"Files found:     {self.stats['files_found']}")
        print(f"Files converted: {self.stats['files_converted']}")
        print(f"Files failed:    {self.stats['files_failed']}")
        if self.errors:
            print("\nERRORS:")
            for path, error in self.errors:
                print(f"  ✗ {path}: {error}")
        if not self.dry_run:
            if self.keep_txt:
                print(f"\n✓ .txt files preserved")
                print(f"✓ New .md files created alongside")
            else:
                print(f"\n✓ .txt files converted to .md and deleted")
                if not self.no_backup:
                    print(f"✓ Backups saved to: {self.backup_dir}")
        log_file = self.root_dir / "CONVERSION_LOG.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.log))
        print(f"\nDetailed log saved to: {log_file}")
        print("\n" + "="*70)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Convert .txt files to .md with YAML frontmatter")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--delete-txt", action="store_true", help="Delete original .txt files")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup directory")
    args = parser.parse_args()
    converter = MetaTagConverter(ROOT_DIR, dry_run=args.dry_run, keep_txt=not args.delete_txt, no_backup=args.no_backup)
    converter.run()

if __name__ == "__main__":
    main()
