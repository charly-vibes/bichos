# bichos — Bio-Mimetic Swarm Intelligence Framework

# List available recipes
default:
    @just --list

# Install dependencies
install:
    uv sync

# Install with dev dependencies
install-dev:
    uv sync --all-extras

# Format code
fmt:
    uv run ruff format .
    uv run ruff check --fix .

# Lint (check only, no fixes)
lint:
    uv run ruff check .
    uv run ruff format --check .

# Type check
typecheck:
    uv run mypy src/

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=bichos --cov-report=html

# Run all quality checks
check: lint typecheck test

# Validate the OpenSpec proposal (strict)
validate:
    openspec validate add-entomological-framework --strict

# Show OpenSpec proposal overview
spec:
    openspec show add-entomological-framework

# Set up dev environment (deps + git hooks)
setup:
    uv sync --all-extras
    lefthook install

# Install git hooks via lefthook
hooks:
    lefthook install

# Run git hooks against all files
hooks-run:
    lefthook run pre-commit

# Show wai project status
status:
    wai status

# Show ready beads issues
ready:
    bd ready
