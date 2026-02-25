# Change: Add Multi-Provider Model Configuration

## Why

`bichos analyze` currently wires its LLM backend through a bare `ant_model: str`
field (default `"openai:gpt-4o"`), which PydanticAI resolves using built-in
provider defaults. This works for OpenAI and Anthropic where credentials come from
standard env vars, but it is impossible to express a custom `base_url` — required
for both OpenRouter (OpenAI-compatible proxy) and locally-hosted Ollama.

Users who want to run bichos without cloud API keys — either to save cost (via
OpenRouter) or to work fully offline (via Ollama) — have no supported path today.

## What Changes

Introduce a `ModelConfig` data class inside `HiveConfig` that captures:
- **provider** — `openai | anthropic | openrouter | ollama`
- **name** — model identifier (e.g. `llama3.2`, `anthropic/claude-3.5-sonnet`)
- **base_url** — optional endpoint override (auto-defaulted for openrouter/ollama)
- **api_key_env** — optional env-var name to read the key from

A `build_model()` helper constructs the correct PydanticAI `Model` object from
`ModelConfig`, then `run_ant()` uses that object instead of the bare string.

The CLI gains a `--model <provider>:<name>` flag for quick overrides and a
`--base-url` flag for non-standard endpoints, both overriding the JSON config.

Backwards compatibility: the existing `ant_model` string field is kept as a
deprecated alias and promoted to `ModelConfig` via a `model_validator`.

## Impact

### Affected Specs
- **ADDED**: `model-provider` (new spec; did not exist before this change)
- **MODIFIED**: `cli` (new flags on `analyze`)

### Affected Code
- `src/bichos/config.py` — add `ModelConfig`, `build_model()`, deprecate `ant_model`
- `src/bichos/agents/ant/agent.py` — use `build_model()` instead of bare string
- `src/bichos/cli.py` — add `--model` and `--base-url` to `analyze`
- `tests/test_config.py` — new; unit tests for `build_model()` and config parsing
- `tests/test_ant_agent.py` — update `_make_simple_ant_deps` helper and `test_forager_handles_dead_end` (both contain `HiveConfig(ant_model="test")`)
