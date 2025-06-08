import React, { useEffect, useState } from 'react';
import TopNav from './TopNav';
import { Bar } from 'react-chartjs-2';
import { authFetch } from '../api';

// Chart.js registration
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [statusCounts, setStatusCounts] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        // Fetch totals and full OD forms list in parallel
        const [statsRes, odRes] = await Promise.all([
          authFetch({ method: 'get', url: 'dashboard/' }),
          authFetch({ method: 'get', url: 'odforms/' })
        ]);

        if (statsRes.status !== 200) throw new Error();
        if (odRes.status !== 200) throw new Error();

        setStats(statsRes.data);

        // Compute counts by status
        const counts = odRes.data.reduce((acc, od) => {
          acc[od.status] = (acc[od.status] || 0) + 1;
          return acc;
        }, {});
        setStatusCounts(counts);
      } catch (err) {
        setError('Failed to fetch dashboard data');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-4 text-center">Loading Dashboard…</div>;
  if (error)   return <div className="p-4 text-center text-red-600">{error}</div>;

  const { buildings, units, odforms: totalOD } = stats;
  const { active = 0, inactive = 0, done_deal = 0 } = statusCounts;

  const chartData = {
    labels: ['Active', 'Inactive', 'Done Deal'],
    datasets: [
      {
        label: 'OD Forms by Status',
        data: [active, inactive, done_deal],
        backgroundColor: [
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 159, 64, 0.6)',
          'rgba(153, 102, 255, 0.6)'
        ]
      }
    ]
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar omitted for brevity */}
      <div className="flex-1">
        <TopNav />
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Total Buildings" value={buildings} color="blue" />
            <StatCard title="Total Units" value={units} color="green" />
            <StatCard title="Total OD Forms" value={totalOD} color="purple" />
          </div>

          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-4">OD Forms Status Breakdown</h2>
            <div className="w-full max-w-lg mx-auto">
              <Bar data={chartData} options={{ responsive: true }} />
            </div>
          </div>
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