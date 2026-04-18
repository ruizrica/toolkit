---
description: "Turn any codebase into a beautiful, interactive single-page HTML course that teaches how the code works — with animated visualizations, embedded quizzes, and code-with-plain-English translations"
argument-hint: "[path, GitHub URL, or 'this' for current project]"
allowed-tools: ["Task", "Read", "Write", "Edit", "Bash", "Glob", "Grep", "Skill"]
context: fork
agent: opus
---

# /code2course — Codebase to Interactive Course

Transform any codebase into a stunning, self-contained HTML course with scroll-based navigation, animated visualizations, embedded quizzes, and code-with-plain-English side-by-side translations.

## Target Codebase

Parse `$ARGUMENTS` to determine the target codebase:

- **GitHub URL** (e.g., `https://github.com/user/repo`) → Clone it to `/tmp/<repo-name>` first
- **Local path** (e.g., `./my-project` or `/path/to/project`) → Use directly
- **"this"** or empty → Use the current working directory

If no argument is provided, introduce yourself:

> **I can turn any codebase into an interactive course that teaches how it works — no coding knowledge required.**
>
> Just point me at a project:
> - **A local folder** — e.g., `/code2course ./my-project`
> - **A GitHub link** — e.g., `/code2course https://github.com/user/repo`
> - **The current project** — `/code2course this`

## Instructions

Invoke the bundled `codebase-to-course` skill and follow its 4-phase process.

The skill lives inside this plugin at:

```
plugins/toolkit/skills/codebase-to-course/SKILL.md
plugins/toolkit/skills/codebase-to-course/references/design-system.md
plugins/toolkit/skills/codebase-to-course/references/interactive-elements.md
```

Use the Skill tool (`Skill` name: `codebase-to-course`) so Claude Code's skill loader resolves it via the plugin's manifest. If the Skill tool is unavailable, fall back to reading the `SKILL.md` file directly from the plugin directory.

## Process Summary

1. **Codebase Analysis** — deeply understand the target codebase (read all key files, trace data flows, map components)
2. **Curriculum Design** — structure 5–8 modules (do NOT ask for approval — just build it)
3. **Build the Course** — generate a single self-contained HTML file, one module at a time
4. **Review and Open** — open the HTML in the browser for review

## Output

Save the generated course HTML file to the current working directory as `<project-name>-course.html`.
