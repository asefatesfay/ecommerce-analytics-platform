import axios from 'axios';
import type {
  OverviewMetrics,
  RevenueData,
  CustomerData,
} from '../types/analytics';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false,
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class AnalyticsService {
  static async getOverview(): Promise<OverviewMetrics> {
    console.log('🚀 Making API call to /api/v1/analytics/overview');
    const response = await apiClient.get<OverviewMetrics>(
      '/api/v1/analytics/overview'
    );
    console.log('📡 Raw API response:', response);
    console.log('📄 Response data:', response.data);
    console.log('🔍 Response structure:', typeof response.data);
    
    // The FastAPI endpoint returns the data directly, not wrapped
    return response.data;
  }

  static async getRevenue(params?: {
    group_by?: 'day' | 'week' | 'month' | 'quarter';
    date_from?: string;
    date_to?: string;
  }): Promise<RevenueData> {
    console.log('🚀 Making API call to revenue endpoint');
    const response = await apiClient.get<RevenueData>(
      '/api/v1/analytics/revenue',
      { params }
    );
    console.log('📊 Revenue response:', response.data);
    
    return response.data;
  }

  static async getCustomers(params?: {
    segment?: string;
  }): Promise<CustomerData> {
    console.log('🚀 Making API call to customers endpoint');
    const response = await apiClient.get<CustomerData>(
      '/api/v1/analytics/customers',
      { params }
    );
    console.log('👥 Customer response:', response.data);
    
    return response.data;
  }

  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/');
    return response.data;
  }
}