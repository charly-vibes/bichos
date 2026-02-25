---
name: Impl: Run
description: Stage 2/3 of the Implementation Pipeline. Full TDD cycle - Red → Green → Refactor → Check. Does not commit.
category: Implementation Pipeline
tags: [impl, tdd, implementation, test-first]
---

# Impl: Run — Stage 2 of 3

Implement the claimed issue using Test-Driven Development.
Do NOT commit — the main orchestrator commits after `/impl:review`.

ISSUE ID:
$ARGUMENTS

---

## STEP 1: Read Everything First

```bash
bd show $ARGUMENTS                    # issue description
wai search "ISSUE: $ARGUMENTS"        # implementation plan from /impl:gather
```

Read ALL files listed in "Read first" before writing a single line of code.
Do NOT start implementing until you understand the full context.

---

## STEP 2: RED — Write Failing Tests First

For each behavior described in the acceptance criteria:

1. Write the test in `tests/test_<module>.py`
2. Confirm it FAILS:
   ```bash
   uv run pytest tests/test_<module>.py::test_<name> -v
   ```
3. If it passes before implementation → the test is wrong, fix it

Tests MUST be written before any implementation code. No exceptions.

---

## STEP 3: GREEN — Implement Minimal Code

Write the minimum code to make the tests pass:
- No extra features beyond what tests require
- Use types and interfaces exactly as specified in the ticket
- Import from sibling modules using absolute imports (`from bichos.xxx`)

```bash
uv run pytest tests/test_<module>.py -v    # run after each file written
```

---

## STEP 4: REFACTOR — Clean Up

With all tests passing:
- Remove duplication
- Improve names
- Add docstrings where logic is non-obvious (not for every function)
- Do NOT change behavior

```bash
uv run pytest tests/test_<module>.py -v    # confirm still green
```

---

## STEP 5: CHECK — Full Suite

```bash
just check
```

If `just` is not available:
```bash
uv run ruff check src/
uv run ruff format --check src/
uv run mypy src/
uv run pytest -v
```

Fix ALL errors before reporting done. Do not skip errors.

---

## OUTPUT

Report:
- Tests written: N (list test function names)
- Files created: list with full paths
- Files modified: list with full paths
- `just check` result: PASS / FAIL (show output if FAIL)
- Any deviations from the ticket spec (reason required)
- Recommended next step: `/impl:review`

Do NOT commit. The orchestrator commits after review.
