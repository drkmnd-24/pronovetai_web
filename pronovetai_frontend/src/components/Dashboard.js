import React, { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import TopNav from "./TopNav";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register the required chart components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const Dashboard = () => {
  const [buildings, setBuildings] = useState([]);
  const [units, setUnits] = useState([]);
  const [odForms, setOdForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        setError("No access token found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const [buildingsRes, unitsRes, odFormsRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/buildings/", {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch("http://127.0.0.1:8000/api/units/", {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }),
          fetch("http://127.0.0.1:8000/api/odforms/", {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }),
        ]);

        if (!buildingsRes.ok || !unitsRes.ok || !odFormsRes.ok) {
          throw new Error(
            "Failed to fetch data from the API. Please check your credentials."
          );
        }

        const buildingsData = await buildingsRes.json();
        const unitsData = await unitsRes.json();
        const odFormsData = await odFormsRes.json();

        if (!Array.isArray(buildingsData)) {
          throw new Error("Unexpected data format for buildings.");
        }
        if (!Array.isArray(unitsData)) {
          throw new Error("Unexpected data format for units.");
        }
        if (!Array.isArray(odFormsData)) {
          throw new Error("Unexpected data format for office demand forms.");
        }

        setBuildings(buildingsData);
        setUnits(unitsData);
        setOdForms(odFormsData);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError(err.message || "Error fetching data");
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (error) {
    return <div className="p-8 text-center text-red-600">{error}</div>;
  }

  if (loading) {
    return <div className="p-8 text-center">Loading dashboard...</div>;
  }

  // Calculate available vacant units per building
  const buildingVacancy = buildings.map((building) => {
    const vacantCount = units.filter(
      (unit) => unit.building === building.id && unit.vacancy_status === "vacant"
    ).length;
    return { ...building, vacantCount };
  });

  // Calculate leases expiring within the next 30 days
  const today = new Date();
  const expiringLeases = units.filter((unit) => {
    if (!unit.lease_expiry_date) return false;
    const leaseExpiry = new Date(unit.lease_expiry_date);
    const diffDays = (leaseExpiry - today) / (1000 * 60 * 60 * 24);
    return diffDays >= 0 && diffDays <= 30;
  });

  // Count OD forms by status
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
          odStatusCounts["done_deal"] || 0,
        ],
        backgroundColor: "rgba(75, 192, 192, 0.5)",
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6 text-center">Dashboard Overview</h1>
        {/* Grid container for the first row (Buildings & Expiring Leases) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-50 p-4 rounded shadow">
            <h2 className="text-2xl font-semibold mb-4">Buildings</h2>
            {buildingVacancy.length === 0 ? (
              <p>No buildings found.</p>
            ) : (
              <ul>
                {buildingVacancy.map((building) => (
                  <li key={building.id} className="mb-2">
                    <strong>{building.name}</strong> - Vacant Units: {building.vacantCount}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="bg-gray-50 p-4 rounded shadow">
            <h2 className="text-2xl font-semibold mb-4">Expiring Leases</h2>
            {expiringLeases.length === 0 ? (
              <p>No leases expiring within the next 30 days.</p>
            ) : (
              <ul>
                {expiringLeases.map((unit) => (
                  <li key={unit.id} className="mb-2">
                    <strong>{unit.name}</strong> (Building ID: {unit.building}) - Lease Expiry: {unit.lease_expiry_date}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        {/* Grid container for the second row (OD Forms Overview & Chart) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div className="bg-gray-50 p-4 rounded shadow">
            <h2 className="text-2xl font-semibold mb-4">Office Demand (OD) Forms</h2>
            {odForms.length === 0 ? (
              <p>No office demand records.</p>
            ) : (
              <ul>
                {odForms.map((od) => (
                  <li key={od.id} className="mb-2">
                    <strong>ID:</strong> {od.id} - <strong>Status:</strong> {od.status} - <strong>Intent:</strong> {od.intent}
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="bg-gray-50 p-4 rounded shadow flex flex-col items-center">
            <h2 className="text-2xl font-semibold mb-4">OD Forms Status Chart</h2>
            <div className="w-full max-w-md">
              <Bar data={chartData} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
