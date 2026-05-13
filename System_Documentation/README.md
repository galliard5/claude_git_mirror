---
name: System Documentation README
type: documentation-index
keywords: [system, documentation, index, navigation, docker, indexer, search, audit]
description: Entry point for the System_Documentation directory; one-line summary of each reference doc.
---

# System Documentation

Reference docs for the infrastructure layer of the corpus — the Docker filesystem MCP container, the index builder, the corpus-search server, and the audit history. Worldbuilding content lives elsewhere; this folder is about how the *plumbing* works.

## Files

- **`Architecture.md`** — High-level picture of how Docker, the indexer, the two custom MCP servers, and the on-disk artifacts (indexes, search.db) fit together. Start here.
- **`Docker_Filesystem.md`** — The Docker filesystem MCP container. Dockerfile walkthrough, the `/corpus` mount, container vs Windows paths, restart procedure.
- **`Indexer.md`** — `build_indexes.py`, `cfg_loader.py`, `indexer.cfg`, `index_tools_mcp_server.py`, `refresh_indexes.bat`. Full `indexer.cfg` reference, all pattern syntax, the `line_N` sentinel, and how `rebuild_indexes(load=...)` exposes it to Claude.
- **`Search_Server.md`** — `search_mcp_server.py`. FTS5 schema (BM25 weights, UNINDEXED columns), `corpus_meta` companion table, full query syntax, the three filters (`category_filter`, `type_filter`, `missing_filter`), porter stemming.
- **`Security_Audit.md`** — Audit habits for Claude-authored Python scripts, the verified-clean walkthrough history of `build_search_index.py`, and danger-keyword checklist for future audits.
- **`Troubleshooting.md`** — Cross-component issues: stale index symptoms, search returning empty, container restart, recovering a corrupted `search_index.db`, hygiene queries.

## Conventions

- All paths in these docs use the Docker-container form (`/corpus/...`) for MCP tool examples, and the Windows host form (`D:\claude\filesystem\...`) for git, CMD, and Explorer operations. The same file has both addresses.
- Anything described as "hardcoded" lives in the source listed in `Indexer.md` or `Search_Server.md` — grep there before assuming a path is configurable.
- These docs are indexed by corpus-search (`type: documentation-*`), so `corpus-search:search_corpus("docker rebuild", type_filter="documentation-component")` will find the right file.
