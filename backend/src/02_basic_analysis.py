"""
E-commerce Analytics - Core Business Queries
===========================================

This script demonstrates key business analytics queries using DuckDB
for e-commerce data analysis. Includes revenue analysis, customer insights,
product performance, and marketing attribution.
"""

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# Setup
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


def connect_to_database():
    """Connect to the e-commerce DuckDB database."""
    data_dir = Path(__file__).parent.parent / "data"
    db_path = data_dir / "ecommerce.duckdb"

    if not db_path.exists():
        print("❌ Database not found. Please run 01_data_generation.py first!")
        return None

    print(f"🦆 Connecting to database: {db_path}")
    return duckdb.connect(str(db_path))


def revenue_analysis(conn):
    """Analyze revenue trends and patterns."""
    print("\n💰 REVENUE ANALYSIS")
    print("=" * 50)

    # Monthly revenue trend
    print("📈 Monthly Revenue Trend:")
    monthly_revenue = conn.execute(
        """
        SELECT
            month,
            order_count,
            ROUND(revenue, 2) as revenue,
            ROUND(avg_order_value, 2) as avg_order_value,
            ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2) as revenue_change
        FROM monthly_revenue
        ORDER BY month
    """
    ).fetchdf()

    print(monthly_revenue.to_string(index=False))

    # Revenue by customer segment
    print("\n👥 Revenue by Customer Segment:")
    segment_revenue = conn.execute(
        """
        SELECT
            c.customer_segment,
            COUNT(DISTINCT c.customer_id) as customers,
            COUNT(o.order_id) as orders,
            ROUND(SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END), 2) as total_revenue,
            ROUND(AVG(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE NULL END), 2) as avg_order_value,
            ROUND(COUNT(o.order_id) * 1.0 / COUNT(DISTINCT c.customer_id), 2) as orders_per_customer
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_segment
        ORDER BY total_revenue DESC
    """
    ).fetchdf()

    print(segment_revenue.to_string(index=False))

    # Revenue by product category
    print("\n🏷️ Revenue by Product Category:")
    category_revenue = conn.execute(
        """
        SELECT
            p.category,
            COUNT(DISTINCT p.product_id) as products,
            SUM(oi.quantity) as units_sold,
            ROUND(SUM(oi.total_price), 2) as total_revenue,
            ROUND(AVG(oi.unit_price), 2) as avg_selling_price,
            ROUND(SUM(oi.total_price) / SUM(oi.quantity), 2) as revenue_per_unit
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """
    ).fetchdf()

    print(category_revenue.to_string(index=False))

    return monthly_revenue, segment_revenue, category_revenue


