---
name: Python_Scripts_Protocol
type: rules-reference
keywords: [python, scripts, protocol, conventions, cli, rules]
description: Terse rules for running and writing Python scripts in the Python/ directory.
---

**Authoritative rules for Python scripts.** For reasoning, examples, and extended guidance, see `System_Documentation/Python_Scripts.md`.

---

## RUNNING SCRIPTS

- All scripts live in `Python/` (Windows host path: `D:\claude\filesystem\Python\`)
- Run from CMD: `cd D:\claude\filesystem\Python && python script_name.py [options]`
- Use `python` not `python3` in all CMD calls and `.bat` files
- Last verified Python version: 3.14.3
- Each script has header comments describing what it does, its arguments, and its category — **read the header before running an unfamiliar script**

---

## SCRIPT CATEGORIES

**Modification scripts** — write to or rename corpus files (e.g. `validate_naming.py`, `cleanup_legacy_tags.py`, `convert_to_markdown.py`, `process_session_summary.py`):
- Must be called with `--dry-run` first to preview changes
- Will prompt for confirmation before applying any modification
- Never run without reviewing the dry-run output first

**Rebuild / read-only scripts** — generate derived artifacts, never modify corpus files (e.g. `build_indexes.py`):
- Safe to run freely; no corpus side-effects
- Support `--no-pause` for unattended/automated execution
- Preferred invocation: `index-tools:rebuild_indexes` (in-session) or `refresh_indexes.bat` (manual)

---

## REQUIRED HEADER FORMAT (.py files)

Every script must open with:
```python
# name: Script Name
# keywords: [keyword1, keyword2]
# description: What this script does
#
# Human-readable top-level description
#
# Command line arguments:
#   --dry-run: Preview without executing (modification scripts only)
#   --no-pause: Skip end-of-run pause (rebuild scripts only)
```

---

## WRITING NEW SCRIPTS

Before writing a new script:
1. Check `Python/` — the utility may already exist
2. Determine category (modification vs rebuild) — this governs whether `--dry-run` is required
3. Write the header block first
4. For modification scripts: implement `--dry-run`, preview output, and confirmation prompt before any write

Full conventions and rationale: `System_Documentation/Python_Scripts.md`
