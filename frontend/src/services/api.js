import axios from 'axios';

// Use explicit backend URL since we are running as separate services
// Fallback to /api for local dev if needed
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add token if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('csb_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle response errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('csb_token');
        }
        return Promise.reject(error);
    }
);

export default api;
