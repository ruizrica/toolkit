<p align="center">
  <img src="../../assets/toolkit.png" alt="Setup" width="120">
</p>

# /setup

Create a WIP branch and worktree for isolated development. This command sets up a separate working directory where you can make changes without affecting the main branch.

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
4. **Create Worktree** - Set up sibling directory: `../<project>-wip`
5. **Report** - Display the worktree path and instructions

## What Gets Created

| Item | Example | Description |
|------|---------|-------------|
| Branch | `wip-20260130-103000` | New branch for development |
| Worktree | `../myproject-wip/` | Separate working directory |

## Directory Structure

Before:
```
projects/
└── myproject/          ← You are here
    ├── src/
    └── ...
```

After:
```
projects/
├── myproject/          ← Main worktree (unchanged)
│   ├── src/
│   └── ...
└── myproject-wip/      ← New WIP worktree
    ├── src/
    └── ...
```

## Output Example

```
Created WIP worktree:

📁 Worktree: ../myproject-wip
🌿 Branch: wip-20260130-103000

To work in the worktree:
  cd ../myproject-wip

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
git worktree add ../project-wip wip-YYYYMMDD-HHMMSS  # Create worktree
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

# Change to worktree
cd ../myproject-wip

# ... do your development work ...

# Merge back to main
/save
```

## See Also

- [/save](save.md) - Commit, merge, and cleanup
- [/stable](stable.md) - Create stable checkpoint
