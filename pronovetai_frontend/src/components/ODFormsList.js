// src/components/ODFormsList.js
import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const ODFormsList = () => {
  const [odForms, setOdForms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    fetch("http://127.0.0.1:8000/api/odforms/", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setOdForms(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching OD Forms");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div>
      <TopNav />
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">OD Forms</h1>
        <ul>
          {odForms.map((od) => (
            <li key={od.id} className="mb-2">
              ID: {od.id} - Status: {od.status} - Intent: {od.intent}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ODFormsList;
