---
name: File System Reference
keywords: [reference, schemas, templates, procedures, protocols]
description: Supplementary procedures, tool schemas, and standards — load on demand from file_system_instructions.md
---

This file supplements `file_system_instructions.md`. Load when needed for:
- Complete tool schemas with examples (filesystem, memory, corpus-search)
- Template usage
- Index refresh tooling and conventions
- Python script protocols
- Detailed file format standards

---

TOOL SCHEMA REFERENCE
=====================

Complete schemas for all filesystem, memory, and corpus-search tools, captured by direct introspection via `tool_search`. If a schema appears wrong or a tool returns an unexpected error, re-verify with `tool_search` and update this section.

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

**Tip:** Use `dryRun=true` first when applying many edits to a file in a single batch. The returned diff lets you verify the full result before committing.

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
**Use case:** Full structural snapshots when working on a specific subtree (e.g. confirming the layout under `Cendrel/` before adding new content). The `Python\map_directory.py` script uses this internally; in Claude work it's most useful for verifying complex multi-level structures at once rather than repeated `list_directory` calls.

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

**⚠ Note:** Pattern is glob-style (`*.ext`, `**/*.ext`), NOT regex. Matches against filenames only — for body-content search, use `corpus-search:search_corpus` instead.

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

## Corpus Search Tools (2)

Custom MCP server exposing FTS5 ranked search over the corpus. See the CORPUS SEARCH section in `file_system_instructions.md` for the high-level when-to-use guidance. Schemas:

### `corpus-search:search_corpus`
Full-text ranked search across name, keywords, description, category, and content. Returns formatted output: ranked path list with snippets showing matched context (terms wrapped in `**`).
```
params:
  query: string (required)         — FTS5 expression
  limit?: integer                  — default 10
  category_filter?: string|null    — optional path-segment filter
```
**FTS5 query syntax:**
- `Vogt` — single term (porter stem matches Vogt, Vogts, etc.)
- `Vogt security` — both words present (implicit AND)
- `Vogt OR Sable` — either term
- `"Reshaping Cascade"` — exact phrase (escape inner quotes by doubling: `""`)
- `petition NOT rejected` — boolean exclusion
- `transform*` — prefix match (matches transformed, transformation)

**`category_filter` examples:**
- `"Aethelmark"` — restrict to Aethelmark subtree
- `"Manor"` — restrict to manor-related content
- `"Senior_Staff"` — restrict to that specific subfolder

**BM25 ranking weights:** name (10×), keywords (5×), description (3×), content (1×). Higher score magnitude = better match. Hits in name and frontmatter rise above pure body matches automatically.

**Common pitfalls:**
- Apostrophes are tokenizer separators: `Isalia's` indexes as `["isalia", "s"]`. Search `Isalia` to match.
- Special characters can produce FTS5 syntax errors — wrap problem terms in double quotes or use prefix matching.
- Files without YAML frontmatter still get indexed (filename is used as name) but lose the high-weight metadata fields.

### `corpus-search:index_status`
Returns the database path, total indexed file count, and last-built timestamp. No params.

**Use case:** Before relying on a search result for time-sensitive work, confirm the index is fresh. If `index_status` shows the build is older than a recent corpus change, prompt the user to refresh.

## Schema verification command

If any schema above appears wrong or a tool returns an unexpected parameter error:
```
tool_search(query="<keyword that matches the tool>")
```
This loads the live tool definition from the MCP server and shows the current schema. Update this reference if the live schema differs from what's documented here.

---

INDEX REFRESH TOOLING
=====================

Three derived files are rebuilt from the corpus on demand. All three are gitignored.

| File | Built by | Purpose |
|------|----------|---------|
| `directory_index.md` | `Python/map_directory.py` | Compressed directory tree (loaded at session start) |
| `directory_index_with_files.md` | `Python/map_directory_with_files.py` | Directory tree with full file list (load on demand) |
| `Python/search_index.db` | `Python/build_search_index.py` | SQLite FTS5 index for `corpus-search` MCP server |

## `refresh_indexes.bat` (canonical refresh path)

`Python/refresh_indexes.bat` runs all three rebuild scripts in sequence with errorlevel chaining. Sub-second total runtime. Double-click from Explorer or invoke from CMD.

**Sequence:** `map_directory.py → map_directory_with_files.py → build_search_index.py`. If any step fails (non-zero exit), the chain halts at that step with a `[FAIL]` message and pauses for inspection.

## `--no-pause` flag

All three rebuild scripts accept `--no-pause` to skip the "Press Enter to exit" prompt. The bat file uses this flag so the orchestrated chain runs unattended. When run individually (e.g. double-clicked from Explorer), scripts pause at the end so output stays visible.

```cmd
python build_search_index.py            # interactive: pauses for Enter
python build_search_index.py --no-pause # automated: exits immediately
```

## Runtime stats

Each rebuild script prints a `Runtime:` line in its summary block (e.g. `0.063s`). This is display-only — never written to the index files themselves — and exists for sanity-checking that nothing has gotten unexpectedly slow.

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
- No required header. The legacy `<meta>...</meta>` pseudo-XML tag from early in the project is deprecated; new `.txt` files don't need it.
- `.md` is also acceptable in `Stories/` and is the preferred format for new creative work.

**.py files (Python/ only):**
```python
# name: Script Name
# keywords: [keyword1, keyword2]
# description: What this script does
#
# Human-readable top-level description
#
# Command line arguments:
#   --dry-run: Preview without executing (modification scripts only)
#   --no-pause: Skip end-of-run pause (rebuild scripts only)
```

---

PYTHON SCRIPTS PROTOCOL
========================

- Last verified Python version: 3.14.3
- All scripts live in `D:\Claude_MCP_folder\Python\`
- Scope: recursively affect project root unless specified otherwise
- Execution environment: Windows CMD

```cmd
python D:\Claude_MCP_folder\Python\script_name.py [options]
```

## Two script categories with different conventions

**Modification scripts** — write to or rename corpus files. Examples: `validate_naming.py`, `cleanup_legacy_tags.py`, `convert_to_markdown.py`, `process_session_summary.py`.

- Must support `--dry-run` flag for preview
- Must require user confirmation before modifying files
- Must preview all proposed changes before applying

**Rebuild / read-only scripts** — generate derived artifacts (indexes, exports), never modify corpus files. Examples: `map_directory.py`, `map_directory_with_files.py`, `build_search_index.py`.

- No `--dry-run` needed (no destructive action on corpus)
- Run freely from CMD or via `refresh_indexes.bat`
- Support `--no-pause` for unattended execution from the bat file

## Naming validation

```cmd
python D:\Claude_MCP_folder\Python\validate_naming.py
```
Scans for naming violations (spaces, ampersands, apostrophes), previews fixes, requires approval. Modification script — supports `--dry-run`.

---

METADATA MAINTENANCE
====================

After significant work on a file, re-read and re-evaluate its metadata (YAML frontmatter for .md files, header comments for .py files). Update keywords and description to reflect current content. Keeps the corpus search index reliable, since name/keywords/description are weighted highest in BM25 ranking.

When a file's metadata changes, the next `refresh_indexes.bat` run picks up the new values automatically — no manual reindex step needed.

---

GIT BRANCHING (Experiments)
===========================

For major mechanics changes or alternative world states:
```cmd
git branch experimental/[short-description]
git checkout experimental/[short-description]
```
Work, test, then keep or discard. Optional for solo work.
