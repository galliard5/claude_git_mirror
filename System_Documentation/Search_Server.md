---
name: Corpus Search Server
type: documentation-component
keywords: [search, fts5, sqlite, bm25, corpus_meta, type_filter, missing_filter, category_filter, porter, stemming, search_mcp_server]
description: Full reference for search_mcp_server.py - FTS5 schema, BM25 weights, the three filters, and the corpus_meta hygiene table.
---

# Corpus Search Server

`Python/search_mcp_server.py` is a custom MCP server exposing full-text ranked search over the corpus. The index is `index/search_index.db` — a SQLite file with one FTS5 virtual table for ranked search and one regular table for structured field filtering.

## Database schema

Two tables. FTS5 handles full-text ranking; SQL equality on `corpus_meta` handles structured field filters that FTS5's tokenizer would mangle.

### `corpus_fts` (FTS5 virtual table)

| Column       | Indexed? | BM25 weight | Source                                  |
|--------------|----------|-------------|-----------------------------------------|
| path         | no       | —           | Relative path from corpus root          |
| name         | yes      | 10×         | YAML frontmatter `name` field           |
| keywords     | yes      | 5×          | YAML frontmatter `keywords` (joined)    |
| description  | yes      | 3×          | YAML frontmatter `description`          |
| category     | yes      | 0×          | Directory portion of the relative path  |
| content      | yes      | 1×          | Markdown body (frontmatter stripped)    |

**Why `path` is UNINDEXED:** Folder names like "Aethelmark" appear in thousands of paths. Indexing them would drown content matches. Path is stored for retrieval but excluded from search.

**Why `category` has weight 0:** It's indexed so `category:"Manor"` column filters work, but a weight of 0 means a bare `Manor` query doesn't get inflated by every file under that directory.

**Tokenizer:** `porter unicode61`. The porter stemmer means `transform`, `transformed`, `transformation` all stem to the same root. Unicode61 handles accented characters reasonably well.

### `corpus_meta` (regular SQL table)

| Column                  | Type      | Source                                              |
|-------------------------|-----------|-----------------------------------------------------|
| path                    | TEXT PK   | Joins to `corpus_fts.path`                          |
| doc_type                | TEXT      | YAML frontmatter `type:` field (exact string)       |
| missing_name            | INTEGER   | 1 if `name:` absent or empty                        |
| missing_keywords        | INTEGER   | 1 if `keywords:` absent or empty                    |
| missing_description     | INTEGER   | 1 if `description:` absent or empty                 |
| missing_type            | INTEGER   | 1 if `type:` absent or empty                        |

Only populated for `.md` files. Non-markdown files get an empty row so the JOIN doesn't drop them.

**Why a second table at all?** FTS5's tokenizer splits on hyphens and underscores. The value `setting-document` tokenizes as `["setting", "document"]` — searching `type:"setting-document"` doesn't work, and you can't filter on a column with an unsearchable value. SQL equality on a regular table sidesteps the whole problem.

**Why IN subqueries, not JOIN conditions?** FTS5 has a known quirk where non-MATCH WHERE clauses on joined tables get silently ignored — the query runs but the filter does nothing. Wrapping `corpus_meta` lookups as `f.path IN (SELECT path FROM corpus_meta WHERE doc_type = ?)` is the workaround.

## The `search_corpus` tool

```python
search_corpus(
    query: str,
    limit: int = 10,
    category_filter: str | None = None,
    type_filter: str | None = None,
    missing_filter: str | None = None,
) -> str
```

All filters compose with AND. Combine any or all in one call.

### Query syntax (FTS5)

| Form                       | Effect                                                                |
|----------------------------|-----------------------------------------------------------------------|
| `Vogt`                     | Single term, porter-stemmed (matches Vogt, Vogts).                    |
| `Vogt security`            | Both terms present (implicit AND).                                    |
| `Vogt OR Sable`            | Either term.                                                          |
| `"Reshaping Cascade"`      | Exact phrase. Escape inner quotes by doubling: `""`.                  |
| `petition NOT rejected`    | Boolean exclusion.                                                    |
| `transform*`               | Prefix match (transformed, transformation, transformative).           |

Inputs are wrapped in parentheses internally for predictable operator precedence. Embedded `"` in user input is escaped (doubled) before being passed to FTS5.

### `category_filter` — FTS5 column filter on path

```python
category_filter="Manor"         # only files under .../Manor/...
category_filter="Senior_Staff"  # only Senior_Staff subfolder
category_filter="Cendrel"       # only Cendrel region
```

Implemented as an FTS5 column filter (`category:"Manor"`) added to the MATCH expression. Works on path segments only — not arbitrary substrings.

### `type_filter` — SQL equality on `corpus_meta.doc_type`

```python
type_filter="setting-document"  # exact match
type_filter="character"
type_filter="session"
```

Case-sensitive, exact-match. Hyphens are fine (this is the whole reason `corpus_meta` exists).

### `missing_filter` — corpus hygiene

Finds files where a required frontmatter field is missing or empty. The most useful corpus-hygiene tool.

```python
missing_filter="type"           # files with no type:
missing_filter="description"    # files with no description:
missing_filter="keywords"       # files with no keywords:
missing_filter="name"           # files with no name:
```

Valid values: `name`, `keywords`, `description`, `type`. Validated server-side before touching the DB.

### Combining filters

All three filters compose freely:

```python
# Files mentioning both terms, restricted to setting docs
search_corpus("vogt isalia", type_filter="setting-document")

# Manor files about transformation that still need a type field
search_corpus("transformation", category_filter="Manor", missing_filter="type")

# All Cendrel files missing type (use any broad query)
search_corpus("*", missing_filter="type", category_filter="Cendrel")
```

For "all files where X is missing" without a content query, you still need a query string — pass any broad term or wildcard.

## The `index_status` tool

```python
index_status() -> str
```

Returns the DB path, total file count, and last-built timestamp. Use to verify freshness before relying on results.

## Result format

Each result includes:
- BM25 score (magnitude — FTS5 returns negative, the tool flips to positive)
- Relative path
- `name`, `keywords`, `description`, `type` from frontmatter
- `Missing:` list if any required fields are absent
- A snippet with `** **` markers around matched terms

## Limitations

- **Stale between rebuilds.** No file watcher. The same staleness model as `directory_index.md` — rebuild after edits.
- **Keyword search only, no semantics.** "Horned creature" won't find Vogt unless that exact phrase is in his file.
- **Frontmatter required for best ranking.** Files without YAML get indexed (filename used as name) but lose the high-weight metadata fields. Run `missing_filter="name"` to find them.
- **Apostrophes are tokenizer separators.** "Isalia's" indexes as `["isalia", "s"]`. Searching `Isalia` finds it; quoted `"Isalia's"` may not.
- **`type_filter` is exact match.** `type_filter="setting"` will NOT match files with `type: setting-document`. Use the full value.

## Security posture

- DB opened **read-only** via SQLite URI (`?mode=ro`). The server cannot write to the database.
- All user input passed via SQLite parameter binding (`?` placeholders). No string concatenation, no SQL injection surface.
- No path arguments exposed. The DB path is hardcoded. The only thing reachable through this server is ranked search over the pre-built tables.
- `missing_filter` is whitelisted server-side against `{"name", "keywords", "description", "type"}`. Any other value is rejected before touching SQL.

See `Security_Audit.md` for the full audit walkthrough.

## Hardcoded paths

```python
_CORPUS_ROOT = Path(os.environ.get("CORPUS_ROOT", r"D:\claude\filesystem"))
DB_PATH = _CORPUS_ROOT / "index" / "search_index.db"
```

`CORPUS_ROOT` env var lets Docker override without editing source. The hardcoded fallback is for native runs. **Must stay in lockstep** with `indexer.cfg [paths] index_directory` and with `index_tools_mcp_server.py SEARCH_DB`.
