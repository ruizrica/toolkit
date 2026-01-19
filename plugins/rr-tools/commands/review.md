---
description: "Perform CodeRabbit review, coordinate parallel agent fixes, and verify completion"
argument-hint: "[--base <branch>] [--type <all|committed|uncommitted>] [--verify-only]"
allowed-tools: ["python", "terminal", "file-system", "claude-code-sdk"]
context: fork
agent: general-purpose
---

# CodeRabbit Review & Fix Workflow

This command orchestrates a complete AI-powered code review and fix workflow:

1. **Initial Review**: Run CodeRabbit with `--plain` mode to get detailed feedback
2. **Parallel Assignment**: Parse review comments and create tasks for multiple agents
3. **Concurrent Fixes**: Multiple agents work simultaneously on different issues
4. **Verification**: Run CodeRabbit again to confirm all issues are resolved
5. **Final Save**: Use `/save` command to persist verified changes

## Usage

```bash
python3 ~/.claude/slash_commands/coderabbit_workflow.py $ARGUMENTS
