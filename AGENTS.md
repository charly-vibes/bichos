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
- **beads (bd)** — issue tracking (tasks, bugs, dependencies)
- **openspec** — specifications and change proposals (see `openspec/AGENTS.md`)

## When to Use What

| Need | Tool | Example |
|------|------|---------|
| Record reasoning/research | wai | `wai add research "findings"` |
| Capture design decisions | wai | `wai add design "architecture choice"` |
| Session context transfer | wai | `wai handoff create <project>` |
| Track work items/bugs | beads | `bd create --title="..." --type=task` |
| Find available work | beads | `bd ready` |
| Manage dependencies | beads | `bd dep add <blocked> <blocker>` |
| Propose system changes | openspec | Read `openspec/AGENTS.md` |
| Define requirements | openspec | `openspec validate --strict` |

Key distinction:
- **wai** = *why* decisions were made (reasoning, context, handoffs)
- **beads** = *what* needs to be done (concrete tasks, status tracking)
- **openspec** = *what the system should look like* (specs, requirements, proposals)

## Starting a Session

1. Run `wai status` to see active projects, current phase, and suggestions.
2. Run `bd ready` to find available work items.
3. Check `openspec list` for active change proposals.
4. Check the phase — it tells you what kind of work is expected:
   - **research** → gather information, explore options
   - **design** → make architectural decisions
   - **plan** → break work into tasks
   - **implement** → write code, guided by research/plans
   - **review** → validate against plans
   - **archive** → wrap up
5. Read existing artifacts with `wai search "<topic>"` before starting new work.

## Capturing Work

Record the reasoning behind your work, not just the output:

```bash
wai add research "findings"         # What you learned, trade-offs
wai add plan "approach"             # How you'll implement, why
wai add design "decisions"          # Architecture choices, rationale
wai add research --file notes.md    # Import longer content
```

Use `--project <name>` if multiple projects exist. Otherwise wai picks the first one.

Phases are a guide, not a gate. Use `wai phase show` / `wai phase next`.

## Ending a Session

Before saying "done", run this checklist:

```
[ ] wai handoff create <project>   # capture context for next session
[ ] bd close <id>                  # mark completed issues
[ ] bd sync --from-main            # pull beads updates
[ ] wai reflect                    # update CLAUDE.md with project patterns (every ~5 sessions)
[ ] git add <files> && git commit  # commit code + handoff
```

### Autonomous Loop

One task per session. The resume loop:

1. `wai prime` — orient (shows ⚡ RESUMING if mid-task)
2. Work on the single task
3. `wai close` — capture state (run this before every `/clear`)
4. `git add <files> && git commit`
5. `/clear` — fresh context

→ Next session: `wai prime` shows RESUMING with exact next steps.

When context reaches ~40%: run `wai close`, then `/clear`.
Do NOT skip `wai close` — it enables resume detection.

## Quick Reference

### wai
```bash
wai status                    # Project status and next steps
wai add research "notes"      # Add research artifact
wai add plan "plan"           # Add plan artifact
wai add design "design"       # Add design artifact
wai search "query"            # Search across artifacts
wai why "why use TOML?"       # Ask why (LLM-powered oracle)
wai why src/config.rs         # Explain a file's history
wai reflect                   # Synthesize project patterns into CLAUDE.md
wai handoff create <project>  # Session handoff
wai phase show                # Current phase
wai doctor                    # Workspace health
```

### beads
```bash
bd ready                     # Available work
bd show <id>                 # Issue details
bd create --title="..."      # New issue
bd update <id> --status=in_progress
bd close <id>                # Complete work
```

### openspec
Read `openspec/AGENTS.md` for full instructions.
```bash
openspec list              # Active changes
openspec list --specs      # Capabilities
```

## Structure

The `.wai/` directory organizes artifacts using the PARA method:
- **projects/** — active work with phase tracking and dated artifacts
- **areas/** — ongoing responsibilities (no end date)
- **resources/** — reference material, agent configs, templates
- **archives/** — completed or inactive items

Do not edit `.wai/config.toml` directly. Use `wai` commands instead.

Keep this managed block so `wai init` can refresh the instructions.

<!-- WAI:END -->

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
bd sync --from-main               # pull beads updates
git add <files> && git commit -m "feat: Phase N — <title>"
```

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
