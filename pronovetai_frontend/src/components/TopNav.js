import React from "react";
import { Link } from "react-router-dom";

const TopNav = () => {
    return (
        <nav className="bg-gray-800 text-white p-4 flex space-x-4">
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
        </nav>
    );
};

export default TopNav;