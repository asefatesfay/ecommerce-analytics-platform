"""
E-commerce Analytics Interactive Dashboard
=========================================

A comprehensive Streamlit dashboard for exploring e-commerce analytics
using DuckDB. Includes interactive filters, visualizations, and real-time
metrics for business intelligence.
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f2f6, #ffffff);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    .sidebar-info {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load data from DuckDB database with caching."""
    data_dir = Path(__file__).parent.parent / 'data'
    db_path = data_dir / 'ecommerce.duckdb'
    
    if not db_path.exists():
        st.error("❌ Database not found. Please run 01_data_generation.py first!")
        st.stop()
    
    conn = duckdb.connect(str(db_path), read_only=True)
    
    # Load main datasets
    customers = conn.execute("SELECT * FROM customers").fetchdf()
    products = conn.execute("SELECT * FROM products").fetchdf()
    orders = conn.execute("SELECT * FROM orders").fetchdf()
    order_items = conn.execute("SELECT * FROM order_items").fetchdf()
    web_sessions = conn.execute("SELECT * FROM web_sessions").fetchdf()
    
    # Load analytical views
    monthly_revenue = conn.execute("SELECT * FROM monthly_revenue ORDER BY month").fetchdf()
    customer_ltv = conn.execute("SELECT * FROM customer_ltv").fetchdf()
    product_performance = conn.execute("SELECT * FROM product_performance").fetchdf()
    
    conn.close()
    
    return {
        'customers': customers,
        'products': products,
        'orders': orders,
        'order_items': order_items,
        'web_sessions': web_sessions,
        'monthly_revenue': monthly_revenue,
        'customer_ltv': customer_ltv,
        'product_performance': product_performance
    }

