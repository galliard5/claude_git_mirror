# Claude Code Context — Aethelmark & Gallihammer Projects
<!-- Synced from claude.ai userMemories. Regenerate periodically. -->
<!-- Last sync: 2026-05-19 -->

---

## Filesystem Layout

**MCP Docker root:** `/corpus/`
**Windows host root:** `D:\claude\filesystem\`

**Top-level directories:**
- `World_Building/` — all setting content
- `Core_Rules/` — GM rules, templates, extraction rules
- `Stories/` — creative writing (gitignored)
- `Python/` — utility scripts + MCP servers
- `Trash/` — soft-delete destination
- `index/` — directory_index.md, directory_index_with_files.md, search_index.db
- `System_Documentation/` — reference docs for indexer, corpus search, Docker
- `Other_References/` — miscellaneous reference material
- `Miscelanious_RPG_material/` — RPG PDFs (gitignored, excluded from corpus search)
- `Perchance_prompts/` — Perchance generator prompts
- `Sheet_Import/` — ingest folder for character sheets (gitignored)

**Root files:** `file_system_instructions.md`, `.gitignore`, `Claude_Code_Context.md`

---

## Naming & File Conventions

- All files and folders: `Snake_Case_With_Capitals`
- Default output: `.md`
- Images: `.jpg`, filename matches `.md` counterpart
- YAML frontmatter required on all `.md` files (lines 1–5):

```yaml
---
name: Name
keywords: [keyword1, keyword2]
description: One sentence description.
---
```

---

## Directory Structure (Aethelmark)

```
World_Building/Aethelmark/
├── Cendrel/                          ← Kennel Hounds region
│   ├── Camp_Rochevaux/Characters/
│   ├── Maruvec/Characters/
│   ├── Vauclair/Characters/ + Clans/
│   └── Characters/                   ← region-level NPCs (e.g. Vellancourt)
├── Scenarios/
│   ├── Isalias_Manor/Day_Briefs/     ← Nobles Commission sessions
│   ├── Cendrel/
│   │   ├── Camp_Rochevaux_Campaign/
│   │   ├── Maruvec_Campaign/
│   │   └── Vauclair_Campaign/
│   ├── Viktor_Steinfeld/
│   └── Scenario_prompts/
└── Silberbach/
    ├── Region/
    │   ├── Characters/
    │   ├── Factions/
    │   │   ├── Guilds/[11 guilds]/Characters/
    │   │   ├── Manor/Characters/
    │   │   │   ├── Owner/
    │   │   │   ├── Senior_Staff/
    │   │   │   ├── Companions/
    │   │   │   ├── Transformed_Residents/
    │   │   │   ├── Peripheral_Staff/
    │   │   │   ├── Animals/
    │   │   │   └── Clients/
    │   │   ├── Noble_Houses/[10 houses]/Characters/
    │   │   └── Merchant_Families/[3 families]/Characters/
    │   └── Unique_Enchanted_Items/
    └── Town/Characters/

World_Building/Gallihammer/
├── Archaeos_Expedition/Characters/ + Recovered_Technology/ + Scenarios/ + Ship/ + Sites/
├── Dead_Terra/
├── Equipment/
└── Rogue_Trader/

