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
- **THEN** executing `bichos` invokes the main Click group defined in `bichos.cli`
- **AND** the invocation is equivalent to `python -m bichos.cli`

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
- **THEN** a hive analysis is launched on the target path with a progress indicator
- **AND** on completion the report is written to `bichos-report.md` in the working directory
- **AND** a summary line is printed to stdout

#### Scenario: Analyze subcommand — custom output format
- **WHEN** user runs `bichos analyze <path> --format json`
- **THEN** the analysis report is written to stdout as JSON
- **AND** no markdown file is created

#### Scenario: Analyze subcommand — output file
- **WHEN** user runs `bichos analyze <path> --output report.json --format json`
- **THEN** the JSON report is written to `report.json` instead of stdout

#### Scenario: Stats subcommand
- **WHEN** user runs `bichos stats [--path <cache-dir>]`
- **THEN** the top 10 high-pheromone locations are displayed with intensity scores
- **AND** agent activity summary is shown

#### Scenario: Stats subcommand with empty cache
- **WHEN** user runs `bichos stats` and no analysis has been run yet
- **THEN** message `No pheromone data found. Run 'bichos analyze' first.` is printed to stdout
- **AND** exit code is 0

#### Scenario: Config subcommand
- **WHEN** user runs `bichos config show`
- **THEN** resolved configuration is printed (defaults merged with any override file)
- **AND** bichos searches for config in this priority order: (1) `--config` flag, (2) `./bichos.yaml` in cwd, (3) `~/.config/bichos/config.yaml`

#### Scenario: Clear-cache subcommand
- **WHEN** user runs `bichos clear-cache`
- **THEN** pheromone cache is wiped
- **AND** message `Pheromone cache cleared.` is printed to stdout
- **AND** exit code is 0

#### Scenario: Clear-cache with no existing cache
- **WHEN** user runs `bichos clear-cache` and no cache exists at the configured path
- **THEN** message `No cache found, nothing to clear.` is printed to stdout
- **AND** exit code is 0
