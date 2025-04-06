// src/App.js
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import StaffRegistration from "./components/StaffRegistration";
import ManagerRegistration from "./components/ManagerRegistration";
import Dashboard from './components/Dashboard';
import BuildingsList from "./components/BuildingsList";
import UnitsList from "./components/UnitsList";
import CompaniesList from "./components/CompaniesList";
import ContactsList from "./components/ContactsList";
import ODFormsList from "./components/ODFormsList";
import Profile from "./components/Profile";
import './App.css';

function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register/staff" element={<StaffRegistration />} />
        <Route path="/register/manager" element={<ManagerRegistration />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/list/buildings" element={<BuildingsList />} />
        <Route path="/list/units" element={<UnitsList />} />
        <Route path="/list/companies" element={<CompaniesList />} />
        <Route path="/list/contacts" element={<ContactsList />} />
        <Route path="/list/odforms" element={<ODFormsList />} />
        {/* Default route */}
        <Route path="*" element={<Login />} />
      </Routes>
    </div>
  );
}

export default App;