World_Building/Other_Projects/
├── Neon_Fang/Cells/ + Characters/
├── Souls_Gem/
├── Little_spark/
└── Character_Pool/
```

**Key paths:**
- GM rules: `Core_Rules/core_rules.md`
- System rules: `file_system_instructions.md` (root)
- Templates: `Core_Rules/Templates/`
- Isalia's Manor: `World_Building/Aethelmark/Silberbach/Region/Factions/Manor/`
- Isalia character: `.../Manor/Characters/Owner/Isalia_Kreiger.md`
- Cendrel lore: `World_Building/Aethelmark/Cendrel/`
- Sessions: `Scenarios/Isalias_Manor/`, `Scenarios/Cendrel/`, `Scenarios/Viktor_Steinfeld/`

---

## Project: Gallihammer

Post-collapse science fantasy set ~30,000–40,000 years after a stellar empire's fall. Draws on Warhammer 40K aesthetics and HFY web serial sensibilities.

**Key lore:**
- The Warp is an ecological environment, not a supernatural realm
- The Mechanicus is the dominant post-collapse institution
- Biomancy traces to ancient Luna-based Selenar gene-cults
- AI taboo stems from historical AGI failures

**Active campaign — Archaeos Expedition:**
- PC: **Si'ken** (kobold reshaped into insectoid hybrid scout)
- Vessel: *The Proving Ground* (converted medium transport, ~2.5km; Mechanicus archaeological expedition, Forge-Monastery Valdrekk, planet Calthris)
- Session 1 complete; approaching Chief Enginseer Vos in engineering at session end
- Ship has XCOM-style development system (7 upgrade categories fed by field salvage)
- Crew: Commander Torrin Hale, Ship Master Kael Oenthe, Chief Archaeologist Sera Voss, Chief Enginseer Maret Vos, Skitarii Alpha Dren Harsk, Senior Logik Renn Cade, Senior Archivist Maren Pael, Chirugen Liss Thrace

---

## Project: Aethelmark

Dark fantasy kingdom, 16th century Central European feel, Burgundy-inspired. Runs multiple active campaigns.

**Central feature:** Sapient hound transformation — volunteers undergo permanent biological reshaping. Framework: 5-yr enlistment, speaking collar retained, donor determines sex outcome.

### Silberbach Region

Town of ~5,000–6,000 on the Angerap River. Ruled by Count Elias Valtor from Valtor Keep. Locations: Market_Square, Harbor_District, Old_Temple, Silver_Eel, Drowned_Rat, Merchants_Close, Vanders_Currency_Exchange, Weavers_Row.

**Factions** (all under `Silberbach/Region/Factions/`):
- 11 Guilds (each with `Characters/` subfolder)
- Noble Houses: Kreiger, Valtor, Steinfeld, Waldheim, Kaelen, Aldenberg, Grauwald, Meerhold, Rennic, Rothwyn
- Merchant Families: Farrow, Vale, Welser

### Isalia's Manor

Owner: Isalia Kreiger (blue kobold, 70yo, retired 20th-level barbarian).

**Senior Staff** (sort by job, not transformation status):

| Name | Role | Form |
|------|------|------|
| Captain Albrecht Vogt | Head of Security | Transformed minotaur |
| Sable | Stable Master | Transformed dark bay mare |
| Alric Dain | Lead Alchemist | Human |
| Dr. Selene Korr | Head Physician | Human |
| Elowen Vale | Lead Enchanter | Elf |
| Elias Varn | Estate Steward | Kobold |

**Peripheral Staff:** Lyra, Mira, Rennik, Kira, Renn (woodward, direwolf)

**Transformed Residents:** Anthony Valtor (imperial witness), Kael (amber manticore), Lira (sable doe), Nyssa (moonlit vixen), Silas (obsidian stallion), Vorik (iron boar)

**Services:** transformation, breeding, medical, enchantments, alchemy

### Cendrel (Kennel Hounds Region)

Patron: Comte Edouard Vellancourt. Gritty tone, black-market integration.

| Site | Status | Session path |
|------|--------|-------------|
| Vauclair (border town) | Session 01 done, first volunteer transforming | `Scenarios/Cendrel/Vauclair_Campaign/` |
| Maruvec (city) | Sessions 1,2,4,5,6 done; session 3 missing | `Scenarios/Cendrel/Maruvec_Campaign/` |
| Camp Rochevaux | Sessions 1–7 done, Act 3 pending | `Scenarios/Cendrel/Camp_Rochevaux_Campaign/` |

**Vauclair:** ~3,000 surface + 800–1,000 warren, Greyvasse pass mouth. Clans: Rixek (conservative), Sezzin (merchants), Veth (pragmatic). Garrison: Elise Marenne (commander), Renaud Bastier (kennel master). ⚠ Vauclair alchemist name needs verification — old notes say "Corvel" but may be confused with Aldus Corvel (Silberbach money launderer).

**Maruvec:** PC = Isandar Quickclaw (kobold, 19, dock-born). Squad: Théo Marchais, Sable Venn, Perrin Aldec, Dix. Kennel Master: Colette Varre. Donor hound: Brac. Transformation scheduled end-of-week in-world.

**Camp Rochevaux:** Squad transformed; buyer facility raided; supply chain exposed. Key NPCs added: Lenne Souchard, The Buyer, Gregor, Joren, Gate Man. Lore at `Cendrel/Camp_Rochevaux/` (15 character files, Buyers_Facility.md).

### Other Active Campaigns

**Nobles Commission (Isalia's Manor):**
- Sessions 01–06 in `Scenarios/Isalias_Manor/` (01–05 confirmed complete, 06 verify)
- Supporting files: `Estate_Daily_Life.md`, `Serya_Integration.md`, `Day_Briefs/` (2 files)
- Current in-world date: **22 April 1650**
- Hearing confirmed 3 May; Seria appearing voluntarily

**Viktor Steinfeld:**
- Session 01 complete, 10 Apr 1650. Path: `Scenarios/Viktor_Steinfeld/`
- Viktor is a pregnant mare (foal sire: Greymarch stallion, due late June–early July 1650)
- Estate staff: Lukas (cousin, acting admin), Hannah Voss (stablemaster), Pell, Mrs Aldenmarch
- Active threads: Oswin Brandt embezzlement (51 gold, 3 years, confessed), Corvel money-laundering investigation, Meerhold inspection pending, Voss & Kraemer solicitors summoned

**Sergovy Waldheim:** Pending (mid–late April in-world)

### Noble Houses

Path: `Silberbach/Region/Factions/Noble_Houses/`

- **Kreiger** — Duke Romaine + Duchess Iaxiandra (blue dragon), Isalia's parents
- **Valtor** — Count Elias, Silberbach ruler; Gerran Valtor (steward, embezzler)
- **Steinfeld** — Viktor's house
- **Waldheim** — Sergovy's house, forest/timber
- **Kaelen** — Baron Torvin, reformist
- **Aldenberg** — Corvel connection, Mira von Aldenberg (noble fugitive)
- **Grauwald, Meerhold** (breeding stock), **Rennic** (Lady Seria), **Rothwyn**

Imperial transformation archives sealed at Isalia's manor under imperial privilege.

---

## World Standards (Aethelmark)

- **Date format:** `DD.Month YYYY` (e.g. `22.April.1650`)
- **Currency:** Copper Pence / Silver Dollar / Gold Crown / Platinum Throne (100:10:1:0.1). Treasury bars = 1,000× coin equivalent.
- **Timekeeping:** Canonical church bells — Matutin, Laudes, Prim, Terz, Sext, Non, Vesper, Komplet
- **Calendar:** 12 months, Januar–Dezember
- **Legal hierarchy:** Imperial > Ducal > County > Town > Guild
- **Distance:** Estate ~1 mile from Silberbach Market Square

---

## Tools & Infrastructure

- **MCP servers:** filesystem (`D:\claude\filesystem\`), corpus-search (`Python/search_mcp_server.py`), index-tools (`Python/index_tools_mcp_server.py`). Memory MCP retired 2026-05-19.
- **Claude Desktop config:** `C:\Users\galliard\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Claude\claude_desktop_config.json`
- **Index files:** `index/directory_index.md`, `index/directory_index_with_files.md`, `index/search_index.db`
- **Obsidian:** `.obsidian/` at project root; YAML frontmatter, `**bold**` headers, `[[WikiLink]]` refs
- **Git:** from `D:\claude\filesystem\`; commit format: `[Category]: [Subject] | [Details] | [In-Game Date]`
- **Map format:** `.wxx` (Worldographer); spec at `Core_Rules/Wxx_Map_Format_Spec.md`; toolchain at `Python/worldographer/`
- **Perchance:** `perchance.org/enhanced-ai-story`; template at `Perchance_prompts/`

### Python Utilities (`Python/`)

- `validate_naming.py` — checks underscores, flags spaces/ampersands/apostrophes
- `cleanup_legacy_tags.py` — removes legacy `[TEXT]` tag format
- `convert_to_markdown.py` — batch `.txt` → `.md` with meta → YAML conversion
- `process_session_summary.py` — quick-capture → formatted session logs

### Model Tiers

- **Opus** — world-shaping decisions, lore architecture, deep consistency, central character work
- **Sonnet** — session running (canonical), NPC dialogue, scene execution, day-to-day creative
- **Haiku** — templated expansion, mechanical transforms, batch metadata
- Handoff saves tokens only when source emits a compact spec Haiku expands — not when full content is passed through

### Git Commit Format

```
[Category]: [Subject] | [Details] | [In-Game Date]
```

Categories: `Session:` `Scenario Extraction:` `World Building:` `Character:` `Rules Update:` `Project Maintenance:` `Bulk:`

---

## Key Operational Notes

- Always `filesystem:read_file` immediately before `filesystem:edit_file` — exact string matching required
- Always verify writes with a follow-up read (check YAML frontmatter top, content bottom)
- `filesystem:search_files` with glob `**/*filename*` reliably locates files when exact name uncertain
- Directory creation requires separate calls per level
- Sessions live in `Scenarios/` subfolders — there is no root `Session_Summaries/` directory
- `userMemories` (claude.ai) is the active continuity system; MCP memory graph is retired
