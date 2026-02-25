---
name: Issue: Review
description: Stage 3/3 of the Issue Pipeline. Five-pass Rule of 5 audit of freshly created issues for self-containment.
category: Issue Pipeline
tags: [issues, review, rule-of-5, beads]
---

# Issue: Review — Stage 3 of 3

Review freshly created issues using five iterative passes.
Goal: every issue must be a complete, standalone prompt a fresh agent can implement with zero extra lookups.

ISSUE IDs to review (or "all open" for all open issues):
$ARGUMENTS

---

## PASS 1: Completeness & Clarity

**Question**: Does each issue contain enough information to start work?

For each issue (`bd show <id>`), verify:
- [ ] Title is action-oriented and specific
- [ ] Description has all sections: Goal, Read first, Files, Implementation notes, Constraints, Acceptance
- [ ] File paths are exact full paths from repo root
- [ ] Acceptance criteria are runnable commands (not vague statements like "tests pass")

Severity: CRITICAL if file paths or acceptance criteria are missing.

Output: per-issue assessment — PASS / FAIL with specific gaps

---

## PASS 2: Scope & Atomicity

**Question**: Is each issue one logical unit of work?

- Can one agent complete this in one session? If no → SPLIT_NEEDED
- Does it secretly contain two tasks? → SPLIT_NEEDED
- Is scope bounded with explicit "do NOT" guards?

---

## PASS 3: Dependencies & Ordering

**Question**: Are dependencies correctly wired?

```bash
bd blocked          # show all blocked issues
bd show <id>        # check DEPENDS ON and BLOCKS fields
```

- Missing dependency → add it: `bd dep add <blocked> <blocker>`
- Circular dependency → NEEDS_HUMAN
- Unnecessary dependency → note (don't remove without approval)

---

## PASS 4: Spec Alignment

**Question**: Does the issue trace back to a plan or spec?

- Does the description reference a wai artifact or openspec section?
- Does the acceptance criteria match spec requirements?
- Any spec requirement not covered by any issue? → GAP

---

## PASS 5: Executability & Handoff

**Question**: Could a subagent implement this from the description alone?

Test: given only the description (no session history), can you answer:
1. What file to create or modify? ✓/✗
2. What interfaces to import from sibling modules? ✓/✗
3. What commands to run to verify done? ✓/✗
4. What is explicitly out of scope? ✓/✗

Apply fixes: `bd update <id> --description "..."`

---

## CONVERGENCE CHECK (after each pass from Pass 2)

- New CRITICAL gaps found: N
- New findings vs previous pass: N%
- Status: **CONVERGED** / **CONTINUE** / **NEEDS_HUMAN**

Stop when: no new CRITICAL gaps and <10% new findings vs previous pass.

---

## FINAL REPORT

- Total issues reviewed: N
- Issues updated: N (vs already self-contained: N)
- Top 3 most common gaps
- NEEDS_HUMAN items: list
- Recommended next step: `bd ready` to confirm what's now unblocked
