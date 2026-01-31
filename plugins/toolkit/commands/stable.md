---
tags: [git, checkpoint, stable]
---

# Create Stable Checkpoint

First, run the /save command to commit all current changes.

Then create a stable checkpoint by:

1. Creating a timestamped tag in format `stable-YYYYMMDD-HHMMSS`
2. Creating a checkpoint branch from that tag
3. Generating comprehensive documentation

## Git Operations

```bash
# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
TAG_NAME="stable-${TIMESTAMP}"
BRANCH_NAME="checkpoint/${TAG_NAME}"

# Get current commit hash
COMMIT_HASH=$(git rev-parse HEAD)

# Create annotated tag
git tag -a "${TAG_NAME}" -m "Stable checkpoint created on ${TIMESTAMP}

This tag marks a stable state of the project.
Commit: ${COMMIT_HASH}"

# Create checkpoint branch
git branch "${BRANCH_NAME}" "${TAG_NAME}"

echo "✅ Created stable checkpoint:"
echo "  📌 Tag: ${TAG_NAME}"
echo "  🌿 Branch: ${BRANCH_NAME}"
echo "  🔢 Commit: ${COMMIT_HASH:0:7}"
```

## Generate Documentation

Now create a comprehensive `stable-readme.md` file with:

```bash
# Get project information
FILE_COUNT=$(git ls-files | wc -l | tr -d ' ')
CURRENT_BRANCH=$(git branch --show-current)
RECENT_COMMITS=$(git log --oneline -10)

# Check for environment variables
if [[ -f .env ]]; then
    ENV_VARS=$(grep -v '^#' .env | grep -v '^$' | sed 's/=.*/=<VALUE>/')
elif [[ -f .env.example ]]; then
    ENV_VARS=$(grep -v '^#' .env.example | grep -v '^$')
else
    ENV_VARS=""
fi

# Check for package.json dependencies
if [[ -f package.json ]]; then
    DEPENDENCIES=$(jq '.dependencies' package.json 2>/dev/null || echo "{}")
else
    DEPENDENCIES=""
fi

# Check for requirements.txt
if [[ -f requirements.txt ]]; then
    PY_REQUIREMENTS=$(cat requirements.txt)
else
    PY_REQUIREMENTS=""
fi

# Get last stable tag for comparison
LAST_STABLE=$(git tag -l "stable-*" | sort -V | tail -2 | head -1 || echo "")
if [[ -n "$LAST_STABLE" && "$LAST_STABLE" != "$TAG_NAME" ]]; then
    CHANGES_SINCE=$(git diff --stat "${LAST_STABLE}..HEAD")
else
    CHANGES_SINCE=""
fi
```

Create the documentation file `stable-readme.md` with:

# Stable Checkpoint Documentation

## Checkpoint Information
- **Tag:** `${TAG_NAME}`
- **Branch:** `${BRANCH_NAME}`
- **Commit:** `${COMMIT_HASH}`
- **Timestamp:** ${TIMESTAMP}
- **Created from branch:** ${CURRENT_BRANCH}
- **Total files:** ${FILE_COUNT}

## How to Restore This Checkpoint

### To view this checkpoint:
```bash
git checkout ${TAG_NAME}
```

### To create a new branch from this checkpoint:
```bash
git checkout -b feature/new-branch ${TAG_NAME}
```

### To restore and continue development:
```bash
git checkout ${BRANCH_NAME}
```

## Project State at Checkpoint

Include:
- Recent commit history
- File structure listing
- Environment variables (sanitized)
- NPM dependencies (if package.json exists)
- Python requirements (if requirements.txt exists)
- Changes since last stable checkpoint
- Remote repository information

## Working with This Checkpoint

### To compare with current state:
```bash
git diff ${TAG_NAME}..HEAD
```

### To see what changed in this checkpoint:
```bash
git show ${TAG_NAME}
```

### To merge this checkpoint into another branch:
```bash
git checkout target-branch
git merge ${TAG_NAME}
```

## Push to Remote

If you have a remote repository configured:

```bash
# Push the tag
git push origin ${TAG_NAME}

# Push the checkpoint branch
git push origin ${BRANCH_NAME}
```

## Summary

The stable checkpoint has been created successfully. This checkpoint represents a tested, stable state of the project that can be used as a rollback point or reference for future development.

Finally, commit the documentation:

```bash
git add stable-readme.md
git commit -m "Add stable checkpoint documentation for ${TAG_NAME}"
```

---
*This command creates a comprehensive stable checkpoint with full documentation and recovery options.*