---
name: Docker Filesystem MCP
type: documentation-component
keywords: [docker, filesystem, mcp, container, dockerfile, mount, paths, restart]
description: The Docker filesystem MCP container - Dockerfile, mount layout, path conventions, and restart procedures.
---

# Docker Filesystem MCP

The standard Anthropic filesystem MCP server, packaged in Docker, serving the corpus at `/corpus`.

## Why Docker

- **Path consistency.** The container always sees the corpus at `/corpus`. Claude's tool calls always use that prefix. No "is this Windows or WSL" ambiguity.
- **Isolation.** The MCP server can't reach anything outside the bind mount. Audit boundary is the `docker-compose.yml`, not the script's `open()` calls.
- **Reproducibility.** The same Dockerfile produces the same server on any host that has Docker. If we ever distribute the framework, this becomes the install story.

The two custom Python MCP servers (`corpus-search`, `index-tools`) share the same image — see `Python/Dockerfile`. The filesystem MCP itself is the official one and runs in its own container.

## Path conventions

Two address spaces for the same file:

| Context                             | Address form                                          | Example                                       |
|-------------------------------------|-------------------------------------------------------|-----------------------------------------------|
| MCP tool calls                      | `/corpus/...` (container path)                        | `/corpus/World_Building/Aethelmark/Aethelmark.md` |
| Windows host (git, CMD, Explorer)   | `D:\claude\filesystem\...`                            | `D:\claude\filesystem\World_Building\Aethelmark\Aethelmark.md` |
| Obsidian vault root                 | `D:\claude\filesystem\`                               | (Obsidian sees the vault, not the container) |

**Rule:** Anywhere Claude is reading or writing via MCP tools, use `/corpus/...`. Anywhere a human is typing into CMD, a git command, or File Explorer, use `D:\claude\filesystem\...`.

## The mount

`docker-compose.yml` binds `D:\claude\filesystem\` to `/corpus` inside the container. The mount is the entire corpus root — so the container sees `Core_Rules/`, `World_Building/`, `Python/`, `index/`, etc. at the top of `/corpus`. This single mount line is the security boundary; nothing else from the host is visible.

## The custom-server Dockerfile

`Python/Dockerfile` builds the image used by both custom MCP servers. Walkthrough:

```dockerfile
FROM python:3.12-slim
```
Slim Python base — about 50 MB. Enough for `mcp`, `pyyaml`, and `sqlite3` (stdlib).

```dockerfile
RUN useradd -m -u 1000 mcp
```
Non-root user. Docker Desktop on Windows handles bind-mount permissions transparently, so this doesn't get in the way of corpus read/write — it's defense in depth in case the image is ever used on Linux.

```dockerfile
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Dependencies installed in a separate layer from the application code, so dependency installs are cached and rebuilds only re-pip when `requirements.txt` changes.

```dockerfile
COPY search_mcp_server.py .
COPY index_tools_mcp_server.py .
COPY build_indexes.py .
COPY cfg_loader.py .
```
All four scripts copied. Either MCP server image works for either purpose — the `command:` in `docker-compose.yml` picks which script runs.

```dockerfile
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV CORPUS_ROOT=/corpus
```

- `MCP_TRANSPORT` — `streamable-http` for Docker, `stdio` for local. The MCP framework reads this and picks the right wire format.
- `MCP_HOST=0.0.0.0` — bind on all interfaces *inside the container*. Doesn't expose to the host network; the host only sees what `docker-compose.yml` publishes.
- `MCP_PORT=8000` — overridden per service in docker-compose.
- `CORPUS_ROOT=/corpus` — both Python servers read this env var to find the corpus. The hardcoded fallback in each `.py` file (`D:\claude\filesystem`) only kicks in when running natively without Docker.

```dockerfile
USER mcp
```
Drop privileges before running the server.

No `CMD` — each service in `docker-compose.yml` sets its own.

## Restart procedure

### Restart the filesystem MCP (rare)
```cmd
docker compose restart filesystem
```
Restart only when you've changed the mount config or the filesystem MCP version. The filesystem MCP itself rarely needs touching.

### Restart a custom MCP server (after editing `search_mcp_server.py` or `index_tools_mcp_server.py`)

If running in Docker:
```cmd
docker compose restart corpus-search
docker compose restart index-tools
```

If running as a stdio subprocess of Claude Desktop:
- Quit Claude Desktop completely
- Reopen
- The subprocess relaunches with the new source

### Full rebuild (after Dockerfile or requirements.txt changes)
```cmd
docker compose build
docker compose up -d
```

## Troubleshooting

**"Permission denied" on file write inside container**
Check the bind-mount permissions in `docker-compose.yml`. On Docker Desktop for Windows, the named-user UID inside the container doesn't need to match the host — the layer translates. If you see this on Linux, the host user owning `D:\claude\filesystem\` must match UID 1000 or the mount must be `:rw` with appropriate group settings.

**Container shows files but can't see recent edits**
The bind mount is real-time, not cached. If you don't see recent edits, you're probably looking at a stale `directory_index.md` rather than missing files. Run `rebuild_indexes`.

**Cross-platform path issues**
Always use forward-slash `/corpus/...` paths in MCP tool calls. Windows backslashes leak into MCP calls when copy-pasting from CMD output, and the filesystem MCP rejects them.

**Custom MCP server "tool not found" errors**
The server didn't start. Check `claude_desktop_config.json` for the right command, and check `requirements.txt` is satisfied. `python --version` must be 3.10+ (3.12 in the Docker image).

See also `Troubleshooting.md` for cross-component issues.
