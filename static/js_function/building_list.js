(function () {
    const token = localStorage.getItem('access');
    if (!token) {
        window.location.href = '/';
        return;
    }

    // Tiny helpers
    const toast = (msg, ok = true) => {
        const $el = $(`
      <div class="toast align-items-center ${ok ? 'text-bg-success' : 'text-bg-danger'} border-0 position-fixed bottom-0 end-0 m-3" role="alert">
        <div class="d-flex">
          <div class="toast-body">${msg}</div>
          <button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>`).appendTo('body');
        new bootstrap.Toast($el[0]).show();
    };
    const auth = {Authorization: `Bearer ${token}`};

    // State
    let dt;
    let currentLogsBuildingId = null;

    // DataTable
    dt = $('#buildings-table').DataTable({
        ajax: {
            url: '/api/buildings/',
            headers: auth,
            dataSrc: j => Array.isArray(j) ? j : j.results
        },
        columns: [
            {data: 'name'},
            {data: 'grade_desc', defaultContent: '—'},
            {data: 'is_peza_certified', render: v => v ? 'Yes' : 'No'},
            {data: 'is_strata', render: v => v ? 'Yes' : 'No'},
            {data: 'address_city', defaultContent: '—'},
            {data: null, defaultContent: '—', className: 'last-ts'},   // filled async
            {data: null, defaultContent: '—', className: 'last-by'},   // filled async
            {
                data: null,
                orderable: false,
                searchable: false,
                className: 'text-center',
                render: (_, __, row) => `
          <div class="d-flex justify-content-center gap-1">
            <button class="btn btn-sm btn-outline-secondary logs" data-id="${row.id}" title="Logs"><i class="bi bi-journal-text"></i></button>
            <button class="btn btn-sm btn-outline-primary edit" data-id="${row.id}" title="Edit"><i class="bi bi-pencil-square"></i></button>
            <button class="btn btn-sm btn-outline-danger del" data-id="${row.id}" title="Delete"><i class="bi bi-trash"></i></button>
          </div>`
            }
        ],
        order: [[0, 'asc']],
        pageLength: 25,
        lengthMenu: [25, 50, 100],
        responsive: true,
        drawCallback: function () {
            // fill "last update/by" asynchronously
            const api = this.api();
            api.rows({page: 'current'}).every(function () {
                const d = this.data();
                const $row = $(this.node());
                fetch(`/api/buildings/${d.id}/last_edited/`, {headers: auth})
                    .then(r => r.ok ? r.json() : null)
                    .then(info => {
                        if (!info) return;
                        $row.find('td.last-ts').text(info.timestamp ? new Date(info.timestamp).toLocaleString() : '—');
                        $row.find('td.last-by').text(info.user || '—');
                    })
                    .catch(() => {
                    });
            });
        }
    });

    // Open create modal
    $('#btn-add-building').on('click', () => {
        $('#buildingModalTitle').text('Add Building');
        $('#building_id').val('');
        $('#buildingForm')[0].reset();
        new bootstrap.Modal(document.getElementById('buildingModal')).show();
    });

    // Edit
    $('#buildings-table').on('click', '.edit', async function () {
        const id = this.dataset.id;
        try {
            const r = await fetch(`/api/buildings/${id}/`, {headers: auth});
            if (!r.ok) throw new Error(await r.text());
            const b = await r.json();
            $('#buildingModalTitle').text('Edit Building');
            $('#building_id').val(b.id);
            $('#b_name').val(b.name || '');
            $('#b_grade').val(b.grade || '');
            $('#b_type').val(b.building_type || ''); // expects id
            $('#b_city').val(b.address_city || '');
            $('#b_peza').prop('checked', !!b.is_peza_certified);
            $('#b_strata').prop('checked', !!b.is_strata);
            $('#b_image').val('');
            $('#b_log').val('');
            new bootstrap.Modal(document.getElementById('buildingModal')).show();
        } catch (e) {
            toast('Could not load building', false);
        }
    });

    // Save (create or update)
    $('#saveBuildingBtn').on('click', async () => {
        const id = $('#building_id').val();
        const payload = {
            name: $('#b_name').val().trim(),
            grade: $('#b_grade').val().trim() || null,
            building_type: $('#b_type').val().trim() || null,  // id or null
            address_city: $('#b_city').val().trim() || null,
            is_peza_certified: $('#b_peza').is(':checked'),
            is_strata: $('#b_strata').is(':checked')
        };
        if (!payload.name) {
            return toast('Name is required', false);
        }

        try {
            // create or update
            let r;
            if (id) {
                r = await fetch(`/api/buildings/${id}/`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json', ...auth},
                    body: JSON.stringify(payload)
                });
            } else {
                r = await fetch('/api/buildings/', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', ...auth},
                    body: JSON.stringify(payload)
                });
            }
            if (!r.ok) throw new Error(await r.text());
            const saved = await r.json();

            // optional: upload image
            const file = document.getElementById('b_image').files[0];
            if (file) {
                const fd = new FormData();
                fd.append('building', saved.id);
                fd.append('image', file);
                const ir = await fetch('/api/building-images/', {method: 'POST', headers: auth, body: fd});
                if (!ir.ok) toast('Image upload failed (continuing)', false);
            }

            // optional: log note
            const note = $('#b_log').val().trim();
            if (note) {
                await fetch(`/api/buildings/${saved.id}/logs/`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json', ...auth},
                    body: JSON.stringify({message: note})
                });
            }

            bootstrap.Modal.getInstance(document.getElementById('buildingModal')).hide();
            toast(id ? 'Building updated' : 'Building created');
            dt.ajax.reload(null, false);
        } catch (e) {
            toast('Save failed', false);
        }
    });

    // Delete
    $('#buildings-table').on('click', '.del', async function () {
        const id = this.dataset.id;
        if (!confirm('Delete this building?')) return;
        const r = await fetch(`/api/buildings/${id}/`, {method: 'DELETE', headers: auth});
        if (r.ok) {
            toast('Deleted');
            dt.ajax.reload(null, false);
        } else {
            toast('Delete failed', false);
        }
    });

    // View logs
    $('#buildings-table').on('click', '.logs', async function () {
        const id = this.dataset.id;
        currentLogsBuildingId = id;
        await loadLogs(id);
        new bootstrap.Modal(document.getElementById('logsModal')).show();
    });

    async function loadLogs(buildingId) {
        const list = $('#logsList').empty();
        try {
            const r = await fetch(`/api/buildings/${buildingId}/logs/`, {headers: auth});
            if (!r.ok) throw new Error();
            const rows = await r.json();
            if (!rows.length) {
                list.append('<li class="list-group-item">No logs yet.</li>');
                return;
            }
            rows.forEach(x => {
                const when = x.timestamp ? new Date(x.timestamp).toLocaleString() : '';
                const who = x.user_display || x.user || '—';
                list.append(`<li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="me-3">
            <div class="fw-semibold">${who}</div>
            <div>${x.message || ''}</div>
          </div>
          <span class="badge bg-light text-dark">${when}</span>
        </li>`);
            });
        } catch {
            list.append('<li class="list-group-item text-danger">Could not load logs.</li>');
        }
    }

    // Add log from modal
    $('#addLogBtn').on('click', async () => {
        const msg = $('#logMessage').val().trim();
        if (!msg || !currentLogsBuildingId) return;
        const r = await fetch(`/api/buildings/${currentLogsBuildingId}/logs/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', ...auth},
            body: JSON.stringify({message: msg})
        });
        if (r.ok) {
            $('#logMessage').val('');
            await loadLogs(currentLogsBuildingId);
            dt.ajax.reload(null, false); // refresh “last update/by”
        } else {
            toast('Adding log failed', false);
        }
    });

})();