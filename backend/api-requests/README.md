# 📡 API Requests Collection for E-commerce Analytics

## 🚀 Quick Start Guide

### Prerequisites
- ✅ REST Client extension installed in VS Code
- ✅ API server running on http://localhost:8000
- ✅ DuckDB database with e-commerce data

### How to Use These Requests

1. **Open any `.http` file** in this folder
2. **Click "Send Request"** above any `###` section
3. **View results** in the Response panel
4. **Chain requests** by using previous responses

## 📁 Request Files Overview

| File | Purpose | Key Endpoints |
|------|---------|---------------|
| `01_health_check.http` | ⚡ Server status & docs | Health, `/docs`, `/redoc` |
| `02_analytics_overview_revenue.http` | 💰 KPIs & Revenue | Overview, revenue by time/category |
| `03_customer_analytics.http` | 👥 Customer insights | RFM segments, acquisition channels |
| `04_product_analytics.http` | 📦 Product performance | Top products, category analysis |
| `05_marketing_analytics.http` | 📈 Marketing ROI | Traffic sources, campaigns, devices |
| `06_reports.http` | 📊 Real-time reports | Recent orders, activity feeds |
| `07_advanced_analytics.http` | 🧠 Complex analysis | Executive summaries, deep insights |

## 🎯 Common Use Cases

### **Dashboard Development**
```http
# Start with overview for KPI cards
GET http://localhost:8000/api/v1/analytics/overview

# Then get time-series for charts
GET http://localhost:8000/api/v1/analytics/revenue?group_by=month
```

### **Customer Analysis**
```http
# Get customer segments
GET http://localhost:8000/api/v1/analytics/customers?segment_type=rfm

# Analyze acquisition channels
GET http://localhost:8000/api/v1/analytics/customers?segment_type=acquisition_channel
```

### **Product Insights**
```http
# Top performing products
GET http://localhost:8000/api/v1/analytics/products?sort_by=revenue&limit=10

# Category performance
GET http://localhost:8000/api/v1/analytics/products?group_by=category
```

### **Marketing ROI**
```http
# Channel performance
GET http://localhost:8000/api/v1/analytics/marketing?group_by=traffic_source

# Device analysis
GET http://localhost:8000/api/v1/analytics/marketing?group_by=device_type
```

## 🔧 API Response Format

All endpoints return JSON in this structure:
```json
{
  "status": "success",
  "data": {
    // Specific endpoint data
  },
  "timestamp": "2025-09-27T..."
}
```

## 🚦 Status Codes

- **200 OK**: Request successful
- **422 Unprocessable Entity**: Invalid parameters
- **500 Internal Server Error**: Database or server issue

## 💡 Pro Tips

### **VS Code REST Client Features**
- **Variables**: Use `@baseUrl = http://localhost:8000` at the top
- **Environments**: Create `.http` files for different environments
- **Response References**: Use `{{response.body.data.field}}` from previous requests
- **Authentication**: Add headers like `Authorization: Bearer {{token}}`

### **Testing Workflow**
1. Start with `01_health_check.http` to verify API is running
2. Use `02_analytics_overview_revenue.http` for basic functionality
3. Explore specific areas with dedicated files
4. Use `07_advanced_analytics.http` for complex scenarios

### **Development Integration**
- Copy successful requests into your frontend code
- Use response JSON structure for TypeScript interfaces
- Test parameter combinations for optimal data retrieval
- Monitor response times for performance optimization

## 🎨 Customization Examples

### **Custom Time Ranges**
```http
# Last 7 days revenue
GET http://localhost:8000/api/v1/analytics/revenue?group_by=day&limit=7

# Specific month analysis
GET http://localhost:8000/api/v1/analytics/revenue?group_by=day&start_date=2024-01-01&end_date=2024-01-31
```

### **Filtered Results**
```http
# Top 5 products only
GET http://localhost:8000/api/v1/analytics/products?limit=5

# Specific customer segment
GET http://localhost:8000/api/v1/analytics/customers?segment_type=rfm&segment=Champions
```

---

## 🚀 **Start Testing!**

1. **Open** any `.http` file in this folder
2. **Click "Send Request"** above the `###` lines  
3. **Explore** your e-commerce data interactively!

**Happy API testing!** 🎉