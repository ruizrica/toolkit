---
description: "Save work: commit changes, merge WIP to main, cleanup worktree and branch"
argument-hint: "[commit message]"
allowed-tools: ["Bash", "AskUserQuestion"]
---

# Save and Merge Work

Commits all changes and merges back to main. Handles both:
- **WIP worktree workflow**: merge to main, remove worktree, delete branch
- **Regular branch workflow**: merge to main, delete branch

**Never pushes to remote** - local only.

## Detection Logic

Detect if currently in a linked worktree (not the main worktree):
- Check `git rev-parse --git-common-dir`
- If it contains `/worktrees/`, we're in a linked worktree

## Workflow

### Step 1: Commit Current Changes
```bash
git add .
git diff --cached --quiet || git commit -m "$ARGUMENTS"  # Only commit if changes exist
```
Use provided message or default to "WIP save".

### Step 2: Detect Environment
```bash
CURRENT_BRANCH=$(git branch --show-current)
GIT_COMMON_DIR=$(git rev-parse --git-common-dir)

# Check if linked worktree
if [[ "$GIT_COMMON_DIR" == *"/worktrees/"* ]]; then
    IS_WORKTREE=true
    MAIN_WORKTREE=$(git worktree list | grep -E '\[(main|master)\]' | awk '{print $1}')
    WIP_WORKTREE=$(git rev-parse --show-toplevel)
else
    IS_WORKTREE=false
fi
```

### Step 3: Merge (with conflict handling)

**If in worktree:**
```bash
cd "$MAIN_WORKTREE"
git merge "$CURRENT_BRANCH" --no-edit
```

**If merge fails (exit code != 0):**
1. Get conflicting files:
   ```bash
   CONFLICTS=$(git diff --name-only --diff-filter=U)
   ```

2. Use AskUserQuestion with options:
   - **"Keep WIP changes (Recommended)"** - Your new work overwrites main
   - **"Keep main changes"** - Discard your WIP, keep what's in main
   - **"Resolve manually"** - Leave conflicts, show instructions
   - **"Abort merge"** - Cancel merge, keep worktree for later

3. Based on choice:
   - **Keep WIP**:
     ```bash
     git checkout --ours $CONFLICTS
     git add $CONFLICTS
     git commit -m "Merge $CURRENT_BRANCH (kept WIP changes)"
     ```
   - **Keep main**:
     ```bash
     git checkout --theirs $CONFLICTS
     git add $CONFLICTS
     git commit -m "Merge $CURRENT_BRANCH (kept main changes)"
     ```
   - **Manual**: Output file list and instructions, exit without cleanup
   - **Abort**:
     ```bash
     git merge --abort
     ```
     Exit without cleanup, inform user worktree still exists

### Step 4: Cleanup (only if merge successful)
```bash
git worktree remove "$WIP_WORKTREE" --force
git branch -d "$CURRENT_BRANCH"
```

### Step 5: Report
- Show final git status
- Confirm on main with merged changes
- List what was cleaned up

## Important

- Never push to remote (no git push)
- Always end up on main branch in main worktree (unless aborted)
- Clean up all WIP artifacts (worktree directory, branch)
- Handle edge cases gracefully (no changes, already on main)
- Use AskUserQuestion for conflict resolution decisions
