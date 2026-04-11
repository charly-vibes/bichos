## 1. Packaging And CLI Contracts
- [ ] 1.1 Update package metadata so every module imported by the CLI and orchestrator is declared as a runtime dependency.
- [ ] 1.2 Add packaging smoke tests for `pip install`, `uv tool install`, or equivalent isolated-environment invocation.
- [ ] 1.3 Specify and implement benchmark command behavior for seeded runs, fallback behavior, and path-normalized scoring.

## 2. Orchestrator Contracts
- [ ] 2.1 Define and implement `ant_count` as the total number of ant runs launched, not only a concurrency semaphore.
- [ ] 2.2 Propagate CLI and benchmark seeds into hive execution and ant RNG construction.
- [ ] 2.3 Record report metadata using provider usage data, configured agent counts, and explicit degraded/completed agent accounting.

## 3. Ant Forager Contracts
- [ ] 3.1 Align dead-end traversal behavior with the published leaf-node contract (return current function unchanged).
- [ ] 3.2 Align pheromone intensity and confidence-threshold behavior with the published requirements using `min_confidence` as the authoritative config field.
- [ ] 3.3 Ensure `ExplorationResult.tokens_used` is derived from the underlying model usage rather than model-authored output.

## 4. Verification
- [ ] 4.1 Add regression tests for packaged install imports, benchmark true-positive scoring, seeded determinism, and token accounting.
- [ ] 4.2 Run `openspec validate update-runtime-reliability-contracts --strict`.
- [ ] 4.3 Run `just check`.
