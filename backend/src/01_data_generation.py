"""
E-commerce Data Generation Script
===============================

Generates realistic e-commerce datasets for analysis with DuckDB.
This script creates comprehensive test data including customers, products,
orders, and web analytics data with realistic business patterns.
"""

import sys
import os
import duckdb
from pathlib import Path

# Add utils to path for imports
current_dir = Path(__file__).parent
utils_dir = current_dir / "utils"
sys.path.insert(0, str(utils_dir))

from data_generator import EcommerceDataGenerator


def main():
    """Generate and save all e-commerce datasets."""

    print("🏪 E-commerce Analytics Data Generation")
    print("=" * 50)

    # Configuration - use minimal data for CI/testing
    minimal_mode = os.environ.get("MINIMAL_DATA", "false").lower() == "true"
    
    if minimal_mode:
        config = {
            "num_customers": 100,
            "num_products": 50,
            "num_orders": 200,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }
        print("🏃 Running in MINIMAL mode for faster setup")
    else:
        config = {
            "num_customers": 10000,
            "num_products": 1000,
            "num_orders": 50000,
            "start_date": "2022-01-01",
            "end_date": "2024-12-31",
        }

    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value:,}" if isinstance(value, int) else f"  {key}: {value}")
    print()

    # Initialize generator
    generator = EcommerceDataGenerator(**config)

    # Generate all datasets
    datasets = generator.generate_all_data()

    # Setup data directory
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("\n💾 Saving datasets...")

    # Save as CSV files
    csv_files = {}
    for name, df in datasets.items():
        csv_path = data_dir / f"{name}.csv"
        df.to_csv(csv_path, index=False)
        csv_files[name] = csv_path
        print(f"  ✅ Saved {name}: {len(df):,} rows → {csv_path.name}")

    # Create DuckDB database and load data
    print("\n🦆 Creating DuckDB database...")
    db_path = data_dir / "ecommerce.duckdb"

    with duckdb.connect(str(db_path)) as conn:
        # Create tables and load data
        for name, df in datasets.items():
            table_name = name

            # Create table from DataFrame
            conn.register(f"{name}_temp", df)
            conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {name}_temp")

            print(f"  ✅ Created table '{table_name}': {len(df):,} rows")

        # Create some useful views
        print("\n📊 Creating analytical views...")

        # Monthly revenue view
        conn.execute(
            """
            CREATE OR REPLACE VIEW monthly_revenue AS
            SELECT
                DATE_TRUNC('month', order_date) as month,
                COUNT(*) as order_count,
                SUM(total_amount) as revenue,
                AVG(total_amount) as avg_order_value
            FROM orders
            WHERE status = 'Completed'
            GROUP BY DATE_TRUNC('month', order_date)
            ORDER BY month
        """
        )

        # Customer lifetime value view
        conn.execute(
            """
            CREATE OR REPLACE VIEW customer_ltv AS
            SELECT
                c.customer_id,
                c.customer_segment,
                c.acquisition_channel,
                COUNT(o.order_id) as total_orders,
                SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) as lifetime_value,
                AVG(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE NULL END) as avg_order_value,
                MIN(o.order_date) as first_order_date,
                MAX(o.order_date) as last_order_date
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_segment, c.acquisition_channel
        """
        )

        # Product performance view
        conn.execute(
            """
            CREATE OR REPLACE VIEW product_performance AS
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                p.price,
                COUNT(oi.order_id) as times_ordered,
                SUM(oi.quantity) as total_quantity_sold,
                SUM(oi.total_price) as total_revenue,
                AVG(oi.unit_price) as avg_selling_price,
                (AVG(oi.unit_price) - p.cost) as avg_profit_per_unit
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost
        """
        )

        print("  ✅ Created monthly_revenue view")
        print("  ✅ Created customer_ltv view")
        print("  ✅ Created product_performance view")

        # Show database summary
        print("\n📈 Database Summary:")
        tables = conn.execute("SHOW TABLES").fetchall()
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  📋 {table_name}: {count:,} rows")

        print("\n🎯 Sample Insights:")

        # Total revenue
        total_revenue = conn.execute(
            """
            SELECT SUM(total_amount) FROM orders WHERE status = 'Completed'
        """
        ).fetchone()[0]
        print(f"  💰 Total Revenue: ${total_revenue:,.2f}")

        # Customer segments
        segments = conn.execute(
            """
            SELECT customer_segment, COUNT(*) as count, AVG(lifetime_value) as avg_ltv
            FROM customer_ltv
            WHERE total_orders > 0
            GROUP BY customer_segment
            ORDER BY avg_ltv DESC
        """
        ).fetchall()

        print("  👥 Customer Segments (by avg LTV):")
        for segment, count, avg_ltv in segments:
            print(f"     {segment}: {count:,} customers, ${avg_ltv:.2f} avg LTV")

        # Top categories
        categories = conn.execute(
            """
            SELECT category, SUM(total_revenue) as revenue
            FROM product_performance
            GROUP BY category
            ORDER BY revenue DESC
            LIMIT 5
        """
        ).fetchall()

        print("  🏆 Top Product Categories:")
        for category, revenue in categories:
            print(f"     {category}: ${revenue:,.2f}")

    print("\n🚀 Setup Complete!")
    print(f"   📁 Data files: {data_dir}/")
    print(f"   🗄️  Database: {db_path}")
    print("   📊 Ready for analysis!")

    print(f"\n🔄 Next Steps:")
    print(f"   1. Run: python 02_basic_analysis.py")
    print(f"   2. Open: jupyter notebook")
    print(f"   3. Explore: streamlit run dashboard.py")


if __name__ == "__main__":
    main()
