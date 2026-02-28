"""Tests for ModelConfig schema and ant_model alias validator in config.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from typer.testing import CliRunner

from bichos.cli import app
from bichos.config import HiveConfig, ModelConfig, build_model

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
# build_model() — provider dispatch and API key resolution
# ---------------------------------------------------------------------------


def test_build_model_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    cfg = ModelConfig(provider="openai", name="gpt-4o")
    result = build_model(cfg)
    assert isinstance(result, OpenAIChatModel)


def test_build_model_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
    cfg = ModelConfig(provider="anthropic", name="claude-3-5-sonnet-latest")
    result = build_model(cfg)
    assert isinstance(result, AnthropicModel)


def test_build_model_ollama() -> None:
    # Ollama uses OllamaProvider — no API key required
    cfg = ModelConfig(
        provider="ollama",
        name="llama3.2",
        base_url="http://localhost:11434/v1",
    )
    result = build_model(cfg)
    assert isinstance(result, OpenAIChatModel)


def test_build_model_openrouter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    cfg = ModelConfig(provider="openrouter", name="anthropic/claude-3.5-sonnet")
    result = build_model(cfg)
    assert isinstance(result, OpenAIChatModel)


def test_build_model_unknown_provider() -> None:
    cfg = ModelConfig(provider="unknown_provider", name="some-model")
    with pytest.raises(ValueError, match="Unknown provider"):
        build_model(cfg)


def test_build_model_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cfg = ModelConfig(provider="openai", name="gpt-4o")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_model(cfg)


# ---------------------------------------------------------------------------
# CLI --model and --base-url flags
# ---------------------------------------------------------------------------

_runner = CliRunner()


def test_cli_model_flag(tmp_path: Path) -> None:
    """--model <provider>:<name> overrides the model in HiveConfig."""
    from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats

    report = AnalysisReport(
        bugs=[],
        summary_stats=SummaryStats(
            total_functions_visited=0,
            total_bugs_found=0,
            unique_bugs=0,
            avg_confidence=0.0,
        ),
        pheromone_heatmap={},
        metadata=ReportMetadata(
            repo_path=str(tmp_path),
            agent_count=1,
            timestamp="2026-01-01T00:00:00+00:00",
            total_tokens=0,
        ),
    )

    captured: list[HiveConfig] = []

    async def _mock_run_hive(repo_path: Path, config: HiveConfig) -> AnalysisReport:
        captured.append(config)
        return report

    with patch("bichos.cli.run_hive", new=_mock_run_hive):
        result = _runner.invoke(
            app, ["analyze", str(tmp_path), "--model", "anthropic:claude-3-5-sonnet"]
        )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    assert captured[0].model.provider == "anthropic"
    assert captured[0].model.name == "claude-3-5-sonnet"


def test_cli_base_url_flag(tmp_path: Path) -> None:
    """--base-url overrides the base_url in the model config."""
    from bichos.hive.models import AnalysisReport, ReportMetadata, SummaryStats

    report = AnalysisReport(
        bugs=[],
        summary_stats=SummaryStats(
            total_functions_visited=0,
            total_bugs_found=0,
            unique_bugs=0,
            avg_confidence=0.0,
        ),
        pheromone_heatmap={},
        metadata=ReportMetadata(
            repo_path=str(tmp_path),
            agent_count=1,
            timestamp="2026-01-01T00:00:00+00:00",
            total_tokens=0,
        ),
    )

    captured: list[HiveConfig] = []

    async def _mock_run_hive(repo_path: Path, config: HiveConfig) -> AnalysisReport:
        captured.append(config)
        return report

    with patch("bichos.cli.run_hive", new=_mock_run_hive):
        result = _runner.invoke(
            app,
            [
                "analyze",
                str(tmp_path),
                "--base-url",
                "http://localhost:11434/v1",
            ],
        )

    assert result.exit_code == 0, result.output
    assert len(captured) == 1
    assert captured[0].model.base_url == "http://localhost:11434/v1"


def test_cli_model_invalid_format(tmp_path: Path) -> None:
    """--model without a colon must cause a non-zero exit."""
    result = _runner.invoke(app, ["analyze", str(tmp_path), "--model", "badformat"])
    assert result.exit_code != 0
