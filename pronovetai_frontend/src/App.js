import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import StaffRegistration from "./components/StaffRegistration";
import ManagerRegistration from "./components/ManagerRegistration";
import './App.css';


function App() {
    return (
        <div className="App">
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register/staff" element={<StaffRegistration />} />
                <Route path="/register/manager" element={<ManagerRegistration />} />
                {/* Default route */}
                <Route path="*" element={<Login />} />
            </Routes>
        </div>
    );
}

export default App;