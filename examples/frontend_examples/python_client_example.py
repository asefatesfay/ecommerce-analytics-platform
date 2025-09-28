"""
Python Client Example for E-commerce Analytics API
=================================================

Example showing how to consume the API from Python applications,
including data analysis and report generation.
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EcommerceAnalyticsClient:
    """Python client for E-commerce Analytics API."""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_overview_kpis(self, date_from=None, date_to=None):
        """Get overview KPI metrics."""
        params = {}
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
            
        response = self.session.get(f"{self.base_url}/api/v1/analytics/overview", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_revenue_analytics(self, group_by="month", date_from=None, date_to=None):
        """Get revenue analytics with time series."""
        params = {"group_by": group_by}
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
            
        response = self.session.get(f"{self.base_url}/api/v1/analytics/revenue", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_customer_analytics(self, segment=None):
        """Get customer analytics including RFM segmentation."""
        params = {}
        if segment:
            params['segment'] = segment
            
        response = self.session.get(f"{self.base_url}/api/v1/analytics/customers", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_product_analytics(self, category=None, limit=20):
        """Get product performance analytics."""
        params = {"limit": limit}
        if category:
            params['category'] = category
            
        response = self.session.get(f"{self.base_url}/api/v1/analytics/products", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_marketing_analytics(self):
        """Get marketing attribution analytics."""
        response = self.session.get(f"{self.base_url}/api/v1/analytics/marketing")
        response.raise_for_status()
        return response.json()
    
    def get_recent_orders(self, limit=50):
        """Get recent orders."""
        response = self.session.get(f"{self.base_url}/api/v1/reports/recent-orders", 
                                   params={"limit": limit})
        response.raise_for_status()
        return response.json()

def generate_executive_report(client):
    """Generate an executive summary report."""
    
    print("📊 E-COMMERCE ANALYTICS EXECUTIVE REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get overview metrics
    kpis = client.get_overview_kpis()
    
    print("🎯 KEY PERFORMANCE INDICATORS")
    print("-" * 40)
    print(f"💰 Total Revenue: ${kpis['total_revenue']:,.2f}")
    print(f"🛒 Total Orders: {kpis['total_orders']:,}")
    print(f"👥 Active Customers: {kpis['total_customers']:,}")
    print(f"📊 Average Order Value: ${kpis['avg_order_value']:.2f}")
    print(f"📈 Revenue Growth: {kpis['revenue_growth']:.1f}%")
    print(f"🎯 Conversion Rate: {kpis['conversion_rate']:.2f}%")
    print()
    
    # Customer analytics
    customers = client.get_customer_analytics()
    
    print("👥 CUSTOMER INSIGHTS")
    print("-" * 40)
    print("🏆 Top RFM Segments:")
    for segment in customers['rfm_segments'][:3]:
        print(f"  • {segment['segment']}: {segment['customers']:,} customers (${segment['avg_monetary']:.2f} avg value)")
    
    print("\n📢 Best Acquisition Channels:")
    for channel in customers['acquisition_channels'][:3]:
        print(f"  • {channel['channel']}: {channel['customers']:,} customers (${channel['avg_ltv']:.2f} avg LTV)")
    print()
    
    # Product analytics
    products = client.get_product_analytics(limit=5)
    
    print("📦 PRODUCT PERFORMANCE")
    print("-" * 40)
    print("🏆 Top 5 Products by Revenue:")
    for i, product in enumerate(products['top_products'], 1):
        print(f"  {i}. {product['product_name']} ({product['category']})")
        print(f"     Revenue: ${product['revenue']:,.2f} | Units: {product['units_sold']:,}")
    
    print("\n🏷️ Category Performance:")
    for category in products['category_performance'][:3]:
        print(f"  • {category['category']}: ${category['revenue']:,.2f} ({category['sell_through_rate']:.1f}% sell-through)")
    print()
    
    # Marketing analytics
    marketing = client.get_marketing_analytics()
    
    print("🎯 MARKETING PERFORMANCE")
    print("-" * 40)
    print("📊 Traffic Source ROI:")
    for source in marketing['traffic_sources'][:3]:
        print(f"  • {source['source']}: {source['conversion_rate']:.2f}% conversion, ${source['revenue_per_session']:.2f}/session")
    
    print("\n📱 Device Performance:")
    for device in marketing['device_performance']:
        print(f"  • {device['device']}: {device['conversion_rate']:.2f}% conversion, {device['bounce_rate']:.1f}% bounce rate")
    print()

def create_revenue_visualization(client):
    """Create revenue trend visualization."""
    
    revenue_data = client.get_revenue_analytics(group_by="month")
    
    # Convert to DataFrame for easy plotting
    df = pd.DataFrame(revenue_data['time_series'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Revenue trend
    plt.subplot(2, 2, 1)
    plt.plot(df['date'], df['revenue'], marker='o', linewidth=2, markersize=6)
    plt.title('Monthly Revenue Trend')
    plt.xlabel('Month')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    
    # Orders trend
    plt.subplot(2, 2, 2)
    plt.bar(df['date'], df['orders'], alpha=0.7, color='steelblue')
    plt.title('Monthly Orders')
    plt.xlabel('Month')
    plt.ylabel('Orders')
    plt.xticks(rotation=45)
    
    # Revenue by segment
    plt.subplot(2, 2, 3)
    segments_df = pd.DataFrame(revenue_data['by_segment'])
    plt.pie(segments_df['revenue'], labels=segments_df['segment'], autopct='%1.1f%%', startangle=90)
    plt.title('Revenue by Customer Segment')
    
    # Products by category
    products = client.get_product_analytics()
    plt.subplot(2, 2, 4)
    categories_df = pd.DataFrame(products['category_performance'])
    plt.bar(categories_df['category'], categories_df['revenue'], alpha=0.7, color='lightcoral')
    plt.title('Revenue by Product Category')
    plt.xlabel('Category')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('/Users/x3p8/practice/ML/duckdb/ecommerce_analytics/visualizations/api_analytics_report.png', 
                dpi=300, bbox_inches='tight')
    plt.show()
    
    print("📊 Visualization saved to: visualizations/api_analytics_report.png")

def export_data_to_excel(client):
    """Export analytics data to Excel for further analysis."""
    
    # Create Excel writer
    excel_file = '/Users/x3p8/practice/ML/duckdb/ecommerce_analytics/data/analytics_export.xlsx'
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # Overview KPIs
        kpis = client.get_overview_kpis()
        kpis_df = pd.DataFrame([kpis])
        kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
        
        # Revenue time series
        revenue = client.get_revenue_analytics()
        revenue_ts_df = pd.DataFrame(revenue['time_series'])
        revenue_ts_df.to_excel(writer, sheet_name='Revenue_TimeSeries', index=False)
        
        # Revenue by segment
        segments_df = pd.DataFrame(revenue['by_segment'])
        segments_df.to_excel(writer, sheet_name='Revenue_Segments', index=False)
        
        # Customer RFM segments
        customers = client.get_customer_analytics()
        rfm_df = pd.DataFrame(customers['rfm_segments'])
        rfm_df.to_excel(writer, sheet_name='Customer_RFM', index=False)
        
        # Top products
        products = client.get_product_analytics(limit=50)
        products_df = pd.DataFrame(products['top_products'])
        products_df.to_excel(writer, sheet_name='Top_Products', index=False)
        
        # Marketing data
        marketing = client.get_marketing_analytics()
        traffic_df = pd.DataFrame(marketing['traffic_sources'])
        traffic_df.to_excel(writer, sheet_name='Marketing_Traffic', index=False)
    
    print(f"📁 Data exported to: {excel_file}")

def main():
    """Main demo function."""
    
    print("🚀 E-commerce Analytics API Client Demo")
    print("=" * 50)
    
    # Initialize client
    client = EcommerceAnalyticsClient()
    
    try:
        # Test connection
        health = client.session.get(f"{client.base_url}/").json()
        print(f"✅ Connected to API: {health['message']} (v{health['version']})")
        print()
        
        # Generate reports
        print("1️⃣ Generating Executive Report...")
        generate_executive_report(client)
        
        print("2️⃣ Creating Visualizations...")
        create_revenue_visualization(client)
        
        print("3️⃣ Exporting Data to Excel...")
        export_data_to_excel(client)
        
        print("\n🎉 Demo completed successfully!")
        print("\n🔄 Next Steps:")
        print("  • Integrate API calls into your applications")
        print("  • Build custom dashboards with your preferred frontend")
        print("  • Set up automated reporting and alerting")
        print("  • Extend API with custom endpoints for your business needs")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running:")
        print("   uvicorn ecommerce_analytics.src.api.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()