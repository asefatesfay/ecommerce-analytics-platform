"""
DuckDB SQL Operations Examples
=============================

This script demonstrates advanced SQL operations and analytical queries using DuckDB.
DuckDB excels at OLAP (Online Analytical Processing) workloads and supports
advanced SQL features for data analysis.
"""

import duckdb
import pandas as pd
from datetime import datetime, timedelta
import random

def setup_comprehensive_dataset(conn):
    """Create a comprehensive dataset for SQL demonstrations."""
    print("=== Setting up comprehensive dataset ===")
    
    # Create customers table
    conn.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name VARCHAR,
            email VARCHAR,
            city VARCHAR,
            country VARCHAR,
            signup_date DATE,
            customer_tier VARCHAR
        )
    """)
    
    # Insert customer data
    conn.execute("""
        INSERT INTO customers VALUES
        (1, 'Alice Johnson', 'alice@email.com', 'New York', 'USA', '2023-01-15', 'Premium'),
        (2, 'Bob Smith', 'bob@email.com', 'London', 'UK', '2023-02-20', 'Standard'),
        (3, 'Carol Davis', 'carol@email.com', 'Toronto', 'Canada', '2023-03-10', 'Premium'),
        (4, 'David Wilson', 'david@email.com', 'Sydney', 'Australia', '2023-04-05', 'Standard'),
        (5, 'Eve Brown', 'eve@email.com', 'Berlin', 'Germany', '2023-05-18', 'Gold'),
        (6, 'Frank Miller', 'frank@email.com', 'Paris', 'France', '2023-06-25', 'Standard'),
        (7, 'Grace Lee', 'grace@email.com', 'Tokyo', 'Japan', '2023-07-12', 'Premium'),
        (8, 'Henry Taylor', 'henry@email.com', 'New York', 'USA', '2023-08-30', 'Gold')
    """)
    
    # Create products table
    conn.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name VARCHAR,
            category VARCHAR,
            price DECIMAL(10,2),
            cost DECIMAL(10,2),
            supplier VARCHAR,
            launch_date DATE
        )
    """)
    
    conn.execute("""
        INSERT INTO products VALUES
        (101, 'Laptop Pro', 'Electronics', 1299.99, 800.00, 'TechCorp', '2023-01-01'),
        (102, 'Wireless Mouse', 'Electronics', 29.99, 12.00, 'TechCorp', '2023-01-15'),
        (103, 'Desk Chair', 'Furniture', 199.99, 120.00, 'FurniturePlus', '2023-02-01'),
        (104, 'Monitor 24"', 'Electronics', 249.99, 150.00, 'DisplayTech', '2023-02-15'),
        (105, 'Coffee Mug', 'Home', 14.99, 5.00, 'HomeGoods', '2023-03-01'),
        (106, 'Notebook', 'Office', 8.99, 3.50, 'PaperCorp', '2023-03-15'),
        (107, 'Smartphone', 'Electronics', 799.99, 450.00, 'MobileTech', '2023-04-01'),
        (108, 'Bookshelf', 'Furniture', 149.99, 90.00, 'FurniturePlus', '2023-04-15')
    """)
    
    # Create orders table
    conn.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE,
            status VARCHAR,
            shipping_cost DECIMAL(8,2),
            discount_amount DECIMAL(8,2)
        )
    """)
    
    conn.execute("""
        INSERT INTO orders VALUES
        (1001, 1, '2024-01-15', 'Completed', 9.99, 0.00),
        (1002, 2, '2024-01-16', 'Completed', 15.99, 25.00),
        (1003, 3, '2024-01-17', 'Pending', 12.50, 0.00),
        (1004, 4, '2024-01-18', 'Completed', 8.99, 10.00),
        (1005, 1, '2024-01-19', 'Completed', 0.00, 50.00),
        (1006, 5, '2024-01-20', 'Shipped', 19.99, 0.00),
        (1007, 6, '2024-01-21', 'Completed', 7.99, 5.00),
        (1008, 7, '2024-01-22', 'Cancelled', 0.00, 0.00),
        (1009, 8, '2024-01-23', 'Completed', 14.99, 20.00),
        (1010, 2, '2024-01-24', 'Pending', 11.50, 15.00)
    """)
    
    # Create order_items table
    conn.execute("""
        CREATE TABLE order_items (
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price DECIMAL(10,2)
        )
    """)
    
    conn.execute("""
        INSERT INTO order_items VALUES
        (1001, 101, 1, 1299.99),
        (1001, 102, 2, 29.99),
        (1002, 103, 1, 199.99),
        (1002, 105, 3, 14.99),
        (1003, 104, 2, 249.99),
        (1004, 106, 5, 8.99),
        (1004, 105, 1, 14.99),
        (1005, 107, 1, 799.99),
        (1006, 108, 1, 149.99),
        (1006, 102, 1, 29.99),
        (1007, 105, 2, 14.99),
        (1009, 101, 1, 1299.99),
        (1009, 104, 1, 249.99),
        (1010, 106, 10, 8.99)
    """)
    
    print("✅ Created tables: customers, products, orders, order_items")
    
    # Show table counts
    for table in ['customers', 'products', 'orders', 'order_items']:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} records")

def basic_sql_operations(conn):
    """Demonstrate basic SQL operations."""
    print("\n=== Basic SQL Operations ===")
    
    # SELECT with multiple conditions
    print("1. Complex WHERE clauses:")
    result = conn.execute("""
        SELECT 
            name,
            email,
            city,
            customer_tier,
            signup_date
        FROM customers 
        WHERE customer_tier IN ('Premium', 'Gold')
          AND country = 'USA'
          AND signup_date >= '2023-01-01'
        ORDER BY signup_date
    """).fetchdf()
    print(result)
    
    # String operations
    print("\n2. String operations:")
    result = conn.execute("""
        SELECT 
            product_name,
            UPPER(category) as category_upper,
            LENGTH(product_name) as name_length,
            SUBSTR(product_name, 1, 10) as short_name,
            CASE 
                WHEN price >= 200 THEN 'Expensive'
                WHEN price >= 50 THEN 'Moderate'
                ELSE 'Affordable'
            END as price_category
        FROM products
        ORDER BY price DESC
    """).fetchdf()
    print(result)
    
    # Date operations
    print("\n3. Date operations:")
    result = conn.execute("""
        SELECT 
            name,
            signup_date,
            DATEDIFF('day', signup_date, CURRENT_DATE) as days_since_signup,
            DATEDIFF('month', signup_date, CURRENT_DATE) as months_since_signup,
            EXTRACT('year' FROM signup_date) as signup_year,
            strftime('%B %Y', signup_date) as signup_month_year
        FROM customers
        ORDER BY signup_date
    """).fetchdf()
    print(result)

def joins_and_relationships(conn):
    """Demonstrate different types of joins."""
    print("\n=== Joins and Relationships ===")
    
    # Inner join - orders with customer info
    print("1. Inner Join - Orders with customer details:")
    result = conn.execute("""
        SELECT 
            o.order_id,
            c.name,
            c.city,
            c.customer_tier,
            o.order_date,
            o.status,
            o.shipping_cost
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'Completed'
        ORDER BY o.order_date
    """).fetchdf()
    print(result)
    
    # Left join - all customers with their orders (including those without orders)
    print("\n2. Left Join - All customers with order count:")
    result = conn.execute("""
        SELECT 
            c.name,
            c.customer_tier,
            COUNT(o.order_id) as total_orders,
            COALESCE(SUM(o.shipping_cost), 0) as total_shipping
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name, c.customer_tier
        ORDER BY total_orders DESC
    """).fetchdf()
    print(result)
    
    # Complex join - order details with product information
    print("\n3. Complex Join - Order details with product info:")
    result = conn.execute("""
        SELECT 
            o.order_id,
            c.name as customer_name,
            p.product_name,
            p.category,
            oi.quantity,
            oi.unit_price,
            (oi.quantity * oi.unit_price) as line_total,
            p.price - p.cost as margin_per_unit
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        INNER JOIN products p ON oi.product_id = p.product_id
        WHERE o.status IN ('Completed', 'Shipped')
        ORDER BY o.order_id, p.product_name
    """).fetchdf()
    print(result.head(10))

def aggregation_and_grouping(conn):
    """Demonstrate aggregation functions and grouping."""
    print("\n=== Aggregation and Grouping ===")
    
    # Basic aggregations
    print("1. Sales summary by category:")
    result = conn.execute("""
        SELECT 
            p.category,
            COUNT(DISTINCT oi.order_id) as orders_count,
            SUM(oi.quantity) as total_units_sold,
            SUM(oi.quantity * oi.unit_price) as total_revenue,
            AVG(oi.unit_price) as avg_unit_price,
            MIN(oi.unit_price) as min_price,
            MAX(oi.unit_price) as max_price
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """).fetchdf()
    print(result)
    
    # HAVING clause
    print("\n2. Categories with revenue > $500:")
    result = conn.execute("""
        SELECT 
            p.category,
            SUM(oi.quantity * oi.unit_price) as total_revenue,
            COUNT(DISTINCT oi.order_id) as order_count
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.category
        HAVING SUM(oi.quantity * oi.unit_price) > 500
        ORDER BY total_revenue DESC
    """).fetchdf()
    print(result)
    
    # Multiple grouping levels
    print("\n3. Sales by country and tier:")
    result = conn.execute("""
        SELECT 
            c.country,
            c.customer_tier,
            COUNT(DISTINCT c.customer_id) as customers,
            COUNT(o.order_id) as total_orders,
            SUM(oi.quantity * oi.unit_price) as total_revenue,
            AVG(oi.quantity * oi.unit_price) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.country, c.customer_tier
        ORDER BY c.country, total_revenue DESC
    """).fetchdf()
    print(result)

def window_functions(conn):
    """Demonstrate window functions for analytical queries."""
    print("\n=== Window Functions ===")
    
    # Running totals and rankings
    print("1. Customer rankings by total spend:")
    result = conn.execute("""
        SELECT 
            c.name,
            c.customer_tier,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_spent,
            RANK() OVER (ORDER BY COALESCE(SUM(oi.quantity * oi.unit_price), 0) DESC) as spending_rank,
            DENSE_RANK() OVER (PARTITION BY c.customer_tier ORDER BY COALESCE(SUM(oi.quantity * oi.unit_price), 0) DESC) as tier_rank,
            PERCENT_RANK() OVER (ORDER BY COALESCE(SUM(oi.quantity * oi.unit_price), 0) DESC) as percentile_rank
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.customer_id, c.name, c.customer_tier
        ORDER BY total_spent DESC
    """).fetchdf()
    print(result)
    
    # Moving averages
    print("\n2. Daily order trends with moving average:")
    result = conn.execute("""
        SELECT 
            order_date,
            COUNT(*) as daily_orders,
            SUM(COUNT(*)) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_3day_total,
            AVG(COUNT(*)) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as rolling_3day_avg,
            LAG(COUNT(*), 1) OVER (ORDER BY order_date) as prev_day_orders,
            COUNT(*) - LAG(COUNT(*), 1) OVER (ORDER BY order_date) as daily_change
        FROM orders
        GROUP BY order_date
        ORDER BY order_date
    """).fetchdf()
    print(result)
    
    # First and last values
    print("\n3. First and last orders by customer:")
    result = conn.execute("""
        SELECT 
            c.name,
            o.order_date,
            o.order_id,
            FIRST_VALUE(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as first_order_date,
            LAST_VALUE(o.order_date) OVER (PARTITION BY c.customer_id ORDER BY o.order_date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_order_date,
            ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as order_sequence
        FROM customers c
        INNER JOIN orders o ON c.customer_id = o.customer_id
        ORDER BY c.name, o.order_date
    """).fetchdf()
    print(result)

def common_table_expressions(conn):
    """Demonstrate Common Table Expressions (CTEs)."""
    print("\n=== Common Table Expressions (CTEs) ===")
    
    # Simple CTE
    print("1. Customer lifetime value calculation:")
    result = conn.execute("""
        WITH customer_stats AS (
            SELECT 
                c.customer_id,
                c.name,
                c.customer_tier,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(oi.quantity * oi.unit_price) as total_revenue,
                AVG(oi.quantity * oi.unit_price) as avg_order_value,
                MIN(o.order_date) as first_order_date,
                MAX(o.order_date) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id, c.name, c.customer_tier
        )
        SELECT 
            name,
            customer_tier,
            total_orders,
            COALESCE(total_revenue, 0) as total_revenue,
            COALESCE(avg_order_value, 0) as avg_order_value,
            COALESCE(DATEDIFF('day', first_order_date, last_order_date), 0) as customer_lifespan_days,
            CASE 
                WHEN total_orders >= 3 THEN 'Loyal'
                WHEN total_orders >= 2 THEN 'Regular'
                WHEN total_orders = 1 THEN 'New'
                ELSE 'Inactive'
            END as customer_segment
        FROM customer_stats
        ORDER BY total_revenue DESC
    """).fetchdf()
    print(result)
    
    # Recursive CTE (number sequence example)
    print("\n2. Recursive CTE - Generate date series:")
    result = conn.execute("""
        WITH RECURSIVE date_series AS (
            SELECT DATE '2024-01-15' as date_val
            UNION ALL
            SELECT date_val + INTERVAL '1 day'
            FROM date_series
            WHERE date_val < DATE '2024-01-25'
        ),
        daily_orders AS (
            SELECT 
                ds.date_val,
                COALESCE(COUNT(o.order_id), 0) as orders_count,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) as daily_revenue
            FROM date_series ds
            LEFT JOIN orders o ON ds.date_val = o.order_date
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY ds.date_val
        )
        SELECT 
            date_val,
            orders_count,
            daily_revenue,
            SUM(daily_revenue) OVER (ORDER BY date_val) as cumulative_revenue
        FROM daily_orders
        ORDER BY date_val
    """).fetchdf()
    print(result)

def advanced_analytics(conn):
    """Demonstrate advanced analytical functions."""
    print("\n=== Advanced Analytics ===")
    
    # Product performance analysis
    print("1. Product performance metrics:")
    result = conn.execute("""
        WITH product_metrics AS (
            SELECT 
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                p.cost,
                (p.price - p.cost) as margin_per_unit,
                ((p.price - p.cost) / p.price * 100) as margin_percentage,
                COALESCE(SUM(oi.quantity), 0) as units_sold,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
                COALESCE(SUM(oi.quantity * p.cost), 0) as total_cost,
                COUNT(DISTINCT oi.order_id) as orders_appeared_in
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status = 'Completed'
            GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost
        )
        SELECT 
            product_name,
            category,
            price,
            margin_percentage,
            units_sold,
            total_revenue,
            (total_revenue - total_cost) as total_profit,
            CASE 
                WHEN units_sold = 0 THEN 'No Sales'
                WHEN units_sold >= 5 THEN 'High Seller'
                WHEN units_sold >= 2 THEN 'Medium Seller'
                ELSE 'Low Seller'
            END as performance_category,
            NTILE(4) OVER (ORDER BY total_revenue) as revenue_quartile
        FROM product_metrics
        ORDER BY total_revenue DESC
    """).fetchdf()
    print(result)
    
    # Cohort analysis simulation
    print("\n2. Customer cohort analysis (by signup month):")
    result = conn.execute("""
        WITH customer_cohorts AS (
            SELECT 
                c.customer_id,
                c.name,
                strftime('%Y-%m', c.signup_date) as signup_cohort,
                MIN(o.order_date) as first_order_date,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(oi.quantity * oi.unit_price) as total_spent
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_id, c.name, c.signup_date
        )
        SELECT 
            signup_cohort,
            COUNT(*) as cohort_size,
            SUM(CASE WHEN total_orders > 0 THEN 1 ELSE 0 END) as customers_with_orders,
            ROUND(SUM(CASE WHEN total_orders > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as conversion_rate,
            AVG(COALESCE(total_spent, 0)) as avg_revenue_per_customer,
            AVG(CASE WHEN total_orders > 0 THEN total_spent END) as avg_revenue_per_paying_customer
        FROM customer_cohorts
        GROUP BY signup_cohort
        ORDER BY signup_cohort
    """).fetchdf()
    print(result)

def data_quality_analysis(conn):
    """Demonstrate data quality and validation queries."""
    print("\n=== Data Quality Analysis ===")
    
    # Check for data inconsistencies
    print("1. Data quality checks:")
    
    # Missing or invalid data
    result = conn.execute("""
        SELECT 
            'Customers with missing email' as check_description,
            COUNT(*) as issue_count
        FROM customers 
        WHERE email IS NULL OR email = '' OR email NOT LIKE '%@%'
        
        UNION ALL
        
        SELECT 
            'Products with zero or negative price',
            COUNT(*)
        FROM products 
        WHERE price <= 0
        
        UNION ALL
        
        SELECT 
            'Orders without items',
            COUNT(*)
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE oi.order_id IS NULL
        
        UNION ALL
        
        SELECT 
            'Order items with mismatched prices',
            COUNT(*)
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        WHERE ABS(oi.unit_price - p.price) > 0.01
    """).fetchdf()
    print(result)
    
    # Statistical summaries
    print("\n2. Statistical summaries:")
    result = conn.execute("""
        SELECT 
            'Order Value' as metric,
            COUNT(*) as count,
            ROUND(MIN(total_value), 2) as min_value,
            ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_value), 2) as q1,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_value), 2) as median,
            ROUND(AVG(total_value), 2) as mean,
            ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_value), 2) as q3,
            ROUND(MAX(total_value), 2) as max_value,
            ROUND(STDDEV(total_value), 2) as std_dev
        FROM (
            SELECT 
                o.order_id,
                SUM(oi.quantity * oi.unit_price) as total_value
            FROM orders o
            INNER JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed'
            GROUP BY o.order_id
        ) order_totals
    """).fetchdf()
    print(result)

def main():
    """Main function to run all SQL operation examples."""
    try:
        # Connect to DuckDB
        conn = duckdb.connect()
        print("✅ Connected to DuckDB")
        
        # Setup comprehensive dataset
        setup_comprehensive_dataset(conn)
        
        # Run all SQL examples
        basic_sql_operations(conn)
        joins_and_relationships(conn)
        aggregation_and_grouping(conn)
        window_functions(conn)
        common_table_expressions(conn)
        advanced_analytics(conn)
        data_quality_analysis(conn)
        
        print("\n🎉 All SQL operations examples completed successfully!")
        
        print("\n📚 SQL Features Demonstrated:")
        print("✅ Basic SQL operations (SELECT, WHERE, ORDER BY)")
        print("✅ String and date functions")
        print("✅ JOINs (INNER, LEFT, complex multi-table)")
        print("✅ Aggregation functions and GROUP BY")
        print("✅ HAVING clauses")
        print("✅ Window functions (RANK, ROW_NUMBER, moving averages)")
        print("✅ Common Table Expressions (CTEs)")
        print("✅ Recursive CTEs")
        print("✅ Advanced analytics (cohort analysis, quartiles)")
        print("✅ Data quality validation")
        print("✅ Statistical functions")
        
        print("\n💡 DuckDB SQL Advantages:")
        print("- Fast analytical queries")
        print("- Full SQL standard compliance") 
        print("- Advanced window functions")
        print("- Excellent aggregation performance")
        print("- Support for complex data types")
        print("- Built-in statistical functions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        if 'conn' in locals():
            conn.close()
            print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()