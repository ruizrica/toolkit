<p align="center">
  <img src="../../assets/stable.png" alt="Stable" width="120">
</p>

# /stable

Create a stable checkpoint with tags and comprehensive documentation. This command first runs `/save` to commit current changes, then creates a timestamped tag and checkpoint branch.

## Usage

```bash
/stable [description]
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| description | No | Optional description for the checkpoint |

## How It Works

1. **Save** - Run `/save` to commit all current changes
2. **Create Tag** - Create annotated tag: `stable-YYYYMMDD-HHMMSS`
3. **Create Branch** - Create checkpoint branch from the tag
4. **Generate Docs** - Create comprehensive `stable-readme.md`
5. **Commit Docs** - Add the documentation to the repository

## What Gets Created

| Item | Example | Description |
|------|---------|-------------|
| Tag | `stable-20260130-103000` | Annotated git tag |
| Branch | `checkpoint/stable-20260130-103000` | Checkpoint branch |
| Documentation | `stable-readme.md` | Checkpoint documentation |

## Documentation Contents

The generated `stable-readme.md` includes:

### Checkpoint Information
- Tag name and commit hash
- Timestamp and source branch
- Total file count

### Restore Instructions
- How to view the checkpoint
- How to create a new branch from it
- How to continue development

### Project State
- Recent commit history
- File structure listing
- Environment variables (sanitized)
- Dependencies (npm/pip)
- Changes since last stable checkpoint
- Remote repository information

### Usage Examples
- Compare with current state
- Merge into another branch
- Push to remote

## Example

```bash
/stable v1.0-auth-complete
```

**Output:**
```
✅ Created stable checkpoint:
  📌 Tag: stable-20260130-103000
  🌿 Branch: checkpoint/stable-20260130-103000
  🔢 Commit: a1b2c3d
```

## Documentation Example

```markdown
# Stable Checkpoint Documentation

## Checkpoint Information
- **Tag:** `stable-20260130-103000`
- **Branch:** `checkpoint/stable-20260130-103000`
- **Commit:** `a1b2c3d4e5f6...`
- **Timestamp:** 20260130-103000
- **Created from branch:** main
- **Total files:** 47

## How to Restore This Checkpoint

### To view this checkpoint:
git checkout stable-20260130-103000

### To create a new branch from this checkpoint:
git checkout -b feature/new-branch stable-20260130-103000

### To restore and continue development:
git checkout checkpoint/stable-20260130-103000

## Recent Commits
- a1b2c3d Add user authentication
- b2c3d4e Implement OAuth flow
- c3d4e5f Add login page

## Dependencies
{
  "express": "^4.18.0",
  "passport": "^0.6.0"
}

## Changes Since Last Checkpoint
15 files changed, 847 insertions(+), 123 deletions(-)
```

## Pushing to Remote

After creating a checkpoint:

```bash
# Push the tag
git push origin stable-20260130-103000

# Push the checkpoint branch
git push origin checkpoint/stable-20260130-103000
```

## When to Use

- After completing a major feature
- Before starting risky changes
- At release milestones
- Creating rollback points
- Documenting project state

## Benefits

- **Rollback Point** - Easy to restore if needed
- **Documentation** - Comprehensive project state capture
- **Traceability** - Tagged commits with clear history
- **Backup** - Can be pushed to remote for safety

## See Also

- [/save](save.md) - Commit and merge (used internally)
- [/setup](setup.md) - Create WIP worktree
