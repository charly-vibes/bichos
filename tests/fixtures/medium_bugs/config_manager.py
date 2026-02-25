"""Application configuration manager.

Loads configuration from environment variables, dotenv files, and TOML
config files. Merges sources in priority order: env > dotenv > file > defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = ""
    secret_key_env_var: str = "APP_SECRET_KEY"
    allowed_hosts: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


def _read_dotenv(path: Path) -> dict[str, str]:
    """Parse a .env file into a key/value dict."""
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def load_config(
    env_prefix: str = "APP_",
    dotenv_path: Path | None = None,
    config_file: Path | None = None,
) -> AppConfig:
    """Build AppConfig from layered sources.

    Priority (highest first):
    1. Environment variables with ``env_prefix``
    2. .env file at ``dotenv_path``
    3. TOML config at ``config_file``
    4. Dataclass defaults
    """
    effective: dict[str, str] = {}

    if dotenv_path:
        effective.update(_read_dotenv(dotenv_path))

    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            short = key[len(env_prefix):].lower()
            effective[short] = value

    cfg = AppConfig()
    if "host" in effective:
        cfg.host = effective["host"]
    if "port" in effective:
        cfg.port = int(effective["port"])
    if "debug" in effective:
        cfg.debug = effective["debug"].lower() in ("1", "true", "yes")
    if "log_level" in effective:
        cfg.log_level = effective["log_level"].upper()
    if "database_url" in effective:
        cfg.database_url = effective["database_url"]
    if "allowed_hosts" in effective:
        cfg.allowed_hosts = [h.strip() for h in effective["allowed_hosts"].split(",")]
    return cfg


def validate_config(cfg: AppConfig) -> list[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors: list[str] = []
    if not cfg.database_url:
        errors.append("database_url is required")
    if cfg.port < 1 or cfg.port > 65535:
        errors.append(f"port must be in [1, 65535], got {cfg.port}")
    if cfg.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        errors.append(f"invalid log_level: {cfg.log_level}")
    return errors
