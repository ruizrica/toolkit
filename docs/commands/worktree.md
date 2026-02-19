# /worktree

Create an isolated development worktree with automatic branch and path generation.

## Usage

```bash
/worktree              # Auto-create with timestamp-based branch (wip-YYYYMMDD-HHMMSS)
/worktree [path]       # Custom path, auto-generated branch
/worktree [path] [branch]  # Custom path and branch
```

## Commands

- `/worktree` - Quick start: creates worktree with auto-generated wip-YYYYMMDD-HHMMSS branch
- `/worktree [path] [branch]` - Advanced: specify custom path and branch

Both versions run setup automation:
- Installs dependencies (npm, pnpm, yarn, or pip)
- Copies `.env.example` to `.env` (if present)
- Opens `$EDITOR`/`$VISUAL` when available

## Why this command exists

Provides isolated development environments using git worktrees. The simple form (no args) auto-generates a timestamp-based wip branch for quick starts, while the full form allows custom naming.

## Behavior

- `/worktree` (no arguments):
  - Generates branch name: `wip-YYYYMMDD-HHMMSS`
  - Creates worktree at: `.specbook/worktrees/wip-YYYYMMDD-HHMMSS`
  - No interactive prompts - fully automatic

- `/worktree [path] [branch]` (with arguments):
  - Uses specified path and/or branch
  - When only path provided, auto-generates branch name
  - When branch doesn't exist, creates it with `git worktree add -b`
  - Rolls back created worktree/branch if setup fails

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
