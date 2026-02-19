---
description: "Create an isolated development worktree (auto-generates branch and path)"
argument-hint: "[path] [branch]"
---

# /worktree

Create an isolated development worktree. Auto-generates branch and path when not specified.

- `/worktree` - create worktree with auto-generated branch (wip-YYYYMMDD-HHMMSS)
- `/worktree [path]` - create worktree at custom path, auto-generate branch
- `/worktree [path] [branch]` - create worktree with custom path and branch

```bash
!WORKTREE_ARGS="$ARGUMENTS"
!python3 - <<'PY'
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


def run(command, cwd, *, check=True, capture=False, input_text=None):
    kwargs = {
        "cwd": str(cwd),
        "text": True,
        "check": check,
    }
    if capture:
        kwargs["capture_output"] = True
    if input_text is not None:
        kwargs["input"] = input_text
    return subprocess.run(command, **kwargs)


def fail(message):
    print(f"ERROR: {message}")
    raise SystemExit(1)


def require_git_repo():
    result = run(["git", "rev-parse", "--show-toplevel"], Path.cwd(), capture=True, check=False)
    if result.returncode != 0:
        fail("Not a git repository.")
    return Path(result.stdout.strip())


@dataclass
class WorktreeState:
    path: Path | None = None
    branch: str | None = None
    created_branch: bool = False


def branch_exists(root, branch):
    return run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], root, check=False).returncode == 0


def remote_branch_exists(root, branch):
    return run(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"], root, check=False).returncode == 0


def get_branches(root):
    result = run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads/"], root, capture=True)
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def generate_wip_names():
    """Generate timestamp-based wip branch and path names."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"wip-{timestamp}"
    path = f".specbook/worktrees/{branch_name}"
    return path, branch_name


def choose_branch(root):
    """Interactive branch selection (used when explicitly requested)."""
    branches = get_branches(root)
    if not branches:
        fail("No local branches exist.")
    if shutil.which("fzf"):
        fzf = run(["fzf", "--prompt=branch> "], root, capture=True, input_text="\n".join(branches) + "\n")
        if fzf.returncode == 0 and fzf.stdout.strip():
            return fzf.stdout.strip()
        print("WARN: fzf exited without selection, falling back.")
    if sys.stdin.isatty():
        for index, branch in enumerate(branches, start=1):
            print(f"{index}) {branch}")
        selection = input(f"Select branch [1]: ").strip()
        if selection:
            try:
                idx = int(selection)
                if 1 <= idx <= len(branches):
                    return branches[idx - 1]
            except ValueError:
                pass
        if branches:
            return branches[0]
    return branches[0]


def install_dependencies(root):
    path = Path(root)
    if (path / "package-lock.json").exists() and shutil.which("npm"):
        print("Installing npm dependencies...")
        return_code = run(["npm", "install"], path).returncode
        if return_code != 0:
            fail("npm install failed.")
        return

    if (path / "pnpm-lock.yaml").exists() and shutil.which("pnpm"):
        print("Installing pnpm dependencies...")
        return_code = run(["pnpm", "install"], path).returncode
        if return_code != 0:
            fail("pnpm install failed.")
        return

    if (path / "yarn.lock").exists() and shutil.which("yarn"):
        print("Installing yarn dependencies...")
        return_code = run(["yarn", "install"], path).returncode
        if return_code != 0:
            fail("yarn install failed.")
        return

    if (path / "requirements.txt").exists() and shutil.which("python3"):
        print("Installing python requirements...")
        return_code = run(["python3", "-m", "pip", "install", "-r", "requirements.txt"], path).returncode
        if return_code != 0:
            fail("python dependency install failed.")
        return


def copy_env_if_available(root):
    template = root / ".env.example"
    target = root / ".env"
    if template.exists() and not target.exists():
        target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Copied {template} -> {target}")


def open_editor(root, no_editor=False):
    if no_editor:
        return
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        return
    try:
        subprocess.Popen(editor.split() + [str(root)])
    except FileNotFoundError:
        print(f"WARN: editor '{editor}' not found; skipped auto-open.")


def parse_args(raw):
    tokens = raw.split() if raw.strip() else []

    if len(tokens) > 2:
        fail(f"Too many arguments: {' '.join(tokens)}")

    return {
        "path": tokens[0] if len(tokens) >= 1 else None,
        "branch": tokens[1] if len(tokens) >= 2 else None,
    }


def add_worktree(root, path, branch, run_setup, state, open_editor_flag=True):
    command = ["git", "worktree", "add"]
    created = not branch_exists(root, branch)
    if created:
        if remote_branch_exists(root, branch):
            command.extend(["-b", branch, str(path), f"origin/{branch}"])
        else:
            command.extend(["-b", branch, str(path)])
        state.created_branch = True
    else:
        command.extend([str(path), branch])
    print(f"Creating worktree: {path} ({branch})")
    result = run(command, root, check=False)
    if result.returncode != 0:
        fail(f"git worktree add failed: {result.stderr}")
    state.path = Path(path)
    state.branch = branch
    if run_setup:
        install_dependencies(path)
        copy_env_if_available(path)
        open_editor(path, no_editor=not open_editor_flag)


def rollback(root, state):
    if state.path and state.path.exists():
        run(["git", "worktree", "remove", "--force", str(state.path)], root, check=False)
    if state.created_branch and state.branch:
        run(["git", "branch", "-D", state.branch], root, check=False)


def cmd_create(root, options):
    # Auto-generate branch and path if not provided
    auto_path, auto_branch = generate_wip_names()
    
    branch = options["branch"] or auto_branch
    path = options["path"] or f".specbook/worktrees/{branch}"
    absolute = root / path if not Path(path).is_absolute() else Path(path)
    absolute.parent.mkdir(parents=True, exist_ok=True)

    state = WorktreeState()
    try:
        add_worktree(root, absolute, branch, True, state)
        print(f"Created worktree: {absolute}")
        print(f"Branch: {branch}")
        print("Environment: .env prepared (if .env.example exists)")
        print("Editor launch: attempted (if $EDITOR or $VISUAL is set)")
    except Exception:
        rollback(root, state)
        raise


def print_help():
    print("Usage:")
    print("  /worktree          - Auto-create worktree with timestamp-based branch")
    print("  /worktree [path]   - Create worktree at custom path, auto-generate branch")
    print("  /worktree [path] [branch]  - Create worktree with custom path and branch")
    print("")
    print("Creates a git worktree and runs setup automation in that worktree.")
    print("When run without arguments, generates wip-YYYYMMDD-HHMMSS branch automatically.")
    print("Setup includes: dependency install, .env copy, editor launch.")


def main():
    root = require_git_repo()
    raw_args = os.environ.get("WORKTREE_ARGS", "")
    if raw_args.strip() in {"help", "--help", "-h"}:
        print_help()
        return

    options = parse_args(raw_args)
    cmd_create(root, options)


if __name__ == "__main__":
    main()
PY
