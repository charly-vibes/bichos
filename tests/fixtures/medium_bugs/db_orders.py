"""Order database access layer.

Provides query helpers for the orders table. Used by the order management
service and the reporting pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class OrderRecord:
    order_id: int
    customer_id: int
    status: str
    total_amount: float
    created_at: datetime


class OrderRepository:
    """Persistence layer for customer orders."""

    def __init__(self, connection: Any) -> None:
        self._conn = connection

    def find_by_status(self, status: str) -> list[OrderRecord]:
        """Return all orders matching the given status string.

        Status values: 'pending', 'processing', 'shipped', 'cancelled'.
        """
        cursor = self._conn.cursor()
        # BUG: sql-injection sev=9
        query = f"SELECT order_id, customer_id, status, total_amount, created_at FROM orders WHERE status = '{status}'"  # noqa: S608
        cursor.execute(query)
        return [
            OrderRecord(
                order_id=row[0],
                customer_id=row[1],
                status=row[2],
                total_amount=float(row[3]),
                created_at=row[4],
            )
            for row in cursor.fetchall()
        ]

    def find_by_id(self, order_id: int) -> OrderRecord | None:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT order_id, customer_id, status, total_amount, created_at FROM orders WHERE order_id = %s",
            (order_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return OrderRecord(
            order_id=row[0],
            customer_id=row[1],
            status=row[2],
            total_amount=float(row[3]),
            created_at=row[4],
        )

    def update_status(self, order_id: int, new_status: str) -> bool:
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = %s WHERE order_id = %s",
            (new_status, order_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def create(self, customer_id: int, total_amount: float) -> int:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO orders (customer_id, status, total_amount) VALUES (%s, 'pending', %s) RETURNING order_id",
            (customer_id, total_amount),
        )
        self._conn.commit()
        row = cursor.fetchone()
        return int(row[0])

    def delete_old(self, before: datetime) -> int:
        cursor = self._conn.cursor()
        cursor.execute(
            "DELETE FROM orders WHERE created_at < %s AND status = 'cancelled'",
            (before,),
        )
        self._conn.commit()
        return cursor.rowcount
