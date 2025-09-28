import { Modal } from './Modal';
import { formatCurrency, formatNumber } from '../lib/utils';

interface ChartDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  period: string;
  revenue: number;
  orders: number;
  type: 'revenue' | 'orders';
}

export function ChartDetailModal({ 
  isOpen, 
  onClose, 
  period, 
  revenue, 
  orders, 
  type 
}: ChartDetailModalProps) {
  const primaryValue = type === 'revenue' ? formatCurrency(revenue) : formatNumber(orders);
  const avgOrderValue = revenue / Math.max(orders, 1);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`📊 ${period} Details`}>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <div style={{
          fontSize: '32px',
          fontWeight: 'bold',
          color: type === 'revenue' ? '#3b82f6' : '#10b981',
          marginBottom: '8px'
        }}>
          {primaryValue}
        </div>
        <div style={{
          fontSize: '14px',
          color: '#6b7280',
          fontWeight: '500'
        }}>
          {period} - {type === 'revenue' ? 'Revenue' : 'Orders'}
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gap: '12px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: '#f0fdf4',
          borderRadius: '8px',
          border: '1px solid #bbf7d0'
        }}>
          <span style={{
            fontSize: '14px',
            color: '#166534',
            fontWeight: '500'
          }}>
            💰 Revenue
          </span>
          <span style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#166534'
          }}>
            {formatCurrency(revenue)}
          </span>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: '#ecfdf5',
          borderRadius: '8px',
          border: '1px solid #a7f3d0'
        }}>
          <span style={{
            fontSize: '14px',
            color: '#047857',
            fontWeight: '500'
          }}>
            🛒 Orders
          </span>
          <span style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#047857'
          }}>
            {formatNumber(orders)}
          </span>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 16px',
          backgroundColor: '#fefce8',
          borderRadius: '8px',
          border: '1px solid #fde047'
        }}>
          <span style={{
            fontSize: '14px',
            color: '#a16207',
            fontWeight: '500'
          }}>
            📈 Avg Order Value
          </span>
          <span style={{
            fontSize: '16px',
            fontWeight: '600',
            color: '#a16207'
          }}>
            {formatCurrency(avgOrderValue)}
          </span>
        </div>

        {type === 'revenue' && (
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            backgroundColor: '#f3f4f6',
            borderRadius: '8px',
            border: '1px solid #d1d5db'
          }}>
            <span style={{
              fontSize: '14px',
              color: '#374151',
              fontWeight: '500'
            }}>
              💡 Revenue per Order
            </span>
            <span style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#374151'
            }}>
              {formatCurrency(revenue / Math.max(orders, 1))}
            </span>
          </div>
        )}

        {type === 'orders' && (
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            backgroundColor: '#f3f4f6',
            borderRadius: '8px',
            border: '1px solid #d1d5db'
          }}>
            <span style={{
              fontSize: '14px',
              color: '#374151',
              fontWeight: '500'
            }}>
              💡 Orders Efficiency
            </span>
            <span style={{
              fontSize: '16px',
              fontWeight: '600',
              color: '#374151'
            }}>
              {orders > 100 ? 'High' : orders > 50 ? 'Medium' : 'Low'}
            </span>
          </div>
        )}
      </div>

      <div style={{
        marginTop: '20px',
        padding: '12px',
        backgroundColor: '#eff6ff',
        borderRadius: '8px',
        border: '1px solid #dbeafe',
        textAlign: 'center'
      }}>
        <div style={{
          fontSize: '12px',
          color: '#1e40af',
          fontWeight: '500'
        }}>
          📊 Click on other chart bars to explore different periods
        </div>
      </div>
    </Modal>
  );
}