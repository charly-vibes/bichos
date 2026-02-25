---
name: Impl: Review
description: Stage 3/3 of the Implementation Pipeline. Five-pass Rule of 5 code review. Returns APPROVED / NEEDS_CHANGES / NEEDS_HUMAN.
category: Implementation Pipeline
tags: [impl, review, rule-of-5, code-review]
---

# Impl: Review — Stage 3 of 3

Review all uncommitted implementation changes using five passes.
The orchestrator commits only after this review returns APPROVED.

NO ARGUMENTS — reviews all uncommitted changes.

---

## STEP 1: See the Changes

```bash
git diff HEAD          # all uncommitted changes
git status             # changed file list
```

Read every changed file completely, not just the diff lines.

---

## PASS 1: DRAFT — Does It Solve the Right Problem?

Check the changes against the issue's **Goal** statement:
- Does the implementation match what was asked?
- Are all acceptance criteria satisfied?
- Any files changed that were NOT in the ticket's scope?

Output per file: CORRECT / OFF_TARGET / SCOPE_CREEP

---

## PASS 2: CORRECTNESS — Bugs and Logic Errors

Check for:
- Off-by-one errors, wrong range bounds
- Unhandled `None` / empty list / empty graph cases
- Type mismatches (compare against Pydantic model field types)
- Async errors (missing `await`, unawaited coroutines, race conditions)
- Pheromone intensity outside [0.0, 100.0]
- ACO math: division by zero in probability calculations

Every finding: `file:line` reference + description + severity (CRITICAL/HIGH/MEDIUM/LOW)

---

## PASS 3: CLARITY — Readability

- Are names self-explanatory without comments?
- Do docstrings explain *why*, not just *what*?
- Any magic numbers that should be named constants?
- Would a new contributor understand this in 5 minutes?

---

## PASS 4: EDGE CASES — Boundary Conditions

- Empty inputs: empty list, zero-node graph, empty pheromone cache
- Concurrent access: is pheromone cache access thread-safe?
- LLM semaphore at limit: does it block correctly or deadlock?
- Numerical edges: `log(0)`, `0/0` in ACO probability formula

---

## PASS 5: EXCELLENCE — Production Readiness

- [ ] Tests cover both happy path and edge cases?
- [ ] `just check` passes with zero errors?
- [ ] No hardcoded API keys or secrets
- [ ] No leftover `TODO` / `FIXME` / `print()` from implementation
- [ ] Imports are clean (no unused, no `*` imports)
- [ ] `from __future__ import annotations` present in all new files

---

## CONVERGENCE CHECK (after each pass from Pass 2)

- New CRITICAL issues: N
- Total issues: N (vs previous pass: N)
- Status: **CONVERGED** / **CONTINUE** / **NEEDS_HUMAN**

Stop when: no new CRITICAL issues and <10% new findings vs previous pass.

---

## VERDICT

**APPROVED** — zero CRITICAL issues, safe to commit
**NEEDS_CHANGES** — list CRITICAL/HIGH items with exact fix instructions; re-run `/impl:run <id>`
**NEEDS_HUMAN** — architectural concern or spec conflict; escalate to user

The main orchestrator acts on the verdict:
- APPROVED → `bd close <id>` + `git add <files> && git commit`
- NEEDS_CHANGES → re-run `/impl:run <id>` with the fix list
- NEEDS_HUMAN → pause and ask the user
