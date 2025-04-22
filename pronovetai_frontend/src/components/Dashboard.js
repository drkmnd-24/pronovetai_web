// src/components/Dashboard.js
import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from "chart.js";

// Register required chart components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  // States for data fetching
  const [buildings, setBuildings] = useState([]);
  const [units, setUnits] = useState([]);
  const [odForms, setOdForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch dashboard data on mount
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      setError("No access token found.");
      setLoading(false);
      return;
    }
    Promise.all([
      fetch("http://127.0.0.1:8000/api/buildings/", {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      }),
      fetch("http://127.0.0.1:8000/api/units/", {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      }),
      fetch("http://127.0.0.1:8000/api/odforms/", {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        }
      })
    ])
      .then(async ([buildRes, unitRes, odRes]) => {
        if (!buildRes.ok || !unitRes.ok || !odRes.ok) {
          throw new Error("Error fetching dashboard data");
        }
        const buildData = await buildRes.json();
        const unitData = await unitRes.json();
        const odData = await odRes.json();
        setBuildings(buildData);
        setUnits(unitData);
        setOdForms(odData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="p-4 text-center">Loading Dashboard...</div>;
  }
  if (error) {
    return <div className="p-4 text-center text-red-600">{error}</div>;
  }

  // Compute totals
  const totalBuildings = buildings.length;
  const totalUnits = units.length;
  const totalOD = odForms.length;

  // Calculate OD Forms status counts for chart
  const odStatusCounts = odForms.reduce((acc, od) => {
    const status = od.status;
    acc[status] = (acc[status] || 0) + 1;
    return acc;
  }, {});
  const chartData = {
    labels: ["active", "inactive", "done_deal"],
    datasets: [
      {
        label: "OD Forms Count",
        data: [
          odStatusCounts["active"] || 0,
          odStatusCounts["inactive"] || 0,
          odStatusCounts["done_deal"] || 0
        ],
        backgroundColor: [
          "rgba(75, 192, 192, 0.6)",
          "rgba(255, 159, 64, 0.6)",
          "rgba(153, 102, 255, 0.6)"
        ]
      }
    ]
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      {/* Sidebar (visible on md screens and up) */}
      <aside className="hidden md:block w-64 bg-white shadow">
        <div className="p-4">
          <h2 className="text-lg font-bold mb-4">Menu</h2>
          <ul>
            <li className="mb-2">
              <a href="/dashboard" className="text-gray-800 hover:text-blue-500">
                Dashboard
              </a>
            </li>
            <li className="mb-2">
              <a href="/list/buildings" className="text-gray-800 hover:text-blue-500">
                Buildings
              </a>
            </li>
            <li className="mb-2">
              <a href="/list/units" className="text-gray-800 hover:text-blue-500">
                Units
              </a>
            </li>
            <li className="mb-2">
              <a href="/list/companies" className="text-gray-800 hover:text-blue-500">
                Companies
              </a>
            </li>
            <li className="mb-2">
              <a href="/list/contacts" className="text-gray-800 hover:text-blue-500">
                Contacts
              </a>
            </li>
            <li className="mb-2">
              <a href="/list/odforms" className="text-gray-800 hover:text-blue-500">
                OD Forms
              </a>
            </li>
          </ul>
        </div>
      </aside>

      {/* Main content area */}
      <div className="flex-1">
        <TopNav />
        <div className="p-4">
          <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded shadow">
              <div className="uppercase text-xs font-bold mb-2">
                Total Buildings
              </div>
              <div className="text-3xl font-bold">{totalBuildings}</div>
            </div>
            <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded shadow">
              <div className="uppercase text-xs font-bold mb-2">Total Units</div>
              <div className="text-3xl font-bold">{totalUnits}</div>
            </div>
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded shadow">
              <div className="uppercase text-xs font-bold mb-2">
                Total OD Forms
              </div>
              <div className="text-3xl font-bold">{totalOD}</div>
            </div>
          </div>
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-xl font-bold mb-4">OD Forms Status</h2>
            <div className="w-full max-w-lg">
              <Bar data={chartData} options={{ responsive: true }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
