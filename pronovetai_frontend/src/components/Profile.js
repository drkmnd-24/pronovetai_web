import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";
import { useNavigate } from "react-router-dom";

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [passwordData, setPasswordData] = useState({
    new_password: "",
    confirm_new_password: ""
  });
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [updateMsg, setUpdateMsg] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!token) {
      setError("No access token found. Please log in.");
      setLoading(false);
      return;
    }

    fetch("http://127.0.0.1:8000/api/users/me", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setProfile(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching profile data");
        setLoading(false);
      });

    fetch("http://127.0.0.1:8000/api/users/me/logs", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setLogs(data);
      })
      .catch((err) => {
        console.error("Error fetching logs:", err);
      });
  }, []);

  const handleProfileChange = (e) => {
    setProfile({
      ...profile,
      [e.target.name]: e.target.value
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    });
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("accessToken");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/users/me", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          email: profile.email,
          first_name: profile.first_name,
          last_name: profile.last_name
        })
      });
      if (!res.ok) {
        throw new Error("Failed to update profile");
      }
      setUpdateMsg("Profile updated successfully");
    } catch (error) {
      setUpdateMsg("Error updating profile");
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setUpdateMsg("Passwords do not match");
      return;
    }
    const token = localStorage.getItem("accessToken");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/users/me/change_password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          new_password: passwordData.new_password
        })
      });
      if (!res.ok) {
        throw new Error("Failed to change password");
      }
      setUpdateMsg("Password changed successfully");
      setPasswordData({ new_password: "", confirm_new_password: "" });
    } catch (error) {
      setUpdateMsg("Error changing password");
    }
  };

  if (loading) return <div className="container mx-auto p-4">Loading profile...</div>;
  if (error) return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6 text-center">My Profile</h1>

        {/* Profile Details Form */}
        <form onSubmit={handleUpdateProfile} className="bg-white p-4 rounded shadow mb-6">
          <div className="mb-4">
            <label className="block font-semibold mb-1">Username</label>
            <input
              type="text"
              value={profile.username}
              readOnly
              className="w-full border p-2 rounded bg-gray-200"
            />
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">Email</label>
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleProfileChange}
              className="w-full border p-2 rounded"
            />
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">First Name</label>
            <input
              type="text"
              name="first_name"
              value={profile.first_name}
              onChange={handleProfileChange}
              className="w-full border p-2 rounded"
            />
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">Last Name</label>
            <input
              type="text"
              name="last_name"
              value={profile.last_name}
              onChange={handleProfileChange}
              className="w-full border p-2 rounded"
            />
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">User Role</label>
            <input
              type="text"
              value={profile.role}
              readOnly
              className="w-full border p-2 rounded bg-gray-200"
            />
          </div>
          <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
            Update Profile
          </button>
        </form>

        {/* Change Password Form */}
        <form onSubmit={handleChangePassword} className="bg-white p-4 rounded shadow mb-6">
          <h2 className="text-xl font-bold mb-4">Change Password</h2>
          <div className="mb-4">
            <label className="block font-semibold mb-1">New Password</label>
            <input
              type="password"
              name="new_password"
              value={passwordData.new_password}
              onChange={handlePasswordChange}
              className="w-full border p-2 rounded"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block font-semibold mb-1">Confirm Password</label>
            <input
              type="password"
              name="confirm_new_password"
              value={passwordData.confirm_new_password}
              onChange={handlePasswordChange}
              className="w-full border p-2 rounded"
              required
            />
          </div>
          <button type="submit" className="bg-green-500 text-white px-4 py-2 rounded">
            Change Password
          </button>
        </form>

        {/* Log Section */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Logs</h2>
          {logs.length === 0 ? (
            <p>No logs available</p>
          ) : (
            <ul className="list-disc pl-5">
              {logs.map((log) => (
                <li key={log.id}>
                  {log.message} - <span className="text-sm text-gray-600">{log.timestamp}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {updateMsg && (
          <div className="mt-4 text-center text-blue-600 font-semibold">{updateMsg}</div>
        )}
      </div>
    </div>
  );
};

export default Profile;
