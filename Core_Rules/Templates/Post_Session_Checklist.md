---
name: Post-Session Checklist
keywords: [checklist, workflow, session, documentation, post-session]
description: Step-by-step checklist for Claude to follow at a checkpoint or session end — what to update and in what order
---

# Post-Session Checklist

**Instructions for Claude:** Follow these steps at every checkpoint or session end. Complete them in order. Do not skip steps unless the section explicitly marks them as conditional.

---

## Step 1: Write the Session Summary

1. Copy the `Session_Summary_Quick_Capture.md` template structure
2. Populate every section from the current session
3. Save to `D:\Claude_MCP_folder\Session_Summaries\[Campaign_Name]_Summary_[N].md`
4. Verify the file was written successfully before proceeding

---

## Step 2: Update the Player Character Sheet

File location: `World_Building\[Campaign]\[Character_Name].md`

- Update **Current Date** field
- Update **Active Conditions** — apply new statuses, clear resolved ones
- Update **Permanent Injuries & Alterations** if anything changed
- Update **Memory / Interaction Log** for any significant NPC interactions
- Update **appearance** description if physical changes occurred
- Update **Trust Level** for relevant NPCs if relationships shifted

---

## Step 3: Update the Campaign Timeline

File location: `World_Building\[Campaign]\Timeline_[Campaign].md`

- Update **Current Date** line
- Append new entries to **Event Log** under the current date
- Update **Active Threads** table — status changes, new threads, urgency upgrades
- Move resolved items to **Resolved Threads**

---

## Step 4: Update Affected NPCs (conditional)

Only if an NPC appeared in the session and something meaningfully changed.

File location: `World_Building\[Campaign]\Characters\[NPC_Name].md`

- Update **Trust Level** if attitude shifted
- Update **Active Conditions** if status changed
- Update **Memory / Interaction Log** with the specific interaction
- Update **appearance** or **Permanent Injuries** if physically changed

---

## Step 5: Update Affected Locations (conditional)

Only if a location's status changed — a building damaged, a condition applied or resolved, a situation escalated.

- Update **Active Conditions** section of the relevant location file

---

## Step 6: Verify Metadata

For every file updated, check that the YAML frontmatter is still accurate:

- `name` still matches the file's subject
- `keywords` reflect current state (add `injured`, `pregnant`, `investigated`, etc. where relevant)
- `description` reflects current situation, not outdated context

---

## Step 7: Notify the Player

Once all updates are complete, confirm in a single line:

*"Saved. [Summary filename] written, [N] files updated."*

List the files updated only if the player asks.
