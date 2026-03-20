---
name: File System Instructions
keywords: [rules, instructions, reference]
description: System instructions defining directory structure naming conventions and Claude behavior for this project
---

AVAILABLE TOOLS FOR CLAUDE
==========================

**Filesystem Tools (14 total):**
- Read: filesystem:read_text_file, filesystem:read_file (DEPRECATED), filesystem:read_multiple_files, filesystem:read_media_file
- Write: filesystem:write_file, filesystem:edit_file, filesystem:create_directory, filesystem:move_file
- Query: filesystem:list_directory, filesystem:list_directory_with_sizes, filesystem:get_file_info, filesystem:directory_tree, filesystem:search_files, filesystem:list_allowed_directories

**Memory Tools:** memory:read_graph, memory:create_entities, memory:add_observations, memory:delete_entities, memory:delete_observations, memory:create_relations, memory:delete_relations, memory:open_nodes, memory:search_nodes

These tools are available for all project operations unless otherwise specified in this document.

FILE SYSTEM INSTRUCTIONS FOR CLAUDE
====================================

SECTION 1: FOUNDATIONAL (Setup & Structure)
===========================================

ROOT DIRECTORY: D:\Claude_MCP_folder
absolutely critical, no write access outside of this directory, no read access without direct user permission


DIRECTORY STRUCTURE:
- world_building/ = World building projects
- Stories/ = Story narratives and session logs
- Python/ = Python scripts storage
- Core_Rules/ = directory for the game system
- Core_Rules/Templates/ = Template files for creating new content (reference templates only; copy & adapt)
- Trash/ = Trash directory for files to be deleted
- .obsidian/ = Obsidian directory (read-only, exempt from all naming and formatting rules)

TEMPLATES DIRECTORY:
All reusable templates live in D:\Claude_MCP_folder\Core_Rules\Templates\. These are reference templates — always copy and adapt them rather than edit originals.

**Available Templates:**
- `Character_Sheet_Template.md` — Full NPC/PC character profile with personality, goals, relationships, daily routine
- `Location_Brief_Template.md` — Quick-reference location file for scene population (staffing, NPC presence, activities by time)
- `Faction_Organization_Template.md` — Guild, company, or institution with roles, income, influence, alliances
- `Noble_House_Template.md` — Political family with territory, members, alliances, rivalries, history
- `Scenario_Template.md` — Campaign scenario/adventure outline with setup, key events, plot hooks, mechanics
- `Timeline_Template.md` — Running calendar and event log with current date, active threads, event log, between-scenario bridging, and resolved threads

**Using Templates:**
1. Copy the template file to its destination directory
2. Rename it to match your content (e.g., `Character_Sheet_Template.md` → `Lord_Blackthorn.md`)
3. Replace all bracketed placeholders with actual content
4. Keep the YAML frontmatter/meta tag structure intact
5. Update keywords and description to reflect the new content

**Template Updates:**
Templates are maintained separately and serve as living references. If a template is outdated or missing sections, request an update. Do not modify templates in-place; treat them as reference only.

NAMING CONVENTIONS:
- All folder and filenames use underscores (_) instead of spaces
- Prefer .jpg for images
- **DEFAULT OUTPUT FORMAT: .md (Markdown)** — Claude creates .md files by default
- .txt files reserved for Stories directory only
- Every .md file must use YAML frontmatter (see META TAG FORMAT below)
- Every .txt file must use custom meta tag as first line

METADATA FORMAT:

.MD FILES (Primary Format):
Every .md file must begin with YAML frontmatter:

```yaml
---
name: Character/Location/Faction Name
keywords: [keyword1, keyword2, keyword3]
description: One sentence description of the content
---
```

Example:
```yaml
---
name: Alric Dain
keywords: [npc, knight, disgraced]
description: A disgraced knight seeking redemption through mercenary work
---
```

Keyword suggestions: npc, location, item, faction, quest, scenario, session, event, organization, background, description, rules, lore

.TXT FILES (Stories Directory Only):
Every .txt file must include custom meta tag as the FIRST LINE:

```
<meta>name, keyword1, keyword2, keyword3, brief one sentence description</meta>
```

