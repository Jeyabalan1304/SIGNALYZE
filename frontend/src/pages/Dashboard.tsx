import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, AlertCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { getStats, getCharts } from '../services/api';
import { DashboardStats, DashboardCharts } from '../types/feedback';
import StatCard from '../components/StatCard';

const COLORS = ['#4f46e5', '#10b981', '#f43f5e', '#f59e0b', '#8b5cf6'];

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({ total_feedback: 0, classified_signal: 0, pending_processing: 0 });
  const [charts, setCharts] = useState<DashboardCharts>({ sentiment: [], area: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [s, c] = await Promise.all([getStats(), getCharts()]);
      setStats(s);
      setCharts(c);
    } catch (e) {
      console.error('Failed to load dashboard', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900">Intelligence Dashboard</h2>
        <p className="text-gray-500 mt-1">Global view of customer signals across all channels.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Conversations" 
          value={stats.total_feedback.toLocaleString()} 
          icon={Users} 
          color="bg-primary-600" 
        />
        <StatCard 
          title="Signal Percentage" 
          value={`${stats.classified_signal}%`} 
          icon={TrendingUp} 
          color="bg-emerald-500" 
        />
        <StatCard 
          title="Manual Review Required" 
          value={stats.pending_processing} 
          icon={AlertCircle} 
          color="bg-amber-500" 
        />
        <StatCard 
          title="Production Grade" 
          value="v1.4.2" 
          icon={BarChart3} 
          color="bg-indigo-500" 
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border h-[450px]">
          <h3 className="text-gray-900 font-bold mb-6 text-lg">Sentiment Health Distribution</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={charts.sentiment}
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={105}
                paddingAngle={8}
                dataKey="value"
              >
                {charts.sentiment?.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border h-[450px]">
          <h3 className="text-gray-900 font-bold mb-6 text-lg">Volume by Product Category</h3>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={charts.area}
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={105}
                paddingAngle={8}
                dataKey="value"
              >
                {charts.area?.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
