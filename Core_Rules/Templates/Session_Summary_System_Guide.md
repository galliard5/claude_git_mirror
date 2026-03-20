---
name: Session Summary System Guide
keywords: [workflow, session, documentation, guide, system, reference]
description: Reference guide for Claude on how the post-session documentation system works and when to use each component
---

# Session Summary System — Reference Guide

**Instructions for Claude:** This is your reference for how the documentation system fits together. Read it when loading a new scenario or when uncertain about process. Do not follow it as a step-by-step — use `Post_Session_Checklist.md` for that.

---

## What the System Does

At checkpoints and session ends, Claude generates and saves structured documentation of what happened. This keeps the project files current without requiring manual updates from the player.

Three components:

| Component | Purpose | When Used |
|---|---|---|
| `Session_Summary_Quick_Capture.md` | Output template — the format of the saved summary file | Every checkpoint / session end |
| `Post_Session_Checklist.md` | Claude's process — what to update and in what order | Every checkpoint / session end |
| `Session_Summary_System_Guide.md` | This file — reference for how it all fits together | On load, or when uncertain |

---

## File Locations

| File Type | Location | Format |
|---|---|---|
| Session summaries | `D:\Claude_MCP_folder\Session_Summaries\` | `.md` |
| Character sheets | `D:\Claude_MCP_folder\World_Building\[Campaign]\Characters\` | `.md` |
| Campaign timelines | `D:\Claude_MCP_folder\World_Building\[Campaign]\` | `.md` |
| NPC files | `D:\Claude_MCP_folder\World_Building\[Campaign]\Characters\` | `.md` |
| Location files | `D:\Claude_MCP_folder\World_Building\[Campaign]\[Location]\` | `.md` |

---

## Naming Convention

Session summaries follow this pattern:

`[Campaign_Name]_Summary_[N].md`

Examples:
- `Vauclair_Summary_1.md`
- `Vauclair_Summary_2.md`
- `Steinfeld_Estate_Summary_1.md`

When the player references a summary by name without a number (e.g. "Vauclair Summary"), load all summaries matching that name in order. When a number is given (e.g. "Vauclair Summary 3"), load that file and all lower-numbered files with the same name in order.

---

## Checkpoint Triggers

Offer a save at:
- End of a scene
- Location change
- Quiet moment between beats
- Player-initiated pause
- Whenever tokens are running low

Checkpoint offer format: single line, token status appended. No summary, no recap.

---

## What Goes in a Summary vs. What Goes in Character / Timeline Files

**Summary file** captures what happened in the session — the narrative record. It answers: what occurred, what was decided, where things stand at the end.

**Character and timeline files** are the living project state — updated to reflect the summary's outcomes. They answer: what is currently true about this character or this world right now.

The summary is a snapshot. The character and timeline files are the running state. Both need to be current.

---

## Loading a Previous Session

When resuming from a summary:

1. Player provides the summary name
2. Load that summary and all lower-numbered summaries with the same name, in order
3. Load any character, timeline, or NPC files referenced in the summaries that are relevant to the upcoming session
4. Orient the player briefly — where they are, what is immediately in front of them, what threads are live
5. Do not recap at length. Trust the summaries.

---

## What to Skip

Do not update files that were not affected by the session. A location that was not visited does not need touching. An NPC who did not appear does not need updating. Keep the scope of updates proportional to what actually happened.

---

## YAML Metadata Maintenance

After updating any file, verify the frontmatter is still accurate. Keywords and description should reflect the file's current state, not its state when it was first written. Outdated metadata breaks the index.