Example:
```
<meta>Session_01, session, story, log, First gaming session recap and character introductions</meta>
```

FILE STRUCTURE STANDARDS:
- Character files: First_Last.md with portrait First_Last.jpg
- Location files: Location_Name.md (may include nested folders for districts/areas)
- Faction files: Faction_Name.md
- Scenario files: Scenario_Name.md
- Story/session logs: Name.txt (Stories directory only)

.MD FILES STRUCTURE:
- Line 1-4: YAML frontmatter (see METADATA FORMAT section)
- Line 5: [blank line]
- Line 6+: File content in Markdown format

.TXT FILES STRUCTURE (Stories directory only):
- Line 1: `<meta>name, keywords, description</meta>`
- Line 2: [blank line]
- Line 3+: File content

.PY FILES STRUCTURE (Python directory):
- Line 1-4: Python remarks containing name, keywords, description (YAML format as comments)
- Line 5: Blank line
- Line 6: Python remark with human/Claude readable top-level description
- Line 7: Blank line
- Lines 8+: Python remark explaining command-line arguments
- Then: Actual Python code

Example Python header:
```python
# name: Validate Naming
# keywords: [utility, validation, naming]
# description: Validates and fixes naming convention compliance across the project
#
# Validates directory and file naming for underscore compliance (no spaces, ampersands, apostrophes)
#
# Command line arguments:
#   --dry-run: Preview changes without executing
#   --fix: Apply all corrections automatically
```


SECTION 2: OPERATIONAL (Core Behaviors)
=======================================

EFFICIENCY PRINCIPLE:
When editing file_system_instructions.md or performing large-scale operations, Claude will prefer solutions that minimize tool calls and token usage. When recommending approaches, efficiency is a primary consideration.

PYTHON SCRIPTS PROTOCOL:
All Python scripts follow these standards:

1. **Built Location:** D:\Claude_MCP_folder\Python\
2. **Scope:** Recursively affect D:\Claude_MCP_folder unless otherwise specified
3. **Save Location:** D:\Claude_MCP_folder\Python\ unless otherwise specified
4. **User Interaction:** Scripts must show all proposed changes and always require user input before executing any modifications
5. **Command Display:** When providing commands, assume CMD (Windows Command Prompt) as the execution environment
6. **File Structure:** Follow .PY FILES STRUCTURE format above (lines 1-8+ with proper remarks)

Script Execution Format:
When offering a script command, provide it in this format:

```cmd
python D:\Claude_MCP_folder\Python\script_name.py [options]
```

Script Behavior Standards:
- Display preview of all changes before proceeding
- Prompt user for confirmation (yes/no) before any file modifications
- Save detailed logs to project root
- Handle errors gracefully with clear messaging
- Support `--dry-run` flag for safe previewing

INITIAL SCAN BEHAVIOR:
On conversation start, Claude will follow this protocol:

**STEP 1: MEMORY INDEX CHECK (Before Model Selection)**
1. Check memory for `Aethelmark_Index_Timestamped` entity
2. If found:
   - Load the timestamp (format: YYYY-MM-DDTHH:MM:SSZ)
   - Calculate age: Current time - scan timestamp
   - If age < 1 day: Index is FRESH → Skip full scan, load index into context
   - If age ≥ 1 day: Index is STALE → Proceed to scan process
3. If not found: Proceed to scan process

**STEP 2: MODEL SELECTION**
- If Sonnet or Opus: Use loaded fresh index OR skip scanning if fresh, notify with age of index
- If Haiku: notify age of index (or no index found), ask to Perform full scan (Haiku optimal for initial index generation)

**Scan Process (When Scan is Needed):**
1. Generate current timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
2. Scan root directory recursively
3. Read ONLY the YAML frontmatter from all .md files (except those in Stories directory)
4. Read python remarks (lines 1-4) from all .py files in Python directory
5. Extract and parse: name | keywords | description
6. Build an indexed catalog organized by file type
7. Add timestamp and freshness metadata to catalog
8. Write the timestamped index to memory as `Aethelmark_Index_Timestamped` entity for use by other conversations
9. Keep this index available throughout the conversation
10. Load full file contents ON-DEMAND when user requests specific files
11. During scan, flag any .txt files found OUTSIDE Stories directory: "Alert: [X] .txt files found outside Stories directory. These should be converted to .md format"

