/* ───────── toast helper ──────────────────────────── */
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

/* change modal header & primary-button copy */
function setMode(isEdit) {
    $('#modalTitle').text(isEdit ? 'Edit Company' : 'Create New Company');
    $('#saveBtnText').text(isEdit ? 'Save changes' : 'Create Company');
}

/* ───────── DataTable + CRUD ───────────────────────── */
const $table = $('#companies-table');
const $modal = $('#companyModal');
const $form = $('#companyForm')[0];

let dt, editingId = null;
const token = localStorage.getItem('access');

/* initialise table once DOM is ready */
$(function () {
    if (!token) return (location.href = '/');

    dt = $table.DataTable({
        ajax: {
            url: '/api/companies/',
            headers: {Authorization: `Bearer ${token}`},
            dataSrc: j => Array.isArray(j) ? j : j.results
        },
        columns: [
            {data: 'id', visible: false},       // hidden primary-key
            {data: 'name'},
            {data: 'industry', defaultContent: '—'},
            {data: 'address_bldg', defaultContent: '—'},
            {data: 'address_city', defaultContent: '—'},
            {                        // actions
                data: null, orderable: false, searchable: false, className: 'text-center',
                render: (_, __, row) => `
                <div class="d-flex justify-content-center gap-1">
                    <button class="btn btn-sm btn-outline-primary edit-company"  data-id="${row.id}" title="Edit">
                        <i class="bi bi-pencil-square"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger  delete-company" data-id="${row.id}" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>`
            }
        ],
        order: [[1, 'asc']],     // sort by Company Name
        pageLength: 25,
        responsive: true
    });
});

/* reset modal form → “create” mode */
function resetForm() {
    $form.reset();
    editingId = null;
    setMode(false);
}

/* open modal in “create” mode */
$('[data-bs-target="#companyModal"]').on('click', resetForm);

/* EDIT ------------------------------------------------------------- */
$table.on('click', '.edit-company', async function () {
    const id = this.dataset.id;
    try {
        const r = await fetch(`/api/companies/${id}/`,
            {headers: {Authorization: `Bearer ${token}`}});
        if (!r.ok) throw await r.text();
        const data = await r.json();

        /* populate form (keys must match input[name]) */
        Object.entries(data).forEach(([k, v]) => {
            const el = $form.elements.namedItem(k);
            if (el) el.value = v ?? '';
        });

        editingId = id;
        setMode(true);
        new bootstrap.Modal($modal[0]).show();
    } catch (err) {
        alert('Could not load record: ' + err);
    }
});

/* DELETE ----------------------------------------------------------- */
$table.on('click', '.delete-company', function () {
    const id = this.dataset.id;
    if (!confirm('Delete company #' + id + ' ?')) return;

    fetch(`/api/companies/${id}/`,
        {method: 'DELETE', headers: {Authorization: `Bearer ${token}`}})
        .then(r => r.ok
            ? (toast('Deleted'), dt.ajax.reload(null, false))
            : r.text().then(t => alert('Error: ' + t)));
});

/* CREATE  /  UPDATE ------------------------------------------------ */
$('#saveCompanyBtn').on('click', async e => {
    e.preventDefault();
    if (!$form.checkValidity()) return $form.reportValidity();

    const payload = Object.fromEntries(new FormData($form));
    const url = editingId ? `/api/companies/${editingId}/` : '/api/companies/';
    const opts = {
        method: editingId ? 'PATCH' : 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
    };

    const r = await fetch(url, opts);
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