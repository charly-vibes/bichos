---
name: Beads: Review Tickets
description: Audit and enrich beads tickets using the Rule of 5 so each is fully self-contained for subagent implementation.
category: Beads
tags: [beads, tickets, review, autonomous]
---

# Beads Ticket Review — Rule of 5

Review one or more beads tickets using five iterative stages of refinement.
The goal: every ticket must be a **complete, standalone prompt** that a fresh
subagent can implement with zero additional context lookups.

TICKETS TO REVIEW:
$ARGUMENTS  ← issue ID(s), or "all open" to review every open ticket

PHILOSOPHY: "Breadth-first audit, then editorial enrichment"

---

## STAGE 1: DRAFT — Get the shape right

**Question**: Is the overall goal of the ticket clear?

Focus:
- Run `bd show <id>` for each ticket
- Don't aim for perfection yet — check overall intent only
- Is the ticket solving the right problem at the right scope?
- Does the title match what the description asks for?
- Is this one atomic unit of work, or secretly two tickets?

Output: High-level assessment per ticket — CLEAR / VAGUE / SPLIT_NEEDED

---

## STAGE 2: CORRECTNESS — Is the ticket actionable without extra lookups?

**Question**: Could a subagent implement this from the description alone?

A ticket passes when its description answers ALL of:

| # | Question | Must include |
|---|----------|-------------|
| 1 | What to build? | Exact files to CREATE or MODIFY (full paths from repo root) |
| 2 | What to read first? | Spec sections, source files, or design docs to consult before writing |
| 3 | How to implement? | Key types, signatures, constraints copied from spec/tracer-bullet |
| 4 | How to verify? | Exact commands to confirm done (e.g. `uv run pytest tests/test_X.py -v`) |
| 5 | What NOT to do? | Explicit scope boundary — what is out of scope for this ticket |

For each gap, gather the missing context from:
- `openspec/changes/add-entomological-framework/tracer-bullet.md`
- `openspec/changes/add-entomological-framework/tasks.md`
- Relevant existing source files in `src/bichos/`

Output: Per-ticket list of missing items (1–5 above) with proposed additions

---

## STAGE 3: CLARITY — Can a subagent understand it without reading this conversation?

**Question**: Is the enriched description unambiguous?

Focus:
- Remove pronouns that refer to previous tickets ("it", "the above", "same as before")
- Replace vague phrases ("implement the logic", "add tests") with concrete ones
- Ensure type names, file paths, and method names are spelled exactly as they appear in the codebase
- The description must work even if read in isolation, with no session history

Output: Clarity edits per ticket

---

## STAGE 4: EDGE CASES — What could go wrong during implementation?

**Question**: What would make a subagent go off-track or produce an incomplete result?

Focus:
- Missing interface dependencies (does it need to import from another module that may not exist yet?)
- Ambiguous acceptance criteria (does "tests pass" mean existing tests, new tests, or both?)
- Underspecified constraints (intensity bounds? TTL values? model names?)
- Missing "do NOT" guard rails that prevent scope creep

Output: Edge-case additions and explicit constraints to append

---

## STAGE 5: EXCELLENCE — Ready to hand off to a subagent?

**Question**: Would this ticket, as a prompt, produce a green build on the first try?

Focus:
- Apply all enrichments from Stages 2–4
- Format the final description using this template:

```
## Goal
<one sentence>

## Read first
- openspec/changes/add-entomological-framework/tracer-bullet.md § Phase N
- src/bichos/<dependency>.py   ← understand the interface before writing

## Files
- CREATE src/bichos/<module>/<file>.py
- MODIFY <existing file> (if applicable)

## Implementation notes
<key types, signatures, constraints — copied verbatim from spec>

## Constraints
- <explicit scope limits>
- <value ranges, naming conventions>

## Acceptance
uv run ruff check src/bichos/<module>/
uv run pytest tests/test_<module>.py -v
```

- Update the ticket with `bd update <id> --description "..."`
- Do NOT change status, owner, or any other field

Output: Confirmation that each ticket was updated, or SKIP if it already passed

---

## CONVERGENCE CHECK

After each stage (starting with Stage 2), report:
1. Number of new gaps found at any severity (CRITICAL / HIGH / MEDIUM / LOW)
2. New issues vs previous stage count
3. Convergence status:
   - **CONVERGED**: Zero new gaps at any severity, <10% new issues vs previous stage
   - **CONTINUE**: Proceed to next stage
   - **NEEDS_HUMAN**: Conflicting spec requirements, ambiguous scope, or missing spec section

> **Important:** LOW-severity gaps (e.g. vague phrasing, missing "do NOT" guard) are low-cost
> to fix and must be addressed before a ticket is considered self-contained. There is no
> "noted but not fixed" category.

---

## FINAL REPORT

- Total tickets reviewed
- Tickets updated vs already self-contained
- Top 3 most common gaps found across tickets
- Any NEEDS_HUMAN items requiring user decision
- Recommended next action (`bd ready` to confirm what's now unblocked)

---

## Scope limits

- Do **not** implement anything — only audit and enrich descriptions
- Do **not** create new tickets; only update existing ones
- Do **not** modify spec files, source code, or CLAUDE.md
- Do **not** change ticket status, type, priority, or owner
