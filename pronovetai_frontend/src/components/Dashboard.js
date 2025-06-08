// src/components/Dashboard.js
import React, { useEffect, useState } from 'react';
import TopNav   from './TopNav';
import { Bar }  from 'react-chartjs-2';
import { authFetch } from '../api';

// ––––– Chart.js registration –––––
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

// ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const [stats,        setStats]        = useState(null);
  const [statusCounts, setStatusCounts] = useState({});
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState('');

  useEffect(() => {
    (async () => {
      try {
        /* fetch high-level stats + full OD-form list in parallel */
        const [{ data: top }, { data: odforms }] = await Promise.all([
          authFetch({ method: 'get', url: 'dashboard/' }),
          authFetch({ method: 'get', url: 'odforms/'   })
        ]);

        setStats(top);

        /* tally every distinct status */
        const tallies = {};
        for (const { status } of odforms) {
          tallies[status] = (tallies[status] || 0) + 1;
        }
        setStatusCounts(tallies);
      } catch {
        setError('Failed to fetch dashboard data.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <Centered>Loading Dashboard…</Centered>;
  if (error)   return <Centered className="text-red-600">{error}</Centered>;

  // ─── quick helpers ───────────────────────────────────────
  const colourFor = (status) => ({
    active:      'rgba( 75,192,192,0.6)',
    inactive:    'rgba(255,159, 64,0.6)',
    done_deal:   'rgba(153,102,255,0.6)',
    /* fallback */ default: 'rgba(201,203,207,0.6)'
  }[status] || 'rgba(201,203,207,0.6)');

  const labelFor = (status) =>
    status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  /* build chart arrays in the order returned by Object.keys() */
  const statuses = Object.keys(statusCounts);
  const chartData = {
    labels: statuses.map(labelFor),
    datasets: [
      {
        label: 'OD Forms by Status',
        data:  statuses.map((s) => statusCounts[s]),
        backgroundColor: statuses.map(colourFor)
      }
    ]
  };

  const { buildings, units, odforms } = stats;

  // ─── render ──────────────────────────────────────────────
  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* sidebar left out for brevity */}
      <main className="flex-1">
        <TopNav />

        <section className="p-4">
          <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>

          {/* topline stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Total Buildings" value={buildings} colour="blue"   />
            <StatCard title="Total Units"     value={units}     colour="green"  />
            <StatCard title="Total OD Forms"  value={odforms}   colour="purple" />
          </div>

          {/* bar chart */}
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-4">OD-Forms status breakdown</h2>
            <div className="w-full max-w-lg mx-auto">
              <Bar data={chartData} options={{ responsive: true, plugins:{legend:{display:false}} }} />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

// ─── helpers ───────────────────────────────────────────────
function StatCard({ title, value, colour }) {
  const shades = {
    blue:   'from-blue-500 to-blue-600',
    green:  'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600'
  };
  return (
    <div className={`bg-gradient-to-r ${shades[colour]} text-white p-6 rounded shadow`}>
      <div className="uppercase text-xs font-bold mb-2">{title}</div>
      <div className="text-3xl font-bold">{value}</div>
    </div>
  );
}

function Centered({ children, className = '' }) {
  return <div className={`p-4 text-center ${className}`}>{children}</div>;
}
