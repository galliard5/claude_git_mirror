---
name: Silberbach CIty Annotations
keywords: [map, annotations]
description: Authorial overlay for Silberbach CIty.wxx.
generated: 2026-05-18
---

# Annotations for Silberbach CIty.wxx

Edit this file to add real names, base conditions, intent notes, POIs,
and other authored content. The renderer merges this into the .svg
description block on the next render.

Auto-generated TODO placeholders are scattered throughout. Replace them
with real content or delete them. Templates marked `# === TEMPLATE ===`
are skipped at render time until you fill in non-placeholder values.

## Project

# Pick the project styling for this map. Options: default, aethelmark.
# Defaults to `default` if absent.
project: default

## Intent

### Format
# Operational hints for tools and AI consumers.
- Description self-contained in the comment block. Edit this annotation file,
  not the .svg comment block directly (changes will be overwritten on re-render).
- Re-render via `python wxx_to_svg.py <input.wxx> <output.svg>`.
- Use `--regenerate-annotations` if the .wxx geometry changes.

### Narrative
# Authorial design notes — surfaced to the user when this map is loaded.
# Use `@ambiguous: ...` to flag unresolved authorial decisions.
- TODO: describe the map's intended use (campaign hex-crawl, regional reference, etc.)
- TODO: note any settlements with deliberate design pressures.

## Elevation Overrides

# Per-cell elevation overrides for hexes that meaningfully differ from
# their terrain default. Format: `(col, row): elevation_m`. Optional.
overrides:
  # (15, 12): 1800m   # example: ridge fortress site

## Roads

### road 1
name: TODO  # Stone Bridge (15m clearance) 
base: Stone Bridge (15m clearance) , width≈40ft
flow:
  primary_endpoint: (36, 25)
  secondary_endpoint: (40, 24)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 2
name: TODO  # Stone Bridge (10m clearance) 
base: Stone Bridge (10m clearance) , width≈30ft
flow:
  primary_endpoint: (19, 13)
  secondary_endpoint: (20, 10)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 3
name: TODO  # Wood Bridge (10m clearance) 
base: Wood Bridge (10m clearance) , width≈20ft
flow:
  primary_endpoint: (38, 39)
  secondary_endpoint: (43, 38)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 4
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈30ft
flow:
  primary_endpoint: (-1, 14)
  secondary_endpoint: (22, 17)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 5
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (36, 25)
  secondary_endpoint: (33, 25)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 6
name: TODO  # Fine Stone road
base: Fine Stone road, width≈20ft
flow:
  primary_endpoint: (33, 27)
  secondary_endpoint: (32, 26)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 7
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (22, 17)
  secondary_endpoint: (33, 30)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 8
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈30ft
flow:
  primary_endpoint: (34, 50)
  secondary_endpoint: (33, 34)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 9
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (33, 30)
  secondary_endpoint: (33, 34)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 10
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (40, 24)
  secondary_endpoint: (42, 23)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 11
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (38, 39)
  secondary_endpoint: (35, 39)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 12
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈25ft
flow:
  primary_endpoint: (19, 13)
  secondary_endpoint: (19, 16)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 13
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (-1, 5)
  secondary_endpoint: (46, 50)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 14
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈30ft
flow:
  primary_endpoint: (42, 23)
  secondary_endpoint: (43, -1)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 15
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (43, 38)
  secondary_endpoint: (45, 38)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 16
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (20, 10)
  secondary_endpoint: (20, 9)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 17
name: TODO  # Stone road
base: Stone road, width≈20ft
flow:
  primary_endpoint: (33, 32)
  secondary_endpoint: (24, 18)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 18
name: TODO  # Stone road
base: Stone road, width≈20ft
flow:
  primary_endpoint: (29, 32)
  secondary_endpoint: (29, 33)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 19
