---
name: Impl: Gather
description: Stage 1/3 of the Implementation Pipeline. Pick ONE ready issue, verify self-containment, claim it, and save the implementation plan to wai.
category: Implementation Pipeline
tags: [impl, gather, wai, beads]
---

# Impl: Gather — Stage 1 of 3

Orient to available work, pick ONE issue, verify it's self-contained, and save the implementation plan as a wai artifact.

NO ARGUMENTS — this stage selects work autonomously.

---

## STEP 1: Orient

```bash
wai prime                   # orient to project context and active work
wai search "ISSUE:"         # check for existing implementation plans
bd ready                    # list available work (no blockers)
```

Pick the HIGHEST PRIORITY ready issue.
Tiebreak: lowest beads ID (earliest created).

## STEP 2: Verify Self-Containment

```bash
bd show <id>
```

Check against the Rule of 5 handoff criteria — every item must be present:

| # | Check | Present? |
|---|-------|----------|
| 1 | Files to CREATE or MODIFY (full paths from repo root) | ✓/✗ |
| 2 | Files to read first (spec sections, source files) | ✓/✗ |
| 3 | Key types, signatures, constraints (copied from spec) | ✓/✗ |
| 4 | Exact verification commands (runnable, not vague) | ✓/✗ |
| 5 | Explicit scope boundary ("do NOT implement X here") | ✓/✗ |

**If ANY are missing → run `/bd:review <id>` before proceeding.**
Do NOT continue to `/impl:run` with an incomplete ticket.

## STEP 3: Claim the Issue

```bash
bd update <id> --status=in_progress
```

## STEP 4: Save Implementation Plan to wai

Synthesize a brief plan from the ticket + relevant wai context:

```bash
wai add plan "ISSUE: <id> — <title>

## What to build
<one paragraph summary>

## Read first
- <file/spec list from the ticket>

## Approach
1. Write failing tests for <behavior>
2. Implement <module/file>
3. Run just check

## Acceptance
<exact commands from the ticket>"
```

## OUTPUT

Report:
- Issue ID claimed: `<id>`
- Self-containment result: all 5 checks PASS or which failed
- Wai plan artifact saved: confirm title
- Recommended next step: `/impl:run <id>`
