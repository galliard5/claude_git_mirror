---
name: File System Instructions
keywords: [rules, instructions, reference]
description: Core project rules and procedures for every session
---

AVAILABLE TOOLS FOR CLAUDE
==========================
**Filesystem Tools (14):**
- Read: filesystem:read_text_file, filesystem:read_multiple_files, filesystem:read_media_file, filesystem:read_file (DEPRECATED)
- Write: filesystem:write_file, filesystem:edit_file, filesystem:create_directory, filesystem:move_file
- Query: filesystem:list_directory, filesystem:list_directory_with_sizes, filesystem:get_file_info, filesystem:directory_tree, filesystem:search_files, filesystem:list_allowed_directories

**Memory Tools:** memory:read_graph, memory:create_entities, memory:add_observations, memory:delete_entities, memory:delete_observations, memory:create_relations, memory:delete_relations, memory:open_nodes, memory:search_nodes

---

STARTUP PROCEDURES — EXECUTE ON EVERY CONVERSATION START
=========================================================

## STEP 1: PROJECT ROOT & DIRECTORY STRUCTURE

**Root:** `D:\Claude_MCP_folder` — ALL file operations confined here. No exceptions.

```
D:\Claude_MCP_folder/
├── World_Building/
│   ├── Aethelmark/                    (Active setting)
│   │   ├── Scenarios/                 (Campaigns + sessions by campaign)
│   │   │   ├── Isalias_Estate/
│   │   │   ├── Kennel_Hounds/
│   │   │   │   ├── Maruvec_Campaign/
│   │   │   │   ├── Vauclair_Campaign/
│   │   │   │   └── Camp_Rochevaux/
│   │   │   └── Viktor_Steinfeld/
│   │   ├── Session_Summaries/         (Legacy — sessions now in Scenarios/)
│   │   ├── Silberbach/
│   │   │   ├── Town/
│   │   │   │   ├── Characters/
│   │   │   │   └── [locations: Market_Square, Crescent_House, etc.]
│   │   │   └── Region/
│   │   │       ├── Factions/ (Guilds/, noble_houses/, merchant_families/, manor/)
│   │   │       ├── Characters/
│   │   │       └── unique_enchanted_items/
│   ├── Dead_Terra/  Little_spark/  Neon_Fang/  (Archives)
│   ├── Rogue_Trader/
│   └── Souls_Gem/
├── Core_Rules/
│   ├── core_rules.md                  (GM rules)
│   ├── Scenario_Extraction_Rules.md
│   └── Templates/                     (Reference only — never edit originals)
├── Stories/                           (.txt only)
├── Python/                            (Utility scripts)
├── Trash/
├── file_system_instructions.md        (This file)
└── file_system_reference.md           (Supplementary — load on demand)
```

**Key Paths:**
- GM Rules: `Core_Rules/core_rules.md`
- Extraction Rules: `Core_Rules/Scenario_Extraction_Rules.md`
- Templates: `Core_Rules/Templates/`
- Reference doc: `file_system_reference.md` (load when needed for templates, Python protocols, detailed format standards, scan process)
- Perchance Prompts: Perchance_prompts/

## STEP 2: EFFICIENCY PRINCIPLE

- Minimize tool calls; batch reads with `filesystem:read_multiple_files`
- Batch file writes into single operations
- Estimate token cost before multi-file tasks
- **Model selection:** For multi-file write tasks, consider Opus→Haiku handoff (see MODEL HANDOFF PROTOCOL). Opus plans with no MCP calls; Haiku writes at ~5x lower token cost.

## STEP 3: DIRECTORY INDEX

The directory index is a live snapshot of the project's directory tree, stored in `memory_user_edits` as `Aethelmark_Directory_Index`. It contains the actual directory structure (no filenames) and a `SCAN_TIMESTAMP`.

**Startup procedure:**
1. Check `memory_user_edits` (command="view") for `Aethelmark_Directory_Index`
2. If found: extract `SCAN_TIMESTAMP`, calculate age
   - Age < 1 day → FRESH — load into context, proceed
   - Age ≥ 1 day → STALE — recommend refresh to user
3. If not found: recommend initial scan to user
4. Display: `📁 Directory index loaded | Last scanned: [date] | [FRESH/STALE] | Ready`

**Scanning (when stale or missing):**
1. Run `filesystem:directory_tree` on `D:\Claude_MCP_folder`
2. Remove any existing `Aethelmark_Directory_Index` entries from `memory_user_edits` before saving
3. Store the directory tree + new timestamp in memory as `Aethelmark_Directory_Index`
4. Directories only — no filenames, no file metadata

**Using the index:**
During the session, reference the loaded index + conversation context to predict file locations. Use predicted paths as starting points — verify with `filesystem:search_files` only when uncertain.

## STEP 4: SEMANTIC FILE PLACEMENT

Directory naming conventions enable inference-based placement:

