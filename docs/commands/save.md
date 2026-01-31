<p align="center">
  <img src="../../assets/save.png" alt="Save" width="120">
</p>

# /save

Save work by committing changes, merging WIP to main, and cleaning up the worktree and branch. This command handles both WIP worktree workflows and regular branch workflows.

## Usage

```bash
/save [commit message]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| commit message | No | "WIP save" | Message for the commit |

## How It Works

### Step 1: Commit Current Changes

```bash
git add .
git diff --cached --quiet || git commit -m "[message]"
```

Only commits if there are staged changes.

### Step 2: Detect Environment

Determines if currently in a linked worktree or regular branch:
- Linked worktree: Has worktree-specific git directory
- Regular branch: Standard git checkout

### Step 3: Merge to Main

Merges the current branch into main with conflict handling.

### Step 4: Cleanup

For worktree workflow:
- Removes the worktree directory
- Deletes the WIP branch

For regular branch:
- Deletes the feature branch

## Conflict Handling

If merge conflicts occur, you're prompted to choose:

| Option | Description |
|--------|-------------|
| **Keep WIP changes** | Your new work overwrites main (recommended) |
| **Keep main changes** | Discard your WIP, keep what's in main |
| **Resolve manually** | Leave conflicts, show instructions |
| **Abort merge** | Cancel merge, keep worktree for later |

## Examples

```bash
# Save with default message
/save

# Save with custom message
/save "Add user authentication feature"

# Save after completing a feature
/save "Implement OAuth login with Google provider"
```

## Workflow Diagram

```
┌─────────────────────────────────┐
│ Commit Current Changes          │
│ git add . && git commit -m "..."│
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│ Detect Environment              │
│ Worktree or Regular Branch?     │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│ Switch to Main Worktree         │
│ (if in linked worktree)         │
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│ Merge WIP Branch                │
│ git merge wip-branch --no-edit  │
└────────────────┬────────────────┘
                 │
          ┌──────┴──────┐
          │   Success?  │
          └──────┬──────┘
           ▼           ▼
      ┌────────┐  ┌────────────┐
      │ Yes    │  │ No         │
      └───┬────┘  │ Handle     │
          │       │ Conflicts  │
          │       └─────┬──────┘
          │             │
          └──────┬──────┘
                 ▼
┌────────────────────────────────┐
│ Cleanup                        │
│ Remove worktree, delete branch │
└────────────────────────────────┘
```

## Important Notes

- **Never pushes to remote** - Local operations only
- **Ends on main branch** - Unless merge is aborted
- **Cleans up artifacts** - Worktree directory and branch removed
- **Handles edge cases** - No changes, already on main, etc.

## Requirements

- **Git** - Must be in a git repository
- **Clean working tree** - Or changes will be committed first

## When to Use

- After completing work in a WIP worktree
- When ready to merge a feature branch
- To clean up development artifacts
- Before starting a new feature

## See Also

- [/setup](setup.md) - Create WIP worktree
- [/stable](stable.md) - Create stable checkpoint
