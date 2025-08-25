"""
Product Catalog Tools - Refined for actual ProductCatalog.json

These tools are specifically designed to work with the Sierra Outfitters product catalog
and provide intelligent recommendations based on the actual inventory.
"""

from typing import List, Dict, Any, Optional
from sierra_agent.data.data_provider import DataProvider
from sierra_agent.data.data_types import ToolResult
from sierra_agent.utils.branding import Branding
from .base_tool import BaseTool, ToolParameter


class ProductCatalogTool(BaseTool):
    """Browse and search the complete Sierra Outfitters product catalog."""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
    
    @property
    def tool_name(self) -> str:
        return "browse_catalog"
    
    @property
    def description(self) -> str:
        return "Browse Sierra Outfitters product catalog by category or search terms"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="search_query",
                param_type=str,
                required=False,
                description="Search for specific products (name, description, or category)",
                default=None
            ),
            ToolParameter(
                name="category_filter",
                param_type=str,
                required=False,
                description="Filter by category: Adventure, High-Tech, Food & Beverage, Fashion, Home Decor, etc.",
                default=None
            ),
            ToolParameter(
                name="limit",
                param_type=int,
                required=False,
                description="Maximum products to return",
                default=5,
                validation_rules={"min_value": 1, "max_value": 15}
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        """Browse the catalog with search and filtering."""
        search_query = kwargs.get("search_query")
        category_filter = kwargs.get("category_filter")
        limit = kwargs.get("limit", 5)
        
        products = []
        
        if search_query:
            # Search by query
            products = self.data_provider.search_products(search_query)
            if category_filter:
                # Further filter by category
                products = [p for p in products 
                          if category_filter.lower() in [tag.lower() for tag in p.tags]]
        elif category_filter:
            # Filter by category only
            products = self.data_provider.get_products_by_category(category_filter)
        else:
            # Show popular/featured products
            products = self.data_provider.search_products("Adventure")
            if len(products) < limit:
                additional = self.data_provider.search_products("High-Tech")
                for product in additional:
                    if product.sku not in [p.sku for p in products]:
                        products.append(product)
        
        if not products:
            return ToolResult(
                success=True,
                data={
                    "message": "No products found matching your criteria. Let me show you some popular adventure gear! 🏔️",
                    "suggestions": ["Try searching for: backpack, adventure, high-tech, food, fashion"],
                    "products": []
                },
                error=None
            )
        
        # Limit results and format
        limited_products = products[:limit]
        
        return ToolResult(
            success=True,
            data={
                "products": limited_products,
                "total_found": len(products),
                "showing": len(limited_products),
                "search_query": search_query,
                "category_filter": category_filter,
                "message": f"Found {len(products)} products! Here are the top {len(limited_products)}:"
            },
            error=None
        )


class SmartRecommendationTool(BaseTool):
    """Intelligent product recommendations based on customer needs and context."""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
    
    @property
    def tool_name(self) -> str:
        return "get_recommendations"
    
    @property
    def description(self) -> str:
        return "Get personalized product recommendations based on customer needs or previous purchases"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="recommendation_type",
                param_type=str,
                required=False,
                description="Type: 'similar_to', 'complement_to', 'activity_based', or 'general'",
                default="general"
            ),
            ToolParameter(
                name="reference_skus",
                param_type=list,
                required=False,
                description="SKUs to base recommendations on (for similar_to/complement_to)",
                default=None
            ),
            ToolParameter(
                name="activity_or_need",
                param_type=str,
                required=False,
                description="Customer activity or need (hiking, tech gadgets, fashion, home decor, etc.)",
                default=None
            ),
            ToolParameter(
                name="limit",
                param_type=int,
                required=False,
                description="Number of recommendations",
                default=3,
                validation_rules={"min_value": 1, "max_value": 8}
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        """Generate intelligent recommendations."""
        rec_type = kwargs.get("recommendation_type", "general")
        reference_skus = kwargs.get("reference_skus") or []
        activity_or_need = kwargs.get("activity_or_need")
        limit = kwargs.get("limit", 3)
        
        try:
            if rec_type == "similar_to":
                recommendations = self._get_similar_products(reference_skus, limit)
                rec_message = "Products similar to what you're interested in:"
                
            elif rec_type == "complement_to":
                recommendations = self._get_complementary_products(reference_skus, limit)
                rec_message = "Products that go great with your selection:"
                
            elif rec_type == "activity_based":
                recommendations = self._get_activity_based_recommendations(activity_or_need or "", limit)
                rec_message = f"Perfect products for {activity_or_need or 'your needs'}:"
                
            else:  # general
                recommendations = self._get_general_recommendations(limit)
                rec_message = "Here are some popular Sierra Outfitters products:"
            
            if not recommendations:
                return ToolResult(
                    success=True,
                    data={
                        "recommendations": [],
                        "message": "I'd love to help you find the perfect products! 🏔️ What kind of adventure or activity are you planning?",
                        "suggestion": "Try describing what you're looking for - outdoor activities, tech gadgets, fashion items, or home decor!"
                    },
                    error=None
                )
            
            return ToolResult(
                success=True,
                data={
                    "recommendations": recommendations,
                    "recommendation_type": rec_type,
                    "count": len(recommendations),
                    "message": f"{rec_message} {len(recommendations)} great options for your next adventure! 🏔️"
                },
                error=None
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error generating recommendations: {str(e)}",
                data=None
            )
    
    def _get_similar_products(self, reference_skus: List[str], limit: int) -> List:
        """Find products similar to reference SKUs."""
        if not reference_skus:
            return self._get_general_recommendations(limit)
        
        # Get reference products
        reference_products = []
        for sku in reference_skus:
            if isinstance(sku, str):
                product = self.data_provider.get_product_by_sku(sku)
                if product:
                    reference_products.append(product)
        
        if not reference_products:
            return self._get_general_recommendations(limit)
        
        # Find products with overlapping tags
        similar_products: List[Any] = []
        used_skus = set(reference_skus)
        
        for ref_product in reference_products:
            for tag in ref_product.tags:
                tag_products = self.data_provider.get_products_by_category(tag)
                for product in tag_products:
                    if product.sku not in used_skus and len(similar_products) < limit:
                        similar_products.append(product)
                        used_skus.add(product.sku)
        
        return similar_products[:limit]
    
    def _get_complementary_products(self, reference_skus: List[str], limit: int) -> List:
        """Find products that complement reference SKUs."""
        if not reference_skus:
            return self._get_general_recommendations(limit)
        
        # Define smart complementary relationships based on actual catalog
        complement_rules = {
            # Outdoor/Adventure complements
            "adventure": ["high-tech", "food & beverage", "safety-enhanced"],
            "hiking": ["adventure-ready", "food & beverage"],
            "backpack": ["adventure", "food & beverage", "high-tech"],
            
            # Tech complements  
            "high-tech": ["adventure", "safety-enhanced", "personal flight"],
            "personal flight": ["high-tech", "safety-enhanced"],
            
            # Lifestyle complements
            "fashion": ["luxury", "modern design"],
            "luxury": ["modern design", "interior style"],
            "home decor": ["luxury", "lighting", "modern design"],
            
            # Food complements
            "food & beverage": ["adventure-ready", "versatile"],
        }
        
        # Get reference products and their tags
        reference_products = []
        for sku in reference_skus:
            if isinstance(sku, str):
                product = self.data_provider.get_product_by_sku(sku)
                if product:
                    reference_products.append(product)
        
        if not reference_products:
            return self._get_general_recommendations(limit)
        
        complementary_products: List[Any] = []
        used_skus = set(reference_skus)
        
        # Find complementary products
        for ref_product in reference_products:
            for tag in ref_product.tags:
                tag_lower = tag.lower()
                if tag_lower in complement_rules:
                    for comp_tag in complement_rules[tag_lower]:
                        comp_products = self.data_provider.get_products_by_category(comp_tag)
                        for product in comp_products:
                            if product.sku not in used_skus and len(complementary_products) < limit:
                                complementary_products.append(product)
                                used_skus.add(product.sku)
        
        # Fallback to similar if no complements found
        return complementary_products[:limit] or self._get_similar_products(reference_skus, limit)
    
    def _get_activity_based_recommendations(self, activity: str, limit: int) -> List:
        """Get recommendations based on customer activity or need."""
        if not activity:
            return self._get_general_recommendations(limit)
        
        activity_lower = activity.lower()
        
        # Map activities to relevant categories
        activity_map = {
            "hiking": ["hiking", "backpack", "adventure"],
            "camping": ["adventure", "outdoor gear", "food & beverage"],
            "outdoor": ["adventure", "outdoor gear", "hiking"],
            "tech": ["high-tech", "personal flight", "advanced cloaking"],
            "technology": ["high-tech", "personal flight", "advanced cloaking"],
            "gadgets": ["high-tech", "personal flight"],
            "fashion": ["fashion", "lifestyle"],
            "style": ["fashion", "lifestyle", "luxury"],
            "home": ["home decor", "lighting", "luxury"],
            "interior": ["home decor", "interior style", "modern design"],
            "food": ["food & beverage", "adventure-ready"],
            "travel": ["adventure", "personal flight", "teleportation"],
            "adventure": ["adventure", "adventure-ready", "explorer"],
        }
        
        # Find matching categories
        relevant_tags = []
        for keyword, tags in activity_map.items():
            if keyword in activity_lower:
                relevant_tags.extend(tags)
        
        if not relevant_tags:
            # Fallback: search by activity term directly
            return self.data_provider.search_products(activity)[:limit]
        
        # Get products from relevant categories
        recommendations: List[Any] = []
        used_skus = set()
        
        for tag in relevant_tags:
            products = self.data_provider.get_products_by_category(tag)
            for product in products:
                if product.sku not in used_skus and len(recommendations) < limit:
                    recommendations.append(product)
                    used_skus.add(product.sku)
        
        return recommendations[:limit]
    
    def _get_general_recommendations(self, limit: int) -> List:
        """Get general popular recommendations."""
        # Focus on diverse, interesting products from catalog
        featured_categories = ["Adventure", "High-Tech", "Backpack", "Food & Beverage", "Fashion"]
        recommendations: List[Any] = []
        used_skus = set()
        
        for category in featured_categories:
            products = self.data_provider.get_products_by_category(category)
            for product in products:
                if product.sku not in used_skus and len(recommendations) < limit:
                    recommendations.append(product)
                    used_skus.add(product.sku)
                    if len(recommendations) >= limit:
                        break
        
        return recommendations[:limit]


class ProductDetailsTool(BaseTool):
    """Get detailed information about specific products."""
    
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
    
    @property
    def tool_name(self) -> str:
        return "get_product_info"
    
    @property
    def description(self) -> str:
        return "Get detailed information about specific products by SKU or name"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="product_identifier",
                param_type=str,
                required=True,
                description="Product SKU (e.g., SOBP001) or partial product name"
            ),
            ToolParameter(
                name="include_recommendations",
                param_type=bool,
                required=False,
                description="Whether to include related product recommendations",
                default=True
            )
        ]
    
    def execute(self, **kwargs) -> ToolResult:
        """Get detailed product information."""
        identifier = kwargs["product_identifier"]
        include_recs = kwargs.get("include_recommendations", True)
        
        # Try to find product by SKU first
        product = self.data_provider.get_product_by_sku(identifier)
        
        if not product:
            # Try searching by name
            search_results = self.data_provider.search_products(identifier)
            if search_results:
                product = search_results[0]  # Take the first match
        
        if not product:
            return ToolResult(
                success=False,
                error=f"Product '{identifier}' not found. Try searching our catalog with 'browse_catalog'!",
                data=None
            )
        
        # Build detailed response
        product_info = {
            "product": product,
            "details": {
                "name": product.product_name,
                "sku": product.sku,
                "description": product.description,
                "categories": product.tags,
                "inventory_status": "In Stock" if product.inventory > 0 else "Out of Stock",
                "inventory_count": product.inventory
            }
        }
        
        # Add recommendations if requested
        if include_recs and product.inventory > 0:
            # Get 2-3 related products
            related_products: List[Any] = []
            for tag in product.tags[:2]:  # Use first 2 tags
                tag_products = self.data_provider.get_products_by_category(tag)
                for related in tag_products:
                    if related.sku != product.sku and len(related_products) < 3:
                        related_products.append(related)
            
            product_info["related_products"] = related_products
        
        return ToolResult(
            success=True,
            data=product_info,
            error=None
        )