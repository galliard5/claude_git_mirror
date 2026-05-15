---
name: File System Instructions
keywords: [rules, instructions, reference]
description: Core project rules and procedures for every session
last_edited_utc: 2026-05-15T18:30:00Z
---

AVAILABLE TOOLS FOR CLAUDE
==========================
**Filesystem Tools (14):**
- Read: filesystem:read_text_file, filesystem:read_multiple_files, filesystem:read_media_file, filesystem:read_file (DEPRECATED)
- Write: filesystem:write_file, filesystem:edit_file, filesystem:create_directory, filesystem:move_file
- Query: filesystem:list_directory, filesystem:list_directory_with_sizes, filesystem:get_file_info, filesystem:directory_tree, filesystem:search_files, filesystem:list_allowed_directories

**Memory Tools (9):** memory:read_graph, memory:create_entities, memory:add_observations, memory:delete_entities, memory:delete_observations, memory:create_relations, memory:delete_relations, memory:open_nodes, memory:search_nodes

**Corpus Search Tools (2):** corpus-search:search_corpus, corpus-search:index_status (custom MCP server — see CORPUS SEARCH below)

**Index Tools (1):** index-tools:rebuild_indexes (custom MCP server — see INDEX REBUILD below)

---

WINDOWS FILESYSTEM ENVIRONMENT
==============================

