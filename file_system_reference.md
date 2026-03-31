---
name: File System Reference
keywords: [reference, templates, procedures, protocols]
description: Supplementary procedures and standards — load on demand from file_system_instructions.md
---

This file supplements `file_system_instructions.md`. Load when needed for:
- Template usage
- Full scan process
- Python script protocols
- Detailed file format standards
- Memory recovery

---

SCAN PROCESS (When Index is Stale or Missing)
=============================================

1. Run `filesystem:directory_tree` on `D:\Claude_MCP_folder` recursively
2. Capture directory structure only — no filenames, no file metadata, no YAML reading
3. Generate timestamp (ISO 8601: YYYY-MM-DDTHH:MM:SSZ)
4. Remove any existing `Aethelmark_Directory_Index` entries from `memory_user_edits` before saving
5. Save to `memory_user_edits` as `Aethelmark_Directory_Index`:
   - Include `SCAN_TIMESTAMP=` prefix
   - Include the full directory tree (directories only)
   - This is the live map Claude references for file placement
6. Display: `📁 Directory index loaded | Last scanned: [date] | FRESH | Ready`

**Format example:**
```
Aethelmark_Directory_Index: SCAN_TIMESTAMP=2026-03-30T00:00:00Z | World_Building/(Aethelmark/(Scenarios/(Isalias_Estate/, Kennel_Hounds/(Maruvec_Campaign/, ...), ...), Silberbach/(Town/(Characters/, ...), Region/(Factions/(manor/, ...), Characters/, ...)), ...), Core_Rules/(Templates/), Stories/, Python/, Trash/)
```
Compact notation keeps token cost low while preserving full structure.

---

TEMPLATES
=========

Located: `Core_Rules/Templates/` — Copy and adapt, never edit originals.

Available:
- `Character_Sheet_Template.md` — NPC/PC profile (personality, goals, relationships, routine)
- `Location_Brief_Template.md` — Scene population (staffing, NPC presence, activities by time)
- `Faction_Organization_Template.md` — Guild/institution (roles, income, influence, alliances)
- `Noble_House_Template.md` — Political family (territory, members, alliances, rivalries)
- `Scenario_Template.md` — Adventure outline (setup, key events, hooks, mechanics)
- `Timeline_Template.md` — Calendar/event log (active threads, bridging, resolved)
- `Day_Brief_Template.md` — GM prep for session-ready daily briefs
- `Session_Summary_Quick_Capture.md` — Rapid session summary format

**Usage:** Copy template → rename to match content → replace bracketed placeholders → keep YAML frontmatter intact → update keywords/description.

---

FILE FORMAT STANDARDS
=====================

**.md files:**
- Lines 1–4: YAML frontmatter
- Line 5: blank
- Line 6+: Markdown content
- Character files: `First_Last.md` (portrait: `First_Last.jpg`)

**.txt files (Stories/ only):**
- Line 1: `<meta>name, keywords, description</meta>`
- Line 2: blank
- Line 3+: content

**.py files (Python/ only):**
```python
# name: Script Name
# keywords: [keyword1, keyword2]
# description: What this script does
#
# Human-readable top-level description
#
# Command line arguments:
#   --dry-run: Preview without executing
#   --fix: Apply corrections
```

---

PYTHON SCRIPTS PROTOCOL
========================

- Built and saved in `D:\Claude_MCP_folder\Python\`
- Scope: recursively affect project root unless specified otherwise
- Must preview all changes and require user confirmation before modifying files
- Support `--dry-run` flag
- Execution environment: Windows CMD

```cmd
python D:\Claude_MCP_folder\Python\script_name.py [options]
```

**Naming Validation:**
```cmd
python D:\Claude_MCP_folder\Python\validate_naming.py
```
Scans for naming violations (spaces, ampersands, apostrophes), previews fixes, requires approval.

---

METADATA MAINTENANCE
====================

After significant work on a file, re-read and re-evaluate its metadata (YAML frontmatter for .md, meta tags for .txt, remarks for .py). Update keywords and description to reflect current content. Keeps the catalog reliable.

---

GIT BRANCHING (Experiments)
===========================

For major mechanics changes or alternative world states:
```cmd
git branch experimental/[short-description]
git checkout experimental/[short-description]
```
Work, test, then keep or discard. Optional for solo work.

---

MEMORY RECOVERY PROTOCOL
=========================

If memory is cleared or lost:
1. Read `file_system_instructions.md` as source of truth
2. Rebuild core memory entities from documented sections
3. Notify user: "Memory recovered from instructions. All systems restored."
4. Resume normal operation

Automatic and transparent — no user action required.
