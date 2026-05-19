# name: run_in_sandbox.py
# keywords: [testing, sandbox, docker, corpus, safety]
# description: Copies the corpus to a temporary test directory and runs a modification script inside a Docker container, so the real corpus is never accessible to the script.
#
# Creates a fresh test corpus copy at filesystem/test_corpus/, mounts it read-write
# into a python:3.12-slim container, then mounts the Python scripts directory read-only
# at /corpus/Python. The working directory inside the container is /corpus/Python, so
# relative paths (../) resolve to the test corpus exactly as they would in normal use.
# The real corpus is not mounted and cannot be reached.
#
# Requires Docker Desktop to be running. Uses python:3.12-slim (same base as the MCP
# server image — likely already cached).
#
# Command line arguments:
#   --no-pause: Skip end-of-run pause
#   --keep:     Keep test corpus after run (skip cleanup prompt)
#   script:     Script to run (e.g. validate_naming.py)
#   ...:        Any additional arguments are passed through to the target script
#
# Examples:
#   python run_in_sandbox.py validate_naming.py
#   python run_in_sandbox.py validate_naming.py --dry-run
#   python run_in_sandbox.py batch_update_npcs.py --dry-run
#   python run_in_sandbox.py fix_yaml_compliance.py --no-pause --keep

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
CORPUS_ROOT = SCRIPT_DIR.parent.resolve()
TEST_CORPUS = CORPUS_ROOT / "test_corpus"

DOCKER_IMAGE = "python:3.12-slim"
PIP_DEPS = "PyYAML==6.0.3"

# Top-level names to exclude from the corpus copy.
# Python/ is mounted separately (read-only); the rest are large, gitignored, or derived.
EXCLUDE_NAMES = {
    "Python",
    "index",
    "test_corpus",
    ".git",
    ".github",
    ".obsidian",
    "Stories",
    "Miscelanious_RPG_material",
    "Sheet_Import",
    "Trash",
}


def copy_corpus() -> None:
    if TEST_CORPUS.exists():
        print(f"Removing existing test corpus at {TEST_CORPUS} ...")
        shutil.rmtree(TEST_CORPUS)

    print(f"Copying corpus to {TEST_CORPUS} ...")
    shutil.copytree(
        CORPUS_ROOT,
        TEST_CORPUS,
        ignore=shutil.ignore_patterns(*EXCLUDE_NAMES),
    )
    print("  Done.\n")


def run_in_docker(script_name: str, script_args: list[str]) -> int:
    # Docker Desktop for Windows accepts Windows paths with backslashes in -v flags.
    corpus_mount  = f"{TEST_CORPUS}:/corpus:rw"
    scripts_mount = f"{SCRIPT_DIR}:/corpus/Python:ro"

    # Pass args through as a single shell string so the container shell handles quoting.
    args_str = " ".join(script_args)
    shell_cmd = f"pip install {PIP_DEPS} -q && python {script_name} {args_str}"

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", corpus_mount,
        "-v", scripts_mount,
        "-w", "/corpus/Python",
        "-e", "CORPUS_ROOT=/corpus",
        DOCKER_IMAGE,
        "sh", "-c", shell_cmd,
    ]

    print(f"Running {script_name} in Docker sandbox ...")
    print(f"  /corpus      → test_corpus/  (read-write)")
    print(f"  /corpus/Python → Python/     (read-only)")
    print(f"  Real corpus is not mounted.\n")
    print("-" * 60)

    result = subprocess.run(docker_cmd, text=True)

    print("-" * 60)
    return result.returncode


def offer_cleanup() -> None:
    if not TEST_CORPUS.exists():
        return
    answer = input(f"\nRemove test corpus at {TEST_CORPUS}? [y/N]: ").strip().lower()
    if answer == "y":
        shutil.rmtree(TEST_CORPUS)
        print("Test corpus removed.")
    else:
        print(f"Test corpus retained at {TEST_CORPUS}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a script in a Docker sandbox against a disposable corpus copy."
    )
    parser.add_argument("script", help="Script filename to run (e.g. validate_naming.py)")
    parser.add_argument(
        "script_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed through to the target script",
    )
    parser.add_argument("--no-pause", action="store_true", help="Skip end-of-run pause")
    parser.add_argument(
        "--keep", action="store_true", help="Keep test corpus after run (skip cleanup prompt)"
    )
    args = parser.parse_args()

    target = SCRIPT_DIR / args.script
    if not target.exists():
        print(f"Error: {args.script} not found in {SCRIPT_DIR}")
        sys.exit(1)

    start = time.time()

    copy_corpus()
    returncode = run_in_docker(args.script, args.script_args)

    elapsed = time.time() - start
    print(f"\nRuntime: {elapsed:.1f}s")

    if not args.keep:
        offer_cleanup()

    if not args.no_pause:
        input("\nPress Enter to exit...")

    sys.exit(returncode)


if __name__ == "__main__":
    main()
