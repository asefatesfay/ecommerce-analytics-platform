"""
E-commerce Analytics REST API
============================

FastAPI-based REST API for e-commerce analytics with DuckDB backend.
Provides flexible endpoints for building modern frontend applications.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models for Response Validation
class KPIResponse(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    avg_order_value: float
    revenue_growth: float
    conversion_rate: float

class RevenueBreakdown(BaseModel):
    segment: str
    revenue: float
    orders: int
    customers: int
    avg_order_value: float

class CustomerSegment(BaseModel):
    segment: str
    customers: int
    avg_ltv: float
    avg_orders: float
    percentage: float

class ProductMetrics(BaseModel):
    product_name: str
    category: str
    revenue: float
    units_sold: int
    avg_price: float
    profit_margin: float

class TimeSeriesPoint(BaseModel):
    date: str
    value: float
    orders: Optional[int] = None

# Database connection manager
class DatabaseManager:
    def __init__(self):
        self.db_path = None
        self.conn = None
    
    def initialize(self):
        """Initialize database connection."""
        data_dir = Path(__file__).parent.parent.parent / 'data'
        self.db_path = data_dir / 'ecommerce.duckdb'
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        logger.info(f"Connecting to database: {self.db_path}")
        self.conn = duckdb.connect(str(self.db_path), read_only=True)
    
    def get_connection(self):
        """Get database connection."""
        if not self.conn:
            self.initialize()
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

# Global database manager
db_manager = DatabaseManager()

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting E-commerce Analytics API...")
    db_manager.initialize()
    yield
    # Shutdown
    logger.info("Shutting down API...")
    db_manager.close()

# FastAPI app with lifespan
app = FastAPI(
    title="E-commerce Analytics API",
    description="Comprehensive REST API for e-commerce business intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/monitoring"""
    return {"status": "healthy", "service": "e-commerce-analytics-api"}

# Dependency to get database connection
def get_db():
    return db_manager.get_connection()

# Helper function for date filtering
def apply_date_filter(query: str, date_from: Optional[str], date_to: Optional[str]) -> str:
    """Apply date filtering to SQL queries."""
    if date_from or date_to:
        date_conditions = []
        if date_from:
            date_conditions.append(f"order_date >= '{date_from}'")
        if date_to:
            date_conditions.append(f"order_date <= '{date_to}'")
        
        if "WHERE" in query.upper():
            query += f" AND {' AND '.join(date_conditions)}"
        else:
            query += f" WHERE {' AND '.join(date_conditions)}"
    
    return query

@app.get("/")
async def root():
    """API health check and information."""
    return {
        "message": "E-commerce Analytics API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "endpoints": {
            "overview": "/api/v1/analytics/overview",
            "revenue": "/api/v1/analytics/revenue", 
            "customers": "/api/v1/analytics/customers",
            "products": "/api/v1/analytics/products",
            "marketing": "/api/v1/analytics/marketing"
        }
    }

