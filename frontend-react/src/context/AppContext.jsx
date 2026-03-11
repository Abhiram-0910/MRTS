import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
    const [userId, setUserId] = useState('demo_user');
    const [language, setLanguage] = useState('en');
    const [token, setToken] = useState(null);

    // Automatically fetch a generic auth token so the user can use the app seamlessly
    useEffect(() => {
        const fetchToken = async () => {
            try {
                const formData = new URLSearchParams();
                formData.append('username', 'admin');
                formData.append('password', 'mirai2024');

                const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
                const res = await axios.post(`${API_BASE}/token`, formData, {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                });

                const accessToken = res.data.access_token;
                setToken(accessToken);

                // Globally attach token to axios so ALL requests are authenticated automatically
                axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

            } catch (err) {
                console.error("Failed to authenticate with backend:", err);
                toast.error("Failed to connect securely to the backend.");
            }
        };

        fetchToken();
    }, []);

    return (
        <AppContext.Provider value={{ userId, setUserId, language, setLanguage, token }}>
            {children}
        </AppContext.Provider>
    );
};

export const useAppContext = () => useContext(AppContext);
