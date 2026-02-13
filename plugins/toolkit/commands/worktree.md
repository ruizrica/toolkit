---
description: "Manage git worktrees for isolated agent development"
argument-hint: "<add|setup|list|remove> [path] [branch]"
---

# /worktree

Manage worktrees from the current git repository.

Subcommands:

- `add [path] [branch]` - create a worktree.
- `setup [path] [branch]` - create + run setup automation.
- `list` - list all worktrees.
- `remove <path-or-branch>` - remove a worktree (use `--force` to remove dirty worktree).

```bash
!WORKTREE_ARGS="$ARGUMENTS"
!python3 - <<'PY'
import os
import shlex
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


def choose_branch(root):
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


def get_current_branch(root):
    result = run(["git", "branch", "--show-current"], root, capture=True)
    branch = result.stdout.strip()
    return branch or "main"


def parse_args(raw):
    tokens = shlex.split(raw) if raw.strip() else []
    if not tokens:
        return "help", [], {}

    command = tokens[0]
    rest = tokens[1:]
    options = {"path": None, "branch": None, "force": False}
    positional = []

    i = 0
    while i < len(rest):
        token = rest[i]
        if token in {"--path", "-p"}:
            i += 1
            if i >= len(rest):
                fail(f"Missing value for {token}")
            options["path"] = rest[i]
        elif token in {"--branch", "-b"}:
            i += 1
            if i >= len(rest):
                fail(f"Missing value for {token}")
            options["branch"] = rest[i]
        elif token == "--force":
            options["force"] = True
        elif token.startswith("-"):
            fail(f"Unknown flag: {token}")
        else:
            positional.append(token)
        i += 1

    if positional:
        options["path"] = positional[0] if options["path"] is None else options["path"]
        if len(positional) > 1 and options["branch"] is None:
            options["branch"] = positional[1]
        if len(positional) > 2:
            fail(f"Too many positional args: {' '.join(positional)}")
    return command, positional, options


def list_worktrees(root):
    result = run(["git", "worktree", "list", "--porcelain"], root, capture=True)
    entries = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                entries.append(current)
                current = {}
            current["path"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "", 1)
    if current:
        entries.append(current)

    if not entries:
        print("No worktrees found.")
        return

    print("Path\tBranch")
    print("----\t------")
    for entry in entries:
        branch = entry.get("branch", "(detached)")
        print(f"{entry['path']}\t{branch}")


def find_worktree_by_identifier(root, identifier):
    result = run(["git", "worktree", "list", "--porcelain"], root, capture=True)
    entries = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                entries.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "", 1)
    if current:
        entries.append(current)

    requested = Path(identifier)
    requested_path = requested if requested.is_absolute() else root.joinpath(requested).resolve()

    for entry in entries:
        entry_path = Path(entry["path"])
        if entry_path == requested_path:
            return Path(entry["path"])
        if entry.get("branch") == identifier:
            return Path(entry["path"])
        if Path(entry["path"]).name == identifier:
            return Path(entry["path"])
    return None


def is_dirty_worktree(root, path):
    check = run(["git", "status", "--short"], path, capture=True, check=False)
    return check.returncode == 0 and check.stdout.strip()


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


def cmd_add(root, options):
    branch = options["branch"] or choose_branch(root)
    path = options["path"] or f".specbook/worktrees/{branch}"
    absolute = root / path if not Path(path).is_absolute() else Path(path)
    absolute.parent.mkdir(parents=True, exist_ok=True)

    state = WorktreeState()
    try:
        add_worktree(root, absolute, branch, False, state)
        print(f"Created worktree: {absolute}")
        print(f"Branch: {branch}")
    except Exception:
        rollback(root, state)
        raise


def cmd_setup(root, options):
    branch = options["branch"] or choose_branch(root)
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


def cmd_remove(root, options):
    if options["path"] is None:
        fail("remove requires <path-or-branch>.")

    target = find_worktree_by_identifier(root, options["path"])
    if target is None:
        fail(f"Unable to locate worktree '{options['path']}'.")

    if is_dirty_worktree(root, target) and not options["force"]:
        fail(f"Worktree {target} has uncommitted changes. Use --force to remove anyway.")

    run(["git", "worktree", "remove"] + (["--force"] if options["force"] else []) + [str(target)], root)
    print(f"Removed worktree: {target}")

def print_help():
    print("Usage: /worktree <command> [options]")
    print("  add [path] [branch]       Create and register worktree")
    print("  setup [path] [branch]     Create worktree and run setup automation")
    print("  list                      List all registered worktrees")
    print("  remove <path-or-branch>   Remove worktree (use --force if dirty)")
    print("Flags: --path, --branch, --force")


def main():
    root = require_git_repo()
    command, _, options = parse_args(os.environ.get("WORKTREE_ARGS", ""))

    if command == "help":
        print_help()
        return

    if command == "list":
        list_worktrees(root)
    elif command == "add":
        cmd_add(root, options)
    elif command == "setup":
        cmd_setup(root, options)
    elif command == "remove":
        cmd_remove(root, options)
    else:
        fail(f"Unknown command '{command}'.")


if __name__ == "__main__":
    main()
PY
