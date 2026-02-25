## MODIFIED Requirements

<!--
Dependencies: cli analyze command delegates model selection to model-provider
via HiveConfig.model; --model and --base-url override config file values.
-->

### Read First
- `src/bichos/cli.py`: the existing `analyze()` function and the `--agents`
  override pattern (lines 117–125) — follow the same structure for `--model`
  and `--base-url` overrides
- `specs/model-provider/spec.md`: `ModelConfig` field names and defaults

### Requirement: --model Flag on analyze
The `bichos analyze` subcommand SHALL accept a `--model` flag in
`<provider>:<name>` format that overrides the model in the active config.

**Parsing rule:** `--model` value is split on the **first** `:` only using
`provider, name = value.split(':', 1)`. Everything after the first `:` is the
model name, including any slashes or additional colons (e.g., version tags).

#### Scenario: --model sets provider and name
- **GIVEN** user runs `bichos analyze src/ --model ollama:llama3.2`
- **THEN** `config.model.provider == "ollama"` and `config.model.name == "llama3.2"`
- **AND** analysis proceeds using the Ollama backend

#### Scenario: --model openrouter with slash in name
- **GIVEN** user runs `bichos analyze src/ --model openrouter:anthropic/claude-3.5-sonnet`
- **THEN** `config.model.provider == "openrouter"`
- **AND** `config.model.name == "anthropic/claude-3.5-sonnet"` (slash preserved)

#### Scenario: --model overrides config file
- **GIVEN** a config JSON with `model.provider = "openai"` and `model.name = "gpt-4o"`
- **AND** user runs `bichos analyze src/ --config config.json --model ollama:llama3.2`
- **THEN** the Ollama backend is used, ignoring the config file's model

#### Scenario: invalid --model format shows error
- **GIVEN** user runs `bichos analyze src/ --model badformat`
- **THEN** exit code is non-zero
- **AND** an error message describes the expected `<provider>:<name>` format

### Requirement: --base-url Flag on analyze
The `bichos analyze` subcommand SHALL accept a `--base-url` flag that overrides
`config.model.base_url`, allowing custom endpoints without editing a config file.

#### Scenario: --base-url overrides default Ollama endpoint
- **GIVEN** user runs `bichos analyze src/ --model ollama:llama3.2 --base-url http://gpu-box:11434/v1`
- **THEN** the model connects to `http://gpu-box:11434/v1`

### Do NOT
- Do not modify `--agents`, `--output`, `--config`, `--seed`, or any other
  existing flag on the `analyze` or `stats` subcommands.
- Do not change the override-application logic for `--agents`; model overrides
  must follow the same `model_copy(update={...})` pattern.
