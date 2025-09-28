// Time-based filtering functions for the dashboard

export const generateTimeFilteredData = (timeRange: string) => {
  const baseData = {
    total_revenue: 2847392,
    total_orders: 15847,
    total_customers: 3247,
    avg_order_value: 179.65,
    revenue_growth: 12.5,
    order_growth: 8.3,
    customer_growth: 15.2,
    conversion_rate: 3.4
  };

  // Apply time range multipliers to simulate different periods
  const timeMultipliers = {
    '7days': { revenue: 0.05, orders: 0.05, customers: 0.02, growth: 25.0 },
    '30days': { revenue: 0.2, orders: 0.2, customers: 0.08, growth: 18.0 },
    '3months': { revenue: 0.6, orders: 0.6, customers: 0.3, growth: 15.0 },
    '12months': { revenue: 1.0, orders: 1.0, customers: 1.0, growth: 12.5 },
    'all': { revenue: 1.2, orders: 1.2, customers: 1.0, growth: 8.0 }
  };

  const multiplier = timeMultipliers[timeRange as keyof typeof timeMultipliers] || timeMultipliers['30days'];

  return {
    total_revenue: Math.floor(baseData.total_revenue * multiplier.revenue),
    total_orders: Math.floor(baseData.total_orders * multiplier.orders),
    total_customers: Math.floor(baseData.total_customers * multiplier.customers),
    avg_order_value: Math.round((baseData.avg_order_value * (0.9 + Math.random() * 0.2)) * 100) / 100,
    revenue_growth: Math.round((multiplier.growth * (0.8 + Math.random() * 0.4)) * 10) / 10,
    order_growth: Math.round((multiplier.growth * 0.7 * (0.8 + Math.random() * 0.4)) * 10) / 10,
    customer_growth: Math.round((multiplier.growth * 1.2 * (0.8 + Math.random() * 0.4)) * 10) / 10,
    conversion_rate: Math.round((baseData.conversion_rate * (0.9 + Math.random() * 0.2)) * 10) / 10
  };
};

export const generateTimeFilteredChartData = (timeRange: string) => {
  const periods = {
    '7days': 7,
    '30days': 30,
    '3months': 12,
    '12months': 12,
    'all': 24
  };

  const periodCount = periods[timeRange as keyof typeof periods] || 12;
  const baseRevenue = timeRange === '7days' ? 5000 : timeRange === '30days' ? 15000 : 45000;
  
  return Array.from({ length: periodCount }, (_, i) => {
    const variance = 0.7 + Math.random() * 0.6;
    const trend = timeRange === 'all' ? 1 + (i * 0.02) : 1 + (i * 0.01);
    
    return {
      period: timeRange === '7days' 
        ? `Day ${i + 1}`
        : timeRange === '30days'
        ? `Day ${Math.floor(i * 1) + 1}`
        : timeRange === '3months'
        ? `Week ${i + 1}`
        : `Month ${i + 1}`,
      revenue: Math.floor(baseRevenue * variance * trend),
      orders: Math.floor((baseRevenue * variance * trend) / 180)
    };
  });
};