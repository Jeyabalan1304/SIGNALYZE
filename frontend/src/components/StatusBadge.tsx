import React from 'react';

interface StatusBadgeProps {
  status: string;
  type?: 'sentiment' | 'default';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'default' }) => {
  const getColors = () => {
    const s = status?.toLowerCase();
    if (type === 'sentiment') {
      if (s === 'positive') return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      if (s === 'negative') return 'bg-rose-100 text-rose-700 border-rose-200';
      if (s === 'neutral') return 'bg-amber-100 text-amber-700 border-amber-200';
    }
    if (!status || s === 'unknown' || s === 'pending') return 'bg-gray-100 text-gray-700 border-gray-200';
    return 'bg-blue-100 text-blue-700 border-blue-200';
  };

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getColors()}`}>
      {status || 'N/A'}
    </span>
  );
};

export default StatusBadge;
