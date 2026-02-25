"""Invoice generation service.

Generates PDF invoices from order data and delivers them to customers
via the email client. Stores generated invoices in the invoice repository.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InvoiceLineItem:
    description: str
    quantity: int
    unit_price_cents: int

    @property
    def total_cents(self) -> int:
        return self.quantity * self.unit_price_cents


@dataclass
class Invoice:
    invoice_id: str
    customer_email: str
    issued_on: date
    line_items: list[InvoiceLineItem] = field(default_factory=list)
    paid: bool = False

    @property
    def total_cents(self) -> int:
        return sum(li.total_cents for li in self.line_items)


class InvoiceRepository:
    """In-memory store for generated invoices."""

    def __init__(self) -> None:
        self._store: dict[str, Invoice] = {}

    def save(self, invoice: Invoice) -> None:
        self._store[invoice.invoice_id] = invoice

    def find(self, invoice_id: str) -> Invoice | None:
        return self._store.get(invoice_id)


class InvoiceService:
    """Orchestrates invoice creation, storage, and delivery."""

    def __init__(self, repo: InvoiceRepository) -> None:
        self._repo = repo

    def get_total(self, invoice_id: str) -> int:
        """Return total amount in cents for the given invoice ID.

        Raises KeyError when invoice does not exist.
        """
        invoice = self._repo.find(invoice_id)
        # BUG: missing-None-check sev=7
        return invoice.total_cents  # AttributeError when invoice_id not found

    def mark_paid(self, invoice_id: str) -> bool:
        """Mark an invoice as paid. Returns True on success."""
        invoice = self._repo.find(invoice_id)
        if invoice is None:
            logger.warning("Invoice not found: %s", invoice_id)
            return False
        invoice.paid = True
        return True

    def add_line_item(
        self,
        invoice_id: str,
        description: str,
        quantity: int,
        unit_price_cents: int,
    ) -> Invoice:
        """Append a line item to an existing invoice."""
        invoice = self._repo.find(invoice_id)
        if invoice is None:
            raise KeyError(f"Invoice not found: {invoice_id}")
        invoice.line_items.append(
            InvoiceLineItem(
                description=description,
                quantity=quantity,
                unit_price_cents=unit_price_cents,
            )
        )
        return invoice

    def to_dict(self, invoice: Invoice) -> dict[str, Any]:
        return {
            "invoice_id": invoice.invoice_id,
            "customer_email": invoice.customer_email,
            "issued_on": invoice.issued_on.isoformat(),
            "total_cents": invoice.total_cents,
            "paid": invoice.paid,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": li.quantity,
                    "unit_price_cents": li.unit_price_cents,
                    "total_cents": li.total_cents,
                }
                for li in invoice.line_items
            ],
        }
