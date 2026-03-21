---
name: Model Selection & Scenario Handoff Guide
keywords: [model, opus, sonnet, haiku, selection, handoff, briefing, workflow, scenario, session]
description: Complete protocol for model selection, scenario creation workflow, Sonnet Briefing requirements, and session handoff procedures
---

# Model Selection & Scenario Handoff Guide

**Purpose:** This document defines how different Claude models are used across the campaign workflow — which model does what, when to escalate, how scenarios are handed from Opus to Sonnet, and what the Sonnet Briefing must contain.

**Quick reference version:** See core_rules.md, Section 4A for the summary. This file contains the full protocol.

---

## MODEL ROLES — DETAILED

### Opus — Scenario Architect

Use Opus for tasks that require deep cross-referencing, synthesis across multiple canon files, and complex narrative design:

- **Building new scenarios** — plot structure, NPC motivations, faction movements, branching outcomes
- **Designing NPCs with layered goals** — flaws, behavioral logic, speech patterns that will hold up across sessions
- **Cross-referencing project data** — timeline, faction, and relationship data across multiple directories
- **Writing Sonnet Briefings** — translating scenario complexity into operational playbooks (see below)
- **Scenario extraction** — large or complex scenarios (8+ checkpoints, many new NPCs)
- **Any task where getting it wrong means cascade errors** through multiple files

### Sonnet — Session Runner

Use Sonnet for tasks that require fast, responsive, in-character execution within established parameters:

- **Running active play sessions** — scenarios, NPCs, and locations are already documented
- **Routine session play** — daily life, exploration, straightforward encounters
- **Session checkpoint generation** — writing summaries at natural stopping points
- **File maintenance** — metadata updates, batch edits, organization tasks
- **Scenario extraction** — standard-complexity scenarios (under 8 checkpoints)

### Haiku — Not Recommended

Haiku lacks the context depth for reliable canon adherence across long sessions. Specific risks:

- NPC voice drift within a single scene
- Missing cross-references between files
- Improvising details that contradict established lore
- Struggling with scenarios involving more than 3-4 active NPCs

If Haiku must be used, apply the caution protocol from Scenario_Extraction_Rules.md: pause, warn, and require explicit user confirmation before proceeding.

---

## ESCALATION CRITERIA

### When to Use Opus Instead of Sonnet for Session Play

Start with Sonnet by default. Escalate to Opus when:

1. **Multiple NPC agendas collide** — three or more NPCs with competing goals interacting simultaneously in a single scene
2. **Political or legal proceedings** — hearings, negotiations, trials, or formal disputes where NPC behavioral logic must be deeply grounded in character files
3. **High-stakes social confrontation** — moments where NPC relationships can permanently shift based on subtle dialogue choices
4. **First contact with a major NPC** — establishing voice, quirks, and behavioral patterns that Sonnet will then maintain in future sessions
5. **Deep worldbuilding inference required** — situations where the answer isn't in any single file and must be derived from multiple canon sources

### Signs That a Session Needs Opus

If you're running on Sonnet and notice any of these, consider switching:

- NPC dialogue is flattening toward a generic baseline
- Canon contradictions are appearing (NPC knows something they shouldn't, location details are wrong)
- Complex scenes are losing texture — too many NPCs talking the same way
- The scenario has branched into territory the Sonnet Briefing didn't anticipate
- The player is pushing into social or political territory that requires deep inference

---

## THE SONNET BRIEFING

### What It Is

A condensed operational document produced by Opus alongside every new scenario. It bridges the gap between Opus's deeper reasoning during scenario design and Sonnet's faster execution during play.

### What It Does

- Provides **explicit NPC decision logic** so Sonnet doesn't need to derive it from character files
- Anchors **NPC voices** with concrete speech samples and behavioral guardrails
- Maps **conditional responses**: "If the player does X, this NPC reacts with Y because Z"
- Lists **which canon files to load** for each major scene or location transition
- Flags **canon traps** — areas where improvisation is likely to contradict established lore

### What It Is NOT

- A replacement for reading character and location files (those are still loaded)
- A script (NPCs still react dynamically to player choices within the briefing's parameters)
- Optional (every Opus-built scenario produces one)

### Template

Use **[[Sonnet_Briefing_Template]]** for the complete format.

### File Naming & Location

- **Filename:** `[Scenario_Name]_Sonnet_Briefing.md`
- **Location:** Same directory as the scenario file
- The scenario and its briefing are a matched pair

---

## SCENARIO CREATION WORKFLOW (Opus)

When building a new scenario, Opus follows this sequence:

1. **Read all relevant canon files** — characters, locations, factions, timeline, Master Calendar
2. **Build the scenario** using [[Scenario_Template]]
3. **Generate the Sonnet Briefing** using [[Sonnet_Briefing_Template]]
4. **Batch write both files** to the scenario directory
5. **Verify cross-references** — ensure all linked files exist and are current

The scenario file is the narrative architecture. The Sonnet Briefing is the operational playbook. Both are required before session play begins.

---

## SESSION HANDOFF PROTOCOL

### What Sonnet Loads (In Order)

When transitioning from Opus (scenario creation) to Sonnet (session play), Sonnet loads files in this priority:

1. **The Sonnet Briefing** — first, as the operational anchor
2. **The scenario file** — full plot structure and branching
3. **PC character sheet** — current state, inventory, relationships
4. **Active NPC character files** — as listed in the briefing's "Files to Load" section
5. **Location files for the opening scene** — as listed in the briefing
6. **Most recent session summary** — if resuming a scenario in progress
7. **Master Calendar** — for timeline context and world state

### What Sonnet Does NOT Need to Load

- The full extraction rules (post-session only)
- Template files (reference only)
- Character files for NPCs not yet encountered
- Historical session summaries beyond the most recent (unless briefing specifies)

This keeps Sonnet's context focused on the current session rather than the entire project.

### Mid-Scenario Updates

If Sonnet improvises details during play that become canon (a new minor NPC, a location detail, an NPC relationship shift), these are logged in the **Post-Session Notes** section of the Sonnet Briefing. This gives Opus a clear record of what changed during Sonnet-run sessions when it returns for extraction or major revisions.

---

## RETROACTIVE BRIEFINGS

### Briefings for Existing Scenarios

Scenarios created before this protocol (Viktor Steinfeld, Vauclair, Maruvec, Sergovy Waldheim) do not have Sonnet Briefings. These can be generated retroactively:

1. Opus reads the scenario file and all session summaries
2. Opus generates a Sonnet Briefing reflecting current world state
3. The briefing is saved alongside the existing scenario file

This is recommended before resuming any existing scenario on Sonnet.

---

## REFERENCES

- [[core_rules]] — Section 4A for quick reference summary
- [[Sonnet_Briefing_Template]] — Template for generating briefings
- [[Scenario_Template]] — Template for building scenarios
- [[Scenario_Extraction_Rules]] — Post-scenario consolidation protocol
- [[Character_Sheet_Template]] — NPC documentation format
- [[Location_Brief_Template]] — Location documentation format
