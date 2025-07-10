/* ───────── helpers ─────────────────────────────────────────── */
const fmtDatePH = s =>
    s ? new Date(s).toLocaleDateString('en-PH', {timeZone: 'Asia/Manila'})
        : '—';

const fmtDateTimePH = s =>
    s ? new Date(s).toLocaleString('en-PH',
            {timeZone: 'Asia/Manila', hour12: false})   // 08/07/2025 23:41:07
            .replace(',', '')
        : '—';

const toast = msg => {
    const el = $(`
   <div class="toast align-items-center text-bg-success border-0 position-fixed bottom-0 end-0 m-3" role="alert">
     <div class="d-flex">
       <div class="toast-body">${msg}</div>
       <button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
     </div>
   </div>`).appendTo('body');
    new bootstrap.Toast(el[0]).show();
};

/* change modal header & button copy */
function setMode(isEdit) {
    $('#modalTitle').text(isEdit ? 'Edit OD-Form' : 'Create New OD');
    $('#saveBtnText').text(isEdit ? 'Save changes' : 'Create OD');
}

/* ───────── DataTable + CRUD ───────────────────────────────── */
const $table = $('#odforms-table');
const $modal = $('#exampleModalScrollable');
const $form = $('#odformForm')[0];
let dt, editingId = null;
const token = localStorage.getItem('access');

/* ---------- init table ---------- */
$(function () {
    if (!token) return location.href = '/';

    dt = $table.DataTable({
        ajax: {
            url: '/api/odforms/',
            headers: {Authorization: `Bearer ${token}`},
            dataSrc: j => Array.isArray(j) ? j : j.results
        },
        columns: [
            {data: 'id', visible: false},

            /* Created On – date only (PH time) */
            {
                data: 'created',
                render: (d, type) => type === 'display' ? fmtDatePH(d) : d,
                className: 'whitespace-nowrap'
            },

            /* Edited On – date + time (PH time) */
            {
                data: 'edited_date',
                render: (d, type) => type === 'display' ? fmtDateTimePH(d) : d,
                className: 'whitespace-nowrap'
            },

            {data: 'call_taken_by', defaultContent: '—'},
            {data: 'intent', defaultContent: '—'},

            {
                data: 'status', className: 'text-center',
                render: s => {
                    const m = {
                        draft: 'secondary', pending: 'warning', active: 'primary',
                        done_deal: 'success', inactive: 'secondary', cancelled: 'danger'
                    };
                    return `<span class="badge bg-${m[s] || 'light'}">${s || '—'}</span>`;
                }
            },

            {
                data: null, orderable: false, searchable: false, className: 'text-center',
                render: (_, __, row) => `
        <button class="btn btn-sm btn-outline-primary edit-od" title="Edit" data-id="${row.id}">
          <i class="bi bi-pencil-square"></i>
        </button>
        <button class="btn btn-sm btn-outline-danger  delete-od" title="Delete" data-id="${row.id}">
          <i class="bi bi-trash"></i>
        </button>`
            }
        ],
        order: [[2, 'desc']],         /* sort by Edited On desc */
        pageLength: 25,
        responsive: true
    });
});

/* ---------- helpers ---------- */
function resetForm() {
    $form.reset();
    editingId = null;
    setMode(false);
}

/* ---------- ADD ---------- */
$('[data-bs-target="#exampleModalScrollable"]').on('click', resetForm);

/* ---------- EDIT ---------- */
$table.on('click', '.edit-od', async function () {
    const id = this.dataset.id;
    try {
        const r = await fetch(`/api/odforms/${id}/`, {headers: {Authorization: `Bearer ${token}`}});
        if (!r.ok) throw await r.text();
        const data = await r.json();
        Object.entries(data).forEach(([k, v]) => {
            const el = $form.elements.namedItem(k);
            if (!el) return;
            el.type === 'checkbox' ? el.checked = !!v : el.value = (v ?? '');
        });
        editingId = id;
        setMode(true);
        new bootstrap.Modal($modal[0]).show();
    } catch (err) {
        alert('Could not load record: ' + err);
    }
});

/* ---------- DELETE ---------- */
$table.on('click', '.delete-od', function () {
    const id = this.dataset.id;
    if (!confirm('Delete OD-Form #' + id + ' ?')) return;
    fetch(`/api/odforms/${id}/`, {method: 'DELETE', headers: {Authorization: `Bearer ${token}`}})
        .then(r => r.ok ? (toast('Deleted'), dt.ajax.reload(null, false))
            : r.text().then(t => alert('Error: ' + t)));
});

/* ---------- CREATE / UPDATE ---------- */
$('#saveOdFormBtn').on('click', async e => {
    e.preventDefault();
    if (!$form.checkValidity()) return $form.reportValidity();

    const fd = new FormData($form);

    ['size_minimum', 'size_maximum', 'budget_minimum', 'budget_maximum']
        .forEach(k => {
            if (fd.get(k) === '') fd.delete(k);
        });

    if (editingId) fd.delete('created');              // keep original on edit
    if (!fd.get('created')) fd.set('created', new Date().toISOString());

    const payload = Object.fromEntries(fd);
    const r = await fetch(editingId ? `/api/odforms/${editingId}/` : '/api/odforms/', {
        method: editingId ? 'PATCH' : 'POST',
        headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`},
        body: JSON.stringify(payload)
    });

    const txt = await r.text();
    const data = (() => {
        try {
            return JSON.parse(txt);
        } catch {
            return txt;
        }
    })();

    if (r.ok) {
        bootstrap.Modal.getInstance($modal[0]).hide();
        resetForm();
        dt.ajax.reload(null, false);
        toast(editingId ? 'Updated' : 'Created');
    } else {
        alert('Error ' + r.status + ': ' + (data.detail || txt.slice(0, 300)));
    }
});
