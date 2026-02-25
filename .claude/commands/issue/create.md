---
name: Issue: Create
description: Stage 2/3 of the Issue Pipeline. Read the wai research artifact and generate well-formed beads issues with TDD mandate and wired dependencies.
category: Issue Pipeline
tags: [issues, beads, create, tdd]
---

# Issue: Create — Stage 2 of 3

Read the most recent wai research artifact and generate well-formed beads issues.
Every issue must include the TDD mandate and trace back to the source artifact.

TOPIC (optional filter — matches the /issue:gather topic):
$ARGUMENTS

---

## STEP 1: Read the Research Artifact

```bash
wai search "$ARGUMENTS"    # find the artifact from /issue:gather
```

Read the full artifact. If no artifact is found, STOP and tell the user to run
`/issue:gather <topic>` first.

## STEP 2: Break Down into Atomic Issues

For each proposed work unit from the research:
- One agent must be able to complete it in one session
- It must not secretly be two tasks
- It must have a clear "done" state

## STEP 3: Create Issues

For each work unit, run:

```bash
ID=$(bd create \
  --title="<action-oriented title>" \
  --description="## Goal
<one sentence>

## Read first
- wai artifact: <artifact title from research>
- <source file to read before writing>
- <spec section if applicable>

## Files
- CREATE src/bichos/<module>/<file>.py
- MODIFY <existing file> (if applicable)

## Implementation notes
<key types, signatures, constraints — copied verbatim from the research artifact>

## Constraints
- Write tests BEFORE writing implementation code (TDD mandate)
- <explicit scope limit — what NOT to do in this ticket>
- <value ranges, naming conventions>

## Acceptance
uv run ruff check src/bichos/<module>/
uv run pytest tests/test_<module>.py -v

## Source
Research artifact: <artifact title>" \
  --type=task \
  --priority=2 2>&1 | grep -oE 'bichos-[a-z0-9]+')
echo "Created: $ID"
```

Capture each ID in a shell variable before creating the next issue.

## STEP 4: Wire Dependencies

After ALL issues are created:

```bash
bd dep add <blocked-id> <blocker-id>   # blocked depends on blocker
```

## FINAL REPORT

- Total issues created: N
- Issue IDs: list them
- Dependencies wired: list them
- Any ambiguities that require human decision
- Recommended next step: `/issue:review`
