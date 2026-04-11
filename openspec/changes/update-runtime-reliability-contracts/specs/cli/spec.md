## MODIFIED Requirements

### Requirement: Installable CLI Package
The package SHALL be installable as a CLI tool via standard Python package managers, making `bichos` available as a global command after installation, with all import-time runtime dependencies declared in package metadata.

#### Scenario: Install via pip
- **WHEN** user runs `pip install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** `bichos --help` prints usage without import errors

#### Scenario: Install via uv tool
- **WHEN** user runs `uv tool install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool runs in an isolated environment separate from the user's project
- **AND** `bichos analyze --help` loads without missing-module failures

#### Scenario: Install via pipx
- **WHEN** user runs `pipx install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool runs in its own isolated virtualenv
- **AND** all declared subcommands import successfully

#### Scenario: Ephemeral execution via uvx
- **WHEN** user runs `uvx bichos analyze /path/to/repo`
- **THEN** bichos runs without prior installation
- **AND** the ephemeral environment contains every import-time runtime dependency needed by the CLI and orchestrator

#### Scenario: Editable install via pip (development)
- **WHEN** developer runs `pip install -e .` in the project root
- **THEN** the `bichos` command is available on `PATH` pointing at the local source
- **AND** changes to source are reflected immediately without reinstalling

#### Scenario: Editable install via uv (development)
- **WHEN** developer runs `uv tool install --editable .` in the project root
- **THEN** the `bichos` command is available globally on `PATH` pointing at the local source
- **NOTE** For in-project use without global install, `uv run bichos` is the correct invocation

### Requirement: Benchmark Command Correctness
The CLI SHALL provide benchmark output that is reproducible, grounded in the fixture oracle, and explicit about degraded execution.

#### Scenario: Seeded benchmark run is reproducible
- **WHEN** user runs `bichos benchmark --dataset simple --modes aco --seeds 1 --seed 123`
- **THEN** the seed is propagated into all stochastic ant-selection logic for that run
- **AND** repeating the same command against the same fixture and model configuration produces the same stochastic choices, subject only to provider nondeterminism outside bichos

#### Scenario: Base seed expands deterministically across multiple runs
- **WHEN** user runs `bichos benchmark --seed 123 --seeds 3`
- **THEN** `123` is treated as a base seed for deterministic derivation of the three benchmark runs
- **AND** each run receives a stable derived seed
- **AND** repeating the same command yields the same per-run seed sequence

#### Scenario: True positives are matched against normalized fixture paths
- **WHEN** benchmarking a fixture dataset whose analyzed file paths are relative to the fixture root
- **THEN** planted bugs are scored against a normalized representation that matches ground truth whether reports contain `calculator.py` or `simple_bugs/calculator.py`
- **AND** valid bug reports are not discarded solely because the dataset directory prefix is absent

#### Scenario: Mock fallback is explicit
- **WHEN** benchmark execution falls back to mock reports because credentials are missing or a run fails
- **THEN** the output marks the affected run as degraded or mock-backed
- **AND** aggregate metrics do not silently present mock zeros as equivalent to successful real executions
