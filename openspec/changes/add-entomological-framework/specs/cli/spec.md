## ADDED Requirements

### Requirement: Installable CLI Package
The package SHALL be installable as a CLI tool via standard Python package managers, making `bichos` available as a global command after installation.

#### Scenario: Install via pip
- **WHEN** user runs `pip install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** `bichos --help` prints usage without errors

#### Scenario: Install via uv tool
- **WHEN** user runs `uv tool install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool is isolated from the user's project environment

#### Scenario: Install via pipx
- **WHEN** user runs `pipx install bichos`
- **THEN** the `bichos` command is available on `PATH`
- **AND** the tool runs in its own isolated virtualenv

#### Scenario: Ephemeral execution via uvx
- **WHEN** user runs `uvx bichos analyze /path/to/repo`
- **THEN** bichos runs without prior installation
- **AND** the ephemeral environment is discarded after the run

#### Scenario: Editable install for development
- **WHEN** developer runs `pip install -e .` or `uv sync`
- **THEN** the `bichos` command is available pointing at the local source
- **AND** changes to source are reflected immediately without reinstalling

### Requirement: Entry Point Declaration
The `pyproject.toml` SHALL declare `bichos` as a console script entry point so package managers register it on `PATH` during installation.

#### Scenario: Entry point wired correctly
- **WHEN** the package is installed
- **THEN** `pyproject.toml` contains `[project.scripts] bichos = "bichos.cli:main"`
- **AND** the `main` callable is a Click group or equivalent

#### Scenario: Entry point survives upgrade
- **WHEN** user upgrades via `pip install --upgrade bichos`
- **THEN** the `bichos` command still resolves to the new version

### Requirement: CLI Version Flag
The CLI SHALL report the installed package version via `--version`.

#### Scenario: Version flag
- **WHEN** user runs `bichos --version`
- **THEN** output matches the version in `pyproject.toml` (e.g., `bichos 0.1.0`)
- **AND** exit code is 0

### Requirement: CLI Help Text
Every command and subcommand SHALL expose `--help` with a usage summary, available options, and at least one example.

#### Scenario: Top-level help
- **WHEN** user runs `bichos --help` or `bichos`
- **THEN** available subcommands are listed with one-line descriptions
- **AND** exit code is 0

#### Scenario: Subcommand help
- **WHEN** user runs `bichos analyze --help`
- **THEN** options, required arguments, and an example invocation are shown

### Requirement: CLI Exit Codes
The CLI SHALL return machine-readable exit codes so scripts and CI pipelines can detect failures.

#### Scenario: Successful analysis
- **WHEN** analysis completes without errors
- **THEN** exit code is 0

#### Scenario: Analysis finds issues
- **WHEN** bugs or violations are detected
- **THEN** exit code is 1 (issues found, not an error)

#### Scenario: Runtime error
- **WHEN** an unexpected error occurs (invalid path, missing config, LLM failure)
- **THEN** exit code is 2
- **AND** error message is printed to stderr with actionable guidance

### Requirement: CLI Subcommand Structure
The CLI SHALL expose subcommands covering the primary workflows.

#### Scenario: Analyze subcommand
- **WHEN** user runs `bichos analyze <path> [--config <file>] [--agents <n>]`
- **THEN** a hive analysis is launched on the target path

#### Scenario: Stats subcommand
- **WHEN** user runs `bichos stats [--path <cache-dir>]`
- **THEN** current pheromone statistics are displayed (top hotspots, agent activity)

#### Scenario: Config subcommand
- **WHEN** user runs `bichos config show`
- **THEN** resolved configuration is printed (defaults + any override file)

#### Scenario: Clear-cache subcommand
- **WHEN** user runs `bichos clear-cache`
- **THEN** pheromone cache is wiped and a confirmation is printed
