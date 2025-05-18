// src/api.js
const API_BASE = 'http://127.0.0.1:8000/api';

export async function refreshAccessToken() {
    const refresh = localStorage.getItem('refreshToken');
    if (!refresh) return null;

    const resp = await fetch(`${API_BASE}/token/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
    });

    if (!resp.ok) return null;
    const { access } = await resp.json();
    localStorage.setItem('accessToken', access);
    return access;
}

export async function authFetch(url, options = {}) {
    let token = localStorage.getItem('accessToken');
    let res = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}`} : {}),
        },
    });
        // if token expired, try to refresh once and retry
    if (res.status === 401) {
        const newToken = await refreshAccessToken();
        if (!newToken) {
            // no valid refresh > force logout
            localStorage.clear();
            window.location.href = '/login';
            return;
        }
        // retry original request with new token
        res = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...(options.headers || {}),
                Authorization: `Bearer ${newToken}`,
            },
        });
    }
    return res;
}