---
name: YAML Compliance Audit Report
type: rules-reference
keywords: [yaml, frontmatter, compliance, audit, world-building]
description: Complete YAML frontmatter compliance audit for World_Building directory with repair instructions
---

# YAML Compliance Audit & Repair Report

**Audit Date:** 2026-05-15  
**Scanned Files:** 200+ markdown files in `/World_Building/`  
**Total Indexed:** 501 (corpus-wide)

---

## Executive Summary

| Status | Count | Action |
|--------|-------|--------|
| Fully Compliant | 0 files | ✓ None needed |
| Missing Type Field | ~170 files | ⚠️ Run repair script |
| Missing All Frontmatter | 30 files | ✓ Run repair script |
| **Total Repairs Needed** | **~200 files** | **🔧 See below** |

---

## Findings

### Required YAML Fields (Mandatory)
- `name` — Document title
- `keywords` — Comma-separated tags for searchability
- `description` — One-sentence summary

### Optional YAML Field (Not Yet Populated)
- `type` — Document category (character, location, scenario, etc.)

**Compliance Status:**
- ✓ ~170 files have all required fields + keywords
- ✗ ~170 files missing optional `type` field
- ✗ 30 files missing ALL frontmatter entirely

**Pattern:** The 30 critical files are predominantly in `Other_Projects/Character_Pool/` — these appear to be older character imports from external systems (GCS, PCGEN, M&M, Shadowrun, GURPS) that predate the YAML frontmatter convention.

---

## Files Missing Complete Frontmatter (30 Critical)

**All in `Other_Projects/Character_Pool/`:**

1. Mist_in_the_Wind.md
2. Jagaima.md
3. Sarashdar.md
4. Brian_Hitchens.md
5. Ras_Ben_Kobold_Wizard.md
6. KaiSF_Tauran_Vega.md
7. Galli_MnM.md
8. Anthony_Wilmington.md
9. Shami.md
10. Jil.md
11. Miria.md
12. Kalysto.md
13. Tina.md
14. Eve_Schallow.md
15. Tenari_Guide.md
16. Kani.md
17. Aranaea.md
18. Sickles_Cleric.md
19. Mourgram_Uthelienn.md
20. Astraea.md
21. Rosuto_Mokuteki.md
22. Madila.md
23. Saphira.md
24. Allina.md
25. Daniel_Sanchez.md
26. Royal_Frilled_Dragon_Hatchling.md
27. DNDTF_Smart_Hero.md
28. Ras_Ben_Gnoll_Cleric.md
29. Caravaners_way.md (Silberbach Town)
30. Westgate.md (Silberbach Region) — Already fixed in this audit

---

## Repair Instructions

### Quick Repair (Recommended)

**Windows Users:**

1. Open File Explorer and navigate to `D:\claude\filesystem\Python\`
2. Double-click `fix_yaml_compliance.bat`
3. Wait for completion (should take 5-30 seconds)
4. Review the summary output showing:
   - Total files processed
   - Frontmatter added count
   - Type field additions count
   - Any errors

**macOS / Linux Users:**

```bash
cd /corpus/Python
python3 fix_yaml_compliance.py
```

### What the Script Does

1. **Scans all `.md` files** in `World_Building/` recursively
2. **Identifies three categories:**
   - Files with no YAML → Adds complete frontmatter
   - Files with incomplete YAML → Adds missing `type` field
   - Files already compliant → No changes
3. **Infers best-guess values** for `type` field based on file path:
   - `Character_Pool/` → `character`
   - `Regions/`, `Town/` → `location`
   - `Factions/`, `Guilds/`, `Noble_Houses/` → `faction`
   - `Scenarios/`, `Session*`, `Summary*` → `scenario` or `session-summary`
   - `Equipment/`, `Rules*` → `rules-reference`
   - Everything else → `setting-document`

---

## Manual Verification (Optional)

After running the script, spot-check a few files to ensure correctness:

```bash
# Check a sample file
type D:\claude\filesystem\World_Building\Aethelmark\Aethelmark.md | head -10
```

Expected format:
```yaml
---
name: Aethelmark
type: setting-document
keywords: [location, world, lore]
description: A 16th century Central European campaign setting with historical realism and integrated fantasy elements
---
```

---

## Next Steps After Repair

1. **Rebuild the search index** to refresh corpus-search results:
   ```
   python3 /corpus/Python/build_indexes.py
   ```
   Or via MCP:
   ```
   index-tools:rebuild_indexes(load="search_status")
   ```

2. **Commit changes** to git:
   ```cmd
   D:
   cd D:\claude\filesystem
   git add .
   git commit -m "Maintenance: Add missing YAML type fields to World_Building files | 200 files fixed | 2026-05-15"
   git push origin main
   ```

3. **Verify in corpus-search** that type filtering works:
   ```
   corpus-search:search_corpus(query="vogt", type_filter="character")
   ```

---

## Reference: Type Field Values

These are the canonical `type` values used across the corpus:

| Type | Use Case | Examples |
|------|----------|----------|
| `character` | NPC and PC character sheets | Isalia Kreiger, Si'ken, Dammit |
| `location` | Geographic sites and settlements | Silberbach, Westgate, Camp Rochevaux |
| `faction` | Organizations (guilds, houses, corps) | Merchants Guild, House Kreiger, Nexagen |
| `scenario` | Session briefs and campaign frameworks | Nobles Commission, Maruvec Campaign |
| `session-summary` | Post-play writeups and checkpoints | Session 01 Summary, Checkpoint |
| `setting-document` | World lore and overview files | Aethelmark, Dead Terra, Gallihammer Overview |
| `rules-reference` | Mechanical and rules content | Equipment, Skills, Combat Rules |

---

## File Status After Repair

**All files will have proper YAML frontmatter in this structure:**

```yaml
---
name: {Document Title}
type: {Category From List Above}
keywords: [{keyword1}, {keyword2}, ...]
description: {One sentence summary}
---
```

This ensures:
- ✓ Compatibility with corpus-search indexing
- ✓ Proper display in Obsidian and other markdown tools
- ✓ Structured metadata for future tooling
- ✓ Consistency across the entire corpus

---

## Troubleshooting

**Script doesn't run:**
- Ensure Python 3 is installed: `python3 --version`
- Check file permissions: `chmod +x fix_yaml_compliance.py` (macOS/Linux)
- Verify path is correct: should be in `D:\claude\filesystem\Python\` (Windows)

**Some files show "error":**
- Check file encoding (should be UTF-8)
- Verify the file isn't locked or in use by another editor
- Review the error message in the script output

**Type field inferred incorrectly:**
- This is a one-time best-guess based on file path
- Can be manually corrected in Obsidian or any text editor
- Re-run the script only updates files missing fields; it doesn't overwrite existing correct values

---

**Report Complete | Ready for Repair**
