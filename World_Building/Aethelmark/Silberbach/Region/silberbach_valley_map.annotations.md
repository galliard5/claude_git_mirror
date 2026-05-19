---
name: silberbach_valley_map Annotations
type: location
keywords: [map, annotations]
description: Authorial overlay for silberbach valley map.wxx.
generated: 2026-05-18
---

# Annotations for silberbach valley map.wxx

Edit this file to add real names, base conditions, intent notes, POIs,
and other authored content. The renderer merges this into the .svg
description block on the next render.

## Project

# Pick the project styling for this map. Options: default, aethelmark.
# Defaults to `default` if absent.
project: default

## Intent

### Format
# Operational hints for tools and AI consumers.
- Description self-contained in the comment block. Edit this annotation file,
- Re-render via `python wxx_to_svg.py <input.wxx> <output.svg>`.
- Use `--regenerate-annotations` if the .wxx geometry changes.

### Narrative
# Authorial design notes — surfaced to the user when this map is loaded.
- regional map for the angerap river valley region
- TODO: note any settlements with deliberate design pressures.

## Elevation Overrides

# Per-cell elevation overrides for hexes that meaningfully differ from
# their terrain default. Format: `(col, row): elevation_m`. Optional.
overrides:
  # (15, 12): 1800m   # example: ridge fortress site

## Roads

### road 1
name: Imperial Highway (NW)
base: Cobble and packed dirt, well-travelled, width=30
flow:
  primary_endpoint: (31, 23)
  secondary_endpoint: (-1, 10)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 2
name: Silberbach Road
base: Cobble and packed dirt, width=30
flow:
  primary_endpoint: (31, 23)
  secondary_endpoint: (23, 10)
conditions:
  (31, 23): ref=bridge#4, ref=bridge#5, ref=bridge#6, ref=toll#3

### road 3
name: Aldenburg Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (27, 12)
  secondary_endpoint: (32, 5)
conditions:
  (32, 6): width=10

### road 4
name: Halselund Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (23, 10)
  secondary_endpoint: (10, 7)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 5
name: Halselund Ferry Road 1
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (17, 10)
  secondary_endpoint: (17, 10)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 6
name: Halselund Ferry Road 2
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (16, 12)
  secondary_endpoint: (16, 11)
conditions:
  (16, 11): ref=bridge#3

### road 7
name: Imperial Highway (S)
base: Cobble and packed dirt, well-travelled, width=30
flow:
  primary_endpoint: (33, 30)
  secondary_endpoint: (27, 22)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 8
name: Westgate Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (19, 34)
  secondary_endpoint: (-1, 38)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 9
name: Imperial Highway (S)
base: Cobble and packed dirt, Well-travelled, width=30
flow:
  primary_endpoint: (31, 23)
  secondary_endpoint: (34, 41)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 10
name: Angerap Highway (SW)
base: Cobble and packed dirt, Well-travelled, width=30
flow:
  primary_endpoint: (34, 41)
  secondary_endpoint: (28, 49)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 11
name: Angerap Highway (SE)
base: Cobble and packed dirt, Well-travelled, width=30
flow:
  primary_endpoint: (36, 40)
  secondary_endpoint: (50, 49)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 12
name: Angerap Highway (SW)
base: Cobble and packed dirt, Well-travelled, width=30
flow:
  primary_endpoint: (34, 41)
  secondary_endpoint: (36, 40)
conditions:
  (35, 40): ref=toll#1, ref=bridge#1

### road 13
name: Rothwyn Way
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (15, 27)
  secondary_endpoint: (14, 28)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 14
name: Steindorf Way
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (32, 30)
  secondary_endpoint: (33, 29)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 15
name: Isalia Way
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (33, 25)
  secondary_endpoint: (32, 25)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 16
name: Reinheim Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (10, 7)
  secondary_endpoint: (3, 5)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 17
name: Reinheim Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (3, 6)
  secondary_endpoint: (2, 11)
conditions:
  (3, 6): ref=toll#2, ref=bridge#2

### road 18
name: Reinheim Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (3, 6)
  secondary_endpoint: (3, 5)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 19
name: Waldheim Road
base: Cobble and packed dirt, width=20
flow:
  primary_endpoint: (32, 22)
  secondary_endpoint: (42, 24)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 20
name: Aldenburg Road
base: Cobble and packed dirt, switchbacks, width=15
flow:
  primary_endpoint: (32, 5)
  secondary_endpoint: (33, 3)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 21
