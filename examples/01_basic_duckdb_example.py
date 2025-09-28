"""
DuckDB Basic Operations - Getting Started
=========================================

This script demonstrates the fundamental operations you can perform with DuckDB.
DuckDB is an in-process SQL OLAP database management system.
"""

import duckdb
import pandas as pd

def basic_connection_example():
    """Demonstrate basic DuckDB connection and operations."""
    print("=== Basic DuckDB Connection ===")
    
    # Method 1: In-memory database (data will be lost when connection closes)
    conn = duckdb.connect()
    
    # Method 2: Persistent database (data saved to file)
    # conn = duckdb.connect('my_database.db')
    
    print("✅ Connected to DuckDB successfully!")
    return conn

def create_table_example(conn):
    """Create a simple table and insert some data."""
    print("\n=== Creating Tables and Inserting Data ===")
    
    # Create a table
    conn.execute("""
        CREATE TABLE employees (
            id INTEGER,
            name VARCHAR,
            department VARCHAR,
            salary INTEGER,
            hire_date DATE
        )
    """)
    
    # Insert some sample data
    conn.execute("""
        INSERT INTO employees VALUES 
            (1, 'Alice Johnson', 'Engineering', 75000, '2022-01-15'),
            (2, 'Bob Smith', 'Marketing', 65000, '2021-06-20'),
            (3, 'Carol Davis', 'Engineering', 80000, '2020-03-10'),
            (4, 'David Wilson', 'Sales', 55000, '2023-02-01'),
            (5, 'Eve Brown', 'Marketing', 70000, '2021-11-30')
    """)
    
    print("✅ Created 'employees' table and inserted 5 records")

def basic_queries_example(conn):
    """Demonstrate basic SQL queries."""
    print("\n=== Basic SQL Queries ===")
    
    # Simple SELECT
    print("All employees:")
    result = conn.execute("SELECT * FROM employees").fetchall()
    for row in result:
        print(f"  {row}")
    
    # SELECT with WHERE clause
    print("\nEngineering department employees:")
    result = conn.execute("""
        SELECT name, salary 
        FROM employees 
        WHERE department = 'Engineering'
        ORDER BY salary DESC
    """).fetchall()
    for row in result:
        print(f"  {row[0]}: ${row[1]:,}")
    
    # Aggregate functions
    print("\nSalary statistics by department:")
    result = conn.execute("""
        SELECT 
            department,
            COUNT(*) as employee_count,
            AVG(salary) as avg_salary,
            MAX(salary) as max_salary,
            MIN(salary) as min_salary
        FROM employees 
        GROUP BY department
        ORDER BY avg_salary DESC
    """).fetchall()
    
    for row in result:
        print(f"  {row[0]}: {row[1]} employees, avg: ${row[2]:,.0f}, max: ${row[3]:,}, min: ${row[4]:,}")

def dataframe_integration_example(conn):
    """Demonstrate DuckDB integration with pandas DataFrames."""
    print("\n=== DuckDB + Pandas Integration ===")
    
    # Query DuckDB table into a pandas DataFrame
    df = conn.execute("SELECT * FROM employees").df()
    print("DuckDB table as pandas DataFrame:")
    print(df)
    print(f"\nDataFrame shape: {df.shape}")
    print(f"Data types:\n{df.dtypes}")
    
    # Create a new DataFrame and query it with DuckDB
    new_data = pd.DataFrame({
        'product': ['Widget A', 'Widget B', 'Widget C', 'Widget D'],
        'price': [19.99, 29.99, 39.99, 49.99],
        'category': ['Electronics', 'Electronics', 'Home', 'Home']
    })
    
    print(f"\n=== Querying pandas DataFrame with DuckDB ===")
    print("Original DataFrame:")
    print(new_data)
    
    # Query the DataFrame directly using DuckDB
    result = conn.execute("""
        SELECT 
            category,
            COUNT(*) as product_count,
            AVG(price) as avg_price,
            SUM(price) as total_price
        FROM new_data 
        GROUP BY category
        ORDER BY avg_price DESC
    """).df()
    
    print("\nAggregated results:")
    print(result)

def advanced_features_example(conn):
    """Demonstrate some advanced DuckDB features."""
    print("\n=== Advanced DuckDB Features ===")
    
    # Window functions
    print("Employee salary rankings within departments:")
    result = conn.execute("""
        SELECT 
            name,
            department,
            salary,
            RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
            DENSE_RANK() OVER (ORDER BY salary DESC) as overall_rank
        FROM employees
        ORDER BY department, dept_rank
    """).fetchall()
    
    for row in result:
        print(f"  {row[0]} ({row[1]}): ${row[2]:,} - Dept Rank: {row[3]}, Overall Rank: {row[4]}")
    
    # Date functions
    print("\nEmployee tenure analysis:")
    result = conn.execute("""
        SELECT 
            name,
            hire_date,
            DATEDIFF('day', hire_date, CURRENT_DATE) as days_employed,
            DATEDIFF('year', hire_date, CURRENT_DATE) as years_employed
        FROM employees
        ORDER BY days_employed DESC
    """).fetchall()
    
    for row in result:
        print(f"  {row[0]}: {row[1]} ({row[3]} years, {row[2]} days)")

def main():
    """Main function to run all examples."""
    try:
        # Connect to DuckDB
        conn = basic_connection_example()
        
        # Create table and insert data
        create_table_example(conn)
        
        # Run basic queries
        basic_queries_example(conn)
        
        # Demonstrate DataFrame integration
        dataframe_integration_example(conn)
        
        # Show advanced features
        advanced_features_example(conn)
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("1. Try modifying the queries above")
        print("2. Create your own tables with different data types")
        print("3. Experiment with loading data from CSV/JSON files")
        print("4. Explore DuckDB's analytical functions and extensions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Close the connection
        if 'conn' in locals():
            conn.close()
            print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()