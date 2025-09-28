import { Modal } from './Modal';
import { formatCurrency, formatNumber, formatPercent } from '../lib/utils';

interface MetricDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  icon: string;
  primaryValue: string;
  details: Array<{
    label: string;
    value: string | number;
    type?: 'currency' | 'number' | 'percent';
    color?: 'positive' | 'negative' | 'neutral';
  }>;
  timeRange: string;
}

export function MetricDetailModal({ 
  isOpen, 
  onClose, 
  title, 
  icon, 
  primaryValue, 
  details, 
  timeRange 
}: MetricDetailModalProps) {
  const formatValue = (value: string | number, type?: string) => {
    if (typeof value === 'string') return value;
    
    switch (type) {
      case 'currency': return formatCurrency(value);
      case 'number': return formatNumber(value);
      case 'percent': return `${value.toFixed(1)}%`;
      default: return value.toString();
    }
  };

  const getColorStyle = (color?: string) => {
    switch (color) {
      case 'positive': return { color: '#059669' };
      case 'negative': return { color: '#dc2626' };
      case 'neutral': 
      default: return { color: '#374151' };
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`${icon} ${title}`}>
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <div style={{
          fontSize: '36px',
          fontWeight: 'bold',
          color: '#1f2937',
          marginBottom: '8px'
        }}>
          {primaryValue}
        </div>
        <div style={{
          fontSize: '14px',
          color: '#6b7280',
          fontWeight: '500'
        }}>
          for {timeRange}
        </div>
      </div>

      <div style={{ 
        display: 'grid', 
        gap: '16px'
      }}>
        {details.map((detail, index) => (
          <div key={index} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px',
            border: '1px solid #e5e7eb'
          }}>
            <span style={{
              fontSize: '14px',
              color: '#6b7280',
              fontWeight: '500'
            }}>
              {detail.label}
            </span>
            <span style={{
              fontSize: '16px',
              fontWeight: '600',
              ...getColorStyle(detail.color)
            }}>
              {formatValue(detail.value, detail.type)}
            </span>
          </div>
        ))}
      </div>

      <div style={{
        marginTop: '24px',
        padding: '16px',
        backgroundColor: '#eff6ff',
        borderRadius: '8px',
        border: '1px solid #dbeafe'
      }}>
        <div style={{
          fontSize: '12px',
          color: '#1e40af',
          fontWeight: '500',
          textAlign: 'center'
        }}>
          💡 Click on other metrics or charts to explore more details
        </div>
      </div>
    </Modal>
  );
}