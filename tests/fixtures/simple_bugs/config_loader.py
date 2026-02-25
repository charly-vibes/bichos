"""Config loader from environment variables.

BUG #3: load_config() reads SECRET_KEY from environment but falls back to a
hardcoded default string "changeme" — running in production with the default
secret key is a security vulnerability.
"""

from __future__ import annotations

import os


def load_config() -> dict[str, str]:
    return {
        "host": os.environ.get("APP_HOST", "localhost"),
        "port": os.environ.get("APP_PORT", "8080"),
        # BUG: hardcoded fallback for a secret — security vulnerability
        "secret_key": os.environ.get("SECRET_KEY", "changeme"),
        "debug": os.environ.get("DEBUG", "false"),
    }


def get_database_url() -> str:
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    name = os.environ.get("DB_NAME", "app")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"
