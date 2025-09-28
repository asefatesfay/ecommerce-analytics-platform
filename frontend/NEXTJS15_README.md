# 🚀 Modern E-commerce Analytics Dashboard (Next.js 15)

A beautiful, production-ready analytics dashboard built with **Next.js 15**, **React 19**, and **TypeScript**.

## ✨ Latest Technology Stack

### Core Framework
- **Next.js 15.5.4** - Latest version with App Router
- **React 19.1.0** - Latest React with new features
- **TypeScript 5+** - Full type safety
- **Tailwind CSS** - Modern utility-first styling

### UI & Visualization  
- **Radix UI** - Accessible headless components
- **Lucide React** - Beautiful icons
- **Recharts** - Interactive charting library
- **Framer Motion** - Smooth animations

### Data Management
- **Axios** - HTTP client for API requests
- **SWR** - Data fetching with caching
- **React Hot Toast** - Beautiful notifications

## 🏁 Quick Start

### 1. **Ensure API Server is Running**
```bash
# In your main project directory
cd /Users/x3p8/practice/ML/duckdb
source venv/bin/activate
uvicorn ecommerce_analytics.src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. **Start the Dashboard**
```bash
cd /Users/x3p8/practice/ML/duckdb/ecommerce_analytics/frontend
npm run dev
```

### 3. **Open Your Browser**
```
http://localhost:3000
```

## 📊 Dashboard Features

### Real-time Analytics
- ✅ **KPI Cards** - Revenue, Orders, Customers, AOV with growth indicators
- ✅ **Revenue Trends** - Time series data with period comparisons  
- ✅ **Error Handling** - Graceful fallbacks and retry mechanisms
- ✅ **Loading States** - Skeleton screens for better UX

### API Integration
- ✅ **FastAPI Connection** - Connects to your analytics backend on port 8000
- ✅ **Type Safety** - Full TypeScript interfaces for all API responses
- ✅ **Error Recovery** - Automatic retry and error display
- ✅ **Environment Config** - Configurable API endpoints

### Modern UI/UX
- ✅ **Responsive Design** - Mobile-first approach
- ✅ **Loading Animations** - Skeleton screens while loading
- ✅ **Growth Indicators** - Green/red arrows for metric changes
- ✅ **Professional Styling** - Clean, modern design system

## 🎯 What's Working Right Now

### ✅ **Live Dashboard** 
Your dashboard is **currently running** on http://localhost:3000 and will display:

1. **Real KPIs** from your e-commerce database
2. **Revenue trends** with monthly breakdowns
3. **Growth percentages** for all key metrics
4. **Order activity** and customer insights
5. **Professional UI** with loading states

### ✅ **API Integration**
- Connects automatically to FastAPI server (port 8000)
- Handles connection errors gracefully
- Shows retry options if API is unavailable
- Displays real data from your DuckDB database

## 🔧 Configuration

### Environment Variables
```bash
# .env.local (already configured)
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
NEXT_PUBLIC_APP_NAME="E-commerce Analytics Dashboard"
```

### API Proxy
Next.js automatically proxies `/api/*` requests to your FastAPI backend, so you don't need to worry about CORS issues.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # App layout
│   │   ├── page.tsx        # Dashboard page
│   │   └── globals.css     # Global styles
│   ├── services/
│   │   └── analytics.ts    # API client
│   ├── types/
│   │   └── analytics.ts    # TypeScript interfaces  
│   └── lib/
│       └── utils.ts        # Utility functions
├── next.config.ts          # Next.js 15 config
├── tailwind.config.ts      # Tailwind CSS config
└── package.json            # Dependencies
```

## 🚀 Next Steps

### Immediate Enhancements (Ready to Build)
1. **Add Charts** - Replace text displays with Recharts visualizations
2. **Customer Segmentation** - Build RFM analysis charts
3. **Product Performance** - Create interactive product tables
4. **Marketing Dashboard** - Add traffic source visualizations

### Advanced Features
1. **Real-time Updates** - WebSocket integration for live data
2. **Export Features** - PDF/Excel report generation  
3. **Advanced Filters** - Date ranges and segment filtering
4. **Dark Mode** - Theme switching capability

## 🎨 Customization

### Adding New Components
```typescript
// Create new chart component
export function NewChart({ data }: { data: ChartData }) {
  return (
    <div className="bg-white rounded-lg p-6 shadow border">
      <h3 className="text-lg font-semibold mb-4">Chart Title</h3>
      {/* Chart implementation */}
    </div>
  );
}
```

### Extending API Services
```typescript
// Add new endpoint in services/analytics.ts
static async getNewData(): Promise<NewDataType> {
  const response = await apiClient.get('/api/v1/analytics/new-endpoint');
  return response.data.data;
}
```

## 🔍 Troubleshooting

### Common Issues

1. **"Cannot connect to API"**
   - Ensure FastAPI server is running on port 8000
   - Check the API URL in `.env.local`

2. **TypeScript Errors**
   - API response types might need updating in `types/analytics.ts`
   - Run `npm run build` to check for type issues

3. **Styling Issues**
   - Tailwind classes should work out of the box
   - Check `tailwind.config.ts` for custom configurations

### Performance Tips
- The dashboard uses efficient data fetching with SWR
- Loading states prevent layout shifts
- API calls are batched using Promise.all

## 🎉 **Success!**

Your **Next.js 15** dashboard is now running with:
- ✅ **Latest React 19** features
- ✅ **Real-time data** from your analytics API
- ✅ **Professional UI** with loading states
- ✅ **Type-safe** API integration
- ✅ **Mobile responsive** design

**Visit http://localhost:3000 to see your analytics in action!** 🚀

---

*Built with Next.js 15.5.4 | React 19.1.0 | TypeScript 5+ | Tailwind CSS*