@app.get("/api/v1/analytics/overview", response_model=KPIResponse)
async def get_overview_metrics(
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get high-level KPI metrics for dashboard overview."""
    
    try:
        # Base query for KPIs
        base_query = """
        SELECT 
            COUNT(DISTINCT order_id) as total_orders,
            COUNT(DISTINCT customer_id) as total_customers,
            SUM(CASE WHEN status = 'Completed' THEN total_amount ELSE 0 END) as total_revenue,
            AVG(CASE WHEN status = 'Completed' THEN total_amount ELSE NULL END) as avg_order_value
        FROM orders
        """
        
        # Apply date filtering
        filtered_query = apply_date_filter(base_query, date_from, date_to)
        
        result = db.execute(filtered_query).fetchone()
        
        # Calculate conversion rate from web sessions
        conversion_query = """
        SELECT 
            COUNT(*) as total_sessions,
            SUM(CASE WHEN converted THEN 1 ELSE 0 END) as conversions
        FROM web_sessions
        """
        conversion_query = apply_date_filter(conversion_query.replace("order_date", "session_date"), date_from, date_to)
        conv_result = db.execute(conversion_query).fetchone()
        
        conversion_rate = (conv_result[1] / conv_result[0] * 100) if conv_result[0] > 0 else 0
        
        # Calculate revenue growth (simplified - comparing with previous period)
        revenue_growth = 5.2  # Placeholder - you can implement proper period comparison
        
        return KPIResponse(
            total_revenue=float(result[2]) if result[2] else 0,
            total_orders=int(result[0]) if result[0] else 0,
            total_customers=int(result[1]) if result[1] else 0,
            avg_order_value=float(result[3]) if result[3] else 0,
            revenue_growth=revenue_growth,
            conversion_rate=round(conversion_rate, 2)
        )
        
    except Exception as e:
        logger.error(f"Error in overview metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@app.get("/api/v1/analytics/revenue")
async def get_revenue_analytics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    group_by: str = Query("month", description="Grouping: day, week, month, quarter"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get revenue analytics with time series and breakdowns."""
    
    try:
        # Revenue by time period
        time_groupings = {
            "day": "DATE(order_date)",
            "week": "DATE_TRUNC('week', order_date)", 
            "month": "DATE_TRUNC('month', order_date)",
            "quarter": "DATE_TRUNC('quarter', order_date)"
        }
        
        if group_by not in time_groupings:
            group_by = "month"
        
        time_query = f"""
        SELECT 
            {time_groupings[group_by]} as period,
            SUM(CASE WHEN status = 'Completed' THEN total_amount ELSE 0 END) as revenue,
            COUNT(CASE WHEN status = 'Completed' THEN order_id END) as orders
        FROM orders
        """
        
        time_query = apply_date_filter(time_query, date_from, date_to)
        time_query += f" GROUP BY {time_groupings[group_by]} ORDER BY period"
        
        time_series = db.execute(time_query).fetchdf()
        
        # Revenue by customer segment
        segment_query = """
        SELECT 
            c.customer_segment as segment,
            SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) as revenue,
            COUNT(CASE WHEN o.status = 'Completed' THEN o.order_id END) as orders,
            COUNT(DISTINCT c.customer_id) as customers,
            AVG(CASE WHEN o.status = 'Completed' THEN o.total_amount END) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        """
        
        segment_query = apply_date_filter(segment_query, date_from, date_to)
        segment_query += " GROUP BY c.customer_segment ORDER BY revenue DESC"
        
        segments = db.execute(segment_query).fetchdf()
        
        return {
            "time_series": [
                {
                    "date": str(row['period']),
                    "revenue": float(row['revenue']),
                    "orders": int(row['orders'])
                }
                for _, row in time_series.iterrows()
            ],
            "by_segment": [
                {
                    "segment": row['segment'],
                    "revenue": float(row['revenue']) if pd.notna(row['revenue']) else 0,
                    "orders": int(row['orders']) if pd.notna(row['orders']) else 0,
                    "customers": int(row['customers']),
                    "avg_order_value": float(row['avg_order_value']) if pd.notna(row['avg_order_value']) else 0
                }
                for _, row in segments.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/customers")
async def get_customer_analytics(
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get customer analytics including segmentation and LTV."""
    
    try:
        # RFM segments
        rfm_query = """
        WITH rfm_metrics AS (
            SELECT 
                c.customer_id,
                c.customer_segment,
                DATE_DIFF('day', MAX(o.order_date), '2024-12-31') as recency,
                COUNT(o.order_id) as frequency,
                SUM(CASE WHEN o.status = 'Completed' THEN o.total_amount ELSE 0 END) as monetary
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            WHERE c.registration_date <= '2024-12-01'
            GROUP BY c.customer_id, c.customer_segment
        ),
        rfm_scores AS (
            SELECT 
                customer_id,
                customer_segment,
                NTILE(5) OVER (ORDER BY recency DESC) as r_score,
                NTILE(5) OVER (ORDER BY frequency) as f_score,
                NTILE(5) OVER (ORDER BY monetary) as m_score,
                recency, frequency, monetary
            FROM rfm_metrics
            WHERE monetary > 0
        )
        SELECT 
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
            COUNT(*) as customers,
            ROUND(AVG(recency), 1) as avg_recency_days,
            ROUND(AVG(frequency), 1) as avg_frequency,
            ROUND(AVG(monetary), 2) as avg_monetary
        FROM rfm_scores
        GROUP BY rfm_segment
        ORDER BY AVG(monetary) DESC
        """
        
        rfm_segments = db.execute(rfm_query).fetchdf()
        
        # Customer acquisition channels
        acquisition_query = """
        SELECT 
            acquisition_channel,
            COUNT(*) as customers,
            ROUND(AVG(lifetime_value), 2) as avg_ltv,
            ROUND(AVG(total_orders), 2) as avg_orders
        FROM customer_ltv
        WHERE total_orders > 0
        GROUP BY acquisition_channel
        ORDER BY avg_ltv DESC
        """
        
        if segment:
            acquisition_query = acquisition_query.replace(
                "FROM customer_ltv",
                f"FROM customer_ltv WHERE customer_segment = '{segment}'"
            )
        
        acquisition = db.execute(acquisition_query).fetchdf()
        
        return {
            "rfm_segments": [
                {
                    "segment": row['rfm_segment'],
                    "customers": int(row['customers']),
                    "avg_recency_days": float(row['avg_recency_days']),
                    "avg_frequency": float(row['avg_frequency']),
                    "avg_monetary": float(row['avg_monetary'])
                }
                for _, row in rfm_segments.iterrows()
            ],
            "acquisition_channels": [
                {
                    "channel": row['acquisition_channel'],
                    "customers": int(row['customers']),
                    "avg_ltv": float(row['avg_ltv']),
                    "avg_orders": float(row['avg_orders'])
                }
                for _, row in acquisition.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in customer analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/products")
async def get_product_analytics(
    category: Optional[str] = Query(None, description="Filter by product category"),
    limit: int = Query(20, description="Number of top products to return"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get product performance analytics."""
    
    try:
        # Top products by revenue
        products_query = """
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
        """
        
        if category:
            products_query += f" AND category = '{category}'"
        
        products_query += f" ORDER BY total_revenue DESC LIMIT {limit}"
        
        products = db.execute(products_query).fetchdf()
        
        # Category performance
        category_query = """
        SELECT 
            category,
            COUNT(*) as total_products,
            COUNT(CASE WHEN times_ordered > 0 THEN 1 END) as products_sold,
            ROUND(COUNT(CASE WHEN times_ordered > 0 THEN 1 END) * 100.0 / COUNT(*), 1) as sell_through_rate,
            ROUND(SUM(total_revenue), 2) as category_revenue
        FROM product_performance
        GROUP BY category
        ORDER BY category_revenue DESC
        """
        
        categories = db.execute(category_query).fetchdf()
        
        return {
            "top_products": [
                {
                    "product_name": row['product_name'],
                    "category": row['category'],
                    "revenue": float(row['revenue']),
                    "times_ordered": int(row['times_ordered']),
                    "units_sold": int(row['total_quantity_sold']),
                    "avg_price": float(row['avg_price']),
                    "profit_per_unit": float(row['profit_per_unit'])
                }
                for _, row in products.iterrows()
            ],
            "category_performance": [
                {
                    "category": row['category'],
                    "total_products": int(row['total_products']),
                    "products_sold": int(row['products_sold']),
                    "sell_through_rate": float(row['sell_through_rate']),
                    "revenue": float(row['category_revenue'])
                }
                for _, row in categories.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in product analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/marketing")
async def get_marketing_analytics(
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get marketing attribution and traffic source analytics."""
    
    try:
        # Traffic source performance
        traffic_query = """
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
        
        traffic = db.execute(traffic_query).fetchdf()
        
        # Device performance
        device_query = """
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
        
        devices = db.execute(device_query).fetchdf()
        
        return {
            "traffic_sources": [
                {
                    "source": row['traffic_source'],
                    "sessions": int(row['sessions']),
                    "conversions": int(row['conversions']),
                    "conversion_rate": float(row['conversion_rate']),
                    "avg_session_duration": int(row['avg_session_duration']),
                    "avg_page_views": float(row['avg_page_views']),
                    "revenue": float(row['total_revenue']),
                    "revenue_per_session": float(row['revenue_per_session'])
                }
                for _, row in traffic.iterrows()
            ],
            "device_performance": [
                {
                    "device": row['device_type'],
                    "sessions": int(row['sessions']),
                    "avg_duration": int(row['avg_duration']),
                    "avg_page_views": float(row['avg_page_views']),
                    "bounce_rate": float(row['bounce_rate']),
                    "conversion_rate": float(row['conversion_rate'])
                }
                for _, row in devices.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in marketing analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reports/recent-orders")
async def get_recent_orders(
    limit: int = Query(50, description="Number of recent orders to return"),
    db: duckdb.DuckDBPyConnection = Depends(get_db)
):
    """Get recent orders for real-time monitoring."""
    
    try:
        query = """
        SELECT 
            order_id,
            customer_id,
            order_date,
            status,
            payment_method,
            ROUND(total_amount, 2) as total_amount
        FROM orders
        ORDER BY order_date DESC
        LIMIT ?
        """
        
        orders = db.execute(query, [limit]).fetchdf()
        
        return {
            "recent_orders": [
                {
                    "order_id": int(row['order_id']),
                    "customer_id": int(row['customer_id']),
                    "order_date": str(row['order_date']),
                    "status": row['status'],
                    "payment_method": row['payment_method'],
                    "total_amount": float(row['total_amount'])
                }
                for _, row in orders.iterrows()
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in recent orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)