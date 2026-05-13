---
name: Corpus Search Index README
keywords: [search, fts5, mcp, sqlite, infrastructure]
description: Documentation for the FTS5-based corpus search MCP server.
---

# Corpus Search Index

Full-text ranked search over the worldbuilding corpus, exposed to Claude via a custom MCP server.

## Files

- `build_indexes.py` — Single walk that (re)builds `directory_index.md`, `directory_index_with_files.md`, and `search_index.db`
- `search_mcp_server.py` — MCP server exposing `search_corpus` and `index_status` tools to Claude
- `search_index.db` — SQLite database containing both tables below (auto-generated, gitignored)

## Indexed scope

Walks `/corpus` (the Docker container path for `D:\claude\filesystem\`) recursively. Excludes:

- `Trash/`
- `Python/`
- `Perchance_prompts/`
- `Sheet_Import/`
- `Miscelanious_rpg_material/`
- Hidden/build dirs (`.git`, `.github`, `.vscode`, `__pycache__`, `node_modules`)

## Schema

Two tables in `search_index.db`. FTS5 handles full-text ranking; `corpus_meta` handles structured field filtering.

### `corpus_fts` (FTS5 virtual table)

| Column      | Indexed? | BM25 weight | Source                                  |
|-------------|----------|-------------|-----------------------------------------|
| path        | no       | —           | Relative path from corpus root          |
| name        | yes      | 10×         | YAML frontmatter `name` field           |
| keywords    | yes      | 5×          | YAML frontmatter `keywords` (joined)    |
| description | yes      | 3×          | YAML frontmatter `description`          |
| category    | yes      | 0×          | Directory portion of the relative path  |
| content     | yes      | 1×          | Markdown body (frontmatter stripped)    |

### `corpus_meta` (regular SQL table)

| Column              | Type    | Source                                              |
|---------------------|---------|-----------------------------------------------------|
| path                | TEXT PK | Joins to `corpus_fts.path`                          |
| doc_type            | TEXT    | YAML frontmatter `type:` field (exact string)       |
| missing_name        | INTEGER | 1 if `name:` absent or empty in frontmatter         |
| missing_keywords    | INTEGER | 1 if `keywords:` absent or empty in frontmatter     |
| missing_description | INTEGER | 1 if `description:` absent or empty in frontmatter  |
| missing_type        | INTEGER | 1 if `type:` absent or empty in frontmatter         |

`corpus_meta` is only populated for `.md` files. Non-markdown files get an empty row.

**Why two tables?** FTS5's tokenizer splits on hyphens and underscores, making structured values like `setting-document` unsearchable as FTS5 tokens. SQL equality handles them correctly, so `type_filter` and `missing_filter` bypass FTS5 entirely and use `WHERE` clauses on `corpus_meta`.

## MCP tools

### `search_corpus(query, limit=10, category_filter=None, type_filter=None, missing_filter=None)`

Ranked full-text search with optional structured filters. All filters compose with AND — you can combine any or all of them in one call.

**`query`** — FTS5 expression:

```
Vogt                    single term (porter stemmed)
Vogt isalia             both terms present (implicit AND)
Vogt OR Sable           either term
"Reshaping Cascade"     exact phrase
petition NOT rejected   boolean exclusion
transform*              prefix match
```

**`category_filter`** — restricts to files in a path segment (FTS5 column filter):

```
category_filter="Manor"         only files under .../Manor/...
category_filter="Senior_Staff"  only Senior_Staff subfolder
category_filter="Cendrel"       only Cendrel region
```

**`type_filter`** — SQL equality on the `type:` frontmatter field:

```
type_filter="setting-document"  only setting documents
type_filter="character"         only character files
type_filter="session"           only session files
```

Hyphenated values work correctly here (unlike FTS5 terms).

**`missing_filter`** — finds files where a frontmatter field is absent or empty:

```
missing_filter="type"           files with no type: field
missing_filter="description"    files with no description:
missing_filter="keywords"       files with no keywords:
missing_filter="name"           files with no name:
```

**Combining filters** — all compose freely:

```
query="vogt isalia", type_filter="setting-document"
  → files mentioning both, restricted to setting documents

query="transformation", category_filter="Manor", missing_filter="type"
  → Manor files about transformation that still need a type field

query="*", missing_filter="type", category_filter="Cendrel"
  → all Cendrel files missing type (use * or any broad term)
```

### `index_status()`

Returns database path, file count, and last-built timestamp. Use to check staleness before relying on results.

## Rebuilding

Run after corpus drift (new files, edits, moves):

**Via MCP tool (preferred):** `index-tools:rebuild_indexes`

**Via bat file:** Double-click `refresh_indexes.bat` from Explorer

**Direct CMD:**
```cmd
cd D:\claude\filesystem\Python
python build_indexes.py
```

Takes ~0.5 seconds. Drops and recreates all three outputs.

## Limitations

- **Stale between rebuilds.** No file watcher — same staleness model as `directory_index.md`.
- **Keyword search only.** No semantic similarity. "Horned creature" won't find Vogt unless that phrase is in his file.
- **Frontmatter required for best ranking.** Files without YAML frontmatter still get indexed (filename used as name) but lose the high-weight metadata fields.
- **Apostrophes are tokenizer separators.** "Isalia's" indexes as ["isalia", "s"]. Searching `Isalia` finds it; `"Isalia's"` may not match.
- **`type_filter` requires exact match.** `type_filter="setting"` will not match files with `type: setting-document`. Use the full exact value.

## Troubleshooting

**MCP server fails to start in Claude Desktop**
- Check that `pip install mcp pyyaml` ran successfully
- Verify `python --version` is 3.10+ (3.14.x confirmed working)
- If `python` isn't on Claude Desktop's PATH, edit the config to use the absolute path to `python.exe`. Find it with `where python` in CMD.

**Search returns "Index not found"**
- Run `python build_indexes.py` from `D:\claude\filesystem\Python\`

**Search returns FTS5 syntax errors**
- The query likely contains a special character. Wrap problem terms in double quotes or use prefix matching.
- Note: `type_filter` and `missing_filter` use SQL equality and do not have FTS5 syntax constraints.

**Results feel stale**
- Call `index_status()` to check the last-built timestamp. Rebuild if needed.

**`type_filter` returning unexpected results**
- Check the exact `type:` value in the file's frontmatter — filter is case-sensitive and exact-match.
- Rebuild the index if the file was recently edited.
