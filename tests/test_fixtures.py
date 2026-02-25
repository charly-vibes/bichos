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


# ---------------------------------------------------------------------------
# MANIFEST.md tests
# ---------------------------------------------------------------------------

MANIFEST_PATH = Path(__file__).parent / "fixtures" / "MANIFEST.md"
FIXTURES_ROOT = Path(__file__).parent / "fixtures"

# Pattern matching a markdown table row with a pipe-separated file path
MANIFEST_ROW_RE = re.compile(r"^\|\s*([\w_/]+\.py)\s*\|", re.MULTILINE)


def _parse_manifest_rows(content: str) -> list[str]:
    """Return list of file paths from all table rows in MANIFEST.md."""
    return MANIFEST_ROW_RE.findall(content)


def test_manifest_exists() -> None:
    assert MANIFEST_PATH.exists(), f"MANIFEST.md not found at {MANIFEST_PATH}"


def test_manifest_has_required_columns() -> None:
    content = MANIFEST_PATH.read_text()
    # Check that a header row with all required columns is present
    assert "| File" in content or "| file" in content.lower(), (
        "MANIFEST.md missing 'File' column header"
    )
    assert "Line" in content, "MANIFEST.md missing 'Line' column header"
    assert "Function" in content, "MANIFEST.md missing 'Function' column header"
    assert "Bug Type" in content, "MANIFEST.md missing 'Bug Type' column header"
    assert "Severity" in content, "MANIFEST.md missing 'Severity' column header"
    assert "Description" in content, "MANIFEST.md missing 'Description' column header"


def test_manifest_has_exactly_4_simple_bugs_rows() -> None:
    content = MANIFEST_PATH.read_text()
    simple_rows = re.findall(r"^\|\s*simple_bugs/\S+\.py", content, re.MULTILINE)
    assert len(simple_rows) == 4, (
        f"Expected 4 rows for simple_bugs/, got {len(simple_rows)}: {simple_rows}"
    )


def test_manifest_has_exactly_10_medium_bugs_rows() -> None:
    content = MANIFEST_PATH.read_text()
    medium_rows = re.findall(r"^\|\s*medium_bugs/\S+\.py", content, re.MULTILINE)
    assert len(medium_rows) == 10, (
        f"Expected 10 rows for medium_bugs/, got {len(medium_rows)}: {medium_rows}"
    )


def test_manifest_contains_calculator_division_by_zero() -> None:
    """Spot-check: calculator.py division-by-zero entry is present with sev=8."""
    content = MANIFEST_PATH.read_text()
    assert "simple_bugs/calculator.py" in content, (
        "MANIFEST.md missing simple_bugs/calculator.py entry"
    )
    assert "division-by-zero" in content, (
        "MANIFEST.md missing division-by-zero bug type"
    )
    # The row for calculator.py must contain sev 8
    for line in content.splitlines():
        if "simple_bugs/calculator.py" in line:
            assert "8" in line, f"calculator.py row missing severity 8: {line!r}"
            break


def test_manifest_contains_config_loader_hardcoded_creds() -> None:
    """Spot-check: config_loader.py hardcoded-creds sev=9."""
    content = MANIFEST_PATH.read_text()
    assert "simple_bugs/config_loader.py" in content
    assert "hardcoded-creds" in content


def test_manifest_contains_db_users_sql_injection() -> None:
    """Spot-check: db_users.py sql-injection sev=9."""
    content = MANIFEST_PATH.read_text()
    assert "medium_bugs/db_users.py" in content
    assert "sql-injection" in content


def test_manifest_contains_metrics_collector_unused_import() -> None:
    """Spot-check: metrics_collector.py unused-import sev=2."""
    content = MANIFEST_PATH.read_text()
    assert "medium_bugs/metrics_collector.py" in content
    assert "unused-import" in content


def test_manifest_entries_match_actual_bug_markers() -> None:
    """Verify each file listed in MANIFEST.md actually has a BUG marker."""
    content = MANIFEST_PATH.read_text()
    file_paths = re.findall(
        r"^\|\s*((?:simple_bugs|medium_bugs)/\S+\.py)", content, re.MULTILINE
    )
    missing: list[str] = []
    for rel_path in file_paths:
        abs_path = FIXTURES_ROOT / rel_path
        if not abs_path.exists():
            missing.append(f"{rel_path}: file not found")
            continue
        file_content = abs_path.read_text()
        if "# BUG" not in file_content and "#BUG" not in file_content:
            missing.append(f"{rel_path}: no BUG marker found in source")
    assert not missing, (
        "MANIFEST.md entries without matching BUG markers:\n" + "\n".join(missing)
    )