**MCP filesystem paths**: The filesystem MCP server runs in Docker and serves Linux paths.
  - MCP tool operations use: `/corpus/` as root (e.g. `/corpus/World_Building/Aethelmark/`)
  - Windows host path: `D:\claude\filesystem\` (for git, CMD, File Explorer, Obsidian)
**MCP filesystem tools only**: Use filesystem MCP tools exclusively for corpus operations.
**Root directory**: `/corpus` inside the Docker container — ALL MCP operations confined here.

---

STARTUP PROCEDURES — EXECUTE ON EVERY CONVERSATION START
=========================================================

## STEP 1: PROJECT ROOT & TOP-LEVEL STRUCTURE + DEFERRED TOOL LOAD

**[FIRST] Preload all MCP tools (prevents deferred-tool load errors on first calls):**
Call `tool_search("filesystem read write edit memory corpus index")` immediately at session start.
This loads all 14 filesystem tools, 9 memory tools, 2 corpus-search tools, and 1 index-tools tool into the registry so they're ready for immediate use. Zero cost after first call; eliminates the red parameter-error on initial tool invocations.

**Root:** `/corpus` (Docker container path) — ALL MCP file operations confined here. No exceptions.
**Host path:** `D:\claude\filesystem\` — use this for git, CMD, and native Windows tools.

**BIOS freshness check (every session):**
1. After preloading tools (see above), read `head=8` of `/corpus/file_system_instructions.md`
2. Compare `last_edited_utc` against the project-instructions copy in your context
3. If they differ: warn user `📝 Project-instructions copy of file_system_instructions.md is older than disk version (disk: [date], project: [date]) — consider re-mirroring`
4. If they match or project copy is newer: no message; proceed normally

This catches the common failure mode where the on-disk file is edited but the project-instructions mirror is forgotten.

**Top-level directories:**
- `World_Building/` — All setting content: Aethelmark (active), Gallihammer, archived projects
- `Core_Rules/` — GM rules (`core_rules.md`), extraction rules, templates (never edit originals)
- `Stories/` — Creative writing (gitignored). Originally `.txt`-only; `.md` is fine now.
- `Python/` — Utility scripts and the corpus-search MCP server (see CORPUS SEARCH below)
- `Perchance_prompts/` — Perchance generator prompts
- `Sheet_Import/` — Ingest folder for older/found character sheets pulled from archives. Raw drops at the top level; processed files move to `Sheet_Import/processed/`. Gitignored. Excluded from corpus search index.
- `System_Documentation/` — Reference docs for the indexer, corpus search, Docker, and audit history. Start at `README.md`.
- `Trash/` — Soft-delete destination (no permanent deletes)
- `Miscelanious_RPG_material/` — RPG rulebooks in PDF (often image-based, not text-extractable). Gitignored. Excluded from corpus search index.
- `.github/` — GitHub Codespaces auto-generated; leave alone

**Root files:**
- `file_system_instructions.md` — This file (project rules)
- `file_system_reference.md` — Supplementary reference (load on demand)
- `.gitignore` — Excludes derived artifacts, ingest folders, and personal content from version control

**Index files (now under `/index/`):**
- `index/directory_index.md` — Live directory map (gitignored, see DIRECTORY INDEX below)
- `index/directory_index_with_files.md` — Directory map with full file list (gitignored, load only for heavy filesystem operations)
- `index/search_index.db` — SQLite FTS5 corpus search index (gitignored, consumed by the corpus-search MCP server)

Full directory structure is maintained in `index/directory_index.md` — do not duplicate here.

**GitHub/Codespaces auto-generated files** (created when using GitHub Codespaces for collaborative editing):
- `.vscode/` — VS Code workspace settings; leave alone (regenerated on each Codespaces session)
- `README.md` — Repository overview; can edit for onboarding collaborators, but non-essential
- `.github/pull_request_template` — PR template for collaborators; safe to ignore or customize

## STEP 2: EFFICIENCY PRINCIPLE

- Minimize tool calls; batch reads with `filesystem:read_multiple_files`
- Batch file writes into single operations
- Estimate token cost before multi-file tasks
- **Model selection:** Three tiers — Opus for judgment-heavy work, Sonnet for session running and day-to-day creative execution, Haiku for templated or mechanical execution. See MODEL TIERS & HANDOFF PROTOCOL for tier guidance and handoff format.

## STEP 3: DIRECTORY INDEX

The directory index lives at `/corpus/index/directory_index.md`, generated by `Python/build_indexes.py`. It contains:
- **YAML header** (lines 1–8): frontmatter with `scan_utc` timestamp and `claude_section_end` line number
- **Compressed Claude section** (lines 9–N): single-space-indented tree, no decorators — optimised for token count

**Startup procedure:**
1. Read YAML header only: `filesystem:read_text_file` on `/corpus/index/directory_index.md` with `head=8`
2. Read the Claude section using `head=` with the `claude_section_end` value from YAML. Load into context.
3. Display: `📁 Directory index loaded | Scanned: [date] | Ready`

The index is loaded once at session start and trusted for the duration of the conversation. **No periodic staleness checks.** If the index turns out to be wrong about something mid-session (predicted path doesn't exist, corpus-search returns empty for content that should obviously exist, user mentions structural changes), call `index-tools:rebuild_indexes` to refresh — see STEP 4 below.

**Using the index:**
Reference the loaded compressed tree + conversation context to predict file locations. Use predicted paths as starting points — verify with `filesystem:search_files` or `corpus-search:search_corpus` only when uncertain.

**Mid-session reload after rebuild:** If `index-tools:rebuild_indexes` returns fresh content via `load="directory"` or `load="with_files"`, that fresh content supersedes the index loaded at session start. Use only the most recent.

## STEP 4: INDEX REBUILD

The `index-tools` MCP server exposes one tool for refreshing the on-disk indexes when needed. The tool runs the build scripts directly and optionally returns freshly-built content in the same call.

**`index-tools:rebuild_indexes(load=None)`** — Rebuilds both directory indexes and the corpus search index, then optionally returns content based on `load`:

- `load=None` (default) — rebuild only, return summary
- `load="directory"` — return fresh directory_index.md Claude section
- `load="with_files"` — return fresh directory_index_with_files.md Claude section
- `load="search_status"` — return corpus search index_status (file count + timestamp)

Total runtime: ~0.5 seconds. The bat file `Python/refresh_indexes.bat` is the manual equivalent (double-click from Explorer).

**When to call it:**
- Predicted path lookups failing repeatedly (directory has drifted)
- corpus-search returning empty for content that should obviously exist (search index stale)
- User explicitly says "I just made structural changes, refresh"
- Before heavy filesystem operations where stale paths would cascade

**When NOT to call it:**
- Reflexively at session start (the index loaded at startup is sufficient)
- On a timer (we use reactive freshness, not periodic checks)
- Just because some time has passed (corpus drift between sessions is fine — directory structure is mostly stable)
- After every minor edit (rebuilds are fast but not free; group structural changes)

**Choosing the `load` value:**
- Need to re-orient on directory structure → `"directory"`
- About to do filesystem-intensive work needing full file listings → `"with_files"`
- Just confirming search index rebuilt cleanly → `"search_status"`
- Refreshing proactively, no immediate read needed → leave as default (None)

## STEP 5: CORPUS SEARCH

A custom MCP server (`Python/search_mcp_server.py`) exposes full-text ranked search over the corpus via SQLite FTS5. Two tools:

- **`corpus-search:search_corpus(query, limit=10, category_filter=None)`** — BM25-ranked search across name, keywords, description, category, and content. Returns ranked paths with snippets showing matched context. Higher scores = better matches.
- **`corpus-search:index_status()`** — Returns file count and last-built timestamp. Use to check freshness before relying on results.

**FTS5 query syntax:**
- `Vogt` — single term (porter stem matches Vogt, Vogts, etc.)
- `Vogt security` — both words present (implicit AND)
- `Vogt OR Sable` — either term
- `"Reshaping Cascade"` — exact phrase
- `petition NOT rejected` — boolean exclusion
- `transform*` — prefix match (matches transformed, transformation)

**When to reach for it:**
- Cross-reference questions: "where else is X mentioned" — filesystem search only matches filenames; corpus search matches body content
- Grounding before drafting: pulling all prior references to a character/location before writing session content
- Ambiguous file location: faster than guessing paths when the directory index doesn't make placement obvious
- Session prep: confirming established lore on factions, items, or events that may have been touched in earlier sessions

**When NOT to use it:**
- You already know the path → read the file directly
- Looking for a filename pattern → `filesystem:search_files` is the right tool
- Listing everything in a folder → `filesystem:list_directory`

**Index scope:** Indexes all `.md` files under `/corpus` except: `Trash/`, `Python/`, `Perchance_prompts/`, `Sheet_Import/`, `Miscelanious_rpg_material/`, and hidden/build dirs. The index is a binary SQLite file at `index/search_index.db` — gitignored, rebuilt on demand.

**Refreshing the index:** Use `index-tools:rebuild_indexes` (preferred — runs all three outputs in one pass via `build_indexes.py`). Manual alternative: `refresh_indexes.bat` (double-click from Explorer). Sub-second runtime. Call `corpus-search:index_status` if you need to confirm freshness without rebuilding.

## STEP 6: SEMANTIC FILE PLACEMENT

Directory naming conventions enable inference-based placement.

### Naming convention

**All files and folders use `Snake_Case_With_Capitals`** — underscores between words, leading capital on each significant word. Examples: `Manor`, `House_Steinfeld`, `Senior_Staff`, `Camp_Rochevaux`, `Isalia_Kreiger.md`. JPG filenames match their .md counterparts (`Isalia_Kreiger.jpg`, not `isalia_kreiger.jpg`).

### Top-level placement (Aethelmark)

- **Settings & overview files:** `World_Building/Aethelmark/` (root level — e.g. `Aethelmark.md`, `World_Standards.md`, `Hanging_Threads.md`, `Master_Calendar.md`)
- **Silberbach region:** `World_Building/Aethelmark/Silberbach/`
- **Cendrel region (Kennel Hounds setting):** `World_Building/Aethelmark/Cendrel/`
- **Scenarios (sessions, day briefs, scenario design):** `World_Building/Aethelmark/Scenarios/[Campaign_or_Manor_Name]/`

### Silberbach (the town and surrounding region)

- **Town characters:** `Silberbach/Town/Characters/`
- **Town locations:** `Silberbach/Town/[Location_Name]/`
- **Regional characters:** `Silberbach/Region/Characters/`
- **Regional factions:** `Silberbach/Region/Factions/[Faction_Name]/`
  - **Guilds:** `Region/Factions/Guilds/[Guild_Name]/Characters/` (e.g. Brewers Guild contacts)
  - **Noble Houses:** `Region/Factions/Noble_Houses/[House_Name]/Characters/`
  - **Merchant Families:** `Region/Factions/Merchant_Families/[House_Name]/Characters/`
  - **Isalia's Manor:** `Region/Factions/Manor/` — see *Manor character placement* below

### Cendrel (the Kennel Hounds region — separate campaign from Silberbach)

Cendrel is a related-but-separate region running in parallel with Silberbach (think *Tales of the Sword Coast* alongside *Neverwinter Nights*). Lore lives in `Cendrel/`; sessions live in `Scenarios/Kennel_Hounds/`.

- **Regional patron / overarching figures:** `Cendrel/Characters/` (e.g. Comte Edouard Vellancourt)
- **Setting overview:** `Cendrel/Cendrel.md`, `Cendrel/Kennel_Hounds_Setting.md`, `Cendrel/Timeline_Kennel_Hounds.md`
- **Per-location:** `Cendrel/[Location_Name]/` — currently `Camp_Rochevaux`, `Maruvec`, `Vauclair`. Each has its own `Characters/` subfolder for that location's NPCs.
- **Vauclair-specific:** also has `Vauclair/Clans/` for the three kobold warren clans (Rixek, Sezzin, Veth)
- **Sessions:** `Scenarios/Kennel_Hounds/[Campaign_Name]/` — sessions live separate from lore, named e.g. `Maruvec_Campaign/`, `Vauclair_Campaign/`, `Camp_Rochevaux_Sessions/`

### Manor character placement

Path: `Silberbach/Region/Factions/Manor/Characters/`

Split by **role**, not by transformation status. Pick the best subfolder based on what the character does:

- **Owner/** — Isalia and her direct biographical materials only
- **Senior_Staff/** — department heads (alchemist, head physician, head accountant, security captain, lead enchanter, stable master, head steward, steward, quartermaster, messenger coordinator)
- **Companions/** — breeding programme contractors and intimate-services contractors
- **Transformed_Residents/** — transformed residents whose primary identity is "resident" with no work role assigned (or who are still in adjustment)
- **Peripheral_Staff/** — lower-rank named staff (receptionists, couriers, surrogate group, kitchen assistants, support contractors)
- **Animals/** — non-sapient kennel and stable beasts (mastiff studs, breeding mares, etc.)
- **Clients/** — manor clients (one-off or recurring)

**Sorting rule for transformed-and-working characters:** Sort by their JOB, not by their transformation status.

Examples:
- Vogt (transformed minotaur, Head of Security) → **Senior_Staff** (his job is department head)
- Sable (transformed mare, Stable Master) → **Senior_Staff** (her job is department head)
- Marek (transformed wolf, courier) → **Peripheral_Staff** (his job is courier)
- Kael (manticore stud contractor) → **Companions** (his job is breeding contractor)
- Goran (transformed percheron, no contract, no job) → **Transformed_Residents** (no job to sort by)
- Vesna (8-month-old transformed wolf, still adjusting) → **Transformed_Residents** (no work role yet)

If a character doesn't fit cleanly into any of these seven subfolders, **recommend a new subfolder (with a one-line rationale) before creating it** — don't force-fit and don't silently expand the structure.

### Other top-level

- **Rules:** `Core_Rules/` | **Templates:** `Core_Rules/Templates/`
- **Stories/logs:** `Stories/` | **Scripts:** `Python/`

When uncertain: `filesystem:search_files` to verify. Otherwise trust the structure.

---

NAMING & METADATA
=================

**Naming:** All files and folders use `Snake_Case_With_Capitals` — underscores between words, leading capital on each significant word. Examples: `Manor`, `House_Steinfeld`, `Isalia_Kreiger.md`, `Camp_Rochevaux`. JPG filenames match their .md counterparts (`Isalia_Kreiger.jpg`, not `isalia_kreiger.jpg`). Default output: `.md`. Images: `.jpg` preferred. `.txt` is acceptable in `Stories/`.

**YAML frontmatter (all .md files, lines 1–5):**
```yaml
---
name: Name
type: [optional document category]
keywords: [keyword1, keyword2]
description: One sentence description
---
```

**Field guide:**
- `name` — Document title (required). Use `Snake_Case_With_Capitals`.
- `type` — (optional) Document category for meta-organization. Examples: `setting-document`, `race-document`, `character-sheet`, `scenario`, `rules-reference`. No spaces; use hyphens. Omit if not applicable.
- `keywords` — (required) Comma-separated tags for searchability and discovery.
- `description` — (required) One-sentence summary of document purpose and scope.

*Note:* The legacy `<meta>` pseudo-XML tag format (a single-line tag at the top of `.txt` files) is deprecated. New `.txt` files in `Stories/` don't need it; old files that have it can be left alone or migrated to YAML opportunistically.

---

STRUCTURAL CHANGE PROTOCOL
==========================

When the corpus structure changes meaningfully during a session, update `memory_user_edits` with a brief summary so future sessions inherit the change without needing a fresh index read at the start of every conversation.

**Triggers (any of these):**
- New top-level or major subfolder created
- File moves of more than 2 items at once
- `.gitignore` additions or removals
- New scenarios, campaigns, or major directory branches
- Renames affecting more than 1 file
- Folder reorganization (e.g. splitting a Characters/ folder by role)

**What to record in memory:**
- What changed (one-line summary)
- Where it happened (path)
- Why, if non-obvious

**Examples:**
- "Cendrel/Maruvec/Characters/ added 3 new NPCs from session 3"
- "Moved old Sergovy_Waldheim scenario from Scenarios/ to Trash/"
- "Sheet_Import/Processed/ created and 12 sheets relocated there"
- "Manor/Characters/ split: added Companions/ subfolder for breeding contractors"

**Timing:** Update memory BEFORE the git commit at end of session, so memory and disk land in sync. The next session's startup picks up both.

This protocol is what makes `index-tools:rebuild_indexes` rare-use rather than reflexive. With a memory-first habit, future-Claude already knows about the change and only needs to rebuild when memory is silent on something that should obviously exist.

---

CORE WORKFLOWS
==============

## BATCH WRITE PROTOCOL

1. Accumulate changes during work session
2. Maintain visible pending list: `[PENDING] X files ready to write`
3. User triggers write: "commit", "save all", "batch write", "done"
4. Execute batch write → verify each file with `filesystem:read_text_file`
5. Propose git commit → execute on approval

## GIT COMMIT & PUSH TO GITHUB

**Environment:** Windows CMD only. No bash. Provide copy-paste `cmd` blocks.

**Format:** `[Category]: [Subject] | [Details] | [In-Game Date]`

**Categories:** `Session:` `Scenario Extraction:` `World Building:` `Character:` `Rules Update:` `Project Maintenance:` `Bulk:`

**Example:**
```
Session: Maruvec Campaign 02 | Donor selection, squad briefing | Date: 8 March 1651
```

**Copy & Paste This Block:**
```cmd
D:
cd D:\claude\filesystem
git add .
git commit -m "Your commit message"
git push origin main
```
Replace `"Your commit message"` with your actual message. Select all, copy, paste into CMD. GitHub becomes your backup.

## FILE EDITING

**CRITICAL:** Always `filesystem:read_text_file` immediately before using `filesystem:edit_file`. Never rely on remembered content — `edit_file` requires exact string matching.

Process: Read → identify exact target text → edit with verified string.

## VERIFIED TOOL SCHEMAS (quickref)

The most common tools, condensed. **Full schemas with examples for all 14 filesystem + 9 memory + 2 corpus-search + 1 index-tools tools live in `file_system_reference.md` under TOOL SCHEMA REFERENCE.** Load that file when in doubt about parameters or for tools used less often.

- `filesystem:read_text_file` — `path`, `head?`, `tail?` ⚠ head/tail mutually exclusive
- `filesystem:read_multiple_files` — `paths` (array)
- `filesystem:write_file` — `content`, `path`
- `filesystem:edit_file` — `path`, `edits` [{oldText, newText}], `dryRun?`
- `filesystem:create_directory` — `path`
- `filesystem:move_file` — `source`, `destination`
- `filesystem:list_directory` — `path`
- `filesystem:search_files` — `path`, `pattern`, `excludePatterns?`
- `filesystem:list_allowed_directories` — no params
- `corpus-search:search_corpus` — `query`, `limit?`, `category_filter?`
- `corpus-search:index_status` — no params
- `index-tools:rebuild_indexes` — `load?` (None | "directory" | "with_files" | "search_status")

⚠ If a parameter error fires, run `tool_search` with a relevant keyword to load the live schema.

## WINDOWS PATH REQUIREMENTS

**MCP tool paths** (inside Docker container — use these with filesystem tools):
  - ✓ Correct: `/corpus/World_Building/Aethelmark/filename.md`
  - ✗ Wrong: `D:\claude\filesystem\World_Building\...`

**Windows host paths** (for git, CMD, File Explorer — NOT for MCP tools):
  - ✓ Correct: `D:\claude\filesystem\World_Building\Aethelmark\filename.md`
  - Host root: `D:\claude\filesystem\`

**Directory verification**: Use `filesystem:list_directory` with `/corpus/...` paths
**Search when uncertain**: `filesystem:search_files` with patterns like `*.md`

**Case-only renames are supported**: `filesystem:move_file` with source `kael.jpg` → destination `Kael_the_Amber_Manticore.jpg` works in a single call. Use this to standardize JPG filenames to match their .md counterparts.

## FILE CREATION VERIFICATION

After EVERY `filesystem:write_file`: 
1. Immediately verify with `filesystem:read_text_file` (head=5, tail=5)
2. Check file exists in directory: `filesystem:list_directory` (only when in doubt — the head/tail read above is normally enough)
3. Verify content matches expected structure (YAML frontmatter, etc.)

**Common verification pattern**:
```
filesystem:write_file(content, path)
filesystem:read_text_file(path, head=8)  // Verify frontmatter
filesystem:read_text_file(path, tail=5)  // Verify completion
```

`write_file` can return success but fail silently — ALWAYS verify. (This is the canonical write-verification pattern; ERROR HANDLING below references it rather than re-stating it.)

## MODEL TIERS & HANDOFF PROTOCOL

Three tiers, each with a different sweet spot. Pick by what the work actually needs, not by reflex.

### The three tiers

**Opus** — world-shaping decisions, central character development, lore architecture, multi-step worldbuilding consistency, deep math, anything where per-sentence judgment carries weight. Use where its ceiling matters; expensive elsewhere.

**Sonnet** — session running (canonical use case), NPC dialogue in-play, mechanical resolution with voice, scene execution from a prepped brief, mid-tier creative work. The cost/quality curve bends most usefully here. Sonnet often matches Opus on subjective session quality because GM execution is templated once setup is done — Opus's advantage is in *preparation*, not *execution*.

**Haiku** — templated expansion from clear specs, mechanical transforms, format conversions, batch metadata, filling slots in a known structure. Loses voice and grounding when asked to make judgment calls.

### When each model is the source

- **Opus direct** — central work where Opus's judgment IS the deliverable (main session prep, central character creation, lore architecture)
- **Sonnet direct** — session running, mid-tier NPCs, scene execution, day-to-day creative work
- **Haiku direct** — mechanical execution from a clear spec already in hand

### Handoff trigger phrases

When the user's request matches one of these shapes, **propose a handoff before starting work** (don't auto-invoke — confirm first):

- "Create N [peripheral entities]" where N ≥ 3 — Mode A candidate
- "Format / convert / normalize these files" — Mode B candidate
- "Apply this template to..." — Mode A candidate
- "Clean up / standardize / batch update..." — Mode B candidate (or Python script — check `Python/` first)
- "Generate summaries for sessions X through Y" — Mode A candidate
- End-of-session: "wrap up / write the summary" — Mode A handoff to Haiku from Sonnet

If unsure whether the work qualifies, ask: *"This looks like it could be a Mode A/B handoff — want me to structure it that way, or execute on this model?"*

### When to hand off

Handoff splits work between a judgment model (Opus or Sonnet) and an execution model (Haiku) by emitting instructions for Haiku to execute in a separate session. **Cost savings only materialize when the source model's output volume drops meaningfully** — i.e. when it emits a compact spec that Haiku expands, or compact instructions Haiku applies mechanically. Handoff of full file content (source generates the actual file text, Haiku just writes it) is NOT cheaper — the content gets emitted twice and the second emission is pure overhead.

Use handoff when:
- The output is templated or mechanical — filling slots, applying transforms, format conversion
- The spec fits in a paragraph and any competent assistant could execute it from the brief
- You'd accept Haiku-quality output without wanting to rewrite

Keep on source when:
- Voice, tone, or per-sentence judgment matters
- The content depends on grounding in prior canon
- Math, multi-step logic, or worldbuilding consistency is central
- You'd second-guess the output if Haiku produced it

**Test:** If I wrote the prompt for this as a brief, would a competent assistant produce roughly the same output? If yes → handoff. If no → keep on source.

### Source model for handoffs

- **Opus → Haiku** — when the spec itself needs Opus-grade decisions (peripheral content for central characters, lore-sensitive batch work)
- **Sonnet → Haiku** — when the spec is routine creative work (session summary formatting after a Sonnet-run session, batch peripheral NPCs from established templates, mid-session mechanical transforms). This is the common case; Sonnet writes specs fine.

### Two handoff modes

**Mode A — Templated Expansion**
Source emits compact specs (~200 tokens). Haiku expands each using a known template.
Good for: peripheral NPCs, filler location descriptions, batch background characters, session summary formatting from beat lists.

**Mode B — Mechanical Transformation**
Source identifies what to change. Haiku executes mechanical edits.
Good for: format conversions, case-normalizing filenames, batch metadata updates, applying a structural change to many files.
*Often, a Python script is the right tool here instead — check `Python/` for existing utilities; each script includes header comments describing what it does and how to run it. To write a new script, load `Python_Scripts_Protocol.md` (terse rules) or `System_Documentation/Python_Scripts.md` (full conventions with reasoning).*

### Source Phase

Output a HANDOFF BLOCK with:
- MODE and pre-formatted git commit message
- Per-file: path + spec (Mode A) or path + operation + params (Mode B)

**Source must not call filesystem or memory MCP tools during this phase.** Tool calls during handoff defeat the purpose.

### Handoff Block Format — Mode A (Templated Expansion)

```
===HANDOFF START===
MODE: templated_expansion
COMMIT: "Category: Subject | Details | Date"
TEMPLATE: Core_Rules/Templates/[Template_Name].md

