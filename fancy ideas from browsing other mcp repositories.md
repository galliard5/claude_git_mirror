https://github.com/cdeust/Cortex

**Cross-encoder reranking on top of FTS5.** This is the one piece of Cortex that's unambiguously useful and you don't currently have. FTS5 BM25 is great at "documents containing these tokens" but bad at "documents semantically about this thing." A reranker pass on the top-25 results from FTS5 would catch cases where the right document uses different vocabulary than the query. FlashRank specifically is small, ONNX-based, no GPU needed, runs in <1s. Worth bookmarking if you ever feel corpus-search is missing things it shouldn't.

**Synaptic tagging (the actual idea, not the name).** When you write a strong/important note, retroactively flag related older notes as "this is part of an active thread." For your workflow that translates to: when you write a session summary, the entities mentioned get a "recently touched" timestamp bumped, so next session's prep query naturally surfaces them. Lightweight to implement — just a `last_referenced_utc` field updated whenever an entity name appears in a new write.


[https://github.com/tumf/mcp-text-editor](https://github.com/tumf/mcp-text-editor)

**Worth pulling? One thing, maybe:** The pattern of "read returns hash, edit requires hash" is genuinely good engineering for the multi-agent case. If you ever set up a workflow where, say, you edit in Obsidian while a Claude session also edits the same files in parallel, you'd want exactly this. Right now: not a problem you have.

honestly if other people are working on the same file, they would be on a local copy, and we'd probably either paste all the edits into a single file and have you help mesh them, or give you the various versions, do a diff then mesh the changes into a coherant form


[https://github.com/gregario/dnd-oracle](https://github.com/gregario/dnd-oracle) [https://github.com/gregario/warhammer-oracle](https://github.com/gregario/warhammer-oracle)

**The architectural pattern is the actually-interesting takeaway.** Look at what they did: **SQLite + small MCP wrapper exposing typed search tools over canonical reference data.** That's structurally identical to your `corpus-search` server — same backend (SQLite + FTS5), same MCP delivery, same shape of tool definitions. The difference is they're indexing third-party canonical data; you're indexing your own worldbuilding.

Which suggests a pattern you might want to adopt: **a second corpus-search server, or an extended one, that indexes purpose-shaped views of your data.** Right now `corpus-search` does full-text BM25 across all .md files. That's good for "where is X mentioned" but bad for structured queries like "list all Manor staff in Senior_Staff with their roles" or "all NPCs with the kobold tag, sorted by location." You'd need to either grep YAML frontmatter manually or read whole folders.

A "structured oracle" alongside corpus-search would extract YAML frontmatter from every file at index-build time and let you query it directly — `lookup_npc(name="Vogt")` returns the file path plus parsed frontmatter; `search_npcs(faction="Manor", role="Senior_Staff")` returns matched files. That's where their pattern is genuinely worth lifting. **But:** you don't have this need urgently — your folder structure already does most of this work via semantic placement, and reading a small folder is cheap. Worth bookmarking, not worth building tonight.

**The "compare 2-4 entities side by side" tool is a nice UX pattern** — small, focused, a specific job. If you ever build out the structured-frontmatter oracle, baking in `compare_npcs(["Vogt", "Sable"])` to spit out aligned property tables would be a clean affordance.

Smart move. The 5e SRD as a starting skeleton is exactly what it's good for — the _structure_ of how creatures, spells, items, and classes get described is reusable; the specific stats and balance assumptions aren't.

Quick groundwork before you commit:

**Source: go straight to 5e-bits/5e-database, skip dnd-oracle entirely.** That's where dnd-oracle gets its data — the README links it explicitly. It's the canonical community fork of the 5e SRD as structured JSON, well-maintained, CC-BY-4.0 licensed (proper attribution gets you full rights). dnd-oracle's contribution is just a SQLite index over the JSON; you don't want their schema, you want the JSON itself. Repo: `https://github.com/5e-bits/5e-database`, the data lives in `src/` as one JSON file per category.

**Categories you'd want, with what to keep vs strip:**

- **Monsters** (`5e-SRD-Monsters.json`, ~334 entries): keep `name`, `size`, `type`, `alignment` placeholder, `senses`, `languages`, `proficiencies` structure, `actions`/`legendary_actions` structure, flavor descriptions. Strip every numeric: `armor_class`, `hit_points`, `hit_dice`, `speed`, all `stats`, `damage_resistances`, `damage_immunities`, `condition_immunities`, `challenge_rating`, `xp`. What's left is "this is a thing called a Beholder, it's Large, it's an Aberration, it floats, it has these named abilities." That's the worldbuilding skeleton.
- **Spells** (`5e-SRD-Spells.json`, ~319 entries): keep `name`, `school`, `casting_time` flavor, `range` flavor, `components` (V/S/M descriptions), `duration` flavor, `desc` (the actual text). Strip `level` (5e-specific), `damage` blocks, `dc` saves, `attack_bonus`, anything numeric. What's left: "Fireball — evocation — an explosion of flame at a point you choose."
- **Equipment** (`5e-SRD-Equipment.json`, ~237 entries): keep `name`, `equipment_category`, `weapon_category`/`armor_category`, `weapon_range`, properties (descriptive flags like "Versatile", "Heavy", "Two-Handed" — those describe shape and use), `desc`. Strip `cost`, `weight`, `damage`, `armor_class` numbers, `range` numerics. What's left: "Greatsword — martial melee weapon — two-handed."
- **Magic items** (`5e-SRD-Magic-Items.json`, ~239): keep `name`, `equipment_category`, `desc` (the flavor), `rarity` if you want a tiering hint. Strip nothing else really — magic items are mostly flavor, and you can rewrite power levels later.
- **Conditions** (`5e-SRD-Conditions.json`, ~15): keep all of it. Conditions are mostly already system-agnostic concepts — Blinded, Charmed, Frightened, Grappled, Prone — these translate to any system because they describe states, not mechanics.
- **Races** (`5e-SRD-Races.json`, ~9 + subraces): keep `name`, `age` flavor, `alignment` flavor, `size` flavor, `size_description`, `language_desc`, `traits` _names and descriptions_ but not their mechanics. Strip ability bonuses, speed numerics. The worldbuilding skeleton of "what is a Tiefling" survives stripping the +2 Cha.
- **Classes** (`5e-SRD-Classes.json`, ~12): mostly skip. Class is the most system-bound concept; "Wizard" as a description-of-a-profession is fine but it's all bound up with d20 mechanics. Maybe pull `name` and the proficiency flavor for setting feel, drop the rest.
- **Skills, proficiencies, ability-scores, alignments**: skip — pure 5e mechanical scaffolding.

**Practical conversion path:**

The JSON → markdown pass is the big chunk of work. A Python script in your `Python/` folder does the heavy lifting in maybe 100 lines:

1. Read each JSON category
2. For each entity, build the YAML frontmatter (`name`, `keywords` from `type`/`category` tags, `description` from the first sentence of `desc`)
3. Write the body as markdown with whatever subset of fields you want to keep
4. Output to a staging folder under, say, `World_Building/Aethelmark/Bestiary_Skeleton/` (or wherever feels right) — gitignored or in a separate commit so you can review before mass-importing

Important: **don't dump 1,198 files directly into your live worldbuilding tree.** That'd swamp your corpus-search index with non-canon material. Stage it in its own folder, browse, cherry-pick what's useful, drop the file into the appropriate Aethelmark location with edits to make it yours, leave the staging folder out of the search index (add to the corpus-search exclude list, same treatment as `Sheet_Import/`).

**Anticipating one trap:** SRD names are genericized for legal reasons — "Beholder" is "Spectator" or absent entirely, "Mind Flayer" is missing, "Drow" became "Dark Elf" or got stripped. The OGL purge in 2023 cut a lot. You'll find the SRD has the iconic _types_ but the named iconic monsters are largely scrubbed. For Aethelmark this is fine — you don't want D&D's branded monsters anyway, you want the structural template "what does a creature entry look like." Just don't expect to find Beholders in there.

**Want me to draft the conversion script now, or save it for a fresh session?** It's the kind of task where Opus-plans / Haiku-executes via your handoff protocol works well — Opus designs the field-mapping carefully (which fields keep, which strip, how to re-shape), then a fresh Haiku session does the file-by-file write. Late-night-Opus could draft the field-mapping table for review tomorrow, then you fire the write phase when ready. Up to you.



https://github.com/CheMiguel23/MemoryMesh

Quick triage version since you're tight on time:

This is the most relevant project of the night to your actual workflow, but probably still not what you should adopt. 335 stars, healthy fork count, real audience — not a vanity project. And the README is honest: minimal buzzwords, "knowledge graph server," "RPG and interactive storytelling," named limitations including the conflicting-knowledge problem they haven't solved. That's a refreshing change from quantum-consciousness-mesh.

**What it actually is:** an extension of the official MCP knowledge-graph memory server (the one you already have via `memory:create_entities` etc.), with two real additions:

1. **Schema-driven dynamic tools.** You define schemas like `add_npc.schema.json` declaring required fields (race, location, etc.) and relationships, and the server auto-generates `add_npc` / `update_npc` / `delete_npc` MCP tools with those constraints baked in. The AI gets forced to fill in required fields and gets validated against enums.
2. **Visual graph viewer + schema editor** as standalone HTML pages.

Your existing `memory:` tools are the freeform version of this — any node, any relations, no schema enforcement. MemoryMesh trades flexibility for structure.

**The relevance for your worldbuilding is real but smaller than it looks at first.** You already have a knowledge graph for your worldbuilding — your filesystem is one. Folder placement encodes node type (Senior_Staff, Companions, Animals). YAML frontmatter encodes properties. WikiLinks encode relationships. corpus-search is your query engine. The question is whether _also_ mirroring this into an actual graph database adds value.

Honest answer: probably not for your use case. Your worldbuilding lives in long-form prose where context matters — Vogt's character file isn't usefully reduced to "name=Vogt, race=minotaur, location=Manor, role=Security." The prose is where the worldbuilding _is_. A knowledge graph captures the skeleton but loses the body. You'd be maintaining two parallel representations and they'd drift.

**The one place this pattern would shine:** runtime session state. During an active scene, "where is everyone right now," "who knows what," "who's holding which item," "who's in conflict with whom." This is exactly the kind of structured-state-that-changes-frequently that prose files handle badly. If you ever wanted me to track real-time state during a play session — Si'ken's current HP, who's in which corridor of the ship, what the squad knows vs. doesn't — a graph with structured tools beats prose updates every time. But that's a play-session tool, not a worldbuilding tool, and right now you mostly do session prep + post-session extraction, with the session itself happening in chat.

**The actually-useful idea worth lifting, separate from installing:** schema-driven tool generation. The pattern of "define your data shape declaratively, get CRUD tools auto-generated with validation" is genuinely good engineering. If you ever build that "structured oracle over your YAML frontmatter" we discussed earlier with the dnd-oracle pattern, the schema approach is the cleaner version — define the shape once, get all the tools for free.

**Don't install tonight, even if you were going to.** It needs `npm run build`, schema files placed in a specific dist directory, restart Claude Desktop. Late-night infrastructure changes are how you wake up to a broken setup.

That's the read. Talk to you after the reset — and the SRD-skeleton extraction script we paused on is a good first task for the fresh window.