import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";


const BuildingsList = () => {
    const [buildings, setBuildings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        fetch("http://127.0.0.1:8000/api/buildings/", {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            }
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

    if (loading) return <div className="p-4">Loading...</div>;
    if (error) return <div className="p-4 text-red-600">{error}</div>;

    return (
        <div>
            <TopNav />
            <div className="p-4">
                <h1 className="text-2xl font-bold mb-4">Buildings</h1>
                <ul>
                    {buildings.map((b) => (
                        <li key={b.id} className="mb-2">
                            {b.name} - {b.address ? b.address.street_address: "No address"}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};


export default BuildingsList;