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
[ ] bd close <id>                  # mark completed issues
[ ] git add <files> && git commit  # commit after EVERY completed task (mandatory)
[ ] bd sync --from-main            # pull beads updates
[ ] wai handoff create <project>   # capture context for next session
[ ] wai reflect                    # update CLAUDE.md with project patterns (every ~5 sessions)
```

### Autonomous Orchestration Pattern

**The main agent is an orchestrator only — it never holds implementation context.**
Every stage is an independent subagent. **wai artifacts are the shared memory between stages.**
Never implement files yourself in the main agent; only close tickets and commit.

---

#### Pipeline 1 — Issue Pipeline (creating new work items)

```
Stage 1 (Gather):   /issue:gather <topic>   → research codebase, save to wai
Stage 2 (Create):   /issue:create           → read wai, generate bd tickets
Stage 3 (Review):   /issue:review           → Rule of 5 audit, update tickets
```

Each stage = one independent subagent. Output lives in wai, not in the main agent context.

---

#### Pipeline 2 — Implementation Pipeline (one ticket per iteration)

```
Stage 1 (Gather):   /impl:gather            → pick ONE issue, verify, save plan to wai
Stage 2 (Implement):/impl:run <id>          → TDD: red→green→refactor, just check
Stage 3 (Review):   /impl:review            → Rule of 5 code review, APPROVED or NEEDS_CHANGES
```

Then in the main agent (after APPROVED):
```bash
bd close <id>
git add <files> && git commit -m "feat(...): ..."
```

---

**Key rules:**
- Each stage = ONE independent subagent. Never chain two stages in one subagent.
- Stages communicate via wai artifacts — not by passing raw text between them.
- `/impl:review` returns APPROVED / NEEDS_CHANGES / NEEDS_HUMAN. Act on it.
- Never implement files yourself in the main agent; review verdict and commit only.
- Context warning thresholds: >30% → plan to clear after this task. >40% → clear now.

→ Next session: `wai prime` shows ⚡ RESUMING with exact next steps.
Do NOT skip `wai close` before `/clear` — it enables resume detection.

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

### skills (slash commands)

Issue Pipeline (gather → create → review):
```
/issue:gather <topic>        # Stage 1: research topic, save wai artifact
/issue:create                # Stage 2: read wai, generate bd tickets with TDD mandate
/issue:review [id(s)]        # Stage 3: Rule of 5 audit, update tickets
```

Implementation Pipeline (gather → run → review):
```
/impl:gather                 # Stage 1: pick ONE issue, verify, save plan to wai
/impl:run <id>               # Stage 2: TDD red→green→refactor, just check
/impl:review                 # Stage 3: Rule of 5 code review → APPROVED / NEEDS_CHANGES
```

Ticket enrichment:
```
/bd:review <id>              # Audit + enrich one ticket (Rule of 5)
/bd:review all open          # Audit all open tickets at once
```

OpenSpec:
```
/openspec:proposal           # Scaffold a new OpenSpec change
/openspec:apply              # Implement an approved OpenSpec change
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