def customer_analysis(conn):
    """Analyze customer behavior and lifetime value."""
    print("\n🎯 CUSTOMER ANALYSIS")
    print("=" * 50)

    # Customer acquisition analysis
    print("📊 Customer Acquisition by Channel:")
    acquisition = conn.execute(
        """
        SELECT
            acquisition_channel,
            COUNT(*) as customers,
            ROUND(AVG(lifetime_value), 2) as avg_ltv,
            ROUND(AVG(total_orders), 2) as avg_orders,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as pct_of_customers
        FROM customer_ltv
        WHERE total_orders > 0
        GROUP BY acquisition_channel
        ORDER BY avg_ltv DESC
    """
    ).fetchdf()

    print(acquisition.to_string(index=False))

    # Customer cohort analysis (monthly)
    print("\n📅 Customer Cohort Analysis (First 6 months):")
    cohorts = conn.execute(
        """
        WITH customer_cohorts AS (
            SELECT
                c.customer_id,
                DATE_TRUNC('month', c.registration_date) as cohort_month,
                MIN(o.order_date) as first_order_month
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Completed'
            WHERE c.registration_date >= '2024-01-01'
            GROUP BY c.customer_id, DATE_TRUNC('month', c.registration_date)
        ),
        cohort_table AS (
            SELECT
                cohort_month,
                DATE_DIFF('month', cohort_month, first_order_month) as month_number,
                COUNT(DISTINCT customer_id) as customers
            FROM customer_cohorts
            WHERE first_order_month IS NOT NULL
            GROUP BY cohort_month, DATE_DIFF('month', cohort_month, first_order_month)
        )
        SELECT
            cohort_month,
            SUM(CASE WHEN month_number = 0 THEN customers ELSE 0 END) as month_0,
            SUM(CASE WHEN month_number = 1 THEN customers ELSE 0 END) as month_1,
            SUM(CASE WHEN month_number = 2 THEN customers ELSE 0 END) as month_2,
            SUM(CASE WHEN month_number = 3 THEN customers ELSE 0 END) as month_3,
            SUM(CASE WHEN month_number = 4 THEN customers ELSE 0 END) as month_4,
            SUM(CASE WHEN month_number = 5 THEN customers ELSE 0 END) as month_5
        FROM cohort_table
        GROUP BY cohort_month
        ORDER BY cohort_month
        LIMIT 10
    """
    ).fetchdf()

    print(cohorts.to_string(index=False))

    # RFM Analysis (Recency, Frequency, Monetary)
    print("\n🔍 RFM Customer Segmentation:")
    rfm = conn.execute(
        """
        WITH rfm_metrics AS (
            SELECT
                c.customer_id,
                DATE_DIFF('day', MAX(o.order_date), '2024-12-31') as recency,
                COUNT(o.order_id) as frequency,
                SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) as monetary
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            WHERE c.registration_date <= '2024-12-01'  -- At least 1 month to evaluate
            GROUP BY c.customer_id
        ),
        rfm_scores AS (
            SELECT
                customer_id,
                recency,
                frequency,
                monetary,
                NTILE(5) OVER (ORDER BY recency DESC) as r_score,
                NTILE(5) OVER (ORDER BY frequency) as f_score,
                NTILE(5) OVER (ORDER BY monetary) as m_score
            FROM rfm_metrics
            WHERE monetary > 0  -- Only customers who made purchases
        ),
        rfm_segments AS (
            SELECT
                customer_id,
                CASE
                    WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
                    WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
                    WHEN r_score >= 3 AND f_score >= 2 THEN 'Potential Loyalists'
                    WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
                    WHEN r_score >= 2 AND f_score >= 3 THEN 'At Risk'
                    WHEN r_score <= 2 AND f_score >= 4 THEN 'Cannot Lose Them'
                    WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating'
                    ELSE 'Others'
                END as rfm_segment,
                recency,
                frequency,
                monetary
            FROM rfm_scores
        )
        SELECT
            rfm_segment,
            COUNT(*) as customers,
            ROUND(AVG(recency), 1) as avg_recency_days,
            ROUND(AVG(frequency), 1) as avg_frequency,
            ROUND(AVG(monetary), 2) as avg_monetary
        FROM rfm_segments
        GROUP BY rfm_segment
        ORDER BY AVG(monetary) DESC
    """
    ).fetchdf()

    print(rfm.to_string(index=False))

    return acquisition, cohorts, rfm


def product_analysis(conn):
    """Analyze product performance and inventory insights."""
    print("\n📦 PRODUCT ANALYSIS")
    print("=" * 50)

    # Top performing products
    print("🏆 Top 10 Products by Revenue:")
    top_products = conn.execute(
        """
        SELECT
            product_name,
            category,
            times_ordered,
            total_quantity_sold,
            ROUND(total_revenue, 2) as revenue,
            ROUND(avg_selling_price, 2) as avg_price,
            ROUND(avg_profit_per_unit, 2) as profit_per_unit
        FROM product_performance
        WHERE times_ordered > 0
        ORDER BY total_revenue DESC
        LIMIT 10
    """
    ).fetchdf()

    print(top_products.to_string(index=False))

    # Product category analysis
    print("\n📊 Category Performance Analysis:")
    category_analysis = conn.execute(
        """
        SELECT
            category,
            COUNT(*) as total_products,
            COUNT(CASE WHEN times_ordered > 0 THEN 1 END) as products_sold,
            ROUND(COUNT(CASE WHEN times_ordered > 0 THEN 1 END) * 100.0 / COUNT(*), 1) as sell_through_rate,
            ROUND(AVG(CASE WHEN times_ordered > 0 THEN total_revenue END), 2) as avg_revenue_per_product,
            ROUND(SUM(total_revenue), 2) as category_revenue
        FROM product_performance
        GROUP BY category
        ORDER BY category_revenue DESC
    """
    ).fetchdf()

    print(category_analysis.to_string(index=False))

    # Slow moving inventory
    print("\n⚠️ Slow Moving Products (Need Attention):")
    slow_movers = conn.execute(
        """
        SELECT
            product_name,
            category,
            ROUND(price, 2) as current_price,
            COALESCE(times_ordered, 0) as times_ordered,
            COALESCE(total_quantity_sold, 0) as quantity_sold,
            COALESCE(ROUND(total_revenue, 2), 0) as revenue
        FROM product_performance
        WHERE times_ordered IS NULL OR times_ordered <= 5
        ORDER BY price DESC
        LIMIT 15
    """
    ).fetchdf()

    print(slow_movers.to_string(index=False))

    return top_products, category_analysis, slow_movers


