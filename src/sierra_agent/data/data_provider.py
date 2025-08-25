"""
Data Provider Module

Clean, focused data provider for Sierra Outfitters core business operations:
- Order tracking and status
- Product catalog and recommendations
- Early risers promotion
"""

import json
import logging
import os
import random
import re
import string
from datetime import datetime, time, timedelta, timezone
from typing import Any, Dict, List, Optional

from .data_types import Order, Product, Promotion

logger = logging.getLogger(__name__)

class DataProvider:
    """Centralized data provider for Sierra Outfitters business operations."""

    def __init__(self, data_dir: str = "data") -> None:
        """Initialize the data provider with data directory."""

        self.data_dir = data_dir
        self.customer_orders: List[Dict[str, Any]] = []
        self.product_catalog: List[Dict[str, Any]] = []

        # Load data files
        self._load_customer_orders()
        self._load_product_catalog()

        logger.info("DataProvider initialized")

    def _load_customer_orders(self) -> None:
        """Load customer orders from JSON file."""
        orders_file = os.path.join(self.data_dir, "CustomerOrders.json")

        try:
            if os.path.exists(orders_file):
                with open(orders_file) as f:
                    self.customer_orders = json.load(f)

            else:

                self.customer_orders = []
        except Exception as e:

            logger.exception(f"Error loading customer orders: {e}")
            self.customer_orders = []

    def _load_product_catalog(self) -> None:
        """Load product catalog from JSON file."""
        catalog_file = os.path.join(self.data_dir, "ProductCatalog.json")

        try:
            if os.path.exists(catalog_file):
                with open(catalog_file) as f:
                    self.product_catalog = json.load(f)

            else:

                self.product_catalog = []
        except Exception as e:

            logger.exception(f"Error loading product catalog: {e}")
            self.product_catalog = []

    def get_order_status(self, email: str, order_number: str) -> Optional[Order]:
        """
        Get order status information.

        Args:
            email: Customer email address
            order_number: Order number (e.g., #W001)

        Returns:
            Order object or None if not found
        """

        for order_data in self.customer_orders:
            if (order_data["Email"].lower() == email.lower() and
                order_data["OrderNumber"].lower() == order_number.lower()):

                return Order(
                    customer_name=order_data["CustomerName"],
                    email=order_data["Email"],
                    order_number=order_data["OrderNumber"],
                    products_ordered=order_data["ProductsOrdered"],
                    status=order_data["Status"],
                    tracking_number=order_data.get("TrackingNumber")
                )


        return None

    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get product information by SKU."""
        for product_data in self.product_catalog:
            if product_data["SKU"] == sku:
                return Product(
                    product_name=product_data["ProductName"],
                    sku=product_data["SKU"],
                    inventory=product_data["Inventory"],
                    description=product_data["Description"],
                    tags=product_data.get("Tags", [])
                )
        return None

    def search_products(self, query: str, category: Optional[str] = None) -> List[Product]:
        """
        Search products by query and optional category.

        Args:
            query: Search query (searches name, description, and tags)
            category: Optional category filter

        Returns:
            List of matching Product objects
        """

        query_lower = query.lower()
        query_words = query_lower.split()
        scored_results = []

        for product_data in self.product_catalog:
            # Skip if category filter doesn't match
            if category and category.lower() not in [tag.lower() for tag in product_data.get("Tags", [])]:
                continue

            # Search in name, description, and tags with scoring
            product_name = product_data.get("ProductName", "").lower()
            description = product_data.get("Description", "").lower()
            tags = " ".join(product_data.get("Tags", [])).lower()

            score = 0
            matches_found = 0

            for word in query_words:
                word_pattern = r"\b" + re.escape(word) + r"\b"

                # Higher score for name matches (most relevant)
                if re.search(word_pattern, product_name):
                    score += 10
                    matches_found += 1
                # Medium score for tag matches
                elif re.search(word_pattern, tags):
                    score += 5
                    matches_found += 1
                # Lower score for description matches
                elif re.search(word_pattern, description):
                    score += 2
                    matches_found += 1

            # Only include if at least one word matches
            if matches_found > 0:
                product = Product(
                    product_name=product_data["ProductName"],
                    sku=product_data["SKU"],
                    inventory=product_data["Inventory"],
                    description=product_data["Description"],
                    tags=product_data.get("Tags", [])
                )
                scored_results.append((score, product))

        # Sort by score (descending) and extract products
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [product for score, product in scored_results]


    def get_products_by_category(self, category: str) -> List[Product]:
        """Get all products in a specific category."""

        results = []
        category_lower = category.lower()

        for product_data in self.product_catalog:
            if any(tag.lower() == category_lower for tag in product_data.get("Tags", [])):
                product = Product(
                    product_name=product_data["ProductName"],
                    sku=product_data["SKU"],
                    inventory=product_data["Inventory"],
                    description=product_data["Description"],
                    tags=product_data.get("Tags", [])
                )
                results.append(product)

        return results

    def is_early_risers_time(self) -> bool:
        """
        Check if current time is within Early Risers promotion hours (8:00-10:00 AM PT).

        Returns:
            True if current time is within promotion hours
        """
        # Get current time in Pacific timezone
        pacific_tz = timezone(timedelta(hours=-7))  # PST (adjust for daylight saving as needed)
        current_time = datetime.now(pacific_tz).time()

        # Check if current time is between 8:00 AM and 10:00 AM
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(10, 0)   # 10:00 AM

        return start_time <= current_time <= end_time


    def generate_discount_code(self) -> str:
        """
        Generate a unique discount code for Early Risers promotion.

        Returns:
            Unique discount code
        """
        # Generate a random 8-character code
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


    def get_early_risers_promotion(self) -> Optional[Promotion]:
        """
        Get Early Risers promotion details if currently valid.

        Returns:
            Promotion object if valid, None otherwise
        """
        if not self.is_early_risers_time():
            return None

        discount_code = self.generate_discount_code()

        return Promotion(
            name="Early Risers Promotion",
            discount_percentage=10,
            valid_hours="8:00 AM - 10:00 AM PT",
            discount_code=discount_code,
            description="Get 10% off your purchase during early morning hours!"
        )

