// src/components/ManagerRegistration.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authFetch } from '../api';

const ManagerRegistration = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirm_password: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match.');
      return;
    }

    try {
      const res = await authFetch('/register/manager', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      const data = await res.json();

      if (res.ok) {
        // If the backend returns tokens on registration
        if (data.access && data.refresh) {
          localStorage.setItem('accessToken', data.access);
          localStorage.setItem('refreshToken', data.refresh);
          localStorage.setItem('username', data.username || formData.username);
          navigate('/dashboard');
        } else {
          // Otherwise, just show success and go to login
          setSuccess('Manager account created successfully.');
          setFormData({
            username: '',
            email: '',
            first_name: '',
            last_name: '',
            password: '',
            confirm_password: ''
          });
          navigate('/login');
        }
      } else {
        setError(data.detail || 'Registration failed.');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    }
  };

  const handleCancel = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white p-8 rounded shadow">
        <h2 className="text-2xl font-bold mb-6 text-center">Manager Registration</h2>
        {error && <div className="mb-4 text-red-500">{error}</div>}
        {success && <div className="mb-4 text-green-500">{success}</div>}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block mb-1">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="email" className="block mb-1">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="first_name" className="block mb-1">First Name</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="last_name" className="block mb-1">Last Name</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="password" className="block mb-1">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <div className="mb-6">
            <label htmlFor="confirm_password" className="block mb-1">Confirm Password</label>
            <input
              type="password"
              id="confirm_password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
              required
            />
          </div>
          <button type="submit" className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">
            Register Manager
          </button>
        </form>
        <div className="mt-4">
          <button
            onClick={handleCancel}
            className="w-full bg-gray-500 text-white py-2 rounded hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ManagerRegistration;