def marketing_analysis(conn):
    """Analyze marketing effectiveness and conversion funnels."""
    print("\n🎯 MARKETING ANALYSIS")
    print("=" * 50)

    # Traffic source performance
    print("📊 Traffic Source Performance:")
    traffic_analysis = conn.execute(
        """
        SELECT
            traffic_source,
            COUNT(*) as sessions,
            SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) as conversions,
            ROUND(SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as conversion_rate,
            ROUND(AVG(session_duration_seconds), 0) as avg_session_duration,
            ROUND(AVG(page_views), 1) as avg_page_views,
            ROUND(SUM(revenue), 2) as total_revenue,
            ROUND(SUM(revenue) / COUNT(*), 2) as revenue_per_session
        FROM web_sessions
        GROUP BY traffic_source
        ORDER BY total_revenue DESC
    """
    ).fetchdf()

    print(traffic_analysis.to_string(index=False))

    # Device performance
    print("\n📱 Device Type Performance:")
    device_analysis = conn.execute(
        """
        SELECT
            device_type,
            COUNT(*) as sessions,
            ROUND(AVG(session_duration_seconds), 0) as avg_duration,
            ROUND(AVG(page_views), 1) as avg_page_views,
            ROUND(SUM(CASE WHEN bounced = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as bounce_rate,
            ROUND(SUM(CASE WHEN converted = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as conversion_rate
        FROM web_sessions
        GROUP BY device_type
        ORDER BY conversion_rate DESC
    """
    ).fetchdf()

    print(device_analysis.to_string(index=False))

    # Attribution analysis - first touch vs last touch
    print("\n🔍 Attribution Analysis (Customer Acquisition vs Orders):")
    attribution = conn.execute(
        """
        WITH customer_attribution AS (
            SELECT
                c.customer_id,
                c.acquisition_channel as first_touch_channel,
                COUNT(o.order_id) as total_orders,
                SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) as lifetime_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.acquisition_channel
        ),
        order_attribution AS (
            SELECT
                ws.traffic_source as last_touch_channel,
                COUNT(o.order_id) as orders,
                SUM(o.total_amount) as revenue
            FROM orders o
            JOIN web_sessions ws ON o.customer_id = ws.customer_id
                AND DATE(o.order_date) = DATE(ws.session_date)
                AND ws.converted = true
            WHERE o.status = 'Completed'
            GROUP BY ws.traffic_source
        )
        SELECT
            'First Touch (Acquisition)' as attribution_type,
            first_touch_channel as channel,
            COUNT(*) as customers_acquired,
            ROUND(AVG(lifetime_value), 2) as avg_customer_ltv,
            ROUND(SUM(lifetime_value), 2) as total_ltv
        FROM customer_attribution
        WHERE total_orders > 0
        GROUP BY first_touch_channel

        UNION ALL

        SELECT
            'Last Touch (Orders)' as attribution_type,
            last_touch_channel as channel,
            orders as customers_acquired,
            ROUND(revenue / orders, 2) as avg_customer_ltv,
            ROUND(revenue, 2) as total_ltv
        FROM order_attribution
        ORDER BY attribution_type, total_ltv DESC
    """
    ).fetchdf()

    print(attribution.to_string(index=False))

    return traffic_analysis, device_analysis, attribution


