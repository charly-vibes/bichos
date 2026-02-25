# Tasks: add-model-provider-config

## 1. Config layer

- [ ] 1.1 Add `ModelConfig(provider, name, base_url, api_key_env)` to `src/bichos/config.py`
- [ ] 1.2 Replace `ant_model: str` with `model: ModelConfig` in `HiveConfig`
- [ ] 1.3 Add `@model_validator(mode='before')` that promotes legacy `ant_model` string to `ModelConfig`
  - Only runs when `"ant_model"` key is present AND `"model"` key is absent in the raw dict
  - Split `ant_model` on first `:`: `provider, name = ant_model.split(':', 1)` if `:` present; else `provider="openai"`, `name=ant_model`
  - Set `data["model"] = {"provider": provider, "name": name}` and delete `data["ant_model"]`
  - Must not conflict with the existing `mode='after'` validator `_validate_intensity_range`
- [ ] 1.4 Implement `build_model(cfg: ModelConfig) -> Model` in `src/bichos/config.py`
  - Imports: `import os`; `from pydantic_ai.models import Model`; `from pydantic_ai.models.openai import OpenAIChatModel`; `from pydantic_ai.models.anthropic import AnthropicModel`; `from pydantic_ai.providers.openai import OpenAIProvider`; `from pydantic_ai.providers.anthropic import AnthropicProvider`; `from pydantic_ai.providers.ollama import OllamaProvider`; `from pydantic_ai.providers.openrouter import OpenRouterProvider`
  - Add private helper `_resolve_key(cfg: ModelConfig, default_env: str) -> str` that reads `os.environ.get(cfg.api_key_env or default_env)` and raises `ValueError(f"env var {default_env} is not set")` if result is `None`
  - `openai`: `return OpenAIChatModel(cfg.name, provider=OpenAIProvider(api_key=_resolve_key(cfg, "OPENAI_API_KEY")))`
  - `anthropic`: `return AnthropicModel(cfg.name, provider=AnthropicProvider(api_key=_resolve_key(cfg, "ANTHROPIC_API_KEY")))`
  - `ollama`: `return OpenAIChatModel(cfg.name, provider=OllamaProvider(base_url=cfg.base_url or "http://localhost:11434/v1"))` — MUST pass `base_url` explicitly; `OllamaProvider()` with no args raises `UserError`
  - `openrouter`: `return OpenAIChatModel(cfg.name, provider=OpenRouterProvider(api_key=_resolve_key(cfg, "OPENROUTER_API_KEY")))` — let `UserError` from provider propagate unwrapped

## 2. Agent wiring

- [ ] 2.1 In `src/bichos/agents/ant/agent.py`, replace `model=deps.config.ant_model` (line 74) with `model=build_model(deps.config.model)`
  - Add import: `from bichos.config import build_model`

## 3. CLI flags

- [ ] 3.1 Add `--model <provider>:<name>` flag to `bichos analyze` (parses on first `:`)
- [ ] 3.2 Add `--base-url TEXT` flag to `bichos analyze`
- [ ] 3.3 Apply CLI overrides to `hive_config.model` after config is loaded using `model_copy`:
  ```python
  if model_flag or base_url_flag:
      updates: dict[str, object] = {}
      if model_flag:
          if ":" not in model_flag:
              typer.echo("Error: --model must be in <provider>:<name> format", err=True)
              raise typer.Exit(code=1)
          provider, name = model_flag.split(":", 1)
          updates["provider"] = provider
          updates["name"] = name
      if base_url_flag:
          updates["base_url"] = base_url_flag
      hive_config = hive_config.model_copy(
          update={"model": hive_config.model.model_copy(update=updates)}
      )
  ```

## 4. Tests

- [ ] 4.1 New `tests/test_config.py`: unit-test `build_model()` for all four providers using monkeypatched env vars
- [ ] 4.2 New `tests/test_config.py`: test legacy `ant_model` alias promotion
- [ ] 4.3 New `tests/test_config.py`: test `--model` CLI flag parsing via `CliRunner`
- [ ] 4.4 New `tests/test_config.py`: test invalid `--model` format returns non-zero exit
- [ ] 4.5 Update ALL occurrences of `HiveConfig(ant_model="test")` in `tests/test_ant_agent.py`:
  - `_make_simple_ant_deps` helper (line 68): `config = HiveConfig(model=ModelConfig(provider="openai", name="test"))`
  - `test_forager_handles_dead_end` standalone (line 243): `config = HiveConfig(model=ModelConfig(provider="openai", name="test"))`
  - Add `from bichos.config import ModelConfig` to the test file imports
  - NOTE: `build_model()` is NOT called in unit tests because `forager.override(model=TestModel(...))` intercepts before `forager.run` reaches `build_model`. No special `"test"` sentinel handling is needed inside `build_model()`.

## 5. Validation

- [ ] 5.1 `just check` passes (ruff + mypy + pytest)
- [ ] 5.2 Dogfood run: `uv run bichos analyze src/bichos/ --model ollama:llama3.2` (requires local Ollama)
