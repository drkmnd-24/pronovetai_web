// src/components/BuildingsList.js
import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const BuildingsList = () => {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  // Sorting state: sortKey can be 'name', 'building_type', or 'owner'
  const [sortKey, setSortKey] = useState("");
  const [sortDirection, setSortDirection] = useState("asc");

  // Fetch buildings data
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    fetch("http://127.0.0.1:8000/api/buildings/", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        setBuildings(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching buildings");
        setLoading(false);
      });
  }, []);

  // Function to handle sorting when a sortable header is clicked
  const handleSort = (key) => {
    // Toggle sort direction if clicking same key; otherwise set to ascending.
    if (sortKey === key) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }
  };

  // Sort buildings array based on sortKey and sortDirection.
  const sortedBuildings = [...buildings].sort((a, b) => {
    let aVal, bVal;
    // Determine the value based on key
    if (sortKey === "name") {
      aVal = a.name.toLowerCase();
      bVal = b.name.toLowerCase();
    } else if (sortKey === "building_type") {
      aVal = a.building_type.toLowerCase();
      bVal = b.building_type.toLowerCase();
    } else if (sortKey === "owner") {
      // Use created_by.username if available; otherwise empty string.
      aVal = a.created_by ? a.created_by.username.toLowerCase() : "";
      bVal = b.created_by ? b.created_by.username.toLowerCase() : "";
    } else {
      // If no sort key is set, keep original order.
      return 0;
    }

    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  // Compute pagination: get current page items
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentBuildings = sortedBuildings.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(sortedBuildings.length / itemsPerPage);

  // Pagination functions
  const nextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };
  const prevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  if (loading)
    return <div className="container mx-auto p-4">Loading...</div>;
  if (error)
    return (
      <div className="container mx-auto p-4 text-red-600">{error}</div>
    );

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Buildings</h1>
        <table className="min-w-full bg-white border">
          <thead>
            <tr className="bg-gray-200">
              <th
                className="py-2 px-4 border cursor-pointer"
                onClick={() => handleSort("name")}
              >
                Building Name {sortKey === "name" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
              </th>
              <th className="py-2 px-4 border">Building Address</th>
              <th
                className="py-2 px-4 border cursor-pointer"
                onClick={() => handleSort("building_type")}
              >
                Building Type {sortKey === "building_type" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
              </th>
              <th
                className="py-2 px-4 border cursor-pointer"
                onClick={() => handleSort("owner")}
              >
                Building Owner {sortKey === "owner" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
              </th>
              <th className="py-2 px-4 border">No. of Floors</th>
            </tr>
          </thead>
          <tbody>
            {currentBuildings.map((b) => (
              <tr key={b.id} className="text-center border-t">
                <td className="py-2 px-4 border">{b.name}</td>
                <td className="py-2 px-4 border">
                  {b.address
                    ? `${b.address.street_address}, ${b.address.city}`
                    : "No address"}
                </td>
                <td className="py-2 px-4 border">{b.building_type}</td>
                <td className="py-2 px-4 border">
                  {b.created_by ? b.created_by.username : "N/A"}
                </td>
                <td className="py-2 px-4 border">{b.number_of_floors}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {/* Pagination controls */}
        <div className="flex justify-between items-center mt-4">
          <button
            onClick={prevPage}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Previous
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={nextPage}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};

export default BuildingsList;
