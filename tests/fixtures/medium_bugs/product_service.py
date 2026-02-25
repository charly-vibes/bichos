"""Product catalogue service.

Provides lookup and mutation operations for the product catalogue.
Integrates with the product repository and the pricing engine.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Product:
    product_id: int
    sku: str
    name: str
    price_cents: int
    stock: int
    category: str


class ProductRepository:
    """In-memory stub repository used in tests and staging."""

    def __init__(self) -> None:
        self._products: dict[int, Product] = {}

    def add(self, product: Product) -> None:
        self._products[product.product_id] = product

    def find_by_sku(self, sku: str) -> Product | None:
        return next((p for p in self._products.values() if p.sku == sku), None)

    def find_by_id(self, product_id: int) -> Product | None:
        return self._products.get(product_id)


class ProductService:
    """Domain service for product catalogue operations."""

    def __init__(self, repo: ProductRepository) -> None:
        self._repo = repo

    def get_price(self, sku: str) -> int:
        """Return price in cents for the product with the given SKU.

        Raises KeyError if the SKU is not found.
        """
        product = self._repo.find_by_sku(sku)
        # BUG: missing-None-check sev=7
        return product.price_cents  # AttributeError if SKU not found

    def apply_discount(self, sku: str, percent: float) -> int:
        """Apply a percentage discount and return the new price in cents."""
        if not 0.0 <= percent <= 100.0:
            raise ValueError(f"Discount percent must be in [0, 100], got {percent}")
        product = self._repo.find_by_sku(sku)
        if product is None:
            raise KeyError(f"SKU not found: {sku}")
        new_price = int(product.price_cents * (1.0 - percent / 100.0))
        product.price_cents = max(0, new_price)
        return product.price_cents

    def adjust_stock(self, product_id: int, delta: int) -> int:
        """Adjust stock by delta (positive = restock, negative = sale).

        Returns the new stock level or raises ValueError on negative result.
        """
        product = self._repo.find_by_id(product_id)
        if product is None:
            raise KeyError(f"Product ID not found: {product_id}")
        new_stock = product.stock + delta
        if new_stock < 0:
            raise ValueError(
                f"Insufficient stock for product {product_id}: "
                f"have {product.stock}, requested {-delta}"
            )
        product.stock = new_stock
        return product.stock

    def search(self, query: str, category: str | None = None) -> list[Product]:
        """Full-text search stub — filters by name substring."""
        all_products = list(self._repo._products.values())  # noqa: SLF001
        results = [p for p in all_products if query.lower() in p.name.lower()]
        if category:
            results = [p for p in results if p.category == category]
        return sorted(results, key=lambda p: p.name)

    def to_dict(self, product: Product) -> dict[str, Any]:
        return {
            "product_id": product.product_id,
            "sku": product.sku,
            "name": product.name,
            "price_cents": product.price_cents,
            "stock": product.stock,
            "category": product.category,
        }
