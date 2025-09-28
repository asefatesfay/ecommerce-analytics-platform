// E-commerce Analytics Dashboard - React Example
// ================================================

import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// KPI Dashboard Component
const KPIDashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchKPIs();
  }, []);

  const fetchKPIs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/v1/analytics/overview`);
      setKpis(response.data);
    } catch (err) {
      setError('Failed to fetch KPIs');
      console.error('KPI fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading KPIs...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!kpis) return null;

  return (
    <div className="kpi-dashboard">
      <h2>Key Performance Indicators</h2>
      <div className="kpi-grid">
        <div className="kpi-card">
          <h3>Total Revenue</h3>
          <p className="kpi-value">${kpis.total_revenue.toLocaleString()}</p>
          <span className="kpi-growth">+{kpis.revenue_growth}%</span>
        </div>
        
        <div className="kpi-card">
          <h3>Total Orders</h3>
          <p className="kpi-value">{kpis.total_orders.toLocaleString()}</p>
        </div>
        
        <div className="kpi-card">
          <h3>Active Customers</h3>
          <p className="kpi-value">{kpis.total_customers.toLocaleString()}</p>
        </div>
        
        <div className="kpi-card">
          <h3>Avg Order Value</h3>
          <p className="kpi-value">${kpis.avg_order_value.toFixed(2)}</p>
        </div>
        
        <div className="kpi-card">
          <h3>Conversion Rate</h3>
          <p className="kpi-value">{kpis.conversion_rate}%</p>
        </div>
      </div>
    </div>
  );
};

// Revenue Chart Component
const RevenueChart = () => {
  const [revenueData, setRevenueData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [groupBy, setGroupBy] = useState('month');

  useEffect(() => {
    fetchRevenueData();
  }, [groupBy]);

  const fetchRevenueData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/v1/analytics/revenue`, {
        params: { group_by: groupBy }
      });
      setRevenueData(response.data);
    } catch (err) {
      console.error('Revenue fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading revenue data...</div>;
  if (!revenueData) return null;

  return (
    <div className="revenue-chart">
      <div className="chart-header">
        <h2>Revenue Analytics</h2>
        <select 
          value={groupBy} 
          onChange={(e) => setGroupBy(e.target.value)}
          className="period-selector"
        >
          <option value="day">Daily</option>
          <option value="week">Weekly</option>
          <option value="month">Monthly</option>
          <option value="quarter">Quarterly</option>
        </select>
      </div>
      
      {/* Time Series Chart (use Chart.js, Recharts, or similar) */}
      <div className="time-series">
        <h3>Revenue Trend</h3>
        <div className="chart-placeholder">
          {revenueData.time_series.map((point, index) => (
            <div key={index} className="data-point">
              {point.date}: ${point.revenue.toLocaleString()}
            </div>
          ))}
        </div>
      </div>
      
      {/* Segment Breakdown */}
      <div className="segment-breakdown">
        <h3>Revenue by Customer Segment</h3>
        {revenueData.by_segment.map((segment, index) => (
          <div key={index} className="segment-row">
            <span className="segment-name">{segment.segment}</span>
            <span className="segment-revenue">${segment.revenue.toLocaleString()}</span>
            <span className="segment-orders">{segment.orders} orders</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Product Performance Component  
const ProductPerformance = () => {
  const [products, setProducts] = useState(null);
  const [category, setCategory] = useState('');
  const categories = ['Electronics', 'Automotive', 'Home & Garden', 'Sports', 'Health & Beauty'];

  useEffect(() => {
    fetchProducts();
  }, [category]);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/v1/analytics/products`, {
        params: { category: category || undefined, limit: 10 }
      });
      setProducts(response.data);
    } catch (err) {
      console.error('Products fetch error:', err);
    }
  };

  if (!products) return <div>Loading products...</div>;

  return (
    <div className="product-performance">
      <div className="header">
        <h2>Product Performance</h2>
        <select 
          value={category} 
          onChange={(e) => setCategory(e.target.value)}
          className="category-filter"
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>
      
      <div className="top-products">
        <h3>Top Products</h3>
        <table className="products-table">
          <thead>
            <tr>
              <th>Product</th>
              <th>Category</th>
              <th>Revenue</th>
              <th>Units Sold</th>
              <th>Avg Price</th>
            </tr>
          </thead>
          <tbody>
            {products.top_products.map((product, index) => (
              <tr key={index}>
                <td>{product.product_name}</td>
                <td>{product.category}</td>
                <td>${product.revenue.toLocaleString()}</td>
                <td>{product.units_sold.toLocaleString()}</td>
                <td>${product.avg_price.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Main Dashboard App
const EcommerceDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <KPIDashboard />;
      case 'revenue':
        return <RevenueChart />;
      case 'products':
        return <ProductPerformance />;
      default:
        return <KPIDashboard />;
    }
  };

  return (
    <div className="ecommerce-dashboard">
      <header className="dashboard-header">
        <h1>🏪 E-commerce Analytics Dashboard</h1>
        <nav className="dashboard-nav">
          <button 
            className={activeTab === 'overview' ? 'active' : ''} 
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button 
            className={activeTab === 'revenue' ? 'active' : ''} 
            onClick={() => setActiveTab('revenue')}
          >
            Revenue
          </button>
          <button 
            className={activeTab === 'products' ? 'active' : ''} 
            onClick={() => setActiveTab('products')}
          >
            Products
          </button>
        </nav>
      </header>
      
      <main className="dashboard-content">
        {renderContent()}
      </main>
    </div>
  );
};

export default EcommerceDashboard;

// CSS Styles (add to your CSS file)
const styles = `
.ecommerce-dashboard {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.dashboard-header {
  border-bottom: 2px solid #e0e0e0;
  margin-bottom: 30px;
  padding-bottom: 20px;
}

.dashboard-nav {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.dashboard-nav button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.2s;
}

.dashboard-nav button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.kpi-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #007bff;
}

.kpi-value {
  font-size: 2em;
  font-weight: bold;
  margin: 10px 0;
  color: #333;
}

.kpi-growth {
  color: #28a745;
  font-weight: bold;
}

.products-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.products-table th,
.products-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.products-table th {
  background-color: #f8f9fa;
  font-weight: bold;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 1.2em;
}

.error {
  color: #dc3545;
}
`;

// Usage Instructions:
// 1. Install dependencies: npm install axios
// 2. Add this component to your React app
// 3. Style with the provided CSS
// 4. Ensure your API is running on http://localhost:8000