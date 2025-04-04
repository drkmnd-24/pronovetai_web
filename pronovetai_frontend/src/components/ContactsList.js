// src/components/ContactsList.js
import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const ContactsList = () => {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    fetch("http://127.0.0.1:8000/api/contacts/", {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`
      }
    })
      .then((res) => res.json())
      .then((data) => {
        setContacts(data);
        setLoading(false);
      })
      .catch((err) => {
        setError("Error fetching contacts");
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="container mx-auto p-4">Loading...</div>;
  if (error) return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Contacts</h1>
        <ul>
          {contacts.map((ct) => (
            <li key={ct.id} className="mb-2">
              {ct.first_name} {ct.last_name} - {ct.email}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ContactsList;