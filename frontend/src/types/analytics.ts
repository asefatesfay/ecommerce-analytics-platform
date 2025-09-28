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
  order_growth?: number;
  customer_growth?: number;
}

export interface RevenueData {
  time_series: Array<{
    date: string;
    revenue: number;
    orders: number;
  }>;
  by_segment: Array<{
    segment: string;
    revenue: number;
    orders: number;
    customers: number;
    avg_order_value: number;
  }>;
}

export interface CustomerSegment {
  segment: string;
  count: number;
  avg_ltv: number;
  percentage: number;
}

export interface CustomerData {
  rfm_segments: Array<{
    segment: string;
    customers: number;
    avg_recency_days: number;
    avg_frequency: number;
    avg_monetary: number;
  }>;
  acquisition_channels: Array<{
    channel: string;
    customers: number;
    avg_ltv: number;
    avg_orders: number;
  }>;
}