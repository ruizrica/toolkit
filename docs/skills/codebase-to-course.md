# codebase-to-course

ABOUTME: Documentation for the codebase-to-course skill — generate interactive single-page HTML courses.
ABOUTME: Covers what the skill produces, who it's for, and how to trigger it.

## What is it?

A skill that transforms any codebase into a stunning, interactive single-page HTML course — scroll-based modules, animated visualizations, embedded quizzes, and plain-English translations of code.

Unlike the other toolkit skills, `codebase-to-course` is a **directory-style** skill: it ships with an `SKILL.md` file and two reference files (`references/design-system.md`, `references/interactive-elements.md`) containing CSS tokens, typography, and interactive element patterns.

## Trigger phrases

The skill activates on phrases like:

- "turn this codebase into a course"
- "make a tutorial from this project"
- "explain this code interactively"
- "/code2course" (the slash command delegates here)

## Who it's for

The target learner is a **vibe coder** — someone who builds software by instructing AI coding tools in natural language, without a traditional CS education. They want enough technical fluency to steer AI better, catch hallucinations, and debug when things break.

The course assumes zero technical background and answers "why should I care?" before "how does it work?" for every concept.

## Output

A single self-contained HTML file (no external dependencies beyond Google Fonts) with:

- 5–8 scroll-based modules
- Animated visualizations of data flow and architecture
- Code-with-plain-English side-by-side translations
- Embedded quizzes
- Plain-English definitions for every CS concept

The file is saved to the current working directory as `<project-name>-course.html`.

## How to use

```bash
/code2course ./my-project                            # Local folder
/code2course https://github.com/user/repo             # GitHub URL (cloned first)
/code2course this                                     # Current working directory
```

Or trigger via a natural phrase like "turn this codebase into an interactive course".

## Skill File Location

Bundled at `plugins/toolkit/skills/codebase-to-course/SKILL.md` (plus the `references/` directory). Installed automatically when the plugin is registered.

## See Also

- [/code2course command](../commands/README.md#education) — The slash command wrapper
- [agent-viewer](agent-viewer.md) — Round-trip review skill
