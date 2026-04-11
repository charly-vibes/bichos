## Context
The current repository passes `just check`, but the review found cross-cutting runtime risks that are not fully exercised by the local test suite:
- package metadata omits import-time dependencies used by the CLI and orchestrator
- the orchestrator launches one ant per function while `ant_count` only caps concurrency
- benchmark scoring depends on dataset-directory prefixes that are stripped by the graph builder
- seeded execution is advertised but not propagated
- token accounting is modeled in reports but not populated from provider usage
- some ant-forager requirements and implementation behavior are out of sync

## Goals / Non-Goals
- Goals:
- make packaged CLI installs reliable
- make swarm size, seeds, and report metadata semantically correct
- make benchmark outputs meaningful enough to support product decisions
- restore consistency between published ant-forager requirements and runtime behavior
- Non-Goals:
- redesign the entire ant-forager algorithm
- add new castes or new benchmark datasets
- change speculative research targets unrelated to runtime correctness

## Decisions
- Decision: Treat `ant_count` as total launched ant runs.
- Alternatives considered: keeping the current "one ant per function, ant_count as semaphore" behavior. Rejected because it makes cost and duration scale with graph size instead of configuration and breaks the meaning of `agent_count`.

- Decision: Treat benchmark seeds as first-class execution inputs that must influence all stochastic selection.
- Alternatives considered: leaving seeds as logging-only metadata. Rejected because it makes repeated benchmark runs incomparable.

- Decision: Compute report token usage from provider usage metadata, not from model-authored fields.
- Alternatives considered: asking the model to self-report token usage. Rejected because it is untrustworthy and often zero.

- Decision: Score fixture benchmarks using normalized paths that can match ground truth regardless of whether file paths are root-relative or dataset-relative.
- Alternatives considered: requiring all analyzers to preserve dataset directory prefixes. Rejected because it couples benchmark validity to one incidental path format.

- Decision: Standardize ant-forager behavior on the published contract for this proposal.
- Alternatives considered: redefining the ant-forager contract around current implementation details. Rejected because the current proposal is framed as reliability correction, not a product-behavior redesign.

## Chosen Contract Changes
- `choose_next_function()` returns the current function unchanged at dead ends (leaf nodes).
- pheromone deposition remains gated by a confidence threshold, with the authoritative config field named `min_confidence`
- bug pheromone intensity is proportional to severity and confidence
- `ExplorationResult.tokens_used` is populated from provider usage metadata

## Risks / Trade-offs
- Tightening packaging requirements may expose additional undeclared imports in optional paths.
- Enforcing exact `ant_count` semantics may reduce raw graph coverage per run and require different exploration strategies.
- Deterministic seeding may reveal hidden shared-state or ordering assumptions in tests.
- Benchmark normalization must avoid over-matching unrelated files with the same basename.

## Migration Plan
1. Update spec contracts.
2. Adjust packaging metadata and tests.
3. Refactor orchestrator launch semantics and seed propagation.
4. Fix token accounting and benchmark scoring.
5. Reconcile ant-forager behavior with the resulting specs.

## Open Questions
- Should `ReportMetadata` expose both configured and successful agent counts instead of one field?
- If `ReportMetadata` keeps a single `agent_count` field, should completed and degraded counts live in sibling metadata fields or in summary stats?
