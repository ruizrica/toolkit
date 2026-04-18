---
description: "Initialize project: install CLIs, index memory, generate handbook, install git hooks, write orchestration CLAUDE.md"
---

# /setup

Self-bootstrapping entry point. Detects and installs every external dependency the toolkit needs, seeds the project handbook, wires git hooks for auto-refresh, and writes a `CLAUDE.md` + `AGENTS.md` that encodes the cohesion rules.

Run once per project. Idempotent — safe to re-run to refresh.

```bash
!python3 - <<'PY'
import os
import shutil
import subprocess
from pathlib import Path


def run(command, *, cwd, capture=False, check=True, env=None):
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=capture,
        check=check,
        env=env,
    )


def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(1)


def git_root():
    result = run(["git", "rev-parse", "--show-toplevel"], cwd=Path.cwd(), capture=True, check=False)
    if result.returncode != 0:
        fail("Not a git repository. Run /setup from a project directory.")
    return Path(result.stdout.strip())


def plugin_root():
    """Locate the toolkit plugin's own root (where scripts/ lives)."""
    for candidate in [
        Path.home() / ".claude" / "plugins" / "cache" / "toolkit" / "toolkit",
        Path(__file__).resolve().parent if "__file__" in globals() else None,
    ]:
        if candidate and (candidate / "scripts").exists():
            return candidate
    env_override = os.environ.get("TOOLKIT_PLUGIN_ROOT")
    if env_override and (Path(env_override) / "scripts").exists():
        return Path(env_override)
    # Fall back to searching relative to known layouts
    for candidate in [
        Path.home() / "Workshop" / "GitHub" / "agent-toolkit" / "plugins" / "toolkit",
    ]:
        if candidate.exists():
            return candidate
    fail("Cannot locate toolkit plugin root. Set TOOLKIT_PLUGIN_ROOT=/path/to/plugins/toolkit")


def ensure_cli(name, installer_script, plugin):
    if shutil.which(name):
        print(f"✓ {name}: already on PATH ({shutil.which(name)})")
        return
    script = plugin / "scripts" / installer_script
    if not script.exists():
        fail(f"Installer missing: {script}")
    print(f"⚙ Installing {name} via {script.name} ...")
    result = run(["bash", str(script)], cwd=plugin, check=False)
    if result.returncode != 0 or not shutil.which(name):
        fail(f"{name} install failed; install manually and re-run /setup")
    print(f"✓ {name}: installed")


def index_codebase(root):
    print("⚙ Indexing codebase with agent-memory ...")
    result = run(["agent-memory", "index"], cwd=root, capture=True, check=False)
    if result.returncode != 0:
        fail(f"agent-memory index failed:\n{result.stdout}\n{result.stderr}")
    print("✓ agent-memory: indexed")


def generate_handbook(root, plugin):
    script = plugin / "scripts" / "handbook.py"
    if not script.exists():
        print(f"⚠ SKIP: handbook.py not found at {script}")
        return
    print("⚙ Generating HANDBOOK.md ...")
    result = run(
        ["python3", str(script), "--path", str(root), "--output", "HANDBOOK.md"],
        cwd=root,
        capture=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"⚠ handbook.py failed (non-fatal):\n{result.stdout}\n{result.stderr}")
        return
    print("✓ HANDBOOK.md: generated")


def install_git_hooks(root, plugin):
    script = plugin / "scripts" / "install-git-hooks.sh"
    if not script.exists():
        print(f"⚠ SKIP: install-git-hooks.sh not found at {script}")
        return
    print("⚙ Installing git hooks ...")
    env = os.environ.copy()
    env["TOOLKIT_PLUGIN_ROOT"] = str(plugin)
    result = run(["bash", str(script)], cwd=root, check=False, env=env)
    if result.returncode != 0:
        print("⚠ git hooks install failed (non-fatal)")
        return
    print("✓ git hooks: installed")


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

Auto-generated by `/setup`. Hand-edit below the orchestration section for project-specific notes.

## Orchestration Manifest

This project uses the toolkit plugin. The following rules define how the tools interweave.

### Tool inventory
- **HANDBOOK.md** — AI-optimized multi-layer project reference (regenerated by git hooks)
- **agent-memory CLI** — hybrid semantic + BM25 search over memory files and daily logs
- **agent-viewer CLI** — editable browser review for plans, specs, completions, reports
- Commands: `/haiku`, `/team`, `/handbook`, `/@implement`, `/setup`, `/worktree`, `/save`, `/stable`, `/compact`, `/compact-min`, `/restore`, `/design`, `/kiro`, `/agent-memory`, `/code2course`
- Skills: `agent-memory`, `agent-viewer`, `autoresearch`, `codebase-to-course`

### Cohesion rules (mandatory)

1. **Handbook-first**: for architecture, module, or extension questions, read the relevant layer of `HANDBOOK.md` before diving into files.
2. **Memory-first**: for "what did we decide / where is X / how does Y work" questions, query `agent-memory search` before reading files.
3. **Memory-write**: after significant decisions, run `agent-memory add "…" --source memory --tags "…"`. Compaction auto-saves daily logs.
4. **Plan-via-viewer**: when plan mode is active, or a plan file has just been written, or a diagram is about to be shown, invoke `agent-viewer plan` and wait for `approved` before proceeding. See `skills/agent-viewer.md`.
5. **Spec-via-viewer**: Kiro's 3-document set (requirements/design/tasks) is presented via `agent-viewer spec` with the rich `documents[]` payload.
6. **Completion-via-viewer**: when work wraps, build a `completion-payload.json` (summary + Mermaid + diffs + checklist) and show via `agent-viewer completion`.
7. **Compact/restore loop**: new sessions begin with `/restore` if `.context/session-state.json` exists; long sessions trigger `/compact` via the memory-cycle hook.

### Bootstrap
If `agent-memory` or `agent-viewer` is not on PATH, run `/setup` — it installs what's missing.

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
- TDD: write failing test → watch it fail → make it pass → refactor.

## Architecture Decisions

- Document key tradeoffs and component boundaries here.
"""


def ensure_claude_md(root):
    claude_file = root / "CLAUDE.md"
    if claude_file.exists():
        print(f"✓ CLAUDE.md: already present ({claude_file})")
        return claude_file
    claude_file.write_text(generate_claude_md(root), encoding="utf-8")
    print("✓ CLAUDE.md: written")
    return claude_file


def ensure_agents_md(root):
    agents_file = root / "AGENTS.md"
    if agents_file.exists():
        print("✓ AGENTS.md: already present")
        return
    content = """# Agent Configuration

See [CLAUDE.md](./CLAUDE.md) for the orchestration manifest, cohesion rules, and tool inventory.
"""
    agents_file.write_text(content, encoding="utf-8")
    print("✓ AGENTS.md: written")


def main():
    root = git_root()
    plugin = plugin_root()

    print(f"Toolkit plugin root: {plugin}")
    print(f"Project root:        {root}\n")

    ensure_cli("agent-memory", "install-agent-memory.sh", plugin)
    ensure_cli("agent-viewer", "install-agent-viewer.sh", plugin)

    index_codebase(root)
    generate_handbook(root, plugin)
    install_git_hooks(root, plugin)

    ensure_claude_md(root)
    ensure_agents_md(root)

    print("\n✅ Setup complete.")
    print("\nNext steps:")
    print("  /worktree            — create isolated worktree for your first task")
    print("  /handbook            — refresh HANDBOOK.md on demand")
    print("  /kiro <feature>      — spec-driven feature build")


if __name__ == "__main__":
    main()
PY
```
