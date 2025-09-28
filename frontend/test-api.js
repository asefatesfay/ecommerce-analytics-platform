import { AnalyticsService } from './src/services/analytics.js';

async function testAPI() {
  try {
    console.log('Testing API connection...');
    
    const overview = await AnalyticsService.getOverview();
    console.log('Overview data:', JSON.stringify(overview, null, 2));
    
    const revenue = await AnalyticsService.getRevenue({ group_by: 'month', limit: 12 });
    console.log('Revenue data:', JSON.stringify(revenue, null, 2));
    
    console.log('API test completed successfully!');
  } catch (error) {
    console.error('API test failed:', error);
  }
}

testAPI();