---
description: "Compact session state to Photon for context limit management"
argument-hint: "[resume hint describing current work]"
allowed-tools: ["mcp__photon__photon_memory"]
context: fork
agent: general-purpose
---

# Photon Compact

Save your current session state to Photon before hitting context limits.

## Usage

The resume hint should describe what you're working on so the restore can continue seamlessly.

## Process

1. Derive the project name from the current working directory (use `basename` of the directory)
2. Call `photon_memory` with:
   - `operation`: "compact"
   - `project`: derived project name
   - `resumeHint`: "$ARGUMENTS" (the user's description of current work)

3. Display the snapshot ID and the restore command to use after `/clear`

## Example Output

After compacting, show:
```
Session compacted to Photon.
Snapshot ID: snap_xyz123
Project: my-project

After running /clear, restore with:
  /photon-restore snap_xyz123
```

## Important

After compact, work is blocked. The user must run `/clear` and then `/photon-restore` to continue.
