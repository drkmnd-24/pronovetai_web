import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const TopNav = () => {
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  // Assume that the username is stored in localStorage (set it during login)
  const username = localStorage.getItem("username") || "User";

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  const handleLogout = () => {
    // Clear token and username and navigate to login
    localStorage.removeItem("accessToken");
    localStorage.removeItem("username");
    navigate("/login");
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
        <button onClick={toggleDropdown} className="hover:underline focus:outline-none">
          Welcome, {username} &#9662;
        </button>
        {dropdownOpen && (
          <div className="absolute right-0 mt-2 w-40 bg-white text-black rounded shadow-lg z-10">
            <Link to="/profile" className="block px-4 py-2 hover:bg-gray-200">
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
