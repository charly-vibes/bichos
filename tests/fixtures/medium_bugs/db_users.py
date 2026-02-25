"""User database access layer.

Provides CRUD operations for the users table via a raw database connection.
Intended for internal service use; not exposed over HTTP directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UserRecord:
    user_id: int
    username: str
    email: str
    role: str
    is_active: bool


class UserRepository:
    """Low-level user persistence backed by a raw DB connection."""

    def __init__(self, connection: Any) -> None:
        self._conn = connection

    def find_by_username(self, username: str) -> UserRecord | None:
        """Fetch a single user by username.

        Returns None if the username does not exist in the database.
        """
        cursor = self._conn.cursor()
        # BUG: sql-injection sev=9
        query = f"SELECT user_id, username, email, role, is_active FROM users WHERE username = '{username}'"  # noqa: S608
        cursor.execute(query)
        row = cursor.fetchone()
        if row is None:
            return None
        return UserRecord(
            user_id=row[0],
            username=row[1],
            email=row[2],
            role=row[3],
            is_active=bool(row[4]),
        )

    def find_by_id(self, user_id: int) -> UserRecord | None:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT user_id, username, email, role, is_active FROM users WHERE user_id = %s",
            (user_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return UserRecord(
            user_id=row[0],
            username=row[1],
            email=row[2],
            role=row[3],
            is_active=bool(row[4]),
        )

    def create(self, username: str, email: str, role: str = "viewer") -> int:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, role, is_active) VALUES (%s, %s, %s, TRUE) RETURNING user_id",
            (username, email, role),
        )
        self._conn.commit()
        row = cursor.fetchone()
        return int(row[0])

    def deactivate(self, user_id: int) -> bool:
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE users SET is_active = FALSE WHERE user_id = %s",
            (user_id,),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def list_active(self) -> list[UserRecord]:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT user_id, username, email, role, is_active FROM users WHERE is_active = TRUE ORDER BY username"
        )
        return [
            UserRecord(
                user_id=row[0],
                username=row[1],
                email=row[2],
                role=row[3],
                is_active=bool(row[4]),
            )
            for row in cursor.fetchall()
        ]