name: TODO  # Stone road
base: Stone road, width≈20ft
flow:
  primary_endpoint: (22, 24)
  secondary_endpoint: (31, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 20
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (33, 31)
  secondary_endpoint: (37, 32)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 21
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (33, 28)
  secondary_endpoint: (36, 28)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 22
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (32, 23)
  secondary_endpoint: (34, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 23
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (29, 20)
  secondary_endpoint: (30, 19)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 24
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (26, 18)
  secondary_endpoint: (26, 17)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 25
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (25, 24)
  secondary_endpoint: (25, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 26
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (29, 23)
  secondary_endpoint: (28, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 27
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (22, 21)
  secondary_endpoint: (20, 21)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 28
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (22, 24)
  secondary_endpoint: (21, 23)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 29
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (22, 27)
  secondary_endpoint: (21, 27)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 30
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (25, 30)
  secondary_endpoint: (24, 32)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 31
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (28, 32)
  secondary_endpoint: (29, 29)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 32
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (24, 29)
  secondary_endpoint: (26, 28)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 33
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (31, 19)
  secondary_endpoint: (24, 16)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 34
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (33, 13)
  secondary_endpoint: (37, 16)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 35
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (37, 15)
  secondary_endpoint: (38, 14)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 36
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (34, 14)
  secondary_endpoint: (36, 12)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 37
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈30ft
flow:
  primary_endpoint: (10, 14)
  secondary_endpoint: (35, 40)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 38
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (29, 40)
  secondary_endpoint: (28, 45)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 39
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (25, 39)
  secondary_endpoint: (26, 37)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 40
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (19, 36)
  secondary_endpoint: (21, 33)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 41
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (15, 33)
  secondary_endpoint: (17, 30)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 42
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (21, 38)
  secondary_endpoint: (17, 42)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 43
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (15, 34)
  secondary_endpoint: (11, 37)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 44
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (11, 28)
  secondary_endpoint: (5, 29)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 45
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (10, 21)
  secondary_endpoint: (6, 20)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 46
name: TODO  # Fine Stone road
base: Fine Stone road, width≈20ft
flow:
  primary_endpoint: (31, 32)
  secondary_endpoint: (31, 31)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 47
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (40, 16)
  secondary_endpoint: (39, 16)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 48
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (41, 18)
  secondary_endpoint: (40, 20)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 49
name: TODO  # Stone road
base: Stone road, width≈10ft
flow:
  primary_endpoint: (37, 16)
  secondary_endpoint: (40, 20)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 50
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (22, 24)
  secondary_endpoint: (15, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 51
name: TODO  # Stone road
base: Stone road, width≈30ft
flow:
  primary_endpoint: (15, 22)
  secondary_endpoint: (10, 21)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 52
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈20ft
flow:
  primary_endpoint: (10, 26)
  secondary_endpoint: (16, 24)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 53
name: TODO  # Dirt/cobble road
base: Dirt/cobble road, width≈15ft
flow:
  primary_endpoint: (17, 15)
  secondary_endpoint: (16, 18)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

## Rivers

### river 1
# === STITCH CANDIDATE ===
# Endpoint at (-1, 9) is adjacent to river 2's endpoint at (-1, 10).
# If these are one logical river drawn in two passes, set
# `stitch_with: river N` AND mark one as `direction: reverse`.
# If they're a real confluence (different named tributaries),
# leave them separate and set termination_cell on both.
# Delete this comment once resolved.
name: TODO  # Angerap river corse
base: Angerap river corse
flow:
  origin: TODO
  origin_cell: (-1, 9)
  termination: TODO
  termination_cell: (40, 52)
  direction: forward
conditions:
  # example: (25,18): ref=bridge#1

### river 2
# === STITCH CANDIDATE ===
# Endpoint at (-1, 10) is adjacent to river 1's endpoint at (-1, 9).
# If these are one logical river drawn in two passes, set
# `stitch_with: river N` AND mark one as `direction: reverse`.
# If they're a real confluence (different named tributaries),
# leave them separate and set termination_cell on both.
# Delete this comment once resolved.
name: TODO  # Angerap river
base: Angerap river
flow:
  origin: TODO
  origin_cell: (-1, 10)
  termination: TODO
  termination_cell: (-1, 8)
  direction: forward
conditions:
  # example: (25,18): ref=bridge#1

## Walls

# Wall segments drawn as paths in the .wxx.
# type options: palisade | earthwork | stone | brick | ruins
# condition options: intact | damaged | ruined | under_construction
# towers/gates are auto-detected from nearby features.

### wall 1
name: TODO  # City Wall
type: stone
height_m: 
thickness_m: 
condition: intact
towers: (38,36), (22,14), (29,35), (23,33), (19,26), (19,19)
note: 

## Moat

# Defensive water features. source=river means the waterway itself is the barrier.

### moat 1
name: TODO  # river moat
source: river  # river | dug | dry
width_m: 
depth_m: 
condition: 
is_river_segment: false  # true if the natural river forms this barrier
note: 

## Districts

# Named areas drawn as polygons. Add descriptions and visibility.

### district 1
name: Administrative zone
visibility: known
description: TODO
note: 

### district 2
name: Old Town zone
visibility: known
description: TODO
note: 

### district 3
name: Dockyards 2
visibility: known
description: TODO
note: 

### district 4
name: New Town
visibility: known
description: TODO
note: 

### district 5
name: New Town 2
visibility: known
description: TODO
note: 

### district 6
name: Outskirts
visibility: known
description: TODO
note: 

### district 7
name: Outskirts 2
visibility: known
description: TODO
note: 

### district 8
name: Harbor District
visibility: known
description: TODO
note: 

### district 9
name: Market Square
visibility: known
description: TODO
note: 

### district 10
name: Merchants Close
visibility: known
description: TODO
note: 

### district 11
name: Caravners way
visibility: known
description: TODO
note: 

## Linear Feature Details

# References used by `ref=` annotations on roads and rivers above.
# Wire up by adding `ref=toll#1` etc to a path condition, then define here.
# Templates below are unused — fill in or delete.

### toll#1
# === TEMPLATE — fill in or delete ===
name: Untitled Toll
type: tollbooth
controlled_by: 
fee: 
note: 

### bridge#1
# === TEMPLATE — fill in or delete ===
name: Untitled Bridge
type: bridge
material: stone | wood | rope | ferry
length_m: 
note: 

### ford#1
# === TEMPLATE — fill in or delete ===
name: Untitled Ford
type: ford
difficulty: 
note: 

## Points of Interest

# Available POI types (renderer maps these to icon glyphs):
#
#   Settlements:           capital, city, town, village, hamlet, manor, hold
#   Defensive:             fort, watchtower, keep, ruined_keep, palisade
#   Infrastructure:        tollbooth, bridge, ford, ferry, mill, lighthouse,
#                          well, waystation
#   Religious / Cultural:  shrine, temple, monastery, cemetery, gibbet,
#                          monument, standing_stones
#   Resources:             mine, quarry, lumber_camp, fishing_camp, salt_works
#   Wilderness / Adventure: ruin, dungeon, cave, lair, camp, bandit_camp,
#                          ambush_site, battlefield
#   Natural Landmarks:     waterfall, hot_spring, oasis, grove, ancient_tree,
#                          peak, cliff
#   Generic:               landmark
#
# Visibility values: known | local | hidden
# (See Wxx_Map_Format_Spec.md Appendix A for full vocabulary.)

### poi#1
# === TEMPLATE — fill in or delete ===
name: Untitled POI
type: landmark
cell: (##, ##)
visibility: known
description: 
note: 

### poi#2
# === TEMPLATE — fill in or delete ===
name: Untitled POI
type: landmark
cell: (##, ##)
visibility: known
description: 
note: 

## Feature Visibility Overrides

# By default, all .wxx features render as `known`. Override here if a
# feature should be `local` (unlabeled to outsiders) or `hidden` (GM only).
# Format: `(col, row): visibility`. Coords must match a real feature.
# Example:
# (1, 38): local

## Feature Names

# Worldographer left these features unlabeled. Assign real names below.
# Format: `(col, row): Name`
(33, 35): TODO   # Medieval Gatehouse
(21, 16): TODO   # Medieval Gatehouse
(36, 25): TODO   # Medieval Gatehouse
(40, 24): TODO   # Medieval Gatehouse
(38, 36): TODO   # Medieval Walltower
(22, 14): TODO   # Medieval Walltower
(29, 35): TODO   # Medieval Walltower B
(23, 33): TODO   # Medieval Walltower B
(19, 26): TODO   # Medieval Walltower B
(19, 19): TODO   # Medieval Walltower B
(19, 24): TODO   # Medieval Gatehouse
(25, 19): TODO   # Medieval Market
(25, 19): TODO   # Fountain
