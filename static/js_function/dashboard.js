(function () {
    const token = localStorage.getItem('access');
    if (!token) return (window.location.href = '/');

    /* ---- helper to decode JWT payload ---- */
    function parseJwt(t) {
        try {
            const b64 = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(
                decodeURIComponent(
                    atob(b64)
                        .split('')
                        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                        .join('')
                )
            );
        } catch {
            return null;
        }
    }

    /* ---- fetch dashboard counters right away ---- */
    fetch('/api/dashboard/', {headers: {Authorization: `Bearer ${token}`}})
        .then(r => {
            if (r.status === 401) {
                localStorage.clear();
                return (window.location.href = '/');
            }
            return r.json();
        })
        .then(d => {
            if (!d) return;
            document.getElementById('stat-buildings').textContent = d.buildings ?? 0;
            document.getElementById('stat-units').textContent = d.units ?? 0;
            document.getElementById('stat-odforms').textContent = d.odforms ?? 0;
            document.getElementById('stat-users').textContent = d.users ?? 0;
        })
        .catch(console.error);

    /* ---- once the DOM is ready, fill in the names ---- */
    document.addEventListener('DOMContentLoaded', () => {
        const payload = parseJwt(token);
        if (!payload) return;

        const uname = payload.user_login || payload.username || '';
        const fname = payload.user_first_name || payload.first_name || '';
        const lname = payload.user_last_name || payload.last_name || '';
        const full = `${fname} ${lname}`.trim() || uname || 'User';

        /* guard-check every element just in case */
        const el1 = document.getElementById('navbar-fullname');
        const el2 = document.getElementById('dropdown-greeting');
        const el3 = document.getElementById('card-fullname');
        const el4 = document.getElementById('card-username');

        if (el1) el1.textContent = full;
        if (el2) el2.textContent = `Hello, ${full}!`;
        if (el3) el3.textContent = full;
        if (el4) el4.textContent = uname ? `@${uname}` : '';
    });
})();
