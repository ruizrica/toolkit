---
description: Generate comprehensive project handbook
argument-hint: [--path PROJECT_PATH] [--output FILENAME] [--verbose]
allowed-tools: Bash(python3:*)
context: fork
agent: general-purpose
---

I'll generate a comprehensive project handbook using the handbook generator.

Let me analyze your project and create an AI-optimized handbook with the following structure:
- **Layer 1**: System Overview (Purpose, Tech Stack, Architecture)
- **Layer 2**: Module Map (Core Modules, Data Layer, Utilities)
- **Layer 3**: Integration Guide (APIs, Interfaces, Configuration)
- **Layer 4**: Extension Points (Design Patterns, Customization Areas)

Running handbook generation with arguments: $ARGUMENTS

```bash
python3 ~/.claude/slash_commands/handbook.py $ARGUMENTS
```
