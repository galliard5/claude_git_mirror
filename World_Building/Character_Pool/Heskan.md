---
name: Heskan
keywords: [dnd4e, dragonborn, fighter, maptool, vtt, galliard, dragon-breath, dragonborn-fury]
description: Galliard's D&D 4e Dragonborn Fighter played via MapTool VTT. AC 20, Fort 17, Will 11. Powers include Dragon Breath, Cleave, Knockdown Assault, Passing Attack, Sweeping Blow. Bloodied On macro triggers Dragonborn Fury (+1 attack bonus). Surge value 11, action points tracked.
---

# Heskan

**System:** D&D 4th Edition
**Player:** Galliard
**Source:** `Heskan.rptok` — MapTool virtual tabletop token
**Campaign:** Unknown (the token format and powers suggest a mid-heroic-tier campaign)

## Identity
- **Race:** Dragonborn
- **Class:** Fighter
- **Token label:** "Dex Check" (the default active macro when the token was saved)

The class was stored in the `wisbonus` property field — a data-entry slip during token setup, but it confirms Fighter unambiguously.

## Stats
| Stat | Value |
|------|-------|
| **AC** | 20 |
| **Fortitude** | 17 |
| **Will** | 11 |
| **Dexterity** | 15 |
| **Constitution** | 14 |
| **Intelligence** | 11 |
| **Charisma** | 10 |
| Initiative bonus | 18 (displayed total) |
| Weapon hit bonus | +1 |
| Surge value | 11 |
| Action points | 10 (tracked as property) |

Fort 17 is high for a Fighter, consistent with either a CON-secondary build or the Dragonborn racial Constitution bonus applying. AC 20 at heroic tier suggests medium armor or light armor with a shield. Will 11 is the Fighter floor — not invested in.

The initiative bonus of 18 is the displayed running total as tracked in MapTool, which includes level, ability modifiers, and feat bonuses stacked together.

## Powers (Macros)

| Power | Type | Notes |
|-------|------|-------|
| **Dragon Breath** | Racial encounter | Dragonborn racial power; close blast, deals damage based on constitution |
| **Single Attack** | At-will | Basic attack roll |
| **Longbow** | At-will | Ranged basic attack |
| **Cleave** | At-will | Fighter at-will; hits primary target + adjacent enemy takes STR modifier damage |
| **Knockdown Assault** | Encounter/Daily | Fighter power; attack that knocks prone |
| **Passing Attack** | Encounter | Fighter power; move and attack, shift after |
| **Sweeping Blow** | Encounter | Fighter power; close burst attack hitting multiple enemies |
| **Bloodied On** | Status trigger | Triggers when HP drops to bloodied; turns button red + activates Dragonborn Fury |

### Dragonborn Fury
When the "Bloodied On" macro fires, it adds +1 to `weaponhitbonus`. This is the Dragonborn racial trait — they gain +1 to attacks while bloodied. The MapTool implementation toggles this automatically on the token.

## MapTool Implementation
All ability checks, skills, and powers are implemented as button macros using the formula `1d20 + [bonus] + floor(level/2)` — standard D&D 4e mechanic where half-level adds to all d20 rolls. The macro set covers:
- Attribute checks (STR, DEX, CON, INT, WIS, CHA)
- Skills (Athletics, Endurance, Heal)
- Combat powers (all listed above)
- Saving throws
- Damage/healing tracker
- Bloodied state management

The token was actively used in VTT play — the macro set is complete and functional, not a stub.

## Notes

Heskan is a traditional dragonborn fighter name (Heskan appears in D&D 4e published material as a sample character). This may be that sample character adopted as Galliard's PC, or an original character who happens to share the name. The stat block is consistent with a first-party dragonborn fighter build at roughly level 5–8 heroic tier.

The Longbow on a Fighter is an interesting secondary option — most Fighter powers are melee, but Longbow gives a ranged basic attack for situations where closing isn't viable.

**Madila.rptok** shares the same file size and content as Heskan.rptok — either Madila's token was built on top of a Heskan copy (a common MapTool workflow), or the wrong XML was extracted. Pending correct extraction.