name: Mine Trail
base: Cobble and packed dirt, switchbacks, width=10
flow:
  primary_endpoint: (33, 3)
  secondary_endpoint: (35, 3)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 22
name: Mine Trail
base: Cobble and packed dirt, switchbacks, width=10
flow:
  primary_endpoint: (34, 3)
  secondary_endpoint: (35, 1)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 23
name: Mine Trail
base: Cobble and packed dirt, switchbacks, width=10
flow:
  primary_endpoint: (33, 3)
  secondary_endpoint: (30, 3)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 24
name: Mine Trail
base: Cobble and packed dirt, switchbacks, width=10
flow:
  primary_endpoint: (32, 3)
  secondary_endpoint: (32, 2)
conditions:
  # (col,row): key=value, key=value
  # example: (28,22): ref=bridge#1

### road 25
name: Waldheim Road
base: Cobble and packed dirt, river ford, width=15
flow:
  primary_endpoint: (43, 23)
  secondary_endpoint: (48, 23)
conditions:
  (43, 23): ref=ford#1

## Rivers

### river 1
name: Angerap River
base: width=Wide, moderate current
flow:
  origin: TODO
  origin_cell: (-1, 4)
  termination: ocean
  termination_cell: (41, 50)
  direction: forward
conditions:
  (3, 5): ref=toll#2
  (35, 40): ref=toll#1, ref=bridge#1

### river 2
name: Reinheim River
base: width=10, Rapids Current
flow:
  origin: mountain streams
  origin_cell: (2, 0)
  termination: angerap river
  termination_cell: (3, 5)
  direction: forward
conditions:
  # example: (25,18): ref=bridge#1

### river 3
name: Silberbach rapids
base: treacherous, narrow, current=rapids
flow:
  origin: mountain streams
  origin_cell: (5, 2)
  termination: reinheim river
  termination_cell: (13, -1)
  direction: reverse
conditions:
  # example: (25,18): ref=bridge#1

### river 4
name: Astereon River
base: narrow width, strong current
flow:
  origin: Astereon Lake
  origin_cell: (45, 2)
  termination: Angerap River
  termination_cell: (43, 25)
  direction: forward
  stitch_with: river 5
conditions:
  # example: (25,18): ref=bridge#1

### river 5
name: Astereon River
base: moderate width, swift current
flow:
  origin: Astereon Lake
  origin_cell: (43, 25)
  termination: Angerap River
  termination_cell: (34, 32)
  direction: reverse
  stitch_with: river 4
conditions:
  # example: (25,18): ref=bridge#1

## Linear Feature Details

# References used by `ref=` annotations on roads and rivers above.
# Wire up by adding `ref=toll#1` etc to a path condition, then define here.

### bridge#1
name: Kaelan bridge
type: bridge
material: stone
length_m: 40
note: toll bridge
clearance: 10m

### bridge#2
name: Reinheim Bridge
type: bridge
material: wood
length_m: 30
note: 10m vertical clearance. tends to get washed out

### bridge#3
name: Halselund ferry
type: bridge
material: ferry
length_m: 30
note: 

### bridge#4
name: Silberbach north bridge
type: bridge
material: stone
length_m: 40
note: clearance 10m

### bridge#5
name: Silberback Central Bridge
type: bridge
material: stone
length_m: 40
note: has a guarded gatehouse, inspections, toll point, clearance 15 m

### bridge#6
name: Silberbach South bridge
type: bridge
material: wood
length_m: 40
note: saving up for stone footings, 10m clearance

### ford#1
name: Waldheim way ford
type: ford
difficulty: moderate difficulty, dangerous during heavy rain
note: about 3 feet depth normaly, the path is marked

### toll#1
name: Kaelen bridge toll
type: tollbooth
controlled_by: House Kaelen
fee: 2s/wagon, 5c/person, locals free
note: 

### toll#2
name: Reinheim bridge toll
type: tollbooth
controlled_by: Reinheim township
fee: 3s/wagon, 5c/person, local foot traffic free
note: washes out during heavy rain seasons.. currently saving up for stone footings

### toll#3
name: Silberbach Central bridge toll
type: Gatehouse
controlled_by: Silberbach city hall
fee: 3s/wagon, 5c/person, local foot traffic free
note: guarded gatehouse and inspections

## Points of Interest

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

# known | local | hidden.  Format: `(col, row): visibility`
# (1, 38): local

## Feature Names

# Format: `(col, row): Name`
# (15, 12): Blackrock Pass
