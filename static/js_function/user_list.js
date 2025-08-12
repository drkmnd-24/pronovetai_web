(function () {
    const token = localStorage.getItem('access');
    if (!token) return (window.location.href = '/');

    // Simple toast helper
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

    // CSRF (only needed if your view uses SessionAuthentication)
    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    const API_LIST = '/api/admin/users/';          // list / retrieve / update / delete  (admin-only)
    const API_CREATE_STAFF = '/api/register/staff/';
    const API_CREATE_MANAGER = '/api/register/manager/';
    ''

    let dt; // DataTable instance

    $(function () {
        // Init table
        dt = $('#users-table').DataTable({
            ajax: {
                url: API_LIST,
                headers: {Authorization: `Bearer ${token}`},
                dataSrc: j => Array.isArray(j) ? j : j.results,
                error: (xhr) => {
                    if (xhr.status === 404) {
                        toast('Users API not found. Please add admin users endpoint.', false);
                    }
                }
            },
            columns: [
                {data: 'username'},
                {
                    data: null,
                    render: row => `${row.first_name || ''} ${row.last_name || ''}`.trim() || '—'
                },
                {data: 'email', defaultContent: '—'},
                {data: 'user_type_desc', defaultContent: '—'},
                {
                    data: 'is_staff',
                    render: v => v ? '<span class="badge bg-primary">Yes</span>' : '<span class="badge bg-light text-dark">No</span>',
                    className: 'text-center'
                },
                {
                    data: 'is_superuser',
                    render: v => v ? '<span class="badge bg-danger">Yes</span>' : '<span class="badge bg-light text-dark">No</span>',
                    className: 'text-center'
                },
                {
                    data: 'is_active',
                    render: v => v ? '<span class="badge bg-success">Active</span>' : '<span class="badge bg-secondary">Inactive</span>',
                    className: 'text-center'
                },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    className: 'text-center',
                    render: (_, __, row) => `
                <div class="d-flex justify-content-center gap-1">
                  <button class="btn btn-sm btn-outline-primary edit-user" data-id="${row.id}" title="Edit">
                    <i class="bi bi-pencil-square"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger delete-user" data-id="${row.id}" title="Delete">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>`
                }
            ],
            order: [[0, 'asc']],
            pageLength: 25,
            responsive: true
        });

        // Open modal in create mode
        $('.btn-add-user').on('click', () => {
            $('#userModalTitle').text('Create User');
            $('#userForm')[0].reset();
            $('#editingId').val('');
            $('#is_active').prop('checked', true);
            $('#is_staff').prop('checked', false);
            $('#is_superuser').prop('checked', false);
        });

        // Edit: load record then open modal
        $('#users-table').on('click', '.edit-user', async function () {
            const id = this.dataset.id;
            try {
                const r = await fetch(API_LIST + id + '/', {headers: {Authorization: `Bearer ${token}`}});
                if (!r.ok) throw new Error(await r.text());
                const u = await r.json();

                $('#userModalTitle').text('Edit User');
                $('#editingId').val(u.id);
                const f = $('#userForm')[0];
                f.username.value = u.username || '';
                f.email.value = u.email || '';
                f.first_name.value = u.first_name || '';
                f.last_name.value = u.last_name || '';
                f.user_type.value = u.user_type || u.user_type_desc || '';
                $('#role').val(u.is_superuser ? 'manager' : (u.is_staff ? 'staff' : 'staff'));
                $('#is_active').prop('checked', !!u.is_active);
                $('#is_staff').prop('checked', !!u.is_staff);
                $('#is_superuser').prop('checked', !!u.is_superuser);

                // Clear password fields; leave blank to keep unchanged
                f.password1.value = '';
                f.password2.value = '';

                new bootstrap.Modal(document.getElementById('userModal')).show();
            } catch (e) {
                toast('Could not load user: ' + e.message, false);
            }
        });

        // Delete
        $('#users-table').on('click', '.delete-user', async function () {
            const id = this.dataset.id;
            if (!confirm('Delete this user?')) return;
            const r = await fetch(API_LIST + id + '/', {
                method: 'DELETE',
                headers: {Authorization: `Bearer ${token}`, 'X-CSRFToken': getCookie('csrftoken') || ''}
            });
            if (r.ok) {
                toast('Deleted');
                dt.ajax.reload(null, false);
            } else {
                toast('Delete failed', false);
            }
        });

        // Save (create or update)
        $('#saveUserBtn').on('click', async () => {
            const f = $('#userForm')[0];
            if (!f.checkValidity()) {
                f.reportValidity();
                return;
            }

            const payload = {
                username: f.username.value.trim(),
                email: f.email.value.trim(),
                first_name: f.first_name.value.trim(),
                last_name: f.last_name.value.trim(),
                user_type: f.user_type.value.trim(), // id or label
                is_active: $('#is_active').is(':checked'),
                is_staff: $('#is_staff').is(':checked'),
                is_superuser: $('#is_superuser').is(':checked'),
            };

            const pass1 = f.password1.value;
            const pass2 = f.password2.value;
            if (pass1 || pass2) {
                if (pass1 !== pass2) return toast('Passwords do not match', false);
                payload.password = pass1;
            }

            const id = $('#editingId').val();
            try {
                if (id) {
                    // Update existing (admin-only endpoint)
                    const r = await fetch(API_LIST + id + '/', {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                            Authorization: `Bearer ${token}`,
                            'X-CSRFToken': getCookie('csrftoken') || ''
                        },
                        body: JSON.stringify(payload)
                    });
                    if (!r.ok) throw new Error(await r.text());
                    toast('Updated');
                } else {
                    // Create using existing endpoints (choose by role)
                    const role = document.getElementById('role').value;
                    const createUrl = role === 'manager' ? API_CREATE_MANAGER : API_CREATE_STAFF;

                    // Map to expected serializer fields
                    const body = {
                        username: payload.username,
                        email: payload.email,
                        first_name: payload.first_name,
                        last_name: payload.last_name,
                        user_type: payload.user_type,
                        is_active: payload.is_active,
                        is_staff: payload.is_staff,
                        is_superuser: payload.is_superuser,
                        password: payload.password || undefined
                    };

                    const r = await fetch(createUrl, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`},
                        body: JSON.stringify(body)
                    });
                    if (!r.ok) throw new Error(await r.text());
                    toast('Created');
                }

                bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
                dt.ajax.reload(null, false);
            } catch (e) {
                toast('Save failed: ' + (e.message || e), false);
            }
        });
    });
})();