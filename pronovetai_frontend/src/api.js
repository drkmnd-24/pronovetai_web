// simple axios wrapper with silent refresh helper
import axios from 'axios';

export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api';

const API = axios.create({
  baseURL: API_BASE + '/',
  headers: { 'Content-Type': 'application/json' },
});

export async function refreshAccessToken() {
  const refresh = localStorage.getItem('refreshToken');
  if (!refresh) return null;

  try {
    const { data } = await API.post('token/refresh/', { refresh });
    localStorage.setItem('accessToken', data.access);
    return data.access;
  } catch {
    return null;
  }
}

export async function authFetch(config) {
  const token = localStorage.getItem('accessToken');
  const cfg   = {
    ...config,
    headers: { ...(config.headers || {}),
               ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  };

  try {
    return await API.request(cfg);
  } catch (err) {
    if (err.response?.status !== 401) throw err;
    const newToken = await refreshAccessToken();
    if (!newToken) {
      localStorage.clear();
      window.location.href = '/login';
      return;
    }
    return API.request({ ...cfg,
      headers: { ...cfg.headers, Authorization: `Bearer ${newToken}` },
    });
  }
}

export default API;     // default export = raw axios instance
