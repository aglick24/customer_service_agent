# DataProvider - Sierra Outfitters Data Management

## Overview

The `DataProvider` class is a centralized data management system that replaces the previous mock data approach in `BusinessTools`. It provides access to real customer orders, product catalog, and business operations through JSON data files.

## Features

### 1. Order Status and Tracking
- **Customer Order Lookup**: Find orders by email and order number
- **USPS Tracking Integration**: Automatic generation of tracking URLs using the format:
  ```
  https://tools.usps.com/go/TrackConfirmAction?tLabels={trackingNumber}
  ```
- **Order Details**: Complete order information including products, status, and customer details

### 2. Product Catalog Management
- **Product Search**: Search products by name, description, or tags
- **Category-based Recommendations**: Get products by category (derived from tags)
- **Inventory Status**: Real-time inventory levels and availability
- **Product Recommendations**: AI-powered recommendations based on customer preferences

### 3. Early Risers Promotion
- **Time-based Availability**: 10% discount available from 8:00 AM to 10:00 AM Pacific Time
- **Unique Discount Codes**: Automatic generation of unique codes (format: `EARLY-XXXX`)
- **Real-time Validation**: Checks current time against promotion window

## Data Files

### CustomerOrders.json
Contains customer order data with the following structure:
```json
{
  "CustomerName": "John Doe",
  "Email": "john.doe@example.com",
  "OrderNumber": "#W001",
  "ProductsOrdered": ["SOBP001", "SOWB004"],
  "Status": "delivered",
  "TrackingNumber": "TRK123456789"
}
```

### ProductCatalog.json
Contains product information with the following structure:
```json
{
  "ProductName": "Bhavish's Backcountry Blaze Backpack",
  "SKU": "SOBP001",
  "Inventory": 120,
  "Description": "Conquer the wilderness with the Backcountry Blaze Backpack...",
  "Tags": ["Backpack", "Hiking", "Adventure", "Outdoor Gear"]
}
```

## Usage

### Basic Initialization
```python
from sierra_agent.data.data_provider import DataProvider

# Initialize with default data directory
data_provider = DataProvider()

# Or specify custom data directory
data_provider = DataProvider(data_dir="custom/data/path")
```

### Order Status Lookup
```python
# Get order status and tracking
order_data = data_provider.get_order_status("john.doe@example.com", "#W001")

if order_data:
    print(f"Status: {order_data['order_info']['Status']}")
    print(f"Tracking URL: {order_data['tracking_url']}")
    print(f"Products: {[p['ProductName'] for p in order_data['products']]}")
```

### Product Search and Recommendations
```python
# Search products
results = data_provider.search_products("hiking backpack")

# Get recommendations by category
adventure_products = data_provider.get_products_by_category("adventure")

# Get personalized recommendations
recommendations = data_provider.get_product_recommendations(
    customer_preferences=["hiking", "outdoor", "durable"]
)
```

### Early Risers Promotion
```python
# Check promotion availability
promotion = data_provider.get_early_risers_promotion()

if promotion and promotion["available"]:
    print(f"Discount Code: {promotion['discount_code']}")
    print(f"Discount: {promotion['discount_percentage']}%")
```

## BusinessTools Integration

The `BusinessTools` class now uses `DataProvider` instead of mock data:

```python
from sierra_agent.tools.business_tools import BusinessTools

# BusinessTools automatically initializes DataProvider
business_tools = BusinessTools()

# Order status with natural language processing
order_status = business_tools.get_order_status(
    "I need to check the status of order #W001 for john.doe@example.com"
)

# Product recommendations
recommendations = business_tools.get_product_recommendations(
    "I'm looking for hiking gear and outdoor equipment"
)

# Early risers promotion
promotion = business_tools.get_early_risers_promotion(
    "I'd like to know about the Early Risers promotion"
)
```

## Key Benefits

1. **Real Data**: Uses actual customer orders and product catalog instead of mock data
2. **Centralized Management**: Single source of truth for all business data
3. **Extensible**: Easy to add new data sources and business logic
4. **Performance**: Efficient data loading and caching
5. **Maintainability**: Clear separation of concerns between data and business logic

## Testing

Run the test script to verify functionality:
```bash
python test_data_provider.py
```

This will test:
- Order status and tracking
- Product search and recommendations
- Early risers promotion
- Customer order history
- Inventory status
- BusinessTools integration

## Data Structure

### Order Status Response
```python
{
    "order_info": {
        "CustomerName": "John Doe",
        "Email": "john.doe@example.com",
        "OrderNumber": "#W001",
        "ProductsOrdered": ["SOBP001", "SOWB004"],
        "Status": "delivered",
        "TrackingNumber": "TRK123456789"
    },
    "products": [
        {
            "ProductName": "Bhavish's Backcountry Blaze Backpack",
            "SKU": "SOBP001",
            "Inventory": 120,
            "Description": "...",
            "Tags": ["Backpack", "Hiking", "Adventure", "Outdoor Gear"]
        }
    ],
    "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels=TRK123456789"
}
```

### Product Recommendations Response
```python
{
    "recommendations": [...],
    "count": 5,
    "category": "hiking",
    "preferences": ["outdoor", "durable"]
}
```

### Early Risers Promotion Response
```python
{
    "available": True,
    "discount_code": "EARLY-A1B2",
    "discount_percentage": 10,
    "valid_hours": "8:00 AM - 10:00 AM Pacific Time",
    "description": "Early Risers Promotion - 10% off your entire order!",
    "generated_at": "2025-01-27T08:30:00"
}
```

## Future Enhancements

1. **Database Integration**: Replace JSON files with database connections
2. **Real-time Updates**: Webhook support for live data updates
3. **Caching Layer**: Redis or in-memory caching for performance
4. **API Endpoints**: REST API for external system integration
5. **Data Validation**: Schema validation and data integrity checks
6. **Analytics**: Built-in reporting and business intelligence features