- **Scenarios/sessions:** `Scenarios/[Campaign_Name]/`
- **Town characters:** `Silberbach/Town/Characters/`
- **Town locations:** `Silberbach/Town/[Location_Name]/`
- **Regional characters:** `Silberbach/Region/Characters/`
- **Regional factions:** `Silberbach/Region/Factions/[Faction_Name]/`
- **Isalia's Manor:** `Silberbach/Region/Factions/manor/`
- **Rules:** `Core_Rules/` | **Templates:** `Core_Rules/Templates/`
- **Stories/logs:** `Stories/` | **Scripts:** `Python/`

When uncertain: `filesystem:search_files` to verify. Otherwise trust the structure.

---

NAMING & METADATA
=================

**Naming:** Underscores for all files/folders. Default output: `.md`. Images: `.jpg` preferred. `.txt` reserved for Stories/ only.

**YAML frontmatter (all .md files, lines 1–4):**
```yaml
---
name: Name
keywords: [keyword1, keyword2]
description: One sentence description
---
```

**.txt meta tag (Stories/ only, line 1):**
```
<meta>name, keyword1, keyword2, brief description</meta>
```

---

CORE WORKFLOWS
==============

## BATCH WRITE PROTOCOL

1. Accumulate changes during work session
2. Maintain visible pending list: `[PENDING] X files ready to write`
3. User triggers write: "commit", "save all", "batch write", "done"
4. Execute batch write → verify each file with `filesystem:read_text_file`
5. Propose git commit → execute on approval

## GIT COMMIT FORMAT

**Environment:** Windows CMD only. No bash. Provide copy-paste `cmd` blocks.

Format: `[Category]: [Subject] | [Details] | [In-Game Date]`

Categories: `Session:` `Scenario Extraction:` `World Building:` `Character:` `Rules Update:` `Project Maintenance:` `Bulk:`

Example:
```
Session: Maruvec Campaign 02 | Donor selection, squad briefing | Date: 8 March 1651
```

```cmd
D:
cd D:\Claude_MCP_folder
git add .
git commit -m "Your commit message"
```

## FILE EDITING

**CRITICAL:** Always `filesystem:read_text_file` immediately before using `filesystem:edit_file`. Never rely on remembered content — `edit_file` requires exact string matching.

Process: Read → identify exact target text → edit with verified string.

## TOOL SCHEMA (verified 2026-03-29)

- `filesystem:write_file` — params: `content`, `path`
- `filesystem:edit_file` — params: `path`, `edits` [{oldText, newText}], `dryRun` (optional)
- `filesystem:read_text_file` — params: `path`, `head` (optional), `tail` (optional)
- `filesystem:read_multiple_files` — param: `paths` (array)

⚠ Common failure: using `description`/`file_text` (those are `create_file` params, not `write_file`). If writes fail, run `tool_search` to reload schema.

## FILE CREATION VERIFICATION

After every `filesystem:write_file`: read the file back immediately. Verify content matches and frontmatter is intact. `write_file` has returned false successes — never trust the return alone.

## MODEL HANDOFF PROTOCOL (Opus → Haiku)

Cost optimization: Opus handles reasoning and content generation with NO MCP tool calls. Haiku handles all filesystem writes at ~5x lower token cost.

### Opus Phase (Chat Output Only — No Tool Calls)
1. Do all reasoning, content generation, path planning
2. Output a HANDOFF BLOCK in chat containing:
   - Each file's destination path
   - Each file's full content
   - Pre-formatted git commit message
3. User saves the handoff block to Project Files, or copies it directly

**Opus must not call any filesystem or memory MCP tools during this phase.**
The entire cost saving depends on Opus producing output tokens only.

### Handoff Block Format
```
===HANDOFF START===
COMMIT: "Category: Subject | Details | Date"

---FILE 1---
PATH: World_Building/Aethelmark/Silberbach/Town/Characters/New_NPC.md
CONTENT:
---
name: NPC Name
keywords: [keyword1, keyword2]
description: One sentence
---
[file body here]
---END FILE---

---FILE 2---
PATH: ...
CONTENT:
...
---END FILE---

===HANDOFF END===
```

### Haiku Phase (Execution)
1. Receive handoff block (via Project File or paste)
2. Parse each file entry
3. `filesystem:write_file` to each destination path
4. Verify each with `filesystem:read_text_file` (per FILE CREATION VERIFICATION)
5. Propose git commit using the COMMIT line from the block
6. Confirm: `[HANDOFF COMPLETE] X files written`

### When to Use
- Batch writes of 3+ files where Opus-quality planning matters
- Session extractions, character creation batches, lore builds
- NOT worth it for single quick edits (overhead exceeds savings)

---

ERROR HANDLING
==============

**3-Strike Rule:** If any filesystem command fails 3 times consecutively → HALT, display error details, await user guidance. No automatic retries past 3.

**No Delete Function:** Use `filesystem:move_file` to `Trash/`. If filename exists in Trash/, search for `Filename*` and increment: `Filename_{n+1}.ext`.
