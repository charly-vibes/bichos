"""Tests that verify tests/fixtures/medium_bugs/ contents.

Checks:
- Exactly 20 .py files exist
- All files parse as valid Python (ast.parse)
- Each file has >= 30 lines of code
- Bug inventory markers are correct:
    2 × sql-injection sev=9
    2 × hardcoded-creds sev=9
    2 × race-condition sev=8
    2 × missing-None-check sev=7
    1 × bare-except sev=5
    1 × unused-import sev=2
    10 clean files (no BUG: marker)
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "medium_bugs"

# Pattern: "# BUG: <type> sev=<N>"
BUG_MARKER_RE = re.compile(r"#\s*BUG:\s*(\S+)\s+sev=(\d+)")


def _all_py_files() -> list[Path]:
    return sorted(FIXTURES_DIR.glob("*.py"))


def _collect_bugs(content: str) -> list[tuple[str, int]]:
    """Return list of (bug_type, severity) tuples found in content."""
    bugs = []
    for m in BUG_MARKER_RE.finditer(content):
        bugs.append((m.group(1), int(m.group(2))))
    return bugs


# ---------------------------------------------------------------------------
# File count
# ---------------------------------------------------------------------------


def test_exactly_20_py_files() -> None:
    files = _all_py_files()
    assert len(files) == 20, (
        f"Expected 20 .py files in {FIXTURES_DIR}, found {len(files)}:\n"
        + "\n".join(f.name for f in files)
    )


# ---------------------------------------------------------------------------
# Parse validity
# ---------------------------------------------------------------------------


def test_all_files_are_valid_python() -> None:
    errors: list[str] = []
    for path in _all_py_files():
        try:
            ast.parse(path.read_text())
        except SyntaxError as exc:
            errors.append(f"{path.name}: {exc}")
    assert not errors, "Syntax errors found:\n" + "\n".join(errors)


# ---------------------------------------------------------------------------
# Minimum LOC
# ---------------------------------------------------------------------------


def test_all_files_have_at_least_30_lines() -> None:
    short: list[str] = []
    for path in _all_py_files():
        lines = path.read_text().splitlines()
        if len(lines) < 30:
            short.append(f"{path.name}: {len(lines)} lines")
    assert not short, "Files with fewer than 30 lines:\n" + "\n".join(short)


# ---------------------------------------------------------------------------
# Bug inventory — totals
# ---------------------------------------------------------------------------


def _all_bugs() -> list[tuple[str, int, str]]:
    """Return (bug_type, severity, filename) for every marker across all files."""
    result = []
    for path in _all_py_files():
        for bug_type, sev in _collect_bugs(path.read_text()):
            result.append((bug_type, sev, path.name))
    return result


def test_exactly_2_sql_injection_sev9() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "sql-injection" and sev == 9
    ]
    assert len(matches) == 2, (
        f"Expected 2 sql-injection sev=9, got {len(matches)}: {matches}"
    )


def test_exactly_2_hardcoded_creds_sev9() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "hardcoded-creds" and sev == 9
    ]
    assert len(matches) == 2, (
        f"Expected 2 hardcoded-creds sev=9, got {len(matches)}: {matches}"
    )


def test_exactly_2_race_condition_sev8() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "race-condition" and sev == 8
    ]
    assert len(matches) == 2, (
        f"Expected 2 race-condition sev=8, got {len(matches)}: {matches}"
    )


def test_exactly_2_missing_none_check_sev7() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "missing-None-check" and sev == 7
    ]
    assert len(matches) == 2, (
        f"Expected 2 missing-None-check sev=7, got {len(matches)}: {matches}"
    )


def test_exactly_1_bare_except_sev5() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "bare-except" and sev == 5
    ]
    assert len(matches) == 1, (
        f"Expected 1 bare-except sev=5, got {len(matches)}: {matches}"
    )


def test_exactly_1_unused_import_sev2() -> None:
    matches = [
        (bt, sev, fname)
        for bt, sev, fname in _all_bugs()
        if bt == "unused-import" and sev == 2
    ]
    assert len(matches) == 1, (
        f"Expected 1 unused-import sev=2, got {len(matches)}: {matches}"
    )


def test_exactly_10_clean_files() -> None:
    clean = []
    for path in _all_py_files():
        bugs = _collect_bugs(path.read_text())
        if not bugs:
            clean.append(path.name)
    assert len(clean) == 10, (
        f"Expected 10 clean files (no BUG: markers), got {len(clean)}: {clean}"
    )


# ---------------------------------------------------------------------------
# Exactly one bug per bug file (no double-counting)
# ---------------------------------------------------------------------------


def test_each_bug_file_has_exactly_one_bug_marker() -> None:
    multi: list[str] = []
    for path in _all_py_files():
        bugs = _collect_bugs(path.read_text())
        if len(bugs) > 1:
            multi.append(f"{path.name}: {bugs}")
    assert not multi, "Files with more than one BUG: marker:\n" + "\n".join(multi)
