import React, {useState} from "react";

const StaffRegistration = () => {
    const [formData, setFormData] = useState ({
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
        setFormData({...formData, [e.target.name]: e.target.value});
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
            const response = await fetch('http://127.0.0.1:8000/api/register/staff', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(formData)
            });
            const data = await response.json();
            if (response.ok) {
                setSuccess('Staff account created successfully');
                setFormData({
                    username: '',
                    email: '',
                    first_name: '',
                    last_name: '',
                    password: '',
                    confirm_password: ''
                });
            } else {
                setError(data.detail || 'Registration failed');
            }
        } catch (err) {
            setError('An error occurred, please try again');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="max-w-md w-full bg-white p-8 rounded shadow">
                <h2 className="text-2xl font-bold mb-6 text-center">Staff Registration</h2>
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
                      <button type="submit" className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
                        Register Staff
                      </button>
                </form>
            </div>
        </div>
    );
};

export default StaffRegistration;