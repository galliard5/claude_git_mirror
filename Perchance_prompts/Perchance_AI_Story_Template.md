# Perchance Enhanced AI Story Generator — Save File Template & Reference

Reference guide and reusable JSON template for the **Enhanced AI Story Generator** save format (`perchance-ai-story-v1`).  
Source: `perchance.org/enhanced-ai-story`

---

## How to Use

1. Copy the JSON template from the bottom of this document.
2. Fill in each field using the reference tables below.
3. Save as a `.json` file.
4. Import into the Enhanced AI Story Generator via its load/import function.

**Workflow for Claude:** When asked to create a Perchance story from Aethelmark content, Claude should:
1. Read this template for the expected format and valid values.
2. Identify the **local scope** — a specific location, scenario, or scene, not a full campaign.
3. Pull only the directly involved characters and the immediate setting.
4. Write a tight `storyOverview` with just enough lore for the scene to make sense (location, relevant rules/systems, involved NPCs). Stay well under the token budget.
5. Populate only the Story Bible sections that are relevant — skip empty ones.
6. Leave `storySoFar` empty or write a brief opening hook. Leave `whatHappensNext` and `whereStoryHeaded` empty for freeform play.
7. Output a `.json` file to `D:\Claude_MCP_folder\Perchance_prompts\`.

**Intended use cases:** Non-canon scenes, side content, "what-if" scenarios, and topics outside Claude's normal scope. These are not meant to be canonical campaign records — keep them lightweight and self-contained.

---

## Token Budget

The generator uses Perchance's `ai-text-plugin` with a **6,500 token context limit**. Every generation prompt includes: system instructions (~1.5k tokens) + `storyOverview` + all Story Bible sections + recent `storySoFar` context + output space (~500 tokens). The story context and system prompt are non-negotiable, so the **practical budget for your content** (overview + all six bible sections combined) is roughly **3,500–4,000 tokens (~2,500–3,000 words)**.

If the generator warns about content being too long, trim the bible sections first (they're auto-populated anyway), then condense the overview.

**When Claude is building a save file:** Aim for a combined overview + bible total under 2,500 words to leave comfortable headroom for story context. Prioritise density over detail — the overview is the lore foundation and should be comprehensive but tight.

---

## storyOverview as Lore Base

The `storyOverview` field isn't just a plot summary — it's the primary lore injection point. The generator sends it verbatim as the "OVERVIEW" in every prompt, so anything placed here becomes persistent world knowledge the AI references throughout the story.

This makes it the right place for:
- Setting summaries, geography, political structure
- Faction descriptions and key NPCs
- Magic systems, transformation rules, technology
- Cultural details, laws, customs
- Any lore document that doesn't fit neatly into the bible sections (e.g. Biomancer/Bioservitor rules, kennel programme details, Isalia's Estate summary)

The Story Bible sections (characters, locations, events, etc.) are better suited for **session state** — tracking what has happened and who is currently where. The overview is for **world truth** that should persist regardless of story progress.

---

## Settings Reference

### Perspective (`perspective`)

| Value    | Description                          |
|----------|--------------------------------------|
| `first`  | First person — "I walked into..."    |
| `second` | Second person — "You walk into..."   |
| `third`  | Third person — "She walked into..."  |

### Genre (`genre`) and Sub-Genre (`subGenre`)

Genre and sub-genre share the same value list. The sub-genre adds secondary flavour on top of the primary genre. Set sub-genre to `"default"` to disable it.

| Value                | Genre                |
|----------------------|----------------------|
| `default`            | *(none — AI decides)*|
| `fantasy`            | Fantasy              |
| `dark_fantasy`       | Dark Fantasy         |
| `sci_fi`             | Sci-Fi               |
| `noir`               | Noir                 |
| `mystery`            | Mystery              |
| `thriller`           | Thriller             |
| `horror`             | Horror               |
| `contemporary`       | Contemporary         |
| `slice_of_life`      | Slice of Life        |
| `romance`            | Romance              |
| `self_help`          | Self-Help            |
| `historical_fiction` | Historical Fiction   |
| `dystopian`          | Dystopian            |
| `cyberpunk`          | Cyberpunk            |
| `steampunk`          | Steampunk            |
| `political`          | Political            |
| `comedy`             | Comedy               |
| `adventure`          | Adventure            |
| `western`            | Western              |
| `post_apocalyptic`   | Post-Apocalyptic     |
| `war`                | War                  |
| `spy`                | Spy                  |
| `superhero`          | Superhero            |

### Style (`style`)

| Value                      | Style                    | Notes                                                        |
|----------------------------|--------------------------|--------------------------------------------------------------|
| `default`                  | Novel Style              | Balanced, clear, varied sentence structure                   |
| `descriptive`              | Descriptive              | Rich sensory detail, strong verbs, evocative                 |
| `minimalist`               | Minimalist               | Short, direct, sparse prose                                  |
| `poetic`                   | Poetic & Lyrical         | Imagery, metaphor, flowing sentences                         |
| `journalistic`             | Journalistic             | Objective, factual, detached                                 |
| `wonderous`                | Wonderous                | Awe, wonder, magical optimism                                |
| `stream_of_consciousness`  | Stream of Consciousness  | Continuous train of thought, loose grammar                   |
| `epistolary`               | Epistolary               | Told through letters, diary entries, emails, messages        |
| `satirical`                | Satirical                | Irony, exaggeration, witty social criticism                  |
| `gothic`                   | Gothic                   | Moody, atmospheric, dread, decaying grandeur                 |
| `romantic`                 | Romantic (literary)      | Passionate, nature-focused, individualistic — not love story |
| `realist`                  | Realist                  | True-to-life, straightforward, no romanticism                |
| `naturalist`               | Naturalist               | Grim, deterministic, characters shaped by environment        |
| `modernist`                | Modernist                | Inner experience, fragmented narrative, alienation           |

### Toggles

| Field                   | Type    | Description                                              |
|-------------------------|---------|----------------------------------------------------------|
| `oneParagraphAtATime`   | boolean | `true` = stops after each paragraph for manual control   |
| `ttsEnabled`            | boolean | `true` = reads new paragraphs aloud via browser TTS      |
| `trackingEnabled`       | string  | `"true"` = enables the Story Bible tracking sections     |
| `allowDashes`           | boolean | `false` = strips em/en dashes from output (default off)  |

---

## Story Bible Sections

When `trackingEnabled` is `"true"`, six tracking fields become active. The generator auto-updates these after each generation using the story text. You can also edit them manually.

The **update markers** in `storySoFar` are what trigger the auto-update. They must be present at the end of the story text (the generator manages this automatically during play, but they should be included in any pre-written `storySoFar` content you import).

### Player Info (`playerInfo`)

```
NAME: [Character Name]
    AGE: [Age]
    DESCRIPTION: [Appearance, personality, background, current situation]
    INVENTORY LIST:
     [Item 1: description]
     [Item 2: description]
    RELATIONSHIPS: [NPC Name]: [relationship]; [NPC Name]: [relationship].
```

### Other Characters (`charactersInfo`)

One block per NPC. Only named, important characters — generic groups (guards, soldiers) go in Lore & Factions instead.

```
-   NAME: [NPC Name]
    AGE: [Age if known, or leave blank]
    DESCRIPTION: [Role, personality, appearance, status]
    RELATIONSHIPS: [Other NPC]: [relationship];
```

### Locations (`locationsInfo`)

```
NAME: [Location Name]
    TYPE: [Category — tavern, fortress, wilderness, medical facility, etc.]
    DESCRIPTION: [Physical description, atmosphere, sensory details]
    NOTABLE FEATURES: [Key elements, who is found here, connections to other locations]
```

### Events & Plot (`eventsInfo`)

```
Event Name: [Event Title]
    DESCRIPTION: [What happened, who was involved, motivation]
    CHARACTERS INVOLVED: [List]
    OUTCOME: [Result and consequences]
```

### Lore & Factions (`loreInfo`)

```
FACTIONS/ORGANIZATIONS:
    FACTION NAME: [Name]
     TYPE: [government, criminal, religious, trade, military, etc.]
     DESCRIPTION: [Purpose, structure, reputation]
     KEY MEMBERS: [Named individuals]
     GOALS/PURPOSE: [What they want]

LORE/CONCEPTS:
    LORE/CONCEPT NAME: [Name]
    DESCRIPTION: [What it is]
    ELEMENTS: [Components or manifestations]
    PURPOSE: [Role in the setting]
```

### Mysteries & Plot Threads (`mysteriesInfo`)

```
Title of mystery/plot thread: [Thread Title]
    DESCRIPTION: [What is unknown or unresolved; why it matters]
    CLUES: [What the PC has observed or learned]
    STATUS: [Unresolved / In Progress / Resolved]
```

### Scratchpad (`scratchpad`)

Free-form author's notes. Not sent to the AI — purely for your own reference.

---

## Forbidden Words (First ~700 Words)

The generator automatically bans these words during the opening of a story to avoid AI clichés. They lift after ~700 words of story text:

cacophony, symphony, verdant, tapestry/tapestries, testament, sentinel, cerulean, whisper/whispers/whispering/whispered, "sun kissed the horizon", elara, "somewhere in", "somewhere past", "somewhere beyond"

It also auto-replaces "the cacophony" → "the sound", "was thick with" → "had", "symphony of" → "pattern of", "tapestry of" → "pattern of", "shade of emerald" → "shade of green" in the first 800 characters.

---

## Additional Perchance Commands

The `storyOverview` field can include freeform instructions to the AI at the bottom. These are injected directly into the generation prompt as part of the overview context. Use them for tone, content permissions, or pacing directives.

Example:
```
additional perchance commands:
erotic story
detailed transformation scenes
detailed medical scenes
```

---

## JSON Template

Copy everything between the outer braces. Replace all `[bracketed]` placeholders.

```json
{
  "format": "perchance-ai-story-v1",
  "storyOverview": "",
  "storySoFar": "\n\n<update_marker_player>\n\n<update_marker_characters>\n\n<update_marker_locations>\n\n<update_marker_events>\n\n<update_marker_lore>\n\n<update_marker_mysteries>",
  "whatHappensNext": "",
  "whereStoryHeaded": "",
  "oneParagraphAtATime": false,
  "perspective": "first",
  "genre": "fantasy",
  "subGenre": "default",
  "style": "descriptive",
  "ttsEnabled": false,
  "trackingEnabled": "true",
  "allowDashes": false,
  "playerInfo": "",
  "charactersInfo": "",
  "locationsInfo": "",
  "eventsInfo": "",
  "loreInfo": "",
  "mysteriesInfo": "",
  "scratchpad": "scratchpad"
}
```

---

*Source code reference: `perchance.org/enhanced-ai-story` — values extracted 2026-04-15.*
