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
import string
from datetime import datetime, timezone, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DataProvider:
    """Centralized data provider for Sierra Outfitters business operations."""

    def __init__(self, data_dir: str = "data") -> None:
        """Initialize the data provider with data directory."""
        print("📊 [DATA_PROVIDER] Initializing DataProvider...")
        
        self.data_dir = data_dir
        self.customer_orders: List[Dict[str, Any]] = []
        self.product_catalog: List[Dict[str, Any]] = []
        
        # Load data files
        self._load_customer_orders()
        self._load_product_catalog()
        
        print("✅ [DATA_PROVIDER] DataProvider initialized successfully")
        logger.info("DataProvider initialized")

    def _load_customer_orders(self) -> None:
        """Load customer orders from JSON file."""
        orders_file = os.path.join(self.data_dir, "CustomerOrders.json")
        
        try:
            if os.path.exists(orders_file):
                with open(orders_file, 'r') as f:
                    self.customer_orders = json.load(f)
                print(f"📦 [DATA_PROVIDER] Loaded {len(self.customer_orders)} customer orders")
            else:
                print(f"⚠️ [DATA_PROVIDER] Customer orders file not found: {orders_file}")
                self.customer_orders = []
        except Exception as e:
            print(f"❌ [DATA_PROVIDER] Error loading customer orders: {e}")
            logger.error(f"Error loading customer orders: {e}")
            self.customer_orders = []

    def _load_product_catalog(self) -> None:
        """Load product catalog from JSON file."""
        catalog_file = os.path.join(self.data_dir, "ProductCatalog.json")
        
        try:
            if os.path.exists(catalog_file):
                with open(catalog_file, 'r') as f:
                    self.product_catalog = json.load(f)
                print(f"🏷️ [DATA_PROVIDER] Loaded {len(self.product_catalog)} products")
            else:
                print(f"⚠️ [DATA_PROVIDER] Product catalog file not found: {catalog_file}")
                self.product_catalog = []
        except Exception as e:
            print(f"❌ [DATA_PROVIDER] Error loading product catalog: {e}")
            logger.error(f"Error loading product catalog: {e}")
            self.product_catalog = []

    def get_order_status(self, email: str, order_number: str) -> Optional[Dict[str, Any]]:
        """
        Get order status and tracking information.
        
        Args:
            email: Customer email address
            order_number: Order number (e.g., #W001)
            
        Returns:
            Order information with status and tracking, or None if not found
        """
        print(f"🔍 [DATA_PROVIDER] Looking up order: {order_number} for {email}")
        
        for order in self.customer_orders:
            if (order["Email"].lower() == email.lower() and 
                order["OrderNumber"] == order_number):
                
                # Get product details for the order
                products = []
                for sku in order["ProductsOrdered"]:
                    product = self.get_product_by_sku(sku)
                    if product:
                        products.append(product)
                
                result: Dict[str, Any] = {
                    "order_info": order,
                    "products": products,
                    "tracking_url": None
                }
                
                # Generate tracking URL if tracking number exists
                if order.get("TrackingNumber"):
                    tracking_url = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={order['TrackingNumber']}"
                    result["tracking_url"] = tracking_url
                
                print(f"✅ [DATA_PROVIDER] Found order: {order_number}")
                return result
        
        print(f"❌ [DATA_PROVIDER] Order not found: {order_number} for {email}")
        return None

    def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product information by SKU."""
        for product in self.product_catalog:
            if product["SKU"] == sku:
                return product
        return None

    def search_products(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search products by query and optional category.
        
        Args:
            query: Search query (searches name, description, and tags)
            category: Optional category filter
            
        Returns:
            List of matching products
        """
        print(f"🔍 [DATA_PROVIDER] Searching products: '{query}' category: {category}")
        
        query_lower = query.lower()
        results = []
        
        for product in self.product_catalog:
            # Skip if category filter doesn't match
            if category and category.lower() not in [tag.lower() for tag in product.get("Tags", [])]:
                continue
            
            # Search in name, description, and tags
            searchable_text = (
                product.get("ProductName", "") + " " +
                product.get("Description", "") + " " +
                " ".join(product.get("Tags", []))
            ).lower()
            
            if query_lower in searchable_text:
                results.append(product)
        
        print(f"✅ [DATA_PROVIDER] Found {len(results)} matching products")
        return results

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all products in a specific category."""
        print(f"🏷️ [DATA_PROVIDER] Getting products for category: {category}")
        
        results = []
        category_lower = category.lower()
        
        for product in self.product_catalog:
            if any(tag.lower() == category_lower for tag in product.get("Tags", [])):
                results.append(product)
        
        print(f"✅ [DATA_PROVIDER] Found {len(results)} products in category: {category}")
        return results

    def is_early_risers_time(self) -> bool:
        """
        Check if current time is within Early Risers promotion hours (8:00-10:00 AM PT).
        
        Returns:
            True if current time is within promotion hours
        """
        # Get current time in Pacific timezone
        pacific_tz = timezone(timedelta(hours=-8))  # PST (adjust for daylight saving as needed)
        current_time = datetime.now(pacific_tz).time()
        
        # Check if current time is between 8:00 AM and 10:00 AM
        start_time = time(8, 0)  # 8:00 AM
        end_time = time(10, 0)   # 10:00 AM
        
        is_valid = start_time <= current_time <= end_time
        
        print(f"⏰ [DATA_PROVIDER] Early Risers check: {current_time.strftime('%H:%M')} PT - {'✅ Valid' if is_valid else '❌ Invalid'}")
        return is_valid

    def generate_discount_code(self) -> str:
        """
        Generate a unique discount code for Early Risers promotion.
        
        Returns:
            Unique discount code
        """
        # Generate a random 8-character code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        print(f"🎫 [DATA_PROVIDER] Generated discount code: {code}")
        return code

    def get_early_risers_promotion(self) -> Optional[Dict[str, Any]]:
        """
        Get Early Risers promotion details if currently valid.
        
        Returns:
            Promotion details if valid, None otherwise
        """
        if not self.is_early_risers_time():
            return None
        
        discount_code = self.generate_discount_code()
        
        promotion = {
            "name": "Early Risers Promotion",
            "discount_percentage": 10,
            "valid_hours": "8:00 AM - 10:00 AM PT",
            "discount_code": discount_code,
            "description": "Get 10% off your purchase during early morning hours!"
        }
        
        print(f"🎉 [DATA_PROVIDER] Early Risers promotion active: {discount_code}")
        return promotion
