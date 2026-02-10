import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, trend, color }) => (
  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <h3 className="text-2xl font-bold mt-2 text-gray-900">{value}</h3>
        {trend && (
          <p className="text-xs font-medium text-emerald-600 mt-1">
            {trend} <span className="text-gray-400 font-normal ml-1">vs last week</span>
          </p>
        )}
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

export default StatCard;
