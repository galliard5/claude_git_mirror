---
name: File System Reference
keywords: [reference, schemas, templates, procedures, protocols]
description: Supplementary procedures, tool schemas, and standards — load on demand from file_system_instructions.md
---

This file supplements `file_system_instructions.md`. Load when needed for:
- Complete tool schemas with examples (every filesystem and memory tool)
- Template usage
- Full scan process
- Python script protocols
- Detailed file format standards
- Memory recovery

---

TOOL SCHEMA REFERENCE
=====================

Complete schemas for all filesystem and memory tools, captured by direct introspection via `tool_search`. If a schema appears wrong or a tool returns an unexpected error, re-verify with `tool_search` and update this section.

## Filesystem Read Tools (4)

### `filesystem:read_text_file`
Read complete contents of a text file. Use `head` for first N lines, `tail` for last N lines.
```
params:
  path: string (required)
  head?: number   — first N lines
  tail?: number   — last N lines
```
**⚠ CRITICAL:** Cannot use `head` and `tail` simultaneously — they are mutually exclusive.

**Examples:**
- `path="D:\Claude_MCP_folder\directory_index.md", head=8` — read YAML header only
- `path="D:\...\character.md", tail=10` — verify file completion
- `path="D:\...\file.md"` — read entire file

### `filesystem:read_multiple_files`
Read multiple files in one call. More efficient than sequential reads. Failed reads for individual files don't stop the operation.
```
params:
  paths: array[string] (required, minItems: 1)
```
**Example:** `paths=["D:\...\file1.md", "D:\...\file2.md", "D:\...\file3.md"]`

**⚠ Caveat:** Many large files in one call can produce oversized payloads. If timing out, fall back to sequential `read_text_file` calls.

### `filesystem:read_media_file`
Read an image or audio file. Returns base64 data + MIME type.
```
params:
  path: string (required)
```
**Example:** `path="D:\...\Characters\Owner\Isalia_Kreiger.jpg"`

### `filesystem:read_file` *(DEPRECATED)*
Legacy alias for `read_text_file`. Same params. Do not use in new code.

## Filesystem Write Tools (4)

### `filesystem:write_file`
Create a new file or completely overwrite an existing file. **No warning on overwrite.**
```
params:
  content: string (required)
  path: string (required)
```
**Example:** `content="---\nname: New File\n---\n\nBody", path="D:\...\NewFile.md"`

**Verification pattern (always do this):**
```
filesystem:write_file(content, path)
filesystem:read_text_file(path, head=5)   — verify start
filesystem:read_text_file(path, tail=3)   — verify end
```

### `filesystem:edit_file`
Line-based edits via exact string match. Returns git-style diff.
```
params:
  path: string (required)
  edits: array[{oldText: string, newText: string}] (required)
  dryRun?: boolean   — default false; preview without applying
```
**⚠ CRITICAL:** `oldText` must match the file EXACTLY — whitespace, newlines, all characters. Always `read_text_file` immediately before editing. After any successful edit, prior `read_text_file` output of the same file is stale; re-read before further edits.

**Multi-edit example:**
```
edits=[
  {oldText: "Old line one", newText: "New line one"},
  {oldText: "Old line two", newText: "New line two"}
]
```

**Anchor pattern for short snippets:** Use a two-line anchor for uniqueness when removing or editing short content:
```
oldText="| Line above the target |\n| Target line to remove |"
newText="| Line above the target |"
```

### `filesystem:create_directory`
Create a directory. Silently succeeds if directory already exists. Can create nested paths in one call.
```
params:
  path: string (required)
```
**Example:** `path="D:\Claude_MCP_folder\World_Building\New_Setting\Characters"`

### `filesystem:move_file`
Move or rename files and directories. Single operation handles both. **Fails if destination already exists.**
```
params:
  source: string (required)
  destination: string (required)
```
**Examples:**
- Rename in place: `source="D:\...\Old_Name.md", destination="D:\...\New_Name.md"`
- Move to subfolder: `source="D:\...\Characters\X.md", destination="D:\...\Characters\Senior_Staff\X.md"`
- Soft delete: `source="D:\...\Bad_File.md", destination="D:\Claude_MCP_folder\Trash\Bad_File.md"`
- Case-only rename (Windows-supported): `source="D:\...\kael.jpg", destination="D:\...\Kael_the_Amber_Manticore.jpg"`

