"""Simple synchronous event bus — clean module (no planted bugs)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

EventHandler = Callable[..., None]


class EventBus:
    """Publish/subscribe event bus."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        """Remove a previously registered handler."""
        handlers = self._handlers.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: str, **kwargs: object) -> None:
        """Notify all handlers subscribed to event."""
        for handler in list(self._handlers.get(event, [])):
            handler(**kwargs)

    def handler_count(self, event: str) -> int:
        return len(self._handlers.get(event, []))
