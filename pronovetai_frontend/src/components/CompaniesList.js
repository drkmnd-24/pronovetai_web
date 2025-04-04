// src/components/CompaniesList.js
import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const CompaniesList = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    fetch("http://127.0.0.1:8000/api/companies/", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setCompanies(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching companies");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="container mx-auto p-4">Loading...</div>;
  if (error) return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Companies</h1>
        <ul>
          {companies.map((c) => (
            <li key={c.id} className="mb-2">
              {c.name} - {c.address ? c.address.street_address : "No address"}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default CompaniesList;
