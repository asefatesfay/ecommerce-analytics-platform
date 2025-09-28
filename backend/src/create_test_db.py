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
    data_dir = current_dir.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / 'ecommerce.duckdb'
    
    # Create minimal test data
    customers_data = []
    for i in range(100):
        customers_data.append({
            'customer_id': f'CUST_{i:04d}',
            'first_name': f'Customer{i}',
            'last_name': 'Test',
            'email': f'customer{i}@test.com',
            'registration_date': '2023-01-01',
            'city': 'TestCity',
            'state': 'TestState',
            'country': 'TestCountry'
        })
    
    products_data = []
    categories = ['Electronics', 'Clothing', 'Books', 'Home']
    for i in range(50):
        products_data.append({
            'product_id': f'PROD_{i:04d}',
            'product_name': f'Test Product {i}',
            'category': random.choice(categories),
            'price': round(random.uniform(10, 500), 2),
            'cost': round(random.uniform(5, 250), 2),
            'stock_quantity': random.randint(0, 100)
        })
    
    orders_data = []
    order_items_data = []
    base_date = datetime(2023, 1, 1)
    
    for i in range(200):
        order_date = base_date + timedelta(days=random.randint(0, 365))
        customer_id = f'CUST_{random.randint(0, 99):04d}'
        
        order = {
            'order_id': f'ORD_{i:06d}',
            'customer_id': customer_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'total_amount': 0,
            'order_status': random.choice(['completed', 'pending', 'cancelled'])
        }
        
        # Add 1-3 items per order
        total_amount = 0
        for j in range(random.randint(1, 4)):
            product_idx = random.randint(0, 49)
            quantity = random.randint(1, 3)
            price = products_data[product_idx]['price']
            
            order_items_data.append({
                'order_item_id': f'ITEM_{i:06d}_{j}',
                'order_id': order['order_id'],
                'product_id': f'PROD_{product_idx:04d}',
                'quantity': quantity,
                'unit_price': price,
                'total_price': price * quantity
            })
            
            total_amount += price * quantity
        
        order['total_amount'] = round(total_amount, 2)
        orders_data.append(order)
    
    # Web sessions data
    sessions_data = []
    for i in range(500):
        session_date = base_date + timedelta(days=random.randint(0, 365))
        sessions_data.append({
            'session_id': f'SESS_{i:06d}',
            'customer_id': f'CUST_{random.randint(0, 99):04d}',
            'session_date': session_date.strftime('%Y-%m-%d'),
            'page_views': random.randint(1, 20),
            'session_duration_minutes': random.randint(1, 120),
            'device_type': random.choice(['desktop', 'mobile', 'tablet']),
            'traffic_source': random.choice(['organic', 'paid', 'direct', 'social'])
        })
    
    # Create DataFrames
    customers_df = pd.DataFrame(customers_data)
    products_df = pd.DataFrame(products_data)
    orders_df = pd.DataFrame(orders_data)
    order_items_df = pd.DataFrame(order_items_data)
    sessions_df = pd.DataFrame(sessions_data)
    
    # Create DuckDB database
    print(f"Creating database at: {db_path}")
    
    with duckdb.connect(str(db_path)) as conn:
        # Create and populate tables
        conn.execute("CREATE TABLE customers AS SELECT * FROM customers_df")
        conn.execute("CREATE TABLE products AS SELECT * FROM products_df")
        conn.execute("CREATE TABLE orders AS SELECT * FROM orders_df")
        conn.execute("CREATE TABLE order_items AS SELECT * FROM order_items_df")
        conn.execute("CREATE TABLE web_sessions AS SELECT * FROM sessions_df")
        
        # Verify tables
        result = conn.execute("SHOW TABLES").fetchall()
        print(f"Created tables: {[table[0] for table in result]}")
        
        # Show row counts
        for table in ['customers', 'products', 'orders', 'order_items', 'web_sessions']:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count:,} rows")
    
    print(f"✅ Test database created successfully at {db_path}")
    return db_path

if __name__ == "__main__":
    create_test_database()