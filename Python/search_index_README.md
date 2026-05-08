---
name: Corpus Search Index README
keywords: [search, fts5, mcp, sqlite, infrastructure]
description: Documentation for the FTS5-based corpus search MCP server.
---

# Corpus Search Index

Full-text ranked search over the worldbuilding corpus, exposed to Claude via a custom MCP server.

## Files

- `build_search_index.py` — Walks the corpus and (re)builds `search_index.db` from scratch
- `search_mcp_server.py` — MCP server exposing `search_corpus` and `index_status` tools to Claude
- `search_index.db` — SQLite database with FTS5 virtual table (auto-generated, gitignored recommended)

## Indexed scope

Walks `D:\Claude_MCP_folder` recursively for `.md` files. Excludes:

- `Trash/`
- `Python/`
- `Perchance_prompts/`
- `Sheet_Import/`
- `Miscelanious_rpg_material/`
- Hidden/build dirs (`.git`, `.github`, `.vscode`, `__pycache__`, `node_modules`)

## Schema

FTS5 virtual table `corpus_fts` with columns:

| Column      | Indexed? | Source                                  |
|-------------|----------|-----------------------------------------|
| path        | no       | Relative path from corpus root          |
| name        | yes      | YAML frontmatter `name` field           |
| keywords    | yes      | YAML frontmatter `keywords` (joined)    |
| description | yes      | YAML frontmatter `description`          |
| category    | yes      | Directory portion of the relative path  |
| content     | yes      | Markdown body (frontmatter stripped)    |

BM25 ranking weights: name (10×), keywords (5×), description (3×), content (1×). Category and path don't influence rank.

## Rebuilding

Run after corpus drift (new files, edits, moves):

```cmd
D:
cd D:\Claude_MCP_folder\Python
python build_search_index.py
```

Takes ~1 second for ~200 files. Drops and recreates the table — no migration logic.

## MCP tools (used through Claude)

- `search_corpus(query, limit=10, category_filter=None)` — Ranked FTS search
- `index_status()` — Returns file count and last-built timestamp

Query syntax follows FTS5 standard: `term`, `term1 term2` (AND), `term1 OR term2`, `"exact phrase"`, `term*` (prefix), `NOT term`.

## Limitations

- **Stale between rebuilds.** Same staleness model as `directory_index.md` — no file watcher.
- **Keyword search only.** No semantic similarity. "Horned creature" won't find Vogt unless that phrase is literally in his file.
- **Frontmatter required for best ranking.** Files without YAML frontmatter still get indexed (filename used as name) but lose the high-weight metadata fields.
- **Apostrophes are tokenizer separators.** "Isalia's" indexes as ["isalia", "s"]. Searching "Isalia" finds it; searching `"Isalia's"` may need quoting.

## Troubleshooting

**MCP server fails to start in Claude Desktop**
- Check that `pip install mcp pyyaml` ran successfully
- Verify `python --version` is 3.10+ (3.14.x confirmed working)
- If `python` isn't on Claude Desktop's PATH, edit the config to use the absolute path to `python.exe`. Find it with `where python` in CMD.

**Search returns "Index not found"**
- Run `python build_search_index.py` from `D:\Claude_MCP_folder\Python\`

**Search returns FTS5 syntax errors**
- The query likely contains a special character. Wrap problem terms in double quotes or use prefix matching.

**Results feel stale**
- Call `index_status()` to check the last-built timestamp. Rebuild if needed.
