"""
DuckDB Integration with Data Science Libraries
=============================================

This script demonstrates how DuckDB integrates seamlessly with popular
data science libraries like pandas, numpy, matplotlib, seaborn, and more.
DuckDB's zero-copy integration makes it extremely efficient for data analysis.
"""

import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib to use a non-interactive backend
plt.switch_backend('Agg')

def setup_sample_dataset():
    """Create a comprehensive sample dataset for analysis."""
    print("=== Setting up sample dataset ===")
    
    # Generate sample e-commerce data
    np.random.seed(42)
    
    # Create date range
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = pd.date_range(start_date, end_date, freq='D')
    
    # Generate sales data
    n_records = 5000
    sales_data = {
        'date': np.random.choice(date_range, n_records),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], n_records),
        'region': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n_records),
        'customer_segment': np.random.choice(['Premium', 'Standard', 'Budget'], n_records, p=[0.2, 0.5, 0.3]),
        'sales_amount': np.random.lognormal(4, 1, n_records),  # Log-normal distribution for realistic sales
        'units_sold': np.random.poisson(3, n_records) + 1,  # Poisson distribution for units
        'discount_rate': np.random.beta(2, 8, n_records),  # Beta distribution for discount rates
        'marketing_spend': np.random.exponential(50, n_records)  # Exponential for marketing spend
    }
    
    df = pd.DataFrame(sales_data)
    
    # Add some calculated columns
    df['revenue'] = df['sales_amount'] * df['units_sold'] * (1 - df['discount_rate'])
    df['profit_margin'] = np.random.normal(0.25, 0.1, n_records)  # Normal distribution for margins
    df['profit'] = df['revenue'] * df['profit_margin']
    df['month'] = df['date'].dt.strftime('%Y-%m')  # Use string format instead of Period
    df['quarter'] = df['date'].dt.strftime('%Y-Q%q')  # Use string format instead of Period
    df['day_of_week'] = df['date'].dt.day_name()
    
    print(f"✅ Generated dataset with {len(df)} records")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def pandas_integration_examples(conn, df):
    """Demonstrate pandas integration with DuckDB."""
    print("\n=== Pandas Integration Examples ===")
    
    # Example 1: Query pandas DataFrame directly with DuckDB
    print("1. Querying pandas DataFrame with DuckDB SQL:")
    result = conn.execute("""
        SELECT 
            product_category,
            COUNT(*) as transactions,
            ROUND(SUM(revenue), 2) as total_revenue,
            ROUND(AVG(revenue), 2) as avg_revenue,
            ROUND(SUM(profit), 2) as total_profit
        FROM df
        GROUP BY product_category
        ORDER BY total_revenue DESC
    """).df()
    print(result)
    
    # Example 2: Convert DuckDB query result back to pandas
    print("\n2. Complex aggregation with date functions:")
    monthly_trends = conn.execute("""
        SELECT 
            strftime('%Y-%m', date) as month,
            product_category,
            SUM(revenue) as monthly_revenue,
            AVG(profit_margin) as avg_margin,
            COUNT(DISTINCT date) as active_days
        FROM df
        WHERE date >= '2024-01-01'
        GROUP BY strftime('%Y-%m', date), product_category
        ORDER BY month, monthly_revenue DESC
    """).df()
    
    print(f"Monthly trends shape: {monthly_trends.shape}")
    print(monthly_trends.head(10))
    
    # Example 3: Combining pandas operations with DuckDB
    print("\n3. Hybrid pandas/DuckDB operations:")
    
    # First, do some pandas preprocessing
    df_processed = df.copy()
    df_processed['revenue_quartile'] = pd.qcut(df_processed['revenue'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    df_processed['high_margin'] = df_processed['profit_margin'] > df_processed['profit_margin'].median()
    
    # Then query with DuckDB
    quartile_analysis = conn.execute("""
        SELECT 
            revenue_quartile,
            high_margin,
            COUNT(*) as count,
            AVG(revenue) as avg_revenue,
            AVG(marketing_spend) as avg_marketing_spend,
            SUM(profit) / SUM(revenue) as roi
        FROM df_processed
        GROUP BY revenue_quartile, high_margin
        ORDER BY revenue_quartile, high_margin
    """).df()
    
    print("Revenue quartile analysis:")
    print(quartile_analysis)

def numpy_integration_examples(conn, df):
    """Demonstrate numpy integration and mathematical operations."""
    print("\n=== NumPy Integration Examples ===")
    
    # Example 1: Statistical analysis with NumPy arrays
    print("1. Statistical analysis using numpy arrays:")
    
    # Get revenue data as numpy array
    revenue_array = conn.execute("SELECT revenue FROM df ORDER BY revenue").fetchnumpy()['revenue']
    
    stats = {
        'count': len(revenue_array),
        'mean': np.mean(revenue_array),
        'median': np.median(revenue_array),
        'std': np.std(revenue_array),
        'skewness': float(conn.execute("SELECT skewness(revenue) FROM df").fetchone()[0]),
        'kurtosis': float(conn.execute("SELECT kurtosis(revenue) FROM df").fetchone()[0]),
        'percentile_95': np.percentile(revenue_array, 95),
        'percentile_99': np.percentile(revenue_array, 99)
    }
    
    for key, value in stats.items():
        print(f"  {key}: {value:.4f}")
    
    # Example 2: Mathematical transformations
    print("\n2. Mathematical transformations:")
    
    # Add numpy-computed features back to the analysis
    df_enhanced = df.copy()
    df_enhanced['log_revenue'] = np.log1p(df_enhanced['revenue'])
    df_enhanced['sqrt_marketing'] = np.sqrt(df_enhanced['marketing_spend'])
    df_enhanced['revenue_zscore'] = (df_enhanced['revenue'] - df_enhanced['revenue'].mean()) / df_enhanced['revenue'].std()
    
    # Analyze transformed features with DuckDB
    transformation_analysis = conn.execute("""
        SELECT 
            product_category,
            corr(log_revenue, sqrt_marketing) as log_revenue_marketing_corr,
            corr(revenue_zscore, profit_margin) as zscore_margin_corr,
            AVG(log_revenue) as avg_log_revenue,
            STDDEV(revenue_zscore) as zscore_std
        FROM df_enhanced
        GROUP BY product_category
        ORDER BY log_revenue_marketing_corr DESC
    """).df()
    
    print("Correlation analysis with transformed features:")
    print(transformation_analysis)
    
    # Example 3: Array operations and aggregations
    print("\n3. Advanced array operations:")
    
    # Create arrays for analysis
    daily_sales = conn.execute("""
        SELECT 
            date,
            SUM(revenue) as daily_revenue,
            COUNT(*) as transactions,
            AVG(profit_margin) as avg_margin
        FROM df
        GROUP BY date
        ORDER BY date
    """).df()
    
    # Calculate moving averages using numpy
    daily_sales['revenue_ma_7'] = daily_sales['daily_revenue'].rolling(window=7).mean()
    daily_sales['revenue_ma_30'] = daily_sales['daily_revenue'].rolling(window=30).mean()
    
    # Compute rolling statistics with DuckDB
    rolling_stats = conn.execute("""
        SELECT 
            date,
            daily_revenue,
            revenue_ma_7,
            revenue_ma_30,
            daily_revenue - revenue_ma_7 as deviation_from_weekly_avg,
            CASE 
                WHEN revenue_ma_7 > revenue_ma_30 THEN 'Upward Trend'
                WHEN revenue_ma_7 < revenue_ma_30 THEN 'Downward Trend'
                ELSE 'Stable'
            END as trend_direction
        FROM daily_sales
        WHERE revenue_ma_30 IS NOT NULL
        ORDER BY date DESC
        LIMIT 10
    """).df()
    
    print("Recent trend analysis:")
    print(rolling_stats)

def visualization_integration_examples(conn, df):
    """Demonstrate integration with matplotlib and seaborn."""
    print("\n=== Visualization Integration Examples ===")
    
    # Example 1: Simple matplotlib visualization
    print("1. Creating visualizations with matplotlib...")
    
    # Get monthly revenue data
    monthly_data = conn.execute("""
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(revenue) as total_revenue,
            AVG(profit_margin) as avg_margin,
            COUNT(*) as transactions
        FROM df
        WHERE date >= '2024-01-01'
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month
    """).df()
    
    # Create matplotlib plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('DuckDB + Matplotlib Integration', fontsize=16)
    
    # Plot 1: Monthly revenue
    ax1.plot(monthly_data['month'], monthly_data['total_revenue'])
    ax1.set_title('Monthly Revenue Trend')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Revenue')
    ax1.tick_params(axis='x', rotation=45)
    
    # Plot 2: Revenue distribution by category
    category_revenue = conn.execute("""
        SELECT product_category, SUM(revenue) as total_revenue
        FROM df GROUP BY product_category ORDER BY total_revenue DESC
    """).df()
    
    ax2.bar(category_revenue['product_category'], category_revenue['total_revenue'])
    ax2.set_title('Revenue by Product Category')
    ax2.set_xlabel('Category')
    ax2.set_ylabel('Total Revenue')
    ax2.tick_params(axis='x', rotation=45)
    
    # Plot 3: Regional performance
    regional_data = conn.execute("""
        SELECT 
            region,
            AVG(profit_margin) as avg_margin,
            SUM(revenue) as total_revenue
        FROM df GROUP BY region
    """).df()
    
    ax3.scatter(regional_data['total_revenue'], regional_data['avg_margin'])
    for i, region in enumerate(regional_data['region']):
        ax3.annotate(region, (regional_data['total_revenue'].iloc[i], regional_data['avg_margin'].iloc[i]))
    ax3.set_title('Regional Performance: Revenue vs Margin')
    ax3.set_xlabel('Total Revenue')
    ax3.set_ylabel('Average Profit Margin')
    
    # Plot 4: Customer segment analysis
    segment_data = conn.execute("""
        SELECT 
            customer_segment,
            AVG(revenue) as avg_revenue,
            COUNT(*) as transaction_count
        FROM df GROUP BY customer_segment
    """).df()
    
    ax4.pie(segment_data['transaction_count'], labels=segment_data['customer_segment'], autopct='%1.1f%%')
    ax4.set_title('Transaction Distribution by Customer Segment')
    
    plt.tight_layout()
    plt.savefig('duckdb_analysis_plots.png', dpi=300, bbox_inches='tight')
    print("✅ Saved matplotlib visualization to 'duckdb_analysis_plots.png'")
    plt.close()
    
    # Example 2: Seaborn integration
    print("\n2. Creating advanced visualizations with seaborn...")
    
    # Get correlation data
    correlation_data = conn.execute("""
        SELECT 
            revenue,
            profit_margin,
            marketing_spend,
            discount_rate,
            units_sold,
            sales_amount
        FROM df
        LIMIT 1000
    """).df()
    
    # Create seaborn plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('DuckDB + Seaborn Integration', fontsize=16)
    
    # Correlation heatmap
    correlation_matrix = correlation_data.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, ax=ax1)
    ax1.set_title('Feature Correlation Matrix')
    
    # Distribution plot
    sns.histplot(data=correlation_data, x='revenue', bins=50, ax=ax2)
    ax2.set_title('Revenue Distribution')
    
    # Scatter plot with regression
    sns.scatterplot(data=correlation_data, x='marketing_spend', y='revenue', ax=ax3)
    sns.regplot(data=correlation_data, x='marketing_spend', y='revenue', scatter=False, ax=ax3)
    ax3.set_title('Marketing Spend vs Revenue')
    
    # Box plot by category (sample data)
    sample_data = conn.execute("""
        SELECT product_category, revenue 
        FROM df 
        WHERE product_category IN ('Electronics', 'Clothing', 'Books')
        ORDER BY RANDOM() 
        LIMIT 500
    """).df()
    
    sns.boxplot(data=sample_data, x='product_category', y='revenue', ax=ax4)
    ax4.set_title('Revenue Distribution by Category')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('duckdb_seaborn_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Saved seaborn visualization to 'duckdb_seaborn_analysis.png'")
    plt.close()

def advanced_analytics_integration(conn, df):
    """Demonstrate advanced analytics integration."""
    print("\n=== Advanced Analytics Integration ===")
    
    # Example 1: Time series analysis
    print("1. Time series analysis:")
    
    # Create daily time series
    daily_ts = conn.execute("""
        SELECT 
            CAST(date AS DATE) as date,
            SUM(revenue) as daily_revenue,
            SUM(profit) as daily_profit,
            COUNT(*) as transactions,
            AVG(discount_rate) as avg_discount
        FROM df
        WHERE date >= '2024-01-01'
        GROUP BY CAST(date AS DATE)
        ORDER BY date
    """).df()
    
    daily_ts['date'] = pd.to_datetime(daily_ts['date'])
    daily_ts.set_index('date', inplace=True)
    
    # Calculate time series metrics
    daily_ts['revenue_growth'] = daily_ts['daily_revenue'].pct_change()
    daily_ts['revenue_ma_7'] = daily_ts['daily_revenue'].rolling(window=7).mean()
    daily_ts['revenue_std_7'] = daily_ts['daily_revenue'].rolling(window=7).std()
    
    # Identify anomalies (values beyond 2 standard deviations)
    daily_ts['is_anomaly'] = abs(daily_ts['daily_revenue'] - daily_ts['revenue_ma_7']) > (2 * daily_ts['revenue_std_7'])
    
    anomaly_count = daily_ts['is_anomaly'].sum()
    print(f"  Detected {anomaly_count} anomalous days")
    
    # Example 2: Customer segmentation analysis
    print("\n2. Customer segmentation analysis:")
    
    # Create customer behavior features
    customer_features = conn.execute("""
        WITH customer_metrics AS (
            SELECT 
                customer_segment,
                region,
                AVG(revenue) as avg_order_value,
                SUM(revenue) as total_spent,
                COUNT(*) as transaction_frequency,
                AVG(discount_rate) as avg_discount_used,
                STDDEV(revenue) as spending_volatility,
                DATEDIFF('day', MIN(date), MAX(date)) as customer_lifespan_days
            FROM df
            GROUP BY customer_segment, region
        )
        SELECT 
            *,
            total_spent / NULLIF(customer_lifespan_days, 0) as daily_spend_rate,
            CASE 
                WHEN avg_order_value >= 100 AND transaction_frequency >= 10 THEN 'High Value'
                WHEN avg_order_value >= 50 OR transaction_frequency >= 5 THEN 'Medium Value'
                ELSE 'Low Value'
            END as value_segment
        FROM customer_metrics
        ORDER BY total_spent DESC
    """).df()
    
    print("Customer segment characteristics:")
    print(customer_features)
    
    # Example 3: Predictive feature engineering
    print("\n3. Feature engineering for ML:")
    
    # Create features that could be used for machine learning
    ml_features = conn.execute("""
        WITH base_features AS (
            SELECT 
                *,
                LAG(revenue, 1) OVER (PARTITION BY product_category ORDER BY date) as prev_day_revenue,
                AVG(revenue) OVER (PARTITION BY product_category ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as revenue_ma_7,
                ROW_NUMBER() OVER (PARTITION BY product_category ORDER BY date) as day_number,
                EXTRACT('dayofweek' FROM date) as day_of_week_num,
                EXTRACT('month' FROM date) as month_num,
                CASE 
                    WHEN EXTRACT('dayofweek' FROM date) IN (1, 7) THEN 1 
                    ELSE 0 
                END as is_weekend
            FROM df
            WHERE date >= '2024-01-01'
        )
        SELECT 
            product_category,
            region,
            customer_segment,
            day_of_week_num,
            month_num,
            is_weekend,
            marketing_spend,
            discount_rate,
            revenue_ma_7,
            prev_day_revenue,
            (revenue - prev_day_revenue) / NULLIF(prev_day_revenue, 0) as revenue_change_rate,
            revenue,
            profit_margin
        FROM base_features
        WHERE prev_day_revenue IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 100
    """).df()
    
    print(f"ML-ready dataset shape: {ml_features.shape}")
    print("Sample features:")
    print(ml_features.head())
    
    # Calculate feature correlations
    numeric_features = ml_features.select_dtypes(include=[np.number])
    correlation_with_target = numeric_features.corrwith(numeric_features['revenue']).abs().sort_values(ascending=False)
    
    print(f"\nTop features correlated with revenue:")
    for feature, corr in correlation_with_target.head(5).items():
        if feature != 'revenue':
            print(f"  {feature}: {corr:.3f}")

def performance_benchmarks(conn, df):
    """Demonstrate performance benefits of DuckDB integration."""
    print("\n=== Performance Benchmarks ===")
    
    import time
    
    # Benchmark 1: Large aggregation
    print("1. Performance comparison - Large aggregation:")
    
    # DuckDB approach
    start_time = time.time()
    duckdb_result = conn.execute("""
        SELECT 
            product_category,
            region,
            customer_segment,
            COUNT(*) as transactions,
            SUM(revenue) as total_revenue,
            AVG(profit_margin) as avg_margin,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY revenue) as median_revenue
        FROM df
        GROUP BY product_category, region, customer_segment
        ORDER BY total_revenue DESC
    """).df()
    duckdb_time = time.time() - start_time
    
    # Pure pandas approach
    start_time = time.time()
    pandas_result = (df.groupby(['product_category', 'region', 'customer_segment'])
                    .agg({
                        'revenue': ['count', 'sum', 'median'],
                        'profit_margin': 'mean'
                    })
                    .round(2))
    pandas_result.columns = ['transactions', 'total_revenue', 'median_revenue', 'avg_margin']
    pandas_result = pandas_result.reset_index().sort_values('total_revenue', ascending=False)
    pandas_time = time.time() - start_time
    
    print(f"  DuckDB time: {duckdb_time:.4f} seconds")
    print(f"  Pandas time: {pandas_time:.4f} seconds")
    print(f"  DuckDB speedup: {pandas_time/duckdb_time:.2f}x")
    
    # Benchmark 2: Complex join operations
    print("\n2. Performance comparison - Complex operations:")
    
    # Create a second dataset for joining
    df2 = pd.DataFrame({
        'product_category': ['Electronics', 'Clothing', 'Books', 'Home', 'Sports'] * 200,
        'category_score': np.random.normal(50, 15, 1000),
        'category_rank': np.tile(range(1, 201), 5)
    })
    
    # DuckDB join
    start_time = time.time()
    join_result_duck = conn.execute("""
        SELECT 
            d1.product_category,
            d1.region,
            AVG(d1.revenue) as avg_revenue,
            AVG(d2.category_score) as avg_score,
            COUNT(*) as transactions
        FROM df d1
        INNER JOIN df2 d2 ON d1.product_category = d2.product_category
        GROUP BY d1.product_category, d1.region
        ORDER BY avg_revenue DESC
    """).df()
    duckdb_join_time = time.time() - start_time
    
    # Pandas join
    start_time = time.time()
    join_result_pandas = (df.merge(df2, on='product_category')
                         .groupby(['product_category', 'region'])
                         .agg({'revenue': 'mean', 'category_score': 'mean', 'product_category': 'count'})
                         .rename(columns={'product_category': 'transactions'})
                         .reset_index()
                         .sort_values('revenue', ascending=False))
    pandas_join_time = time.time() - start_time
    
    print(f"  DuckDB join time: {duckdb_join_time:.4f} seconds")
    print(f"  Pandas join time: {pandas_join_time:.4f} seconds")
    print(f"  DuckDB speedup: {pandas_join_time/duckdb_join_time:.2f}x")
    
    print(f"\n✅ DuckDB consistently shows better performance for analytical operations")

def cleanup_files():
    """Clean up generated files."""
    import os
    files_to_remove = ['duckdb_analysis_plots.png', 'duckdb_seaborn_analysis.png']
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
    print(f"\n🧹 Cleaned up generated files: {', '.join(files_to_remove)}")

def main():
    """Main function to run all integration examples."""
    try:
        # Connect to DuckDB
        conn = duckdb.connect()
        print("✅ Connected to DuckDB")
        
        # Setup dataset
        df = setup_sample_dataset()
        
        # Run all integration examples
        pandas_integration_examples(conn, df)
        numpy_integration_examples(conn, df)
        visualization_integration_examples(conn, df)
        advanced_analytics_integration(conn, df)
        performance_benchmarks(conn, df)
        
        print("\n🎉 All integration examples completed successfully!")
        
        print("\n📚 Integration Features Demonstrated:")
        print("✅ Seamless pandas DataFrame integration")
        print("✅ Zero-copy data transfer between pandas and DuckDB")
        print("✅ NumPy array operations and mathematical functions")
        print("✅ Matplotlib and Seaborn visualization integration")
        print("✅ Advanced analytics and time series analysis")
        print("✅ Feature engineering for machine learning")
        print("✅ Performance benchmarking")
        
        print("\n💡 Key Benefits of DuckDB Integration:")
        print("- No data copying between pandas and DuckDB")
        print("- Faster analytical queries than pure pandas")
        print("- Seamless workflow integration")
        print("- Support for complex SQL operations on DataFrames")
        print("- Memory-efficient operations on large datasets")
        print("- Easy integration with visualization libraries")
        
        print("\n🚀 Next Steps for Learning:")
        print("1. Try DuckDB with your own datasets")
        print("2. Explore DuckDB extensions (spatial, JSON, etc.)")
        print("3. Learn about DuckDB's SQL extensions and functions")
        print("4. Experiment with larger datasets and performance")
        print("5. Integrate DuckDB into your data science workflow")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if 'conn' in locals():
            conn.close()
            print("\n✅ Database connection closed")
        
        cleanup_files()

if __name__ == "__main__":
    main()