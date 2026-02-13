# /worktree

Git worktree manager for isolated agent workflows.

## Usage

```bash
/worktree <command> [path] [branch-or-name]
```

## Commands

- `/worktree add [path] [branch]` - create a worktree
- `/worktree setup [path] [branch]` - create worktree + install dependencies + copy `.env.example` + open editor
- `/worktree list` - list registered worktrees
- `/worktree remove <path-or-branch> [--force]` - remove a worktree

## Why this command exists

The previous `/setup` worktree flow has moved here to keep bootstrap and worktree management separate.

## Behavior

- `/worktree add`:
  - Creates `.specbook/worktrees/<branch-or-timestamp>` by default when path is omitted.
  - Uses `git worktree add <path> -b <branch>` when the branch does not exist.
  - Accepts fuzzy/TUI branch selection when `branch` is omitted (uses `fzf` when available).
  - Rolls back created worktree/branch if setup fails.

- `/worktree setup`:
  - Same as `add`, plus:
  - Dependency install (`npm`, `pnpm`, `yarn`, or `python3 -m pip -r requirements.txt`) when lockfiles are found.
  - Copies `.env.example` to `.env` in the new worktree when missing.
  - Opens `$EDITOR`/`$VISUAL` pointing to the new worktree path if available.

- `/worktree list`:
  - Shows all registered worktrees from `git worktree list`.

- `/worktree remove`:
  - Removes selected worktree.
  - Refuses to remove dirty worktree unless `--force` is provided.

## Error handling

- Not in a git repository: command fails early.
- Unknown command or bad args: usage is displayed.
- Dirty worktree on remove: requires `--force`.
- Missing branch for default operations: falls back to fuzzy/interactive selection then default head branch.

## Setup automation summary format

```text
Creating worktree: <path> (<branch>)
Environment: .env prepared (if .env.example exists)
Editor launch: attempted (if editor variables are set)
```

## See Also

- `/setup` - repository initialization + memory indexing
- `/save` - merge and clean up worktree workflows
