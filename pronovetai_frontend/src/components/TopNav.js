import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";

const TopNav = () => {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Retrieve token and username from localStorage
  const token = localStorage.getItem("accessToken");
  const username = localStorage.getItem("username") || "User";

  useEffect(() => {
    console.log("TopNav mounted. Token:", token, "Username:", username);
  }, [token, username]);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = () => {
    console.log("Logging out user.");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    navigate("/login");
  };

  const handleViewProfileClick = () => {
    console.log("View Profile clicked. Token:", token);
    // Always navigate to /profile (if token is missing, Profile component should handle that)
    setDropdownOpen(false);
  };

  return (
    <nav className="bg-gray-800 text-white p-4 flex flex-wrap justify-between items-center">
      <div className="flex space-x-4">
        <Link to="/dashboard" className="hover:underline">
          Dashboard
        </Link>
        <Link to="/list/buildings" className="hover:underline">
          Buildings
        </Link>
        <Link to="/list/units" className="hover:underline">
          Units
        </Link>
        <Link to="/list/companies" className="hover:underline">
          Companies
        </Link>
        <Link to="/list/contacts" className="hover:underline">
          Contacts
        </Link>
        <Link to="/list/odforms" className="hover:underline">
          OD Forms
        </Link>
      </div>
      <div className="relative">
        <button
          onClick={toggleDropdown}
          className="hover:underline focus:outline-none"
        >
          Welcome, {username} &#9662;
        </button>
        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-40 bg-white text-black rounded shadow-lg z-10">
            <Link
              to="/profile"
              onClick={handleViewProfileClick}
              className="block px-4 py-2 hover:bg-gray-200"
            >
              View Profile
            </Link>
            <button
              onClick={handleLogout}
              className="w-full text-left px-4 py-2 hover:bg-gray-200"
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default TopNav;