def create_kpi_metrics(data, date_filter=None):
    """Create KPI metrics for the dashboard."""
    
    # Apply date filtering if provided
    orders = data['orders'].copy()
    if date_filter:
        orders = orders[
            (pd.to_datetime(orders['order_date']) >= date_filter[0]) & 
            (pd.to_datetime(orders['order_date']) <= date_filter[1])
        ]
    
    completed_orders = orders[orders['status'] == 'Completed']
    
    # Calculate KPIs
    total_revenue = completed_orders['total_amount'].sum()
    total_orders = len(completed_orders)
    total_customers = orders['customer_id'].nunique()
    avg_order_value = completed_orders['total_amount'].mean() if total_orders > 0 else 0
    
    # Growth calculations (compare with previous period)
    if len(orders) > 0:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
        current_period_days = (orders['order_date'].max() - orders['order_date'].min()).days
        
        if current_period_days > 30:
            # Compare with previous month
            cutoff_date = orders['order_date'].max() - timedelta(days=30)
            recent_orders = orders[orders['order_date'] >= cutoff_date]
            prev_orders = orders[orders['order_date'] < cutoff_date]
            
            recent_revenue = recent_orders[recent_orders['status'] == 'Completed']['total_amount'].sum()
            prev_revenue = prev_orders[prev_orders['status'] == 'Completed']['total_amount'].sum()
            
            revenue_growth = ((recent_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
        else:
            revenue_growth = 0
    else:
        revenue_growth = 0
    
    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value,
        'revenue_growth': revenue_growth
    }

def create_revenue_charts(data, date_filter=None):
    """Create revenue analysis charts."""
    
    monthly_revenue = data['monthly_revenue'].copy()
    if date_filter:
        monthly_revenue['month'] = pd.to_datetime(monthly_revenue['month'])
        monthly_revenue = monthly_revenue[
            (monthly_revenue['month'] >= date_filter[0]) & 
            (monthly_revenue['month'] <= date_filter[1])
        ]
    
    # Monthly revenue trend
    fig_revenue_trend = px.line(
        monthly_revenue, 
        x='month', 
        y='revenue',
        title='Monthly Revenue Trend',
        labels={'revenue': 'Revenue ($)', 'month': 'Month'}
    )
    fig_revenue_trend.update_traces(line=dict(width=3))
    fig_revenue_trend.update_layout(height=400)
    
    # Revenue by customer segment
    customer_ltv = data['customer_ltv']
    segment_revenue = customer_ltv.groupby('customer_segment')['lifetime_value'].sum().reset_index()
    
    fig_segment = px.pie(
        segment_revenue,
        values='lifetime_value',
        names='customer_segment',
        title='Revenue by Customer Segment'
    )
    fig_segment.update_layout(height=400)
    
    return fig_revenue_trend, fig_segment

def create_product_charts(data):
    """Create product analysis charts."""
    
    # Category performance
    category_perf = data['product_performance'].groupby('category').agg({
        'total_revenue': 'sum',
        'times_ordered': 'sum',
        'total_quantity_sold': 'sum'
    }).reset_index()
    
    fig_category = px.bar(
        category_perf.sort_values('total_revenue', ascending=True),
        x='total_revenue',
        y='category',
        orientation='h',
        title='Revenue by Product Category',
        labels={'total_revenue': 'Revenue ($)', 'category': 'Category'}
    )
    fig_category.update_layout(height=500)
    
    # Top products
    top_products = data['product_performance'].nlargest(10, 'total_revenue')
    
    fig_top_products = px.bar(
        top_products,
        x='product_name',
        y='total_revenue',
        title='Top 10 Products by Revenue',
        labels={'total_revenue': 'Revenue ($)', 'product_name': 'Product'}
    )
    fig_top_products.update_xaxes(tickangle=45)
    fig_top_products.update_layout(height=400)
    
    return fig_category, fig_top_products

def create_customer_charts(data):
    """Create customer analysis charts."""
    
    # Customer acquisition channels
    acquisition = data['customers']['acquisition_channel'].value_counts().reset_index()
    acquisition.columns = ['channel', 'customers']
    
    fig_acquisition = px.pie(
        acquisition,
        values='customers',
        names='channel',
        title='Customer Acquisition Channels'
    )
    fig_acquisition.update_layout(height=400)
    
    # Customer LTV distribution by segment
    fig_ltv_box = px.box(
        data['customer_ltv'][data['customer_ltv']['lifetime_value'] > 0],
        x='customer_segment',
        y='lifetime_value',
        title='Customer Lifetime Value Distribution by Segment'
    )
    fig_ltv_box.update_layout(height=400)
    
    return fig_acquisition, fig_ltv_box

def create_marketing_charts(data):
    """Create marketing analysis charts."""
    
    # Traffic source performance
    traffic_perf = data['web_sessions'].groupby('traffic_source').agg({
        'session_id': 'count',
        'converted': 'sum',
        'revenue': 'sum'
    }).reset_index()
    traffic_perf['conversion_rate'] = (traffic_perf['converted'] / traffic_perf['session_id'] * 100).round(2)
    
    fig_traffic = px.scatter(
        traffic_perf,
        x='session_id',
        y='conversion_rate',
        size='revenue',
        color='traffic_source',
        title='Traffic Source Performance (Bubble = Revenue)',
        labels={
            'session_id': 'Sessions',
            'conversion_rate': 'Conversion Rate (%)',
            'traffic_source': 'Traffic Source'
        }
    )
    fig_traffic.update_layout(height=400)
    
    # Device performance
    device_perf = data['web_sessions'].groupby('device_type').agg({
        'session_id': 'count',
        'converted': 'sum',
        'session_duration_seconds': 'mean'
    }).reset_index()
    device_perf['conversion_rate'] = (device_perf['converted'] / device_perf['session_id'] * 100).round(2)
    
    fig_device = px.bar(
        device_perf,
        x='device_type',
        y='conversion_rate',
        title='Conversion Rate by Device Type',
        labels={'conversion_rate': 'Conversion Rate (%)', 'device_type': 'Device Type'}
    )
    fig_device.update_layout(height=400)
    
    return fig_traffic, fig_device

def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<div class="main-header">🏪 E-commerce Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading data...'):
        data = load_data()
    
    # Sidebar filters
    st.sidebar.markdown('<div class="sidebar-info"><h3>📊 Dashboard Filters</h3></div>', unsafe_allow_html=True)
    
    # Date range filter
    min_date = pd.to_datetime(data['orders']['order_date']).min().date()
    max_date = pd.to_datetime(data['orders']['order_date']).max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Convert to datetime for filtering
    if len(date_range) == 2:
        date_filter = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))
    else:
        date_filter = None
    
    # Customer segment filter
    segments = st.sidebar.multiselect(
        "Customer Segments",
        options=data['customers']['customer_segment'].unique(),
        default=data['customers']['customer_segment'].unique()
    )
    
    # Product category filter
    categories = st.sidebar.multiselect(
        "Product Categories",
        options=data['products']['category'].unique(),
        default=data['products']['category'].unique()
    )
    
    # Info box
    st.sidebar.markdown("""
    <div class="sidebar-info">
    <h4>ℹ️ About This Dashboard</h4>
    <p>Interactive e-commerce analytics dashboard powered by DuckDB and Streamlit.</p>
    <p><strong>Features:</strong></p>
    <ul>
        <li>Real-time KPI monitoring</li>
        <li>Revenue trend analysis</li>
        <li>Customer segmentation</li>
        <li>Product performance</li>
        <li>Marketing attribution</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate KPIs
    kpis = create_kpi_metrics(data, date_filter)
    
    # KPI Cards
    st.subheader("📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${kpis['total_revenue']:,.2f}",
            delta=f"{kpis['revenue_growth']:+.1f}%" if kpis['revenue_growth'] != 0 else None
        )
    
    with col2:
        st.metric(
            label="🛒 Total Orders",
            value=f"{kpis['total_orders']:,}"
        )
    
    with col3:
        st.metric(
            label="👥 Active Customers",
            value=f"{kpis['total_customers']:,}"
        )
    
    with col4:
        st.metric(
            label="📊 Avg Order Value",
            value=f"${kpis['avg_order_value']:.2f}"
        )
    
    # Charts sections
    st.markdown("---")
    
    # Revenue Analysis
    st.subheader("💰 Revenue Analysis")
    col1, col2 = st.columns(2)
    
    fig_revenue_trend, fig_segment = create_revenue_charts(data, date_filter)
    
    with col1:
        st.plotly_chart(fig_revenue_trend, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_segment, use_container_width=True)
    
    st.markdown("---")
    
    # Product Analysis
    st.subheader("📦 Product Analysis")
    
    fig_category, fig_top_products = create_product_charts(data)
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_top_products, use_container_width=True)
    
    st.markdown("---")
    
    # Customer Analysis
    st.subheader("👥 Customer Analysis")
    
    fig_acquisition, fig_ltv_box = create_customer_charts(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_acquisition, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_ltv_box, use_container_width=True)
    
    st.markdown("---")
    
    # Marketing Analysis
    st.subheader("🎯 Marketing Analysis")
    
    fig_traffic, fig_device = create_marketing_charts(data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_traffic, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_device, use_container_width=True)
    
    st.markdown("---")
    
    # Data Tables
    st.subheader("📋 Detailed Data")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top Products", "👑 Top Customers", "📊 Monthly Trends", "🔍 Recent Orders"])
    
    with tab1:
        st.write("**Top 20 Products by Revenue**")
        top_products_detailed = data['product_performance'].nlargest(20, 'total_revenue')[
            ['product_name', 'category', 'times_ordered', 'total_quantity_sold', 'total_revenue', 'avg_selling_price']
        ].round(2)
        st.dataframe(top_products_detailed, use_container_width=True)
    
    with tab2:
        st.write("**Top 20 Customers by Lifetime Value**")
        top_customers = data['customer_ltv'].nlargest(20, 'lifetime_value')[
            ['customer_id', 'customer_segment', 'acquisition_channel', 'total_orders', 'lifetime_value', 'avg_order_value']
        ].round(2)
        st.dataframe(top_customers, use_container_width=True)
    
    with tab3:
        st.write("**Monthly Performance Summary**")
        monthly_summary = data['monthly_revenue'].round(2)
        st.dataframe(monthly_summary, use_container_width=True)
    
    with tab4:
        st.write("**Recent 50 Orders**")
        recent_orders = data['orders'].nlargest(50, 'order_date')[
            ['order_id', 'customer_id', 'order_date', 'status', 'payment_method', 'total_amount']
        ].round(2)
        st.dataframe(recent_orders, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 2rem;">
        🦆 Powered by DuckDB | 🚀 Built with Streamlit | 📊 E-commerce Analytics Dashboard
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()