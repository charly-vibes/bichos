<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

<!-- WAI:START -->
# Workflow Tools

This project uses **wai** to track the *why* behind decisions — research,
reasoning, and design choices that shaped the code. Run `wai status` first
to orient yourself.

Detected workflow tools:
- **wai** — research, reasoning, and design decisions
- **beads** — issue tracking (tasks, bugs, dependencies). CLI command: **`bd`** (not `beads`)
- **openspec** — specifications and change proposals (see `openspec/AGENTS.md`)

> **CRITICAL**: Apply TDD and Tidy First throughout — not just when writing code:
> - **Planning/task creation**: each ticket should map to a red→green→refactor cycle; refactoring tasks must be separate tickets from feature tasks.
> - **Design**: define the test shape (inputs/outputs) before designing the implementation.
> - **Implementation**: write the failing test first, then make it pass, then tidy in a separate commit.

> **When beginning research or creating a ticket**: run `wai search "<topic>"` to check for existing patterns before writing new content.

## Quick Start

1. `wai sync` — ensure agent tools are projected
2. `wai status` — see active projects, phase, and suggestions
3. `bd ready` — find available work items

When context reaches ~40%: stop and tell the user — responses degrade past
this point. Recommend `wai close` then `/clear` to resume cleanly.
Do NOT skip `wai close` — it enables resume detection.

## Detailed Instructions

Full workflow reference — session lifecycle, capturing work, command cheat
sheets, cross-tool sync, and PARA structure — lives in **`.wai/AGENTS.md`**.
Read it at the start of your first session or when you need detailed guidance.

Keep this managed block so `wai init` can refresh the instructions.

<!-- WAI:END -->

<!-- WAI:REFLECT:REF:START -->
## Accumulated Project Patterns

Project-specific conventions, gotchas, and architecture notes live in
`.wai/resources/reflections/`. Run `wai search "<topic>"` to retrieve relevant
context before starting research or creating tickets.

> **Before research or ticket creation**: always run `wai search "<topic>"` to
> check for known patterns. Do not rediscover what is already documented.
<!-- WAI:REFLECT:REF:END -->


<!-- WAI:REFLECT:START -->
## Project-Specific AI Context
_Last reflected: 2026-02-24 · 1 session analyzed_

### Conventions
- This project uses the **entomological codebase framework** as its domain model — biological insect taxonomy maps to software concepts (species → components, genus → modules, etc.)
- OpenSpec proposals are the primary mechanism for proposing architectural changes; always read `openspec/AGENTS.md` before implementing significant changes
- The project is in early/proposal phase — recent commits show framework proposals, not implementation code yet

### Architecture Notes
- The `.wai/` directory uses PARA method organization (projects/, areas/, resources/, archives/)
- Beads (bd) is used for issue tracking; wai is for reasoning/research capture — keep these roles distinct
- This is an ephemeral branch workflow: code merges to main locally, no upstream push
- The `add-entomological-framework` openspec has 0/251 progress — substantial specification work remains unimplemented
<!-- WAI:REFLECT:END -->


## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd sync
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds

---

## Autonomous Build Guide

This project is built autonomously — one tracer-bullet phase per session.

### Session Start

```bash
wai status       # orient
bd ready         # pick lowest-ID unblocked issue
bd show <id>     # read full details
```

### Implementation Reference

| Phase | Beads ID | Spec Location |
|-------|----------|---------------|
| 0: Project Skeleton | bichos-zrt | tracer-bullet.md § Phase 0 |
| 1: Stigmergy System | bichos-40z | tracer-bullet.md § Phase 1 |
| 2: Code Graph Builder | bichos-iz2 | tracer-bullet.md § Phase 2 |
| 3: ACO Mathematics | bichos-6dk | tracer-bullet.md § Phase 3 |
| 4: Ant Forager Agent | bichos-uf8 | tracer-bullet.md § Phase 4 |
| 5: Hive Orchestrator | bichos-ozx | tracer-bullet.md § Phase 5 |
| 6: Validation & Benchmark | bichos-zs5 | tracer-bullet.md § Phase 6 |

Phases 1, 2, 3 are independent and can run in parallel once Phase 0 is closed.

All spec files: `openspec/changes/add-entomological-framework/`

### Key Constraints

- **Layout**: `src/bichos/` (src-layout)
- **Package manager**: `uv` — use `uv run pytest`, `uv sync`
- **Type safety**: type hints on all public APIs, Pydantic for all agent I/O
- **Pheromone cap**: intensity always in [0.0, 100.0]
- **Tests**: unit tests always; integration tests needing API keys → `@pytest.mark.slow`
- **No external infra**: no Redis, Docker, or cloud services required
- **Quality gate**: `just check` must pass before committing

### Session End

```bash
just check                        # lint + typecheck + test
bd close <id>                     # mark phase complete
wai handoff create bichos         # save context
git add <files> && git commit -m "feat: Phase N — <title>"
```

If beads needs any extra follow-up beyond `bd close`, run `bd` and use the
commands your installed version offers.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:ca08a54f -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->
