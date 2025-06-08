import React, { useEffect, useState } from 'react';
import TopNav from './TopNav';
import { authFetch } from '../api';

// Chart.js registration omitted for brevity

export default function Dashboard() {
  const [stats, setStats]   = useState(null);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await authFetch({ method: 'get', url: 'dashboard/' });
        setStats(res.data);
      } catch (err) {
        setError('Failed to fetch dashboard data');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-4">Loading Dashboard…</div>;
  if (error)   return <div className="p-4 text-red-600">{error}</div>;

  const { buildings, units, odforms: odForms } = stats;

  // Prepare chart data for OD form statuses if needed...

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar omitted for brevity */}
      <div className="flex-1">
        <TopNav />
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Total Buildings" value={buildings} color="blue" />
            <StatCard title="Total Units"     value={units}     color="green" />
            <StatCard title="Total OD Forms"  value={odForms}   color="purple" />
          </div>

          {/* Example bar chart if you still want to show statuses */}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }) {
  const colors = {
    blue:   'from-blue-500 to-blue-600',
    green:  'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
  };

  return (
    <div className={`bg-gradient-to-r ${colors[color]} text-white p-6 rounded shadow`}>
      <div className="uppercase text-xs font-bold mb-2">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
}