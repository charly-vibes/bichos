"""Date and time utility functions.

Collection of helpers for parsing, formatting, and manipulating dates.
All public functions are pure (no side effects) and timezone-aware where
relevant.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
_DISPLAY_FORMAT = "%d %b %Y"
_SHORT_FORMAT = "%Y-%m-%d"


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(tz=timezone.utc)


def parse_iso(text: str) -> datetime:
    """Parse an ISO-8601 string into a UTC datetime.

    Accepts both naive ('2024-01-15T12:00:00') and offset-aware forms.
    Raises ValueError on malformed input.
    """
    text = text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).astimezone(timezone.utc)
    except ValueError as exc:
        raise ValueError(f"Cannot parse ISO date: {text!r}") from exc


def format_display(dt: datetime | date) -> str:
    """Format a date/datetime for human display (e.g. '15 Jan 2024')."""
    if isinstance(dt, datetime):
        return dt.strftime(_DISPLAY_FORMAT)
    return dt.strftime(_DISPLAY_FORMAT)


def format_short(dt: datetime | date) -> str:
    """Return a compact YYYY-MM-DD string."""
    if isinstance(dt, datetime):
        return dt.strftime(_SHORT_FORMAT)
    return dt.strftime(_SHORT_FORMAT)


def start_of_day(dt: datetime) -> datetime:
    """Return midnight of the same calendar day in dt's timezone."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    """Return 23:59:59.999999 of the same calendar day."""
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def date_range(start: date, end: date) -> list[date]:
    """Return every calendar date from start up to and including end."""
    if end < start:
        return []
    delta = (end - start).days
    return [start + timedelta(days=i) for i in range(delta + 1)]


def business_days_between(start: date, end: date) -> int:
    """Count weekdays (Mon–Fri) between start and end inclusive."""
    if end < start:
        return 0
    total = 0
    current = start
    while current <= end:
        if current.weekday() < 5:  # 0=Mon … 4=Fri
            total += 1
        current += timedelta(days=1)
    return total


def age_in_years(birth_date: date, reference: date | None = None) -> int:
    """Return full years elapsed since birth_date as of reference (today if None)."""
    ref = reference or date.today()
    years = ref.year - birth_date.year
    if (ref.month, ref.day) < (birth_date.month, birth_date.day):
        years -= 1
    return max(0, years)