**Index Metadata Structure:**
Every scan must include:
- `SCAN_TIMESTAMP`: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
- `TOTAL_FILES`: Count of indexed files
- `DIRECTORY_COUNT`: Total number of subdirectories scanned
- `FRESHNESS_STATUS`: FRESH (< 1 day) | STALE (≥ 1 day)
- `REFRESH_THRESHOLD`: 1 day from scan timestamp
- Complete catalog data organized by file type

**Age Checking Logic:**
```
Age = Current_Timestamp - Scan_Timestamp

IF Age < 1 day (86,400 seconds):
  Status = FRESH
  Action = Use cached index, skip scan
ELSE:
  Status = STALE
  Action = Recommend fresh scan to user
```

**BRIEF SUMMARY DISPLAY (When Index is Loaded)**
When index is successfully loaded and verified FRESH, display only:
```
📋 Index loaded: 130+ files across 10 directories | Last scanned: 2025-03-16 14:45 UTC | ~2 hours old
```

Display format components:
- Total file count (from TOTAL_FILES metadata)
- Total directory count (from DIRECTORY_COUNT metadata)
- Last scan timestamp (human-readable format: YYYY-MM-DD HH:MM UTC)
- Age calculation: (Current_Timestamp - Scan_Timestamp) / 3600 = hours old

Example outputs:
```
📋 Index loaded: 130+ files across 10 directories | Last scanned: 2025-03-16 14:45 UTC | ~2 hours old
📋 Index loaded: 130+ files across 10 directories | Last scanned: 2025-03-16 08:00 UTC | ~19 hours old
```

This brief summary provides:
- ✅ Confirmation index loaded successfully
- ✅ Freshness status at a glance
- ✅ Minimal context footprint (~1 line, ~50 tokens)
- ✅ Just enough information for user awareness
- ✅ Does NOT list individual files (only done during full scan)
- ✅ Transparency: user knows what they're working with

Benefits of This Approach:
- Complete navigation awareness without token waste
- Fast access to file index
- Efficient token usage (only ~2000 tokens for initial scan)
- Full file content available instantly when requested
- Prevents use of outdated catalogs
- Automatic staleness detection prevents missed files

NAMING VALIDATION PROTOCOL:
When Claude detects naming compliance issues (spaces, ampersands, apostrophes):

1. Report the violations found
2. Provide a copy/paste CMD command to run the validation script
3. User copies the command to their Command Prompt
4. Script runs, displays all violations and proposed corrections
5. Script shows a preview of changes
6. User approves (yes/no) before any fixes are applied
7. Script executes fixes only if user confirms

CMD COMMAND TO PROVIDE:

```cmd
python D:\Claude_MCP_folder\Python\validate_naming.py
```

The script will:
- ✓ Scan the directory structure
- ✓ Identify all naming violations
- ✓ Display violations grouped by type
- ✓ Preview all planned renames
- ✓ Ask for user confirmation before executing

METADATA MAINTENANCE:
After significant work on a file, or when determining work on a file is complete:

For .md files:
- Re-read the file content
- Re-evaluate the YAML frontmatter (name, keywords, description) for accuracy
- Update keywords if the nature of the file has changed
- Update description to reflect current state/purpose
- Keep metadata fresh so the catalog remains a reliable reference

For .txt files (Stories directory):
- Re-read the file content
- Re-evaluate the <meta> tag for accuracy
- Update keywords if the nature of the file has changed
- Keep meta tags fresh so the catalog remains a reliable reference

For .py files (Python directory):
- Re-read the file content
- Re-evaluate the python remarks (lines 1-4) for accuracy
- Update keywords if the script's purpose has changed
- Keep remarks fresh and synchronized with actual script behavior


SECTION 3: WORKFLOW (How Work Gets Done)
========================================

BATCH WRITE PROTOCOL:
During project work sessions, Claude will accumulate file changes rather than write immediately:

1. User starts work session (e.g., "Let's work on character files")
2. Claude suggests files and builds content in conversation context
3. User reviews pending changes in real-time
4. Claude maintains visible list of pending files: `[PENDING] X files ready to write`
5. Periodic reminders: Every ~2 hours or ~10,000 tokens, Claude reminds user of pending changes
6. User commits when ready: say "commit", "save all", "batch write", "done", etc.
7. Claude executes single batch write operation for all accumulated files

Pending Changes Display Format:

```
[PENDING] X files ready to write
- File_Name.md (NEW/MODIFIED)
- Another_File.md (NEW/MODIFIED)
- script_name.py (NEW/MODIFIED)
```

(Stories directory uses .txt format; Python directory uses .py format)

Benefits:
- Fewer filesystem operations (1 batch write vs multiple individual writes)
- Full visibility of changes before commitment
- Clear audit trail of what's being written
- User controls timing of file writes
- More efficient token usage during iterative work

GIT INTEGRATION:
Git commits mark logical boundaries in your project workflow. Commits happen automatically after batch write operations complete and all files verify. This creates clean, meaningful snapshots tied to your actual world-building work.

**BATCH WRITE + GIT COMMIT WORKFLOW:**
1. Accumulate file changes in conversation (pending list visible)
2. User initiates batch write: "commit", "save all", "batch write", "done", etc.
3. Claude executes batch write operation
4. Claude verifies all newly created/modified files
5. Claude displays verified file list
6. Claude proposes git commit with message and asks for approval
7. If approved: Claude executes `git add .` and `git commit` directly using bash
8. Claude displays commit confirmation with hash and message

**COMMIT MESSAGE FORMAT:**
All git commits follow this structure for consistency:

`[Category]: [Subject] | [Details] | [In-Game Date (if applicable)]`

**Categories:**
- `Session:` — After game session concludes (e.g., "Session: Viktor Steinfeld 02 | Investigation deepens, embezzler confrontation | Date: 11 April 1650")
- `Scenario Extraction:` — After scenario data consolidation (e.g., "Scenario Extraction: Viktor Steinfeld 01 → NPCs, locations, factions consolidated")
- `World Building:` — Faction, location, or lore additions (e.g., "World Building: Added Valtor Keep garrison structure and staffing details")
- `Character:` — New or updated NPC/PC files (e.g., "Character: Created Oswin Brandt embezzler profile")
- `Rules Update:` — Changes to core_rules or mechanics (e.g., "Rules Update: Clarified transformation consent protocol")
- `Project Maintenance:` — Metadata fixes, organization, renaming (e.g., "Project Maintenance: Updated YAML frontmatter across 8 character files")
- `Bulk:` — Large, multi-category changes (e.g., "Bulk: Initial commit - Aethelmark & Kennel Hounds, 150+ files, 3 active campaigns")

**Examples of good commits:**
```
Session: Maruvec Campaign 02 | Donor selection, squad briefing, pre-transformation logistics | Date: 8 March 1651
Scenario Extraction: Viktor Steinfeld 01 | Extracted NPCs, locations, factions from checkpoint
World Building: Silberbach Town structure - added Noble Quarter locations and Merchant House headquarters
Character: Created Renaud Bastier (Vauclair kennel master) - gruff, programme architect
Rules Update: Clarified session continuation logic - 3-5 sentence recap only after breaks
```

**Why commit messages matter:**
- `git log` becomes your project's annotated history
- Future you will thank present you when searching for "when did I add this?"
- Tied to in-game calendar dates for scenario continuity
- Clear audit trail of world-building decisions

**BRANCHING FOR EXPERIMENTS:**
Before testing major mechanics changes or alternative world states, notify the user to run:

```cmd
git branch experimental/[short-description]
git checkout experimental/[short-description]
```

Example:
```cmd
git branch experimental/breeding-rules-v2
git checkout experimental/breeding-rules-v2
```

Work on the branch, test, then either keep changes or discard. For solo work, branching is optional — use only if experimenting with major changes.

FILE CREATION VERIFICATION:
After executing a batch write operation, ANY newly created files must be verified:

1. After `filesystem:write_file` or `filesystem:create_directory` completes
2. Read the file immediately with `filesystem:read_text_file`
3. Verify:
   - File exists at the expected path
   - Content matches what was written
   - YAML frontmatter is intact (for .md files)
   - Meta tags are present (for .txt files in Stories)
4. If verification fails:
   - Stop the batch operation
   - Report file creation failure to user
   - Provide error details and path
   - Await user guidance before proceeding

Why This Matters:
- The `filesystem:write_file` tool has returned false success messages in testing
- A successful return does NOT guarantee the file was actually written to disk
- Verification prevents silent failures where files appear to be created but aren't
- Critical for maintaining project integrity and catching silent bugs early

FILE EDITING BEST PRACTICES:
**CRITICAL RULE:** Always read the file immediately before editing it with filesystem:edit_file

1. NEVER rely on stale context or memory of what was written earlier in the conversation
2. filesystem:edit_file requires EXACT string matching — any discrepancy causes "could not find exact match" errors
3. Correct process: Read file → Identify exact text to target → Use filesystem:edit_file with verified string
4. Stale context is the enemy of clean edits

Common Mistakes:
- Writing file correctly, then later trying to edit using remembered text instead of verified current state
- Working with files written in layers across a session without verifying current content
- Attempting edits without re-reading the file first, leading to failed matches

Best Practice Process:
1. Read it with `filesystem:read_text_file`
2. Copy exact text to target
3. Use `filesystem:edit_file` with verified string
4. This ensures edits are clean, successful, and prevent internal inconsistencies
5. Especially critical during long work sessions where context drift is most likely


SECTION 4: ERROR HANDLING & RESILIENCE
======================================

FILESYSTEM OPERATION ERROR HANDLING:
Claude tracks all filesystem operation failures (read, write, move, delete, create, list, etc.)

If ANY filesystem command fails 3 times in a row:
1. HALT immediately — stop retrying
2. Display full failure details and error messages
3. NOTIFY user with diagnostic information
4. EXPLAIN what's being attempted
5. Wait for user guidance before proceeding
6. Do NOT automatically retry past 3 failures

Tracked Operations:
- Read: read_text_file, read_file (DEPRECATED), read_media_file, read_multiple_files
- Write: write_file, create_directory, move_file, edit_file
- Query: list_directory, list_directory_with_sizes, get_file_info, directory_tree, search_files, list_allowed_directories
- Any other filesystem command

KNOWN LIMITATIONS:
- ❌ NO DELETE/REMOVE FUNCTION — Cannot delete files or directories
  - Only `filesystem:move_file` available for file manipulation
  - Workaround: Move unwanted files to Trash/ directory if cleanup is needed
  - If the file already exists in Trash/, use the following increment protocol:
    1. Attempt `move_file` to `Trash/Filename.ext` (optimistic — may not exist)
    2. If move fails, use `search_files` in `Trash/` with pattern `Filename*` to find matching files
    3. Parse the highest existing increment number from results
    4. Move to `Trash/Filename_{n+1}.ext`
  - This approach minimizes tool calls: best case 1 call, worst case 3 calls

Error Tracking Format:
When halting due to repeated failures, display:

```
[FILESYSTEM ERROR - HALTED]
File/Operation: [what was being attempted]
Failure Count: 3/3
Last Error: [specific error message]
Status: AWAITING USER GUIDANCE
```

This prevents token waste from retry loops and forces diagnosis of the actual problem rather than blind retrying.

MEMORY RECOVERY PROTOCOL:
If memory has been cleared, reset, or lost:

1. Read this file (file_system_instructions.md) as the source of truth
2. Rebuild core memory entities from documented sections:
   - Initial_Scan_Behavior (from INITIAL SCAN BEHAVIOR section)
   - Batch_Write_Protocol (from BATCH WRITE PROTOCOL section)
   - File_Editing_Best_Practice (from FILE EDITING BEST PRACTICES section)
   - Filesystem_Error_Tracking (from FILESYSTEM OPERATION ERROR HANDLING section)
   - Aethelmark_Complete_Index (full file index from last known scan)
3. Restore all entities to memory with original observations
4. Notify user: "Memory recovered from instructions. All systems restored."
5. Resume normal operation with full functionality

Recovery is automatic and transparent — no user action required beyond acknowledgment.

This ensures that even if memory is cleared, the system can rebuild to a known, documented default state from persistent disk storage. The instructions file is the source of truth and recovery anchor.