def create_visualizations(monthly_revenue, segment_revenue, category_revenue):
    """Create key visualizations for the analysis."""
    print("\n📊 Creating Visualizations...")

    # Setup visualization directory
    viz_dir = Path(__file__).parent.parent / "visualizations"
    viz_dir.mkdir(exist_ok=True)

    # 1. Monthly Revenue Trend
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.plot(
        pd.to_datetime(monthly_revenue["month"]),
        monthly_revenue["revenue"],
        marker="o",
        linewidth=2,
    )
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)

    # 2. Customer Segment Revenue Distribution
    plt.subplot(2, 2, 2)
    colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
    plt.pie(
        segment_revenue["total_revenue"],
        labels=segment_revenue["customer_segment"],
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
    )
    plt.title("Revenue by Customer Segment")

    # 3. Category Revenue Bar Chart
    plt.subplot(2, 2, 3)
    plt.bar(
        category_revenue["category"],
        category_revenue["total_revenue"],
        color="steelblue",
        alpha=0.7,
    )
    plt.title("Revenue by Product Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue ($)")
    plt.xticks(rotation=45, ha="right")

    # 4. Average Order Value by Segment
    plt.subplot(2, 2, 4)
    plt.bar(
        segment_revenue["customer_segment"],
        segment_revenue["avg_order_value"],
        color="lightcoral",
        alpha=0.7,
    )
    plt.title("Average Order Value by Segment")
    plt.xlabel("Customer Segment")
    plt.ylabel("Average Order Value ($)")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(viz_dir / "ecommerce_dashboard.png", dpi=300, bbox_inches="tight")
    print(f"  ✅ Saved dashboard: {viz_dir / 'ecommerce_dashboard.png'}")

    plt.show()


def main():
    """Main analysis pipeline."""
    print("🏪 E-COMMERCE ANALYTICS DASHBOARD")
    print("=" * 60)

    # Connect to database
    conn = connect_to_database()
    if not conn:
        return

    try:
        # Run all analyses
        monthly_revenue, segment_revenue, category_revenue = revenue_analysis(conn)
        acquisition, cohorts, rfm = customer_analysis(conn)
        top_products, category_analysis, slow_movers = product_analysis(conn)
        traffic_analysis, device_analysis, attribution = marketing_analysis(conn)

        # Create visualizations
        create_visualizations(monthly_revenue, segment_revenue, category_revenue)

        print(f"\n🎯 KEY INSIGHTS SUMMARY")
        print("=" * 50)

        # Calculate key metrics
        total_revenue = segment_revenue["total_revenue"].sum()
        total_customers = segment_revenue["customers"].sum()
        avg_ltv = total_revenue / total_customers

        print(f"💰 Total Revenue: ${total_revenue:,.2f}")
        print(f"👥 Total Customers: {total_customers:,}")
        print(f"📈 Average Customer LTV: ${avg_ltv:.2f}")
        top_cat = category_revenue.iloc[0]["category"]
        top_cat_revenue = category_revenue.iloc[0]["total_revenue"]
        print(f"🏆 Top Category: {top_cat} (${top_cat_revenue:,.2f})")

        best_traffic = traffic_analysis.iloc[0]["traffic_source"]
        best_traffic_rate = traffic_analysis.iloc[0]["conversion_rate"]
        print(f"🎯 Best Traffic Source: {best_traffic} ({best_traffic_rate:.2f}% conversion)")

        best_device = device_analysis.iloc[0]["device_type"]
        best_device_rate = device_analysis.iloc[0]["conversion_rate"]
        print(f"📱 Best Device: {best_device} ({best_device_rate:.2f}% conversion)")

        print(f"\n🔄 Next Steps:")
        print(f"   1. Run: streamlit run src/03_dashboard.py")
        print(f"   2. Explore: jupyter notebook analysis/")
        print(f"   3. Check visualizations in: visualizations/")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