---FILE 1---
PATH: World_Building/.../New_NPC.md
SPEC:
  name: Hans Wolfheim
  role: town watch sergeant
  cultural_context: Silberbach standard
  notable_trait: limp from old wound
  voice_note: gruff but fair
---END FILE---

[additional files...]
===HANDOFF END===
```

### Handoff Block Format — Mode B (Mechanical Transformation)

```
===HANDOFF START===
MODE: mechanical_transform
COMMIT: "Category: Subject | Details | Date"

---FILE 1---
PATH: Stories/old_session.txt
OPERATION: replace_meta_with_yaml
PARAMS:
  yaml_frontmatter:
    name: Maruvec_Session_03
    keywords: [session, maruvec]
    description: Pre-transformation phase complete
---END FILE---

[additional files...]
===HANDOFF END===
```

### Haiku Phase

1. Receive handoff block
2. For each entry: apply template (Mode A) or execute operation (Mode B) with `filesystem:write_file` or `filesystem:edit_file`
3. Verify each per FILE CREATION VERIFICATION
4. Propose git commit using COMMIT line
5. Confirm: `[HANDOFF COMPLETE] X files written`

### Quality check

Spot-check 1-2 files visually before committing. If output quality is off, redo on source — handoff is false economy if it triggers a rewrite.

---

ERROR HANDLING
==============

**3-Strike Rule:** If any filesystem command fails 3 times consecutively → HALT, display error details, await user guidance. No automatic retries past 3.

**No Delete Function:** Use `filesystem:move_file` to `Trash/`. If filename exists in Trash/, search for `Filename*` and increment: `Filename_{n+1}.ext`.

## FILESYSTEM ERROR RECOVERY

**File not found**: 
1. `filesystem:list_directory` to verify parent folder
2. `filesystem:search_files` with filename pattern
3. Check exact Windows path format

**Tool parameter errors**:
1. Verify schema with `tool_search filesystem` (or load `file_system_reference.md`)
2. Check `head`/`tail` not used together
3. Confirm `oldText` exact match for edits

**Write verification**: see FILE CREATION VERIFICATION above — single canonical pattern.

**Folder rename / move EPERM (Windows)**: `filesystem:move_file` on a folder occasionally fails with `EPERM: operation not permitted` even when the folder clearly exists and the destination is clear. This is Windows lock contention — typically Obsidian, an editor, antivirus, or a file watcher holding a handle on something inside the folder. **Workaround:**
1. `filesystem:create_directory` for the new path
2. `filesystem:move_file` each child (file or subfolder) individually into the new path
3. `filesystem:move_file` the now-empty original to `Trash/`

Do NOT count the EPERM failure against the 3-strike rule — it is a known environmental issue with a known workaround. If the workaround itself fails for the same folder, then 3-strike applies.
