"""
API Test Script
===============

Simple test script to verify the E-commerce Analytics API endpoints.
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"


def test_api_endpoint(endpoint, description):
    """Test a single API endpoint."""
    print(f"\n🔍 Testing: {description}")
    print(f"   Endpoint: {endpoint}")

    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success ({response.status_code})")

            # Print first few keys or items
            if isinstance(data, dict):
                keys = list(data.keys())[:3]
                print(f"   📊 Keys: {keys}")
                if len(keys) < len(data.keys()):
                    print(f"   ... and {len(data.keys()) - len(keys)} more")
            elif isinstance(data, list) and data:
                print(f"   📊 Items: {len(data)} items")
                if isinstance(data[0], dict):
                    print(f"   📊 First item keys: {list(data[0].keys())}")

        else:
            print(f"   ❌ Failed ({response.status_code})")
            print(f"   Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - Is the API server running?")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")


def main():
    """Run API tests."""
    print("🚀 E-commerce Analytics API Test Suite")
    print("=" * 50)

    # Test all endpoints
    endpoints = [
        ("/", "API Health Check"),
        ("/api/v1/analytics/overview", "Overview KPIs"),
        ("/api/v1/analytics/revenue", "Revenue Analytics"),
        ("/api/v1/analytics/customers", "Customer Analytics"),
        ("/api/v1/analytics/products", "Product Analytics"),
        ("/api/v1/analytics/marketing", "Marketing Analytics"),
        ("/api/v1/reports/recent-orders?limit=10", "Recent Orders"),
        # Test with filters
        ("/api/v1/analytics/revenue?group_by=month", "Revenue by Month"),
        (
            "/api/v1/analytics/products?category=Electronics&limit=5",
            "Electronics Products",
        ),
    ]

    for endpoint, description in endpoints:
        test_api_endpoint(endpoint, description)

    print(f"\n📋 Test Summary:")
    print(f"   • API Documentation: {API_BASE}/docs")
    print(f"   • Alternative Docs: {API_BASE}/redoc")
    print(f"   • Health Check: {API_BASE}/")

    print(f"\n🌐 Frontend Integration Examples:")
    print(
        f"""
    // JavaScript/React example
    const fetchRevenue = async () => {{
        const response = await fetch('{API_BASE}/api/v1/analytics/revenue');
        const data = await response.json();
        return data.time_series;
    }};

    // Python client example
    import requests
    response = requests.get('{API_BASE}/api/v1/analytics/overview')
    kpis = response.json()
    print(f"Total Revenue: ${{kpis['total_revenue']:,.2f}}")
    """
    )


if __name__ == "__main__":
    main()
