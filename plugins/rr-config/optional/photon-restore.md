---
description: "Restore session from Photon snapshot"
argument-hint: "[snapshot_id] or blank for latest"
allowed-tools: ["mcp__photon__photon_memory"]
context: fork
agent: general-purpose
---

# Photon Restore

Restore your session state from a Photon snapshot after clearing context.

## Usage

- `/photon-restore` - Restore from the latest snapshot
- `/photon-restore snap_xyz123` - Restore from a specific snapshot ID

## Process

1. Derive the project name from the current working directory
2. Call `photon_memory` with:
   - `operation`: "restore"
   - `snapshotId`: "$ARGUMENTS" if provided, otherwise omit for latest

   For expanded context (if requested):
   - `detailLevel`: 5-100 in 5% increments
   - `expandQuery`: semantic search query

3. The restore will return context about what you were working on

## Seamless Continuation

After restore, immediately continue the work that was in progress. Do not ask the user what to do - the restore contains the context needed to continue seamlessly.

The resumeHint from the compact operation tells you exactly what was being worked on. Pick up where you left off.
