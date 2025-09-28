#!/usr/bin/env python3
"""
Minimal Test Data Generator for CI
==================================

Creates a minimal DuckDB database for testing purposes.
This is a lightweight version for CI environments.
"""

import os
import sys
from pathlib import Path
import duckdb
import pandas as pd
from datetime import datetime, timedelta
import random


def create_test_database():
    """Create a minimal test database for CI."""
    print("🦆 Creating minimal test database for CI...")

    # Ensure data directory exists
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / "ecommerce.duckdb"

    # Create minimal test data
    customers_data = []
    segments = ["Premium", "Standard", "Basic", "VIP"]
    channels = ["organic", "paid_search", "social_media", "email", "direct", "referral"]
    for i in range(100):
        customers_data.append(
            {
                "customer_id": f"CUST_{i:04d}",
                "first_name": f"Customer{i}",
                "last_name": "Test",
                "email": f"customer{i}@test.com",
                "registration_date": "2023-01-01",
                "city": "TestCity",
                "state": "TestState",
                "country": "TestCountry",
                "customer_segment": random.choice(segments),
                "acquisition_channel": random.choice(channels),
            }
        )

    products_data = []
    categories = ["Electronics", "Clothing", "Books", "Home"]
    for i in range(50):
        products_data.append(
            {
                "product_id": f"PROD_{i:04d}",
                "product_name": f"Test Product {i}",
                "category": random.choice(categories),
                "price": round(random.uniform(10, 500), 2),
                "cost": round(random.uniform(5, 250), 2),
                "stock_quantity": random.randint(0, 100),
            }
        )

    orders_data = []
    order_items_data = []
    base_date = datetime(2023, 1, 1)

    for i in range(200):
        order_date = base_date + timedelta(days=random.randint(0, 365))
        customer_id = f"CUST_{random.randint(0, 99):04d}"

        order = {
            "order_id": f"ORD_{i:06d}",
            "customer_id": customer_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "total_amount": 0,
            "status": random.choice(["Completed", "Pending", "Cancelled"]),
            "payment_method": random.choice(["credit_card", "debit_card", "paypal", "bank_transfer"]),
        }

        # Add 1-3 items per order
        total_amount = 0
        for j in range(random.randint(1, 4)):
            product_idx = random.randint(0, 49)
            quantity = random.randint(1, 3)
            price = products_data[product_idx]["price"]

            order_items_data.append(
                {
                    "order_item_id": f"ITEM_{i:06d}_{j}",
                    "order_id": order["order_id"],
                    "product_id": f"PROD_{product_idx:04d}",
                    "quantity": quantity,
                    "unit_price": price,
                    "total_price": price * quantity,
                }
            )

            total_amount += price * quantity

        order["total_amount"] = round(total_amount, 2)
        orders_data.append(order)

    # Web sessions data
    sessions_data = []
    for i in range(500):
        session_date = base_date + timedelta(days=random.randint(0, 365))
        sessions_data.append(
            {
                "session_id": f"SESS_{i:06d}",
                "customer_id": f"CUST_{random.randint(0, 99):04d}",
                "session_date": session_date.strftime("%Y-%m-%d"),
                "page_views": random.randint(1, 20),
                "session_duration_minutes": random.randint(1, 120),
                "device_type": random.choice(["desktop", "mobile", "tablet"]),
                "traffic_source": random.choice(["organic", "paid", "direct", "social"]),
                "converted": random.choice([True, False]),  # Conversion tracking
            }
        )

    # Create DataFrames
    customers_df = pd.DataFrame(customers_data)
    products_df = pd.DataFrame(products_data)
    orders_df = pd.DataFrame(orders_data)
    order_items_df = pd.DataFrame(order_items_data)
    sessions_df = pd.DataFrame(sessions_data)

    # Create DuckDB database (remove if exists)
    if db_path.exists():
        print(f"Removing existing database: {db_path}")
        db_path.unlink()

    print(f"Creating database at: {db_path}")

    with duckdb.connect(str(db_path)) as conn:
        # Create and populate tables with proper date types
        conn.execute("CREATE TABLE customers AS SELECT * FROM customers_df")
        conn.execute("CREATE TABLE products AS SELECT * FROM products_df")

        # Create orders table with proper date column
        conn.execute(
            """
            CREATE TABLE orders AS
            SELECT
                order_id,
                customer_id,
                CAST(order_date AS DATE) as order_date,
                total_amount,
                status,
                payment_method
            FROM orders_df
        """
        )

        conn.execute("CREATE TABLE order_items AS SELECT * FROM order_items_df")

        # Create web_sessions with proper date column
        conn.execute(
            """
            CREATE TABLE web_sessions AS
            SELECT
                session_id,
                customer_id,
                CAST(session_date AS DATE) as session_date,
                page_views,
                session_duration_minutes,
                device_type,
                traffic_source,
                converted
            FROM sessions_df
        """
        )

        # Create product_performance table (derived from order_items and products)
        conn.execute(
            """
            CREATE TABLE product_performance AS
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                COALESCE(SUM(oi.total_price), 0) as total_revenue,
                COALESCE(COUNT(DISTINCT oi.order_id), 0) as orders_count,
                COALESCE(COUNT(DISTINCT oi.order_id), 0) as times_ordered,  -- Alias for orders_count
                COALESCE(AVG(oi.unit_price), p.price) as avg_selling_price,
                COALESCE(AVG(oi.unit_price * 0.3), p.price * 0.3) as avg_profit_per_unit,
                CASE
                    WHEN COALESCE(SUM(oi.quantity), 0) > 50 THEN 'High'
                    WHEN COALESCE(SUM(oi.quantity), 0) > 20 THEN 'Medium'
                    ELSE 'Low'
                END as performance_tier
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.product_name, p.category, p.price
        """
        )

        # Create customer_ltv view (Customer Lifetime Value)
        conn.execute(
            """
            CREATE OR REPLACE VIEW customer_ltv AS
            SELECT
                c.customer_id,
                c.customer_segment,
                c.acquisition_channel,
                COALESCE(SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END), 0) as monetary,
                COALESCE(SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END), 0) as lifetime_value,
                COALESCE(COUNT(CASE WHEN o.status = 'Completed' THEN o.order_id END), 0) as frequency,
                COALESCE(COUNT(o.order_id), 0) as total_orders,  -- Total orders including all statuses
                COALESCE(MAX(o.order_date), CAST(c.registration_date AS DATE)) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_segment, c.acquisition_channel, c.registration_date
        """
        )

        # Verify tables and views
        tables_result = conn.execute("SHOW TABLES").fetchall()
        views_result = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_type = 'VIEW'"
        ).fetchall()

        print(f"Created tables: {[table[0] for table in tables_result]}")
        print(f"Created views: {[view[0] for view in views_result]}")

        # Show row counts
        for table in [
            "customers",
            "products",
            "orders",
            "order_items",
            "web_sessions",
            "product_performance",
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count:,} rows")

        # Test a few key queries that the API uses
        print(f"\nTesting key queries:")

        # Test orders with status
        completed_orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status = 'Completed'").fetchone()[0]
        print(f"  Completed orders: {completed_orders:,}")

        # Test customer segments
        segments = conn.execute("SELECT customer_segment, COUNT(*) FROM customers GROUP BY customer_segment").fetchall()
        print(f"  Customer segments: {dict(segments)}")

        # Test product performance
        perf_count = conn.execute("SELECT COUNT(*) FROM product_performance WHERE total_quantity_sold > 0").fetchone()[
            0
        ]
        print(f"  Products with sales: {perf_count:,}")

    print(f"✅ Test database created successfully at {db_path}")
    return db_path


if __name__ == "__main__":
    create_test_database()
