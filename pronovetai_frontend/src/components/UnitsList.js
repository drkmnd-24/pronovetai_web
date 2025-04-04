import React, { useEffect, useState } from "react";
import TopNav from "./TopNav";

const UnitsList = () => {
    const [units, setUnits] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const token = localStorage.getItem("accessToken");
        fetch("http://127.0.0.1:8000/api/units/", {
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            }
        })
            .then((res) => res.json())
            .then((data) => {
                setUnits(data);
                setLoading(false);
            })
            .catch((err) => {
                setError("Error fetching units");
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="p-4">Loading...</div>;
    if (error) return <div className="p-4 text-red-600">{error}</div>;

    return (
        <div>
            <TopNav />
            <div className="p-4">
                <h1 className="text-2xl font-bold mb-4">Units</h1>
                <ul>
                    {units.map((u) => (
                        <li key={u.id} className="mb-2">
                            {u.name} - Building ID: {u.building}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default UnitsList;