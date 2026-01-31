<p align="center">
  <img src="../../assets/review.png" alt="Review" width="120">
</p>

# /review

Perform a CodeRabbit review, coordinate parallel agent fixes, and verify completion. This command orchestrates a complete AI-powered code review and fix workflow.

## Usage

```bash
/review [--base <branch>] [--type <all|committed|uncommitted>] [--verify-only]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--base` | No | main | Branch to compare against |
| `--type` | No | all | What to review: `all`, `committed`, or `uncommitted` |
| `--verify-only` | No | false | Only verify, don't fix issues |

## How It Works

1. **Initial Review** - Run CodeRabbit with `--plain` mode for detailed feedback
2. **Parallel Assignment** - Parse review comments and create tasks for multiple agents
3. **Concurrent Fixes** - Multiple agents work simultaneously on different issues
4. **Verification** - Run CodeRabbit again to confirm all issues are resolved
5. **Final Save** - Use `/save` command to persist verified changes

## Examples

```bash
# Review all changes against main
/review

# Review only committed changes
/review --type committed

# Review against a feature branch
/review --base feature/auth

# Just verify without fixing
/review --verify-only
```

## Review Types

| Type | Description |
|------|-------------|
| `all` | Review both staged and unstaged changes |
| `committed` | Review only committed changes |
| `uncommitted` | Review only uncommitted changes |

## Workflow Diagram

```
┌─────────────────┐
│ CodeRabbit      │
│ Initial Review  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse Comments  │
│ Create Tasks    │
└────────┬────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐┌──────┐┌──────┐
│Agent1││Agent2││Agent3│  ← Parallel Fixes
└──┬───┘└──┬───┘└──┬───┘
   └───────┼───────┘
           ▼
┌─────────────────┐
│ CodeRabbit      │
│ Verification    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ /save           │
│ Commit Changes  │
└─────────────────┘
```

## Setup Required

This command requires the CodeRabbit workflow script:

```bash
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/coderabbit_workflow.py ~/.claude/slash_commands/
```

## Requirements

- **CodeRabbit CLI** - Must be installed and configured
- **Python 3.8+** - For the workflow script
- **Git** - For diff operations

## When to Use

- After completing a feature, before merging
- For comprehensive code review with automatic fixes
- When you want parallel issue resolution
- To ensure code quality before commit

## See Also

- [/save](save.md) - Commit and merge changes
- [/stable](stable.md) - Create stable checkpoint
