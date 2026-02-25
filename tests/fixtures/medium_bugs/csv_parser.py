"""CSV parsing utilities with type coercion and validation.

Provides a schema-driven CSV reader that converts raw string values into
typed Python objects and raises descriptive errors on malformed input.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Any


@dataclass
class ColumnSpec:
    name: str
    dtype: type
    required: bool = True
    default: Any = None


class CsvParseError(ValueError):
    """Raised when a CSV row cannot be coerced to the declared schema."""

    def __init__(self, row: int, column: str, message: str) -> None:
        super().__init__(f"Row {row}, column '{column}': {message}")
        self.row = row
        self.column = column


class CsvParser:
    """Schema-driven CSV parser with type coercion."""

    def __init__(self, schema: list[ColumnSpec], delimiter: str = ",") -> None:
        self._schema = schema
        self._delimiter = delimiter

    def parse_string(self, text: str) -> list[dict[str, Any]]:
        """Parse a CSV string and return a list of typed dicts."""
        reader = csv.DictReader(io.StringIO(text), delimiter=self._delimiter)
        return [self._coerce_row(i + 2, row) for i, row in enumerate(reader)]

    def parse_file(self, path: str) -> list[dict[str, Any]]:
        """Parse a CSV file by path."""
        with open(path, newline="", encoding="utf-8") as fh:  # noqa: PTH123
            reader = csv.DictReader(fh, delimiter=self._delimiter)
            return [self._coerce_row(i + 2, row) for i, row in enumerate(reader)]

    def _coerce_row(self, row_num: int, raw: dict[str, str | None]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for spec in self._schema:
            raw_val = raw.get(spec.name)
            if raw_val is None or raw_val.strip() == "":
                if spec.required:
                    raise CsvParseError(row_num, spec.name, "required column is missing or empty")
                result[spec.name] = spec.default
                continue
            try:
                result[spec.name] = spec.dtype(raw_val.strip())
            except (ValueError, TypeError) as exc:
                raise CsvParseError(
                    row_num,
                    spec.name,
                    f"cannot coerce {raw_val!r} to {spec.dtype.__name__}: {exc}",
                ) from exc
        return result

    def validate_headers(self, text: str) -> list[str]:
        """Return a list of missing required column names."""
        reader = csv.DictReader(io.StringIO(text), delimiter=self._delimiter)
        headers = set(reader.fieldnames or [])
        return [
            spec.name
            for spec in self._schema
            if spec.required and spec.name not in headers
        ]
