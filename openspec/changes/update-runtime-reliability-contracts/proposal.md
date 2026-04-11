# Change: Update Runtime Reliability Contracts

## Why
Repository review found several places where the current implementation can appear healthy in local CI while still failing or misleading users in real runs. The main risks are undeclared runtime dependencies, swarm-size semantics that do not match configuration, invalid benchmark scoring, missing token accounting, and behavior that diverges from the published ant-forager contract.

## What Changes
- Clarify installability requirements so packaged CLI environments include every import-time runtime dependency.
- Define benchmark command requirements for deterministic seeding, valid ground-truth matching, and explicit fallback behavior.
- Define hive-orchestrator semantics for configured ant counts, seeded randomness, and report metadata integrity.
- Align ant-forager behavior with its published traversal and pheromone-reporting contracts.

## Impact
- Affected specs: `cli`, `hive-orchestrator`, `ant-forager`, `stigmergy`
- Affected code: `pyproject.toml`, `src/bichos/cli.py`, `src/bichos/hive/orchestrator.py`, `src/bichos/agents/ant/agent.py`, `src/bichos/agents/ant/tools.py`, `src/bichos/config.py`, benchmark tests