## Filesystem Query Tools (6)

### `filesystem:list_directory`
List all files and directories in a path. Output uses `[FILE]` and `[DIR]` prefixes.
```
params:
  path: string (required)
```
**Note:** Empty directories produce no output (the call succeeds but returns nothing). To verify a directory is empty, this returning silence is the confirmation.

### `filesystem:list_directory_with_sizes`
List contents with file sizes. Useful for finding the largest files in a folder.
```
params:
  path: string (required)
  sortBy?: string   — "name" (default) or "size"
```
**Example:** `path="D:\...\Manor", sortBy="size"` — list manor files largest first

### `filesystem:get_file_info`
File/directory metadata: size, created/modified/accessed timestamps, permissions, isDirectory, isFile.
```
params:
  path: string (required)
```
**Use case:** Check if a file exists, when last modified, or how large — without reading content.

### `filesystem:directory_tree`
Recursive JSON tree of a path. Each entry has `name`, `type` (file|directory), and `children` (for directories).
```
params:
  path: string (required)
  excludePatterns?: array[string]   — default []
```
**Use case:** Generating directory_index.md (the Python script does this); rare in normal Claude work because output gets large fast.

### `filesystem:search_files`
Recursive search by glob pattern. Returns full paths.
```
params:
  path: string (required)
  pattern: string (required)
  excludePatterns?: array[string]   — default []
```
**Examples:**
- `path="D:\...\Aethelmark", pattern="*.md"` — every .md in Aethelmark and subdirs
- `path="D:\Claude_MCP_folder", pattern="Briar*"` — every file starting with Briar
- `path="D:\...\Manor", pattern="*.md", excludePatterns=["Trash"]` — with exclusion

**⚠ Note:** Pattern is glob-style (`*.ext`, `**/*.ext`), NOT regex.

### `filesystem:list_allowed_directories`
Returns the list of directories this server can access. No params.

## Memory Tools (9)

These operate on a knowledge graph stored separately from the filesystem. Used rarely in this project (the directory index file plus userMemories cover most needs), but available if needed.

### `memory:read_graph`
Read the entire knowledge graph. No params.

### `memory:search_nodes`
Search graph by query string against entity names, types, and observation content.
```
params:
  query: string (required)
```

### `memory:open_nodes`
Retrieve specific entities by name.
```
params:
  names: array[string] (required)
```

### `memory:create_entities`
Create new entities in the knowledge graph.
```
params:
  entities: array[{name: string, entityType: string, observations: array[string]}] (required)
```

### `memory:add_observations`
Add observations to existing entities.
```
params:
  observations: array[{entityName: string, contents: array[string]}] (required)
```

### `memory:create_relations`
Create relations between entities. Use active voice for relationType.
```
params:
  relations: array[{from: string, to: string, relationType: string}] (required)
```

### `memory:delete_entities`
```
params:
  entityNames: array[string] (required)
```

### `memory:delete_observations`
```
params:
  deletions: array[{entityName: string, observations: array[string]}] (required)
```

### `memory:delete_relations`
```
params:
  relations: array[{from: string, to: string, relationType: string}] (required)
```

## Schema verification command

If any schema above appears wrong or a tool returns an unexpected parameter error:
```
tool_search(query="<keyword that matches the tool>")
```
This loads the live tool definition from the MCP server and shows the current schema. Update this reference if the live schema differs from what's documented here.

---

SCAN PROCESS (When Index is Stale or Missing)
=============================================

**⚠ STALE SECTION below — describes the old `memory_user_edits` index approach. Current approach: the directory index lives in `D:\Claude_MCP_folder\directory_index.md`, generated by `Python\map_directory.py`. See `file_system_instructions.md` Step 3 for the live procedure. The text below is preserved for historical context only.**

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
