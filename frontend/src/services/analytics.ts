import axios from 'axios';
import type {
  ApiResponse,
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
  static async getOverview(): Promise<any> {
    console.log('🚀 Making API call to /api/v1/analytics/overview');
    const response = await apiClient.get(
      '/api/v1/analytics/overview'
    );
    console.log('📡 Raw API response:', response);
    console.log('📄 Response data:', response.data);
    console.log('🔍 Response structure:', typeof response.data);
    
    // Handle different response structures
    if (response.data && response.data.data) {
      console.log('✅ Using response.data.data');
      return response.data.data;
    } else if (response.data) {
      console.log('✅ Using response.data directly');
      return response.data;
    } else {
      console.error('❌ Unexpected response structure');
      throw new Error('Invalid response structure');
    }
  }

  static async getRevenue(params?: {
    group_by?: 'day' | 'month' | 'year' | 'category';
    limit?: number;
  }): Promise<any> {
    console.log('🚀 Making API call to revenue endpoint');
    const response = await apiClient.get(
      '/api/v1/analytics/revenue',
      { params }
    );
    console.log('📊 Revenue response:', response.data);
    
    // Handle different response structures
    if (response.data && response.data.data) {
      return response.data.data;
    } else if (response.data) {
      return response.data;
    }
    return null;
  }

  static async getCustomers(params?: {
    segment_type?: 'rfm' | 'acquisition_channel';
    limit?: number;
  }): Promise<any> {
    console.log('🚀 Making API call to customers endpoint');
    const response = await apiClient.get(
      '/api/v1/analytics/customers',
      { params }
    );
    console.log('👥 Customer response:', response.data);
    
    // Handle different response structures
    if (response.data && response.data.data) {
      return response.data.data;
    } else if (response.data) {
      return response.data;
    }
    return null;
  }

  static async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/');
    return response.data;
  }
}