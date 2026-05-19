# Claude Code Context — Aethelmark & Gallihammer Projects
<!-- Auto-generated from claude.ai userMemories. Refresh periodically. -->
<!-- Host path: D:\claude\filesystem\Claude_Code_Context.md -->

## Purpose & Context

This file provides persistent project context for Claude Code sessions. It covers two major interconnected creative projects: **Gallihammer** (grimdark science fantasy worldbuilding and TTRPG) and **Aethelmark** (dark fantasy worldbuilding and TTRPG). Both are managed as structured file systems under `D:\claude\filesystem\` with MCP filesystem integration, version control via git, and an Obsidian-compatible directory structure.

---

## Filesystem Layout

**MCP Docker paths** (use with MCP tools): `/corpus/` as root
**Windows host path** (use with git, CMD, Explorer): `D:\claude\filesystem\`

```
D:\claude\filesystem\
├── file_system_instructions.md     ← system/project rules (STARTUP: Steps 1–6)
├── .gitignore
├── index/
│   ├── directory_index.md          ← live directory map (check freshness)
│   ├── directory_index_with_files.md
│   └── search_index.db             ← SQLite FTS5 corpus search index
├── World_Building\
│   ├── Gallihammer\
│   └── Aethelmark\
│       ├── Silberbach\
│       │   └── Region\Factions\
│       │       ├── Manor\          ← Isalia's Manor (Characters/, Buildings/)
│       │       ├── Noble_Houses\
│       │       ├── Guilds\
│       │       └── Merchant_Families\
│       ├── Cendrel\                ← Kennel Hounds region
│       │   ├── Camp_Rochevaux\
│       │   ├── Maruvec\
│       │   └── Vauclair\
│       └── Scenarios\
│           ├── Isalias_Estate\
│           └── Kennel_Hounds\
├── Core_Rules\
│   ├── core_rules.md
│   ├── Scenario_Extraction_Rules.md
│   └── Templates\
├── Stories\
├── Python\                         ← utility scripts + MCP servers
├── System_Documentation\
└── .obsidian\
```

**Key location shortcuts:**
- GM rules: `Core_Rules/core_rules.md`
- System rules: `file_system_instructions.md` (root)
- Isalia's Manor: `World_Building/Aethelmark/Silberbach/Region/Factions/Manor/`
- Isalia character: `.../Manor/Characters/Owner/Isalia_Kreiger.md`

---

## Naming & File Conventions

- All files and folders: `Snake_Case_With_Capitals`
- Default output format: `.md`
- YAML frontmatter required on all `.md` files (lines 1–5):
  ```yaml
  ---
  name: Name
  keywords: [keyword1, keyword2]
  description: One sentence description.
  ---
  ```
- Images: `.jpg` preferred, filename matches `.md` counterpart

---

## Project: Gallihammer

Post-collapse science fantasy set ~30,000–40,000 years after a stellar empire's fall. Draws on Warhammer 40K aesthetics and HFY web serial sensibilities.

**Key lore:**
- The Warp is an ecological environment, not a supernatural realm
- The Mechanicus is the dominant post-collapse institution
- Biomancy traces to ancient Luna-based Selenar gene-cults
- AI taboo stems from historical AGI failures

**Active campaign — Archaeos Expedition:**
- Player character: **Si'ken** (kobold reshaped into insectoid hybrid scout)
- Vessel: *The Proving Ground* (converted medium transport, ~2.5km, Mechanicus archaeological expedition vessel, Forge-Monastery Valdrekk on planet Calthris)
- Session 1 complete
- Key crew: Commander Torrin Hale, Ship Master Kael Oenthe, Chief Archaeologist Sera Voss, Chief Enginseer Maret Vos, Skitarii Alpha Dren Harsk, Senior Logik Renn Cade, Senior Archivist Maren Pael, Chirugen Liss Thrace
- Ship has XCOM-style development system (7 upgrade categories fed by field salvage)

---

## Project: Aethelmark

Dark fantasy kingdom (Cendrel) inspired by Burgundy. Burgundy-adjacent European aesthetic, 16th century feel. Runs multiple active campaigns.

**Central feature:** Sapient hound transformation — volunteers undergo permanent biological reshaping — running across multiple pilot sites.

### Active Campaigns

**Nobles Commission (Isalia's Manor):**
- Sessions 01–06 in directory; sessions 01–05 confirmed complete
- Current in-world date: **20 Apr 1650** (Session 04 checkpoint)
- Key events: Corvin/Marta arrival, Crescent collar removal, intake protocol drafting, Aldric Venn intake, hearing confirmed 3 May, Seria appearing voluntarily

**Maruvec Campaign:**
- Sessions 01–02 complete (pre-transformation); session 3 summary status unclear
- PC: **Isandar Quickclaw** (kobold, 19, dock-born)
- Squad: Théo Marchais, Sable Venn, Perrin Aldec, Dix; Kennel Master Colette Varre
- Donor hound Brac selected; transformation scheduled end-of-week in-world

**Camp Rochevaux:**
- Sessions 01–07 summaries present; full extraction complete
- Squad transformed; buyer facility raided; supply chain exposed
- Act 3 pending

**Viktor Steinfeld:**
- Session 01 complete (10 Apr 1650)
- Viktor is a pregnant mare
- Active threads: Oswin Brandt embezzlement (51 gold, 3 years, confessed), Corvel money-laundering investigation, Meerhold inspection pending, Voss & Kraemer solicitors summoned

**Vauclair Campaign:**
- Summary 01 + location/kennel files present; first volunteer transforming

**Sergovy Waldheim:** Pending (mid–late April in-world)

### Key NPCs — Isalia's Manor

| Name | Role | Notes |
|------|------|-------|
| Isalia Kreiger | Owner | Blue kobold, 70, retired 20th-level barbarian |
| Captain Albrecht Vogt | Head of Security | Transformed minotaur |
| Sable | Stable Master | Transformed dark bay mare |
| Alric Dain | Lead Alchemist | Former battlefield surgeon |
| Elowen Vale | Lead Enchanter | Elf, designs speech collars |
| Elias Varn | Estate Steward | Kobold, discreet administrator |
| Dr. Selene Korr | Head Physician | Medical care |
| Renn | Woodward | Transformed direwolf, patrols grounds |

### Manor Character Placement (subfolder rules)

Path: `Manor/Characters/`

- **Owner/** — Isalia only
- **Senior_Staff/** — department heads (sort by job, not transformation status)
- **Companions/** — breeding/intimate-services contractors
- **Transformed_Residents/** — residents with no assigned work role
- **Peripheral_Staff/** — lower-rank named staff
- **Animals/** — non-sapient kennel/stable beasts
- **Clients/** — manor clients

### On the Horizon

- Rochevaux Act 3
- Sergovy Waldheim campaign launch
- Nobles Commission hearing (~2 May in-world)
- Alric fertility appointment (24 Apr in-world)

---

## World Standards (Aethelmark)

- **Date format:** DD.Month YYYY (e.g. `20.April.1650`)
- **Currency:** Copper Pence / Silver Dollar / Gold Crown / Platinum Throne (100:10:1:0.1)
- **Timekeeping:** Canonical church bells (Matutin / Laudes / Prim / Terz / Sext / Non / Vesper / Komplet)
- **Calendar:** 12 months, Januar–Dezember
- **Legal hierarchy:** Imperial > Ducal > County > Town > Guild
- **Distance:** Estate ~1 mile from Silberbach Market Square

---

## Tools & Infrastructure

- **MCP servers:** filesystem (rooted at `D:\claude\filesystem\`), memory (graph, mostly retired), corpus-search (`Python/search_mcp_server.py`), index-tools (`Python/index_tools_mcp_server.py`)
- **Claude Desktop config:** `C:\Users\galliard\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Obsidian:** `.obsidian/` at project root; files use YAML frontmatter, `**bold**` headers, `[[WikiLink]]` internal references
- **Git:** version control from `D:\claude\filesystem\`
- **Perchance:** `perchance.org/enhanced-ai-story` — template at `Python/Perchance_AI_Story_Template.md`
- **Map format:** `.wxx` (Worldographer); spec at `Core_Rules/Wxx_Map_Format_Spec.md`; toolchain at `Python/worldographer/`

### Model Tiers

- **Opus** — world-shaping decisions, lore architecture, deep consistency work
- **Sonnet** — session running (canonical), NPC dialogue, scene execution, day-to-day creative
- **Haiku** — templated expansion, mechanical transforms, batch metadata

### Git Commit Format

```
[Category]: [Subject] | [Details] | [In-Game Date]
```

Categories: `Session:` `Scenario Extraction:` `World Building:` `Character:` `Rules Update:` `Project Maintenance:` `Bulk:`

---

## Key Learnings & Patterns

- `filesystem:edit_file` with `oldText`/`newText` pairs required for in-place edits; always read file immediately before editing
- Always verify writes with a follow-up read (check YAML frontmatter at top, completion at bottom)
- `filesystem:search_files` with glob `**/*filename*` reliably locates files when exact name is uncertain
- Directory creation requires separate calls per level
- Cross-thread MCP file access is not possible
- The MCP memory graph (`memory.jsonl`) is largely retired; `userMemories` (claude.ai) is the active continuity system

---

*Last synced from claude.ai userMemories: 2026-05-19*
