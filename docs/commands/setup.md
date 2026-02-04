<p align="center">
  <img src="../../assets/toolkit.png" alt="Setup" width="120">
</p>

# /setup

Create a WIP branch and worktree for isolated development. This command sets up a separate working directory within `.specbook/worktrees/` where you can make changes without affecting the main branch.

## Usage

```bash
/setup
```

## Arguments

This command takes no arguments. It automatically generates names based on the current timestamp.

## How It Works

1. **Verify** - Confirm we're in a git repository
2. **Generate Names** - Create timestamp-based branch name: `wip-YYYYMMDD-HHMMSS`
3. **Create Branch** - Create the WIP branch from current HEAD
4. **Create Worktree** - Set up directory in `.specbook/worktrees/wip-YYYYMMDD-HHMMSS`
5. **Report** - Display the worktree path and instructions

## What Gets Created

| Item | Example | Description |
|------|---------|-------------|
| Branch | `wip-20260130-103000` | New branch for development |
| Worktree | `.specbook/worktrees/wip-20260130-103000/` | Separate working directory |

## Directory Structure

Before:
```
myproject/             ← You are here
├── src/
├── .specbook/
└── ...
```

After:
```
myproject/             ← Main worktree (unchanged)
├── src/
├── .specbook/
│   └── worktrees/     ← New worktrees directory
│       └── wip-20260130-103000/   ← New WIP worktree
│           ├── src/
│           └── ...
└── ...
```

## Output Example

```
Created WIP worktree:

📁 Worktree: .specbook/worktrees/wip-20260130-103000
🌿 Branch: wip-20260130-103000

You can work in the worktree without changing directories.
The agent will handle operations in the worktree context.

When done, run /save to merge back to main
```

## Benefits

- **Isolation** - Keep main branch clean during development
- **Parallel Work** - Multiple worktrees can exist simultaneously
- **Clean Rollback** - Easy to abandon changes by deleting worktree
- **Safe Experimentation** - Main branch remains untouched

## Git Commands Executed

```bash
git rev-parse --git-dir           # Verify git repo
git checkout main                 # Switch to main
git branch wip-YYYYMMDD-HHMMSS    # Create WIP branch
mkdir -p .specbook/worktrees      # Create worktrees directory
git worktree add .specbook/worktrees/wip-YYYYMMDD-HHMMSS wip-YYYYMMDD-HHMMSS  # Create worktree
```

## Requirements

- **Git** - Must be in a git repository
- **Main/Master branch** - The base branch must exist
- **Write access** - To parent directory for worktree creation

## When to Use

- Starting a new feature or experiment
- Making changes you might want to abandon
- Working on multiple features simultaneously
- Keeping main branch pristine during development

## Workflow

```bash
# Create isolated workspace
/setup

# The agent will now work in .specbook/worktrees/wip-YYYYMMDD-HHMMSS
# No need to change directories - you stay in your project root

# ... agent does development work in the worktree ...

# Merge back to main when ready
/save
```

## See Also

- [/save](save.md) - Commit, merge, and cleanup
- [/stable](stable.md) - Create stable checkpoint
