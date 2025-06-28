import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Login      from './pages/Login.jsx';
import Dashboard  from './pages/Dashboard.jsx';

// quick auth guard
const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken');
  return token ? children : <Navigate to="/login" replace />;
};

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/dashboard" element={<PrivateRoute><Dashboard/></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}
