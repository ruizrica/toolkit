# /worktree

Git worktree manager for isolated agent workflows.

## Usage

```bash
/worktree [path] [branch]
```

## Commands

- `/worktree [path] [branch]` - create a worktree
  - Installs dependencies, copies `.env.example` to `.env` (if present), and opens the editor when possible.

## Why this command exists

The previous `/setup` worktree flow has moved here to keep bootstrap and worktree management separate.

## Behavior

- `/worktree [path] [branch]` (default behavior):
  - Creates `.specbook/worktrees/<branch-or-timestamp>` by default when path is omitted.
  - Uses `git worktree add <path> -b <branch>` when the branch does not exist.
  - Accepts fuzzy/TUI branch selection when `branch` is omitted (uses `fzf` when available).
  - Rolls back created worktree/branch if setup fails.
  - Dependency install (`npm`, `pnpm`, `yarn`, or `python3 -m pip -r requirements.txt`) when lockfiles are found.
  - Copies `.env.example` to `.env` in the new worktree when missing.
  - Opens `$EDITOR`/`$VISUAL` pointing to the new worktree path if available.

## Error handling

- Not in a git repository: command fails early.
- Bad args: usage is displayed.
- Missing branch for default operations: falls back to fuzzy/interactive selection.

## Setup automation summary format

```text
Creating worktree: <path> (<branch>)
Environment: .env prepared (if .env.example exists)
Editor launch: attempted (if editor variables are set)
```

## See Also

- `/setup` - repository initialization + memory indexing
- `/save` - merge and clean up worktree workflows
