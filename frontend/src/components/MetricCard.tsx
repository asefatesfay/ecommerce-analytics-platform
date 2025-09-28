interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: string;
  color?: 'blue' | 'green' | 'yellow' | 'purple' | 'red';
}

export function MetricCard({ title, value, change, changeLabel, icon, color = 'blue' }: MetricCardProps) {
  const colorClasses = {
    blue: { bg: '#eff6ff', border: '#3b82f6', icon: '#2563eb' },
    green: { bg: '#f0fdf4', border: '#22c55e', icon: '#16a34a' },
    yellow: { bg: '#fefce8', border: '#eab308', icon: '#ca8a04' },
    purple: { bg: '#faf5ff', border: '#a855f7', icon: '#9333ea' },
    red: { bg: '#fef2f2', border: '#ef4444', icon: '#dc2626' }
  };

  const colorStyle = colorClasses[color];
  
  const cardStyle = {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    border: `1px solid ${colorStyle.border}20`,
    transition: 'all 0.2s ease-in-out',
    cursor: 'default'
  };

  const iconStyle = {
    width: '48px',
    height: '48px',
    borderRadius: '12px',
    backgroundColor: colorStyle.bg,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '24px',
    marginBottom: '16px'
  };

  const changeStyle = {
    color: change && change > 0 ? '#16a34a' : change && change < 0 ? '#dc2626' : '#6b7280',
    fontSize: '14px',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    marginTop: '8px'
  };

  return (
    <div style={cardStyle}>
      {icon && (
        <div style={iconStyle}>
          <span style={{ color: colorStyle.icon }}>{icon}</span>
        </div>
      )}
      
      <div>
        <h3 style={{ 
          fontSize: '14px', 
          fontWeight: '500', 
          color: '#6b7280', 
          margin: '0 0 8px 0',
          textTransform: 'uppercase',
          letterSpacing: '0.5px'
        }}>
          {title}
        </h3>
        
        <div style={{ 
          fontSize: '28px', 
          fontWeight: '700', 
          color: '#1f2937',
          lineHeight: '1.2',
          marginBottom: change !== undefined ? '0' : '8px'
        }}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>
        
        {change !== undefined && (
          <div style={changeStyle}>
            <span>{change > 0 ? '↗️' : change < 0 ? '↘️' : '→'}</span>
            <span>
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
              {changeLabel && ` ${changeLabel}`}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}