## ADDED Requirements

<!--
Dependencies: model-provider is consumed by hive-orchestrator via AntDeps.config;
the CLI delegates provider selection to HiveConfig.model.
-->

### Read First
Before implementing, read:
- `src/bichos/config.py` (existing `HiveConfig`, `ACOConfig`, `StigmergyConfig` patterns)
- `src/bichos/agents/ant/agent.py` (the `run_ant()` call at line 74 — the bare `model=deps.config.ant_model` is what gets replaced)
- `.venv/lib/python3.12/site-packages/pydantic_ai/providers/` — `openai.py`, `anthropic.py`, `ollama.py`, `openrouter.py`

Required imports for `build_model()` in `src/bichos/config.py`:
```python
import os
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
```

### Requirement: ModelConfig Schema
`HiveConfig` SHALL expose a `model: ModelConfig` field that captures provider,
model name, optional base URL, and optional API-key env-var name.

#### Scenario: Default config uses OpenAI gpt-4o
- **GIVEN** `HiveConfig.default()` is constructed with no arguments
- **THEN** `config.model.provider == "openai"`
- **AND** `config.model.name == "gpt-4o"`
- **AND** `config.model.base_url is None`
- **AND** `config.model.api_key_env is None`

#### Scenario: ModelConfig round-trips through JSON
- **GIVEN** a `HiveConfig` with `model.provider = "ollama"` and `model.name = "llama3.2"`
- **WHEN** the config is serialised with `model_dump_json()` and parsed back
- **THEN** all `ModelConfig` fields are preserved exactly

### Requirement: Backwards-Compatible ant_model Alias
When a JSON config contains the legacy `ant_model` string key, it SHALL be
silently promoted to the equivalent `ModelConfig` without error.

#### Scenario: Legacy ant_model string is promoted
- **GIVEN** a JSON config `{"ant_model": "openai:gpt-4o"}`
- **WHEN** parsed as `HiveConfig`
- **THEN** `config.model.provider == "openai"` and `config.model.name == "gpt-4o"`
- **AND** no validation error is raised

#### Scenario: ant_model without provider prefix
- **GIVEN** a JSON config `{"ant_model": "gpt-4o"}` (no provider prefix)
- **WHEN** parsed as `HiveConfig`
- **THEN** `config.model.name == "gpt-4o"` and provider falls back to `"openai"`

#### Scenario: Both ant_model and model keys are present
- **GIVEN** a JSON config `{"ant_model": "openai:gpt-4o", "model": {"provider": "anthropic", "name": "claude-3-5-sonnet-latest"}}`
- **WHEN** parsed as `HiveConfig`
- **THEN** `config.model.provider == "anthropic"` (the explicit `model` key wins)
- **AND** `ant_model` is silently discarded
- **NOTE** implement this in the `mode='before'` validator: skip promotion when the `"model"` key is already present in the raw dict

### Requirement: build_model() Factory
A `build_model(cfg: ModelConfig) -> pydantic_ai.models.Model` function SHALL
construct the correct PydanticAI model object for each supported provider.

#### Scenario: OpenAI provider uses standard API
- **GIVEN** `ModelConfig(provider="openai", name="gpt-4o")`
- **AND** env var `OPENAI_API_KEY` is set (or `cfg.api_key_env` names an env var that is set)
- **WHEN** `build_model(cfg)` is called
- **THEN** it returns `OpenAIChatModel("gpt-4o", provider=OpenAIProvider(api_key=os.environ[api_key_env]))`
- **IF** neither `OPENAI_API_KEY` nor `cfg.api_key_env` resolves to a set env var,
  `build_model()` raises `ValueError("env var OPENAI_API_KEY is not set")` before constructing the provider

#### Scenario: Anthropic provider uses AnthropicModel
- **GIVEN** `ModelConfig(provider="anthropic", name="claude-3-5-sonnet-latest")`
- **AND** env var `ANTHROPIC_API_KEY` is set (or `cfg.api_key_env` names an env var that is set)
- **WHEN** `build_model(cfg)` is called
- **THEN** it returns `AnthropicModel("claude-3-5-sonnet-latest", provider=AnthropicProvider(api_key=os.environ[api_key_env]))`
- **IF** neither `ANTHROPIC_API_KEY` nor `cfg.api_key_env` resolves to a set env var,
  `build_model()` raises `ValueError("env var ANTHROPIC_API_KEY is not set")` before constructing the provider

#### Scenario: Ollama provider defaults base_url to localhost
- **GIVEN** `ModelConfig(provider="ollama", name="llama3.2")`
- **AND** no `base_url` is set on the config
- **AND** `OLLAMA_BASE_URL` env var is not set
- **WHEN** `build_model(cfg)` is called
- **THEN** it returns an `OpenAIChatModel` constructed with
  `OllamaProvider(base_url="http://localhost:11434/v1")`
- **NOTE** `build_model()` MUST pass `base_url` explicitly to `OllamaProvider`;
  calling `OllamaProvider()` with no arguments raises `UserError` at construction time.
  The API key is managed internally by `OllamaProvider` (defaults to `"api-key-not-set"`).

#### Scenario: Ollama provider respects custom base_url
- **GIVEN** `ModelConfig(provider="ollama", name="llama3.2", base_url="http://gpu-box:11434/v1")`
- **WHEN** `build_model(cfg)` is called
- **THEN** the returned model connects to `http://gpu-box:11434/v1`

#### Scenario: OpenRouter provider uses openrouter base_url
- **GIVEN** `ModelConfig(provider="openrouter", name="anthropic/claude-3.5-sonnet")`
- **AND** env var `OPENROUTER_API_KEY` is set (or `cfg.api_key_env` names an env var that is set)
- **WHEN** `build_model(cfg)` is called
- **THEN** it returns `OpenAIChatModel("anthropic/claude-3.5-sonnet", provider=OpenRouterProvider(api_key=os.environ[api_key_env]))`
- **AND** the provider's base_url is `"https://openrouter.ai/api/v1"` (hardcoded inside `OpenRouterProvider`)
- **IF** neither `OPENROUTER_API_KEY` nor `cfg.api_key_env` resolves to a set env var,
  `OpenRouterProvider.__init__` raises `UserError` — let it propagate without wrapping

#### Scenario: Custom api_key_env is respected
- **GIVEN** `ModelConfig(provider="openai", name="gpt-4o", api_key_env="MY_KEY")`
- **AND** env var `MY_KEY` is set to `"sk-custom"`
- **WHEN** `build_model(cfg)` is called
- **THEN** the model uses `"sk-custom"` as its API key

### Verification
Run `just check` (ruff + mypy + pytest) — all must pass with zero errors.
Mypy strict mode is enabled; `build_model()` must be fully typed with no `Any`.
