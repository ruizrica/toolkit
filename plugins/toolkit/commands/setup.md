---
description: "Create WIP branch and worktree for isolated development"
---

# Setup WIP Worktree

Create an isolated development environment using git worktrees.

## Workflow

1. Verify we're in a git repository
2. Generate timestamp-based branch name: `wip-YYYYMMDD-HHMMSS`
3. Create the WIP branch from current HEAD (usually main)
4. Create worktree in .specbook/worktrees directory: `.specbook/worktrees/wip-${TIMESTAMP}`
5. Report the worktree path for the agent to work in

## Git Commands

!git rev-parse --git-dir || echo "ERROR: Not a git repository"

Get project info and create names:
- TIMESTAMP = current date/time
- BRANCH_NAME = wip-${TIMESTAMP}
- WORKTREE_PATH = .specbook/worktrees/wip-${TIMESTAMP}

!git checkout main 2>/dev/null || git checkout master
!git branch "${BRANCH_NAME}"
!mkdir -p .specbook/worktrees
!rm -rf "${WORKTREE_PATH}" 2>/dev/null
!git worktree add "${WORKTREE_PATH}" "${BRANCH_NAME}"

After setup, tell the user:
- The worktree path where work is isolated
- The branch name created
- When done, run /save to merge back to main
