'use client';

import { useState } from 'react';
import { ChartDetailModal } from './ChartDetailModal';

interface DataPoint {
  period: string;
  revenue: number;
  orders: number;
}

interface ChartProps {
  title: string;
  data: DataPoint[];
  type?: 'revenue' | 'orders';
}

export function SimpleChart({ title, data, type = 'revenue' }: ChartProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedData, setSelectedData] = useState<DataPoint | null>(null);
  if (!data || data.length === 0) {
    return (
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        textAlign: 'center' as const
      }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600' }}>{title}</h3>
        <p style={{ color: '#6b7280' }}>No data available</p>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => type === 'revenue' ? d.revenue : d.orders));
  const minValue = Math.min(...data.map(d => type === 'revenue' ? d.revenue : d.orders));
  const range = maxValue - minValue;

  const containerStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb'
  };

  const chartAreaStyle = {
    display: 'flex',
    alignItems: 'end' as const,
    height: '200px',
    gap: '8px',
    marginTop: '20px',
    padding: '0 8px'
  };

  const formatValue = (value: number) => {
    if (type === 'revenue') {
      return value > 1000000 ? `$${(value / 1000000).toFixed(1)}M` : `$${(value / 1000).toFixed(0)}K`;
    }
    return value > 1000 ? `${(value / 1000).toFixed(1)}K` : value.toString();
  };

  return (
    <div style={containerStyle}>
      <h3 
        onClick={() => {
          const total = data.reduce((sum, item) => sum + (type === 'revenue' ? item.revenue : item.orders), 0);
          // Use modal for chart summary
          const summaryData = {
            period: `${title} Summary (${data.length} periods)`,
            revenue: total,
            orders: type === 'orders' ? total : data.reduce((sum, item) => sum + item.orders, 0)
          };
          setSelectedData(summaryData);
          setIsModalOpen(true);
        }}
        style={{ 
          margin: '0 0 8px 0', 
          fontSize: '18px', 
          fontWeight: '600',
          color: '#1f2937',
          cursor: 'pointer',
          textDecoration: 'underline',
          textDecorationColor: 'transparent',
          transition: 'text-decoration-color 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.textDecorationColor = '#3b82f6';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.textDecorationColor = 'transparent';
        }}
      >
        {title}
      </h3>
      
      <div style={{ 
        fontSize: '14px', 
        color: '#6b7280',
        marginBottom: '16px'
      }}>
        Showing last {data.length} periods
      </div>

      <div style={chartAreaStyle}>
        {data.map((item, index) => {
          const value = type === 'revenue' ? item.revenue : item.orders;
          const height = range > 0 ? ((value - minValue) / range) * 160 + 20 : 20;
          
          return (
            <div key={index} style={{ 
              display: 'flex', 
              flexDirection: 'column' as const,
              alignItems: 'center' as const,
              flex: '1',
              minWidth: '40px'
            }}>
              <div
                onClick={() => {
                  setSelectedData(item);
                  setIsModalOpen(true);
                }}
                style={{
                  width: '100%',
                  height: `${height}px`,
                  backgroundColor: type === 'revenue' ? '#3b82f6' : '#10b981',
                  borderRadius: '4px 4px 0 0',
                  display: 'flex',
                  alignItems: 'end' as const,
                  justifyContent: 'center' as const,
                  position: 'relative' as const,
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = type === 'revenue' ? '#2563eb' : '#059669';
                  e.currentTarget.style.transform = 'scale(1.05)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = type === 'revenue' ? '#3b82f6' : '#10b981';
                  e.currentTarget.style.transform = 'scale(1)';
                }}
              >
                <div style={{
                  position: 'absolute' as const,
                  top: '-25px',
                  fontSize: '11px',
                  fontWeight: '600',
                  color: '#374151',
                  whiteSpace: 'nowrap' as const
                }}>
                  {formatValue(value)}
                </div>
              </div>
              
              <div style={{ 
                marginTop: '8px',
                fontSize: '12px',
                color: '#6b7280',
                textAlign: 'center' as const,
                transform: 'rotate(-45deg)',
                transformOrigin: 'center',
                whiteSpace: 'nowrap' as const,
                minHeight: '20px'
              }}>
                {item.period}
              </div>
            </div>
          );
        })}
      </div>
      
      <div style={{
        marginTop: '20px',
        padding: '16px',
        backgroundColor: '#f9fafb',
        borderRadius: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '14px'
      }}>
        <span style={{ color: '#6b7280' }}>
          Total: {formatValue(data.reduce((sum, item) => sum + (type === 'revenue' ? item.revenue : item.orders), 0))}
        </span>
        <span style={{ color: '#6b7280' }}>
          Avg: {formatValue(data.reduce((sum, item) => sum + (type === 'revenue' ? item.revenue : item.orders), 0) / data.length)}
        </span>
      </div>

      {selectedData && (
        <ChartDetailModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false);
            setSelectedData(null);
          }}
          title={title}
          period={selectedData.period}
          revenue={selectedData.revenue}
          orders={selectedData.orders}
          type={type}
        />
      )}
    </div>
  );
}