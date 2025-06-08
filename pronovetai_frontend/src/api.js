// src/api.js
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://127.0.0.1:8000/api';
const API= axios.create({
  baseURL: API_BASE.replace(/\/+$/, '') + '/',
  headers: { 'Content-Type': 'application/json' }
});

// — Helpers ----------------------------------------------------------------
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
  /* ➊   Allow a bare string: authFetch('units/')  */
  if (typeof config === 'string') {
    config = { url: config, method: 'get' };
  }
  /* ➋   Normalise url so both "units/" and "/units/" work */
  const cleanUrl = config.url.replace(/^\/+/, '');
  const token = localStorage.getItem('accessToken');
  const cfg   = {
    ...config,
    url: cleanUrl,
    headers: {
      ...(config.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  };

  try {
    return await API.request(cfg);
  } catch (err) {
    if (err.response?.status !== 401) throw err;

    // on 401, try silent refresh
    const newToken = await refreshAccessToken();
    if (!newToken) {
      localStorage.clear();
      window.location.href = '/login';
      return;
    }

    return API.request({
      ...cfg,
      headers: {
        ...cfg.headers,
        Authorization: `Bearer ${newToken}`,
      },
    });
  }
}

// — Exports ----------------------------------------------------------------
// named:   refreshAccessToken, authFetch
// default: the raw axios instance (API)
export default API;
