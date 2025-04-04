import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const BuildingsList = () => {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const [sortKey, setSortKey] = useState("");
  const [sortDirection, setSortDirection] = useState("asc");

  const getContactName = (building) => {
    if (building.contacts && building.contacts.length > 0) {
      const ownerContact = building.contacts.find(
        (c) => c.contact_type === "owner"
      );
      if (ownerContact) {
        return `${ownerContact.first_name || ""} ${ownerContact.last_name || ""}`.trim();
      }
      const firstContact = building.contacts[0];
      return `${firstContact.first_name || ""} ${firstContact.last_name || ""}`.trim();
    }
    return "N/A";
  };

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

  // Function to handle sorting when a header is clicked.
  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDirection("asc");
    }
  };

  // Sorting logic for buildings array.
  const sortedBuildings = [...buildings].sort((a, b) => {
    let aVal = "";
    let bVal = "";

    if (sortKey === "name") {
      aVal = a.name.toLowerCase();
      bVal = b.name.toLowerCase();
    } else if (sortKey === "building_type") {
      aVal = a.building_type.toLowerCase();
      bVal = b.building_type.toLowerCase();
    } else if (sortKey === "contact") {
      aVal = getContactName(a).toLowerCase();
      bVal = getContactName(b).toLowerCase();
    } else {
      return 0;
    }

    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  // Pagination: determine current page items
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentBuildings = sortedBuildings.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(sortedBuildings.length / itemsPerPage);

  const nextPage = () => {
    if (currentPage < totalPages) setCurrentPage(currentPage + 1);
  };
  const prevPage = () => {
    if (currentPage > 1) setCurrentPage(currentPage - 1);
  };

  if (loading) return <div className="container mx-auto p-4">Loading...</div>;
  if (error) return <div className="container mx-auto p-4 text-red-600">{error}</div>;

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
                onClick={() => handleSort("contact")}
              >
                Contact Person {sortKey === "contact" ? (sortDirection === "asc" ? "▲" : "▼") : ""}
              </th>
              <th className="py-2 px-4 border">Grade</th>
              <th className="py-2 px-4 border">PEZA Certified</th>
              <th className="py-2 px-4 border">Strata</th>
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
                <td className="py-2 px-4 border">{getContactName(b)}</td>
                <td className="py-2 px-4 border">{b.grade}</td>
                <td className="py-2 px-4 border">{b.is_peza_certified ? "Yes" : "No"}</td>
                <td className="py-2 px-4 border">{b.is_strata ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
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
