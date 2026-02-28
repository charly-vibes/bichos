"""Tests for ModelConfig schema and ant_model alias validator in config.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from bichos.config import HiveConfig, ModelConfig

# ---------------------------------------------------------------------------
# ModelConfig field validation
# ---------------------------------------------------------------------------


def test_model_config_required_fields() -> None:
    cfg = ModelConfig(provider="openai", name="gpt-4o")
    assert cfg.provider == "openai"
    assert cfg.name == "gpt-4o"
    assert cfg.base_url is None
    assert cfg.api_key_env is None


def test_model_config_with_optional_fields() -> None:
    cfg = ModelConfig(
        provider="ollama",
        name="llama3.2",
        base_url="http://localhost:11434/v1",
        api_key_env="OLLAMA_KEY",
    )
    assert cfg.base_url == "http://localhost:11434/v1"
    assert cfg.api_key_env == "OLLAMA_KEY"


def test_model_config_requires_provider() -> None:
    with pytest.raises(ValidationError):
        ModelConfig(name="gpt-4o")  # type: ignore[call-arg]


def test_model_config_requires_name() -> None:
    with pytest.raises(ValidationError):
        ModelConfig(provider="openai")  # type: ignore[call-arg]


def test_model_config_json_round_trip() -> None:
    original = ModelConfig(provider="ollama", name="llama3.2")
    json_str = original.model_dump_json()
    restored = ModelConfig.model_validate_json(json_str)
    assert restored.provider == original.provider
    assert restored.name == original.name
    assert restored.base_url == original.base_url
    assert restored.api_key_env == original.api_key_env


# ---------------------------------------------------------------------------
# ant_model alias validator — colon-separated format
# ---------------------------------------------------------------------------


def test_hive_config_ant_model_colon_format() -> None:
    cfg = HiveConfig(ant_model="openai:gpt-4o")  # type: ignore[call-arg]
    assert cfg.model.provider == "openai"
    assert cfg.model.name == "gpt-4o"


def test_hive_config_ant_model_anthropic() -> None:
    cfg = HiveConfig(ant_model="anthropic:claude-3-5-sonnet-latest")  # type: ignore[call-arg]
    assert cfg.model.provider == "anthropic"
    assert cfg.model.name == "claude-3-5-sonnet-latest"


def test_hive_config_ant_model_colon_splits_on_first_only() -> None:
    # Model name itself contains colons (e.g. openrouter models with slashes are
    # not the same case, but for safety test that split is on first colon only)
    cfg = HiveConfig(ant_model="openrouter:anthropic/claude-3.5-sonnet")  # type: ignore[call-arg]
    assert cfg.model.provider == "openrouter"
    assert cfg.model.name == "anthropic/claude-3.5-sonnet"


# ---------------------------------------------------------------------------
# ant_model alias validator — no-colon fallback
# ---------------------------------------------------------------------------


def test_hive_config_ant_model_no_colon_defaults_openai() -> None:
    cfg = HiveConfig(ant_model="gpt-4o")  # type: ignore[call-arg]
    assert cfg.model.provider == "openai"
    assert cfg.model.name == "gpt-4o"


def test_hive_config_ant_model_test_string() -> None:
    """The 'test' sentinel used in test_ant_agent.py must still work."""
    cfg = HiveConfig(ant_model="test")  # type: ignore[call-arg]
    assert cfg.model.provider == "openai"
    assert cfg.model.name == "test"


# ---------------------------------------------------------------------------
# Both ant_model and model keys present: model key wins
# ---------------------------------------------------------------------------


def test_hive_config_model_wins_over_ant_model() -> None:
    cfg = HiveConfig.model_validate(
        {
            "ant_model": "openai:gpt-4o",
            "model": {"provider": "anthropic", "name": "claude-3-5-sonnet-latest"},
        }
    )
    assert cfg.model.provider == "anthropic"
    assert cfg.model.name == "claude-3-5-sonnet-latest"


# ---------------------------------------------------------------------------
# HiveConfig.model field defaults and accepts ModelConfig
# ---------------------------------------------------------------------------


def test_hive_config_default_model() -> None:
    cfg = HiveConfig()
    assert cfg.model.provider == "openai"
    assert cfg.model.name == "gpt-4o"
    assert cfg.model.base_url is None


def test_hive_config_default_via_class_method() -> None:
    cfg = HiveConfig.default()
    assert cfg.model.provider == "openai"
    assert cfg.model.name == "gpt-4o"


def test_hive_config_accepts_model_config_directly() -> None:
    model = ModelConfig(
        provider="ollama", name="llama3.2", base_url="http://localhost:11434/v1"
    )
    cfg = HiveConfig(model=model)
    assert cfg.model.provider == "ollama"
    assert cfg.model.name == "llama3.2"
    assert cfg.model.base_url == "http://localhost:11434/v1"


def test_hive_config_model_json_round_trip() -> None:
    original = HiveConfig(model=ModelConfig(provider="ollama", name="llama3.2"))
    json_str = original.model_dump_json()
    restored = HiveConfig.model_validate_json(json_str)
    assert restored.model.provider == "ollama"
    assert restored.model.name == "llama3.2"


# ---------------------------------------------------------------------------
# StigmergyConfig intensity range validator
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "min_val,max_val",
    [
        (50.0, 50.0),  # equal — violates constraint
        (80.0, 20.0),  # reversed — min > max
    ],
)
def test_intensity_range_validator_rejects_invalid(
    min_val: float, max_val: float
) -> None:
    with pytest.raises(ValidationError, match="min_intensity must be less than"):
        HiveConfig.model_validate(
            {
                "stigmergy": {
                    "min_intensity": min_val,
                    "max_intensity": max_val,
                }
            }
        )


def test_intensity_range_validator_accepts_valid() -> None:
    """A config where min_intensity < max_intensity should not raise."""
    cfg = HiveConfig.model_validate(
        {
            "stigmergy": {
                "min_intensity": 0.01,
                "max_intensity": 100.0,
            }
        }
    )
    assert cfg.stigmergy.min_intensity < cfg.stigmergy.max_intensity
