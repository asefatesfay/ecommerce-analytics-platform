"""
API Tests
=========

pytest test cases for the E-commerce Analytics API.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api.main import app

client = TestClient(app)


class TestHealthCheck:
    """Test health check endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""
    
    def test_analytics_overview(self):
        """Test the analytics overview endpoint."""
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["total_revenue", "total_orders", "avg_order_value", "customer_count"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
            assert isinstance(data[field], (int, float)), f"Field {field} should be numeric"
    
    def test_revenue_analytics(self):
        """Test the revenue analytics endpoint."""
        response = client.get("/api/v1/analytics/revenue")
        assert response.status_code == 200
        data = response.json()
        
        assert "time_series" in data
        assert isinstance(data["time_series"], list)
        
        if data["time_series"]:
            first_entry = data["time_series"][0]
            assert "date" in first_entry
            assert "revenue" in first_entry
    
    def test_customer_analytics(self):
        """Test the customer analytics endpoint."""
        response = client.get("/api/v1/analytics/customers")
        assert response.status_code == 200
        data = response.json()
        
        # Should have customer segments or metrics
        assert isinstance(data, dict)
        assert len(data) > 0
    
    def test_product_analytics(self):
        """Test the product analytics endpoint."""
        response = client.get("/api/v1/analytics/products")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        
        # Check for common product analytics fields
        if "top_products" in data:
            assert isinstance(data["top_products"], list)


class TestReportsEndpoints:
    """Test reports API endpoints."""
    
    def test_recent_orders(self):
        """Test the recent orders endpoint."""
        response = client.get("/api/v1/reports/recent-orders")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        
        if data:
            first_order = data[0]
            assert "order_id" in first_order
            assert "order_date" in first_order
    
    def test_recent_orders_with_limit(self):
        """Test the recent orders endpoint with limit parameter."""
        response = client.get("/api/v1/reports/recent-orders?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5


class TestParameterValidation:
    """Test API parameter validation."""
    
    def test_revenue_with_group_by(self):
        """Test revenue endpoint with group_by parameter."""
        response = client.get("/api/v1/analytics/revenue?group_by=month")
        assert response.status_code == 200
        
        # Should accept valid group_by values
        valid_group_by = ["day", "week", "month", "quarter"]
        for group_by in valid_group_by:
            response = client.get(f"/api/v1/analytics/revenue?group_by={group_by}")
            assert response.status_code in [200, 422]  # 422 if not implemented
    
    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        # Test invalid limit (negative number)
        response = client.get("/api/v1/reports/recent-orders?limit=-1")
        # Should either return 422 (validation error) or handle gracefully
        assert response.status_code in [200, 422]


class TestErrorHandling:
    """Test error handling."""
    
    def test_nonexistent_endpoint(self):
        """Test that non-existent endpoints return 404."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """Test that invalid HTTP methods are handled."""
        response = client.post("/api/v1/analytics/overview")
        assert response.status_code == 405  # Method Not Allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])