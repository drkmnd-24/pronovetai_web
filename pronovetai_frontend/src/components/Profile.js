import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "../api";
import TopNav from "./TopNav";

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
    const loadData = async () => {
      try {
        const res = await authFetch("/users/me/");
        if (!res.ok) throw new Error("Failed to fetch profile");
        const data = await res.json();
        setProfile(data);
      } catch (err) {
        setError("Error fetching profile data");
      }

      try {
        const resLogs = await authFetch("/users/me/logs");
        if (resLogs.ok) {
          const logsData = await resLogs.json();
          setLogs(logsData);
        }
      } catch (err) {
        console.error("Error fetching logs:", err);
      }

      setLoading(false);
    };

    loadData();
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
    setUpdateMsg("");
    try {
      const res = await authFetch("/users/me/", {
        method: "PATCH",
        body: JSON.stringify({
          email: profile.email,
          first_name: profile.first_name,
          last_name: profile.last_name
        })
      });
      if (!res.ok) throw new Error();
      setUpdateMsg("Profile updated successfully");
    } catch {
      setUpdateMsg("Error updating profile");
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setUpdateMsg("");
    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setUpdateMsg("Passwords do not match");
      return;
    }
    try {
      const res = await authFetch("/users/me/change_password", {
        method: "POST",
        body: JSON.stringify({
          new_password: passwordData.new_password
        })
      });
      if (!res.ok) throw new Error();
      setUpdateMsg("Password changed successfully");
      setPasswordData({ new_password: "", confirm_new_password: "" });
    } catch {
      setUpdateMsg("Error changing password");
    }
  };

  if (loading) return <div className="container mx-auto p-4">Loading profile...</div>;
  if (error)   return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-3xl font-bold mb-6 text-center">My Profile</h1>

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

        <div className="bg-white p-4 rounded shadow">
          <h2 className="text-xl font-bold mb-4">Logs</h2>
          {logs.length === 0 ? (
            <p>No logs available</p>
          ) : (
            <ul className="list-disc pl-5">
              {logs.map(log => (
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
