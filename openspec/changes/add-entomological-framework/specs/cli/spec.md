# CLI Specification

## ADDED Requirements

<!--
Dependencies: `bichos analyze` delegates to hive-orchestrator;
`bichos stats` and `bichos clear-cache` operate on the stigmergy cache.
-->

### Requirement: Installable CLI Package
The package SHALL be installable as a CLI tool via standard Python package managers, making `bichos` available as a global command after installation.

#### Scenario: Install via pip
- **WHEN** user runs `pip install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** `bichos --help` prints usage without errors

#### Scenario: Install via uv tool
- **WHEN** user runs `uv tool install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool runs in an isolated environment separate from the user's project

#### Scenario: Install via pipx
- **WHEN** user runs `pipx install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool runs in its own isolated virtualenv

#### Scenario: Ephemeral execution via uvx
- **WHEN** user runs `uvx bichos analyze /path/to/repo`
- **THEN** bichos runs without prior installation
- **AND** the ephemeral environment is discarded after the run

#### Scenario: Editable install via pip (development)
- **WHEN** developer runs `pip install -e .` in the project root
- **THEN** the `bichos` command is available on `PATH` pointing at the local source
- **AND** changes to source are reflected immediately without reinstalling

#### Scenario: Editable install via uv (development)
- **WHEN** developer runs `uv tool install --editable .` in the project root
- **THEN** the `bichos` command is available globally on `PATH` pointing at the local source
- **NOTE** For in-project use without global install, `uv run bichos` is the correct invocation

### Requirement: Entry Point Declaration
The `pyproject.toml` SHALL declare `bichos` as a `[project.scripts]` console script entry point so package managers register it on `PATH` during installation.

#### Scenario: Entry point is callable after install
- **WHEN** the package is installed via any supported package manager
- **THEN** executing `bichos` invokes the Typer app defined in `bichos.cli`

### Requirement: CLI Version Flag
The CLI SHALL report the installed package version via `--version`.

#### Scenario: Version flag
- **WHEN** user runs `bichos --version`
- **THEN** output is `bichos <version>` matching the version declared in `pyproject.toml`
- **AND** exit code is 0

### Requirement: CLI Help Text
Every command and subcommand SHALL expose `--help` with a usage summary, available options, and at least one example line beginning with `Example:`.

#### Scenario: Top-level help
- **WHEN** user runs `bichos --help` or `bichos` with no arguments
- **THEN** available subcommands are listed with one-line descriptions
- **AND** exit code is 0

#### Scenario: Subcommand help includes example
- **WHEN** user runs `bichos analyze --help`
- **THEN** options and required arguments are shown
- **AND** output contains a line starting with `Example:`

### Requirement: CLI Exit Codes
The CLI SHALL return machine-readable exit codes so scripts and CI pipelines can detect failures.

#### Scenario: Successful analysis, no issues found
- **WHEN** analysis completes and no bugs or violations are detected
- **THEN** exit code is 0

#### Scenario: Analysis finds issues
- **WHEN** bugs or violations are detected
- **THEN** exit code is 1 (issues found; not a tool error)
- **NOTE** Current implementation uses exit code 1 for both issues-found and runtime errors. Exit code 2 for tool errors is planned but not yet implemented.

#### Scenario: Runtime error
- **WHEN** an unexpected error occurs (invalid path, corrupted cache, network failure)
- **THEN** exit code is 2
- **AND** error message is printed to stderr with actionable guidance

#### Scenario: Missing LLM credentials
- **WHEN** user runs `bichos analyze` and no LLM API credentials are configured
- **THEN** exit code is 2
- **AND** stderr names the missing environment variable (e.g., `OPENAI_API_KEY`) and describes how to set it or use a local model

### Requirement: CLI Subcommand Structure
The CLI SHALL expose subcommands covering the primary workflows. Command surface is the authoritative contract; the Hive Orchestrator and Stigmergy system are invoked internally.

#### Scenario: Analyze subcommand — default output
- **WHEN** user runs `bichos analyze <path> [--config <file>] [--agents <n>]`
- **THEN** a hive analysis is launched on the target path
- **AND** on completion a summary table is printed to stdout

#### Scenario: Analyze subcommand — JSON output
- **WHEN** user runs `bichos analyze <path> --output json`
- **THEN** the analysis report is written to stdout as JSON
- **NOTE** File output is not yet implemented; JSON goes to stdout only

#### Scenario: Stats subcommand
- **WHEN** user runs `bichos stats <cache-dir>`
- **THEN** the top 20 high-pheromone locations are displayed with intensity scores

#### Scenario: Stats subcommand with empty cache
- **WHEN** user runs `bichos stats <cache-dir>` and no pheromones exist
- **THEN** message `No pheromones found.` is printed to stdout

#### Scenario: Config subcommand
- **WHEN** user runs `bichos config show`
- **THEN** resolved configuration is printed (defaults merged with any override file)
- **NOTE** Not yet implemented. Configuration is currently passed via `--config` flag to `analyze`.

#### Scenario: Clear-cache subcommand
- **WHEN** user runs `bichos clear-cache`
- **THEN** pheromone cache is wiped
- **AND** message is printed to stdout
- **NOTE** Not yet implemented.

#### Scenario: Benchmark subcommand
- **WHEN** user runs `bichos benchmark [--dataset simple|medium|all] [--modes aco,complexity,random] [--seeds N]`
- **THEN** the swarm is benchmarked across modes and datasets
- **AND** a summary table with precision, recall, F1, and token usage is printed
- **AND** optional `--output-file` writes JSON results to disk
