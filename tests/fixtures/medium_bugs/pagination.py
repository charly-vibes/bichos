"""Cursor-based and offset-based pagination helpers.

Provides generic page/cursor abstractions that can be applied to any
list of items or query builder. Framework-agnostic.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


@dataclass
class CursorPage(Generic[T]):
    items: list[T]
    next_cursor: str | None
    prev_cursor: str | None
    has_more: bool


def paginate(items: list[T], page: int, page_size: int) -> Page[T]:
    """Slice items for the given 1-indexed page and page_size."""
    if page < 1:
        raise ValueError(f"page must be >= 1, got {page}")
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    start = (page - 1) * page_size
    end = start + page_size
    return Page(
        items=items[start:end],
        total=len(items),
        page=page,
        page_size=page_size,
    )


def encode_cursor(offset: int, sort_field: str = "id") -> str:
    """Encode an integer offset into an opaque cursor string."""
    payload = json.dumps({"offset": offset, "sort": sort_field})
    return base64.urlsafe_b64encode(payload.encode()).decode()


def decode_cursor(cursor: str) -> dict[str, str | int]:
    """Decode a cursor string back to its payload dict."""
    try:
        payload = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(payload)  # type: ignore[no-any-return]
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid cursor: {cursor!r}") from exc


def cursor_paginate(items: list[T], cursor: str | None, page_size: int) -> CursorPage[T]:
    """Return a cursor-based page of items."""
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1, got {page_size}")
    offset = 0
    if cursor:
        decoded = decode_cursor(cursor)
        offset = int(decoded.get("offset", 0))
    slice_ = items[offset : offset + page_size + 1]
    has_more = len(slice_) > page_size
    page_items = slice_[:page_size]
    next_cur = encode_cursor(offset + page_size) if has_more else None
    prev_cur = encode_cursor(max(0, offset - page_size)) if offset > 0 else None
    return CursorPage(
        items=page_items,
        next_cursor=next_cur,
        prev_cursor=prev_cur,
        has_more=has_more,
    )
