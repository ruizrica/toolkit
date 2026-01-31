<p align="center">
  <img src="../../assets/handbook.png" alt="Handbook" width="120">
</p>

# /handbook

Generate a comprehensive, AI-optimized project handbook. This command analyzes your codebase and creates structured documentation designed to help AI assistants understand and work with your project.

## Usage

```bash
/handbook [--path PROJECT_PATH] [--output FILENAME] [--verbose]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--path` | No | `.` | Path to the project to analyze |
| `--output` | No | `HANDBOOK.md` | Output filename |
| `--verbose` | No | false | Show detailed analysis progress |

## Output Structure

The handbook is organized into four layers:

### Layer 1: System Overview
- **Purpose** - What the project does and why it exists
- **Tech Stack** - Languages, frameworks, and tools used
- **Architecture** - High-level system design

### Layer 2: Module Map
- **Core Modules** - Primary functionality areas
- **Data Layer** - Database, storage, and data flow
- **Utilities** - Helper functions and shared code

### Layer 3: Integration Guide
- **APIs** - External and internal API documentation
- **Interfaces** - How components communicate
- **Configuration** - Settings and environment variables

### Layer 4: Extension Points
- **Design Patterns** - Patterns used throughout the codebase
- **Customization Areas** - Where and how to extend functionality

## Examples

```bash
# Generate handbook for current project
/handbook

# Analyze a specific project
/handbook --path ./my-project

# Custom output file
/handbook --output PROJECT_DOCS.md

# Full options
/handbook --path ./api --output API_HANDBOOK.md --verbose
```

## Sample Output

```markdown
# Project Handbook: MyApp

## Layer 1: System Overview

### Purpose
MyApp is a task management application that enables teams to...

### Tech Stack
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **Backend**: Node.js, Express, PostgreSQL
- **Infrastructure**: Docker, AWS Lambda

### Architecture
The application follows a microservices architecture with...

## Layer 2: Module Map

### Core Modules
- `src/auth/` - Authentication and authorization
- `src/tasks/` - Task CRUD operations
- `src/teams/` - Team management

...
```

## Setup Required

This command requires the handbook script:

```bash
mkdir -p ~/.claude/slash_commands
cp plugins/toolkit/scripts/handbook.py ~/.claude/slash_commands/
```

## Requirements

- **Python 3.8+** - For the handbook generator script
- **Read access** - To the project directory

## When to Use

- When onboarding to a new codebase
- To create documentation for AI assistants
- Before starting major refactoring
- To understand unfamiliar project structure

## See Also

- [/gherkin](gherkin.md) - Extract business rules
- [gemini-agent](../agents/gemini.md) - Large codebase analysis
