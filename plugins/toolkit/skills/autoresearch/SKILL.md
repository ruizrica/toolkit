ABOUTME: Autonomous Goal-directed Iteration skill. Apply Karpathy's autoresearch principles to ANY task.
ABOUTME: Loops autonomously — modify, verify, keep/discard, repeat — with git as memory and mechanical metrics as the decision function.

## Overview

Use this skill when the user wants to:
- Work autonomously on a measurable goal ("iterate until done", "keep improving", "run overnight")
- Improve a metric through repeated atomic experiments (test coverage, performance, bundle size, etc.)
- Refactor code while maintaining correctness, reducing complexity iteratively
- Optimize anything with a mechanical verification command

Inspired by [Karpathy's autoresearch](https://github.com/karpathy/autoresearch). The core idea: **Modify -> Verify -> Keep/Discard -> Repeat.**

**When to use autoresearch vs manual iteration:**
- **autoresearch**: Goal has a measurable metric, changes are atomic, verification is fast (<30s), you want hands-off autonomous improvement
- **Manual iteration**: Subjective quality, needs human judgment, exploratory design work, no clear metric

## Setup Phase (Do Once)

Before starting the loop, complete these steps:

1. **Read all in-scope files** for full context before any modification
2. **Define the goal** — What does "better" mean? Extract or ask for a mechanical metric:
   - Code: tests pass, build succeeds, coverage %, lint error count
   - Performance: benchmark time (ms), bundle size (KB), response time
   - Content: word count target, readability score, SEO score
   - If no metric exists, define one with the user, or use simplest proxy (e.g. "compiles without errors")
3. **Define scope constraints** — Which files can you modify? Which are read-only?
4. **Create a results log** — Create `autoresearch-results.tsv` in the working directory:
   ```
   # metric_direction: higher_is_better
   iteration	commit	metric	delta	status	description
   ```
5. **Establish baseline** — Run verification on current state. Record as iteration #0
6. **Confirm and go** — Show user the setup summary, get confirmation, then BEGIN THE LOOP

## The Autonomous Loop

```
LOOP (forever until interrupted, or N times if user specifies):
  1. REVIEW: Read current state of in-scope files
     - Read last 10-20 entries from results log
     - Read git log --oneline -20 to see recent changes
     - Identify: what worked, what failed, what's untried
  2. IDEATE: Pick next change. Priority order:
     a. Fix crashes/failures from previous iteration
     b. Exploit successes — variants of what worked
     c. Explore new approaches not yet attempted
     d. Combine near-misses — two discards might work together
     e. Simplify — remove code while maintaining metric
     f. Radical experiments when stuck (>5 consecutive discards)
  3. MODIFY: Make ONE focused, atomic change
     - The change should be explainable in one sentence
     - Write the description BEFORE making the change
  4. COMMIT: git add + git commit -m "experiment: <description>"
     - Commit BEFORE verification so rollback is clean
  5. VERIFY: Run the mechanical metric command
     - Capture output, extract metric value
     - Timeout: if >2x normal time, kill and treat as crash
  6. DECIDE (no ambiguity):
     - IMPROVED -> Keep commit, log "keep"
     - SAME/WORSE -> git reset --hard HEAD~1, log "discard"
     - CRASHED -> Try to fix (max 3 attempts), else revert, log "crash"
     - SIMPLICITY OVERRIDE: barely improved but much more complex = discard;
       unchanged but simpler = keep
  7. LOG: Append result to autoresearch-results.tsv
  8. REPEAT: Go to step 1
```

## Critical Rules

1. **Loop until done** — NEVER STOP. NEVER ASK "should I continue?" Loop until interrupted or iteration count reached
2. **Read before write** — Always re-read files. After rollbacks, state may differ from what you expect
3. **One change per iteration** — Atomic changes. If it breaks, you know exactly why
4. **Mechanical verification only** — No subjective "looks good". Use metrics with numbers
5. **Automatic rollback** — Failed changes revert instantly via git reset. No debates
6. **Simplicity wins** — Equal results + less code = KEEP. Tiny improvement + ugly complexity = DISCARD
7. **Git is memory** — Every kept change is committed. Read your own git history to learn patterns
8. **When stuck, think harder** — Re-read files, re-read goal, combine near-misses, try radical changes. Don't ask for help unless truly blocked by missing access/permissions

## Results Logging

Track every iteration in `autoresearch-results.tsv` (add to .gitignore):

```tsv
iteration	commit	metric	delta	status	description
0	a1b2c3d	85.2	0.0	baseline	initial state — test coverage 85.2%
1	b2c3d4e	87.1	+1.9	keep	add tests for auth middleware edge cases
2	-	86.5	-0.6	discard	refactor test helpers (broke 2 tests)
3	-	0.0	0.0	crash	add integration tests (DB connection failed)
4	c3d4e5f	88.3	+1.2	keep	add tests for error handling in API routes
```

Every 10 iterations, print a brief progress summary:
```
=== Autoresearch Progress (iteration 20) ===
Baseline: 85.2% -> Current best: 92.1% (+6.9%)
Keeps: 8 | Discards: 10 | Crashes: 2
Last 5: keep, discard, discard, keep, keep
```

## Communication Protocol

- DO NOT ask "should I keep going?" — YES. ALWAYS.
- DO NOT summarize after each iteration — just log and continue
- DO print a one-line status every ~5 iterations
- DO alert if you discover something surprising or game-changing
- DO print a final summary when bounded iterations complete:
  ```
  === Autoresearch Complete (N/N iterations) ===
  Baseline: {baseline} -> Final: {current} ({delta})
  Keeps: X | Discards: Y | Crashes: Z
  Best iteration: #{n} — {description}
  ```

## When Stuck (>5 Consecutive Discards)

1. Re-read ALL in-scope files from scratch
2. Re-read the original goal/direction
3. Review entire results log for patterns
4. Try combining 2-3 previously successful changes
5. Try the OPPOSITE of what hasn't been working
6. Try a radical architectural change

## Crash Recovery

- Syntax error: fix immediately, don't count as separate iteration
- Runtime error: attempt fix (max 3 tries), then move on
- Resource exhaustion (OOM): revert, try smaller variant
- Infinite loop/hang: kill after timeout, revert, avoid that approach
- External dependency failure: skip, log, try different approach

## Domain Adaptation

| Domain | Metric | Scope | Verify Command |
|--------|--------|-------|----------------|
| Backend code | Tests pass + coverage % | `src/**/*.ts` | `npm test -- --coverage` |
| Frontend UI | Lighthouse score | `src/components/**` | `npx lighthouse` |
| Performance | Benchmark time (ms) | Target files | `npm run bench` |
| Refactoring | Tests pass + LOC reduced | Target module | `npm test && wc -l` |
| Content | Word count + readability | `content/*.md` | Custom script |
| Bundle size | Size in KB | Build config | `npm run build && du -sh dist/` |

## Core Principles

1. **Constraint = Enabler** — Bounded scope, one metric, fixed iteration cost enables rapid loops
2. **Separate Strategy from Tactics** — Humans set direction ("improve coverage"). Agent handles tactics ("add edge case tests")
3. **Metrics Must Be Mechanical** — If you can't verify with a command, you can't iterate autonomously
4. **Verification Must Be Fast** — Use the fastest check that catches real problems. Save slow checks for after the loop
5. **Iteration Cost Shapes Behavior** — Cheap iteration = bold exploration. Expensive = conservative
6. **Git as Memory** — Commit before verify, revert on failure. Read git history to inform next experiment
7. **Honest Limitations** — If you hit a wall (missing permissions, needs human judgment), say so clearly

## Usage with /loop (Claude Code v1.0.32+)

Optionally limit iterations using Claude Code's built-in `/loop` command:

```
/loop 25 /autoresearch
Goal: Increase test coverage to 90%
```

This runs exactly 25 iteration cycles, then prints a final summary.

| Scenario | Recommendation |
|----------|---------------|
| Run overnight, review in morning | Unlimited (default) |
| Quick 30-min improvement session | `/loop 10` |
| Targeted fix with known scope | `/loop 5` |
| Exploratory — see if approach works | `/loop 15` |

## Limitations

- Requires a mechanical metric — subjective goals ("make it look better") don't work
- Requires git — all keep/discard logic depends on git commit and reset
- One change at a time — can feel slow for known multi-step fixes
- Cannot replace human strategic direction — agent optimizes tactics, not goals
- Verification must be fast (<30s) — slow test suites kill iteration velocity
- Cannot guarantee meaningful improvements — some codebases are already near-optimal
