---
description: "Initialize project context and prime agent-memory"
---

# /setup

Initialize the repository context for agent workflows.

```bash
!python3 - <<'PY'
import os
import re
import shutil
import subprocess
from pathlib import Path

def run(command, *, cwd, capture=False, check=True):
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=capture,
        check=check,
    )


def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(1)


def git_root():
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=Path.cwd(), capture=True, check=False)
    if result.returncode != 0:
        fail("Not a git repository. Run /setup from a project directory.")
    return Path(result.stdout.strip())


def require_agent_memory():
    if shutil.which("agent-memory") is None:
        fail(
            "agent-memory CLI is missing from PATH.\n"
            "Install it: pip3 install --break-system-packages -e ~/.toolkit/tools/agent-memory"
        )


def index_codebase(root):
    print("Running agent-memory index ...")
    result = run(["agent-memory", "index"], cwd=root, capture=True, check=False)
    if result.returncode != 0:
        fail(f"agent-memory index failed:\n{result.stdout}\n{result.stderr}")
    if result.stdout.strip():
        print(result.stdout.strip())
    print("agent-memory index complete.")


def detect_stack(root):
    detected = []
    if (root / "package.json").exists():
        detected.append("Node.js / TypeScript")
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        detected.append("Python")
    if (root / "go.mod").exists():
        detected.append("Go")
    if (root / "Cargo.toml").exists():
        detected.append("Rust")
    if (root / "pom.xml").exists():
        detected.append("Java")
    if not detected:
        detected.append("Unknown")
    return sorted(detected)


def top_level_dirs(root):
    ignore = {".git", ".venv", "node_modules", "dist", "build", "target"}
    dirs = []
    for item in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if item.is_dir() and not item.name.startswith(".") and item.name not in ignore:
            dirs.append(item.name)
    return dirs


def generate_claude_md(root):
    stack_lines = "\n- ".join(detect_stack(root))
    dir_lines = "\n- ".join(top_level_dirs(root)) or "(project scaffold)"
    return f"""# Project Context

## Memory Tool Primacy

Use `agent-memory` before reading files for repeated context questions.

- `agent-memory query \"...\"` for semantic recall.
- `agent-memory recall \"...\"` for direct memory retrieval.
- `agent-memory search \"...\" --keyword` for exact match lookup.

## When to use search vs file reads

- Use memory search for architecture decisions, standards, and historical notes.
- Use file reads for current implementation details and active work-in-progress code.

## Project Structure

- Top-level: `{root}`
- Directories:
  - {dir_lines}

## Tech Stack

- {stack_lines}

## Coding Conventions

- Keep changes scoped and small.
- Respect existing naming and file layout conventions.
- Prefer deterministic, reviewable edits over broad refactors.

## Architecture Decisions

- Document key tradeoffs and component boundaries here.
"""


def ensure_claude_md(root):
    claude_file = root / "claude.md"
    if claude_file.exists():
        print("SKIP: claude.md already exists")
        return claude_file

    claude_file.write_text(generate_claude_md(root), encoding="utf-8")
    print("Created: claude.md")
    return claude_file


def ensure_agents_md(root):
    agents_file = root / "agents.md"
    if agents_file.exists():
        print("SKIP: agents.md already exists")
        return

    content = """# Agent Configuration

See [claude.md](./claude.md) for project context, coding standards, and memory tool usage guidelines.

## Memory Tool Usage
This project uses the agent-memory CLI. Refer to claude.md for detailed instructions on context retrieval.
"""
    agents_file.write_text(content, encoding="utf-8")
    print("Created: agents.md")


def main():
    root = git_root()
    require_agent_memory()
    index_codebase(root)

    context = ensure_claude_md(root)
    ensure_agents_md(root)

    print("\nSetup summary:")
    print("- agent-memory index: complete")
    print(f"- context file: {context}")
    print("- agents file: agents.md")
    print("\nNext steps:")
    print("1) Run /worktree [path] [branch] to create your first worktree")
    print("2) Run /worktree [path] [branch] again for additional worktrees")


if __name__ == "__main__":
    main()
PY
