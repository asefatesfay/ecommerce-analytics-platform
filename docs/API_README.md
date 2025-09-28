# E-commerce Analytics REST API

## Overview

This API provides comprehensive e-commerce analytics endpoints for building flexible frontend applications.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   REST API      │    │   DuckDB        │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Tech Stack
- **Backend**: FastAPI (Python)
- **Database**: DuckDB
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Authentication**: JWT tokens (optional)
- **Caching**: Redis (optional)

## API Endpoints

### 📊 Core Analytics
- `GET /api/v1/analytics/overview` - Key performance indicators
- `GET /api/v1/analytics/revenue` - Revenue trends and breakdowns
- `GET /api/v1/analytics/customers` - Customer analytics and segments
- `GET /api/v1/analytics/products` - Product performance metrics
- `GET /api/v1/analytics/marketing` - Marketing attribution and ROI

### 🔍 Detailed Reports
- `GET /api/v1/reports/revenue-trends` - Time-series revenue data
- `GET /api/v1/reports/customer-cohorts` - Cohort analysis
- `GET /api/v1/reports/product-performance` - Product rankings
- `GET /api/v1/reports/rfm-segments` - Customer segmentation

### 📈 Real-time Data
- `GET /api/v1/realtime/metrics` - Live KPIs
- `GET /api/v1/realtime/orders` - Recent orders
- `GET /api/v1/realtime/traffic` - Website traffic

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn redis
   ```

2. **Start the API server**:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API**:
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Frontend Integration Examples

### React Example
```javascript
// Fetch revenue data
const fetchRevenue = async () => {
  const response = await fetch('/api/v1/analytics/revenue?period=30d');
  const data = await response.json();
  return data;
};
```

### Vue Example
```javascript
// Get customer segments
async getCustomerSegments() {
  const { data } = await this.$http.get('/api/v1/analytics/customers');
  this.segments = data.segments;
}
```

## Benefits of API Architecture

✅ **Frontend Flexibility**: Use any framework (React, Vue, Angular, mobile)
✅ **Scalability**: Independent scaling of frontend and backend
✅ **Performance**: Optimized queries with caching
✅ **Multi-client**: Serve web, mobile, and third-party integrations
✅ **Testing**: Easy API testing with automated tools
✅ **Documentation**: Auto-generated API docs with FastAPI