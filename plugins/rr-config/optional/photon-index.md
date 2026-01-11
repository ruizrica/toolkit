---
description: "Index codebase for semantic search (runs in background)"
argument-hint: "[project-path]"
allowed-tools: ["Bash(nohup:*)", "Bash(python3:*)", "Bash(tail:*)", "Bash(echo:*)"]
context: fork
agent: general-purpose
---

# Photon Index

Trigger codebase indexing for Photon's semantic search (`analyze:*` operations).

## Usage

Parse the user's request:
- `$ARGUMENTS` may contain a project path (defaults to current working directory)
- Project ID defaults to the directory basename

## Execution

Run the standalone Python indexer in the background:

```bash
PROJECT_PATH="${1:-.}"
PROJECT_ID="$(basename "$(cd "$PROJECT_PATH" && pwd)")"

nohup python3 /Users/ricardo/Workshop/Github-Work/photon/bin/photon-index.py \
  --project "$PROJECT_ID" \
  --path "$PROJECT_PATH" \
  > /tmp/photon-index.log 2>&1 &

echo "[photon-index] Started in background (PID: $!)"
echo "[photon-index] Project: $PROJECT_ID"
echo "[photon-index] Path: $PROJECT_PATH"
echo "[photon-index] Log: /tmp/photon-index.log"
echo "[photon-index] Check progress: tail -f /tmp/photon-index.log"
```

## When to Run Proactively

Run this command after major code changes to keep the semantic index fresh:
- After implementing new features (new files created)
- After major refactoring (file structure changes)
- After deleting or moving multiple files
- Before starting deep codebase analysis

The command runs in background - you can continue working while it indexes.

## Check Progress

Monitor indexing progress:
```bash
tail -20 /tmp/photon-index.log
```

## Prerequisites

One of:
- `PHOTON_TOKEN` environment variable
- Token in `~/.photon/credentials` file

## Examples

User: "index this project"
→ Index current working directory

User: "index /path/to/my-app"
→ Index specified path

User: "run indexing after this refactor"
→ Run indexer in background after completing changes
