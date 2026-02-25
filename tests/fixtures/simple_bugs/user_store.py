"""In-memory user store.

BUG #2: get_user() returns None silently when user not found, but callers
access the return value without checking — any caller doing
    store.get_user(id).name
will raise AttributeError on missing users.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str
    email: str
    active: bool = True


class UserStore:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}

    def add(self, user: User) -> None:
        self._users[user.id] = user

    def get_user(self, user_id: int) -> User | None:
        # BUG: returns None without documentation; callers assume non-None
        return self._users.get(user_id)

    def list_active(self) -> list[User]:
        return [u for u in self._users.values() if u.active]

    def deactivate(self, user_id: int) -> None:
        user = self.get_user(user_id)
        # BUG propagation: AttributeError if user_id not found
        user.active = False  # type: ignore[union-attr]

    def count(self) -> int:
        return len(self._users)
