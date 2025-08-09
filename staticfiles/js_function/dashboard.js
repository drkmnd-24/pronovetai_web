(function () {
    const token = localStorage.getItem("access");
    if (!token) return window.location.href = "/";

    /* ---------- helper to pull payload out of a JWT ---------- */
    function parseJwt(t) {
        try {
            const b64 = t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(decodeURIComponent(atob(b64).split('').map(c =>
                '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
            ).join('')));
        } catch {
            return null;
        }
    }

    /* ---------- fill dashboard statistics (your old code) ---- */
    fetch(`/api/dashboard/?_=${Date.now()}`, {          // ← forces fresh GET
        headers: {Authorization: `Bearer ${token}`},
        credentials: "include",
    })
        .then(r => {
            if (r.status === 401) {
                localStorage.clear();
                return window.location.href = "/";
            }
            return r.json();
        })
        .then(d => {
            if (!d) return;
            document.getElementById("stat-buildings").textContent = d.buildings ?? 0;
            document.getElementById("stat-units").textContent = d.units ?? 0;
            document.getElementById("stat-odforms").textContent = d.odforms ?? 0;
            document.getElementById("stat-users").textContent = d.users ?? 0;
        })
        .catch(console.error);

    /* ---------- put the logged-in user’s name in the header --- */
    const payload = parseJwt(token);
    if (payload) {
        /*  adjust these keys to whatever you store in your JWT   */
        const uname = payload.user_login || payload.username || "";
        const fname = payload.user_first_name || payload.first_name || "";
        const lname = payload.user_last_name || payload.last_name || "";
        const full = `${fname} ${lname}`.trim() || uname;

        document.getElementById("navbar-fullname").textContent = full;
        document.getElementById("dropdown-greeting").textContent = `Hello, ${full}!`;

        document.getElementById("card-fullname").textContent = full;
        document.getElementById("card-username").textContent = uname ? `@${uname}` : '';
    }

    document.getElementById("logout-btn")?.addEventListener("click", async (e) => {
        e.preventDefault();
        try {
            await fetch("/api/logout/", {
                method: "POST",
                credentials: "include",   // send the sessionid cookie
            });
        } catch { /* network errors ignored */
        }

        localStorage.clear();
        window.location.href = "/";
    });

    /* ---- contacts that expire soon ---- */
    fetch(`/api/contacts/expiring?_=${Date.now()}`, {
        headers: {Authorization: `Bearer ${token}`},
        credentials: "include",
    })
        .then(r => r.json())
        .then(list => {
            const $table = $("#expire-table");
            const counter = document.getElementById("expire-count");

            /* build rows once – same order as <thead> */
            const rows = list.map(r => ([
                `<a href="/contactlist/?id=${r.id}">View</a>`,
                r.company,
                r.location,
                `<a href="/buildinglist/?name=${encodeURIComponent(r.building)}">${r.building}</a>`,
                r.unit_name,
                r.lease_expiry,
                r.gfa,
            ]));

            /* create or refresh DataTable */
            if ($.fn.dataTable.isDataTable($table)) {
                $table.DataTable().clear().rows.add(rows).draw();
            } else {
                $table.DataTable({
                    data: rows,
                    columns: [
                        {title: "Action", orderable: false, searchable: false},
                        {title: "Company Name"},
                        {title: "Location"},
                        {title: "Building"},
                        {title: "Unit Name"},
                        {title: "Lease Expiry", type: "date"},
                        {title: "Unit&nbsp;GFA", className: "text-end"},
                    ],
                    pageLength: 10,
                    lengthMenu: [10, 25, 50, 100],
                    responsive: true
                });
            }

            if (counter) counter.textContent = `(${list.length} records)`;
        })
        .catch(console.error);
})();