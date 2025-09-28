export interface ApiResponse<T> {
  status: string;
  data: T;
  timestamp: string;
}

export interface OverviewMetrics {
  total_revenue: number;
  total_orders: number;
  total_customers: number;
  avg_order_value: number;
  conversion_rate: number;
  revenue_growth: number;
  order_growth: number;
  customer_growth: number;
}

export interface RevenueData {
  time_series: Array<{
    period: string;
    revenue: number;
    orders: number;
  }>;
  by_category: Array<{
    category: string;
    revenue: number;
    percentage: number;
  }>;
  total_revenue: number;
  growth_rate: number;
}

export interface CustomerSegment {
  segment: string;
  count: number;
  avg_ltv: number;
  percentage: number;
}

export interface CustomerData {
  segments: CustomerSegment[];
  acquisition_channels: Array<{
    channel: string;
    customers: number;
    conversion_rate: number;
    avg_ltv: number;
  }>;
  total_customers: number;
  avg_ltv: number;
}