/* ───────── toast helper ─────────────────────────── */
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

/* swap modal copy between Create / Edit */
function setMode(isEdit) {
    $('#modalTitle').text(isEdit ? 'Edit Contact' : 'Create New Contact');
    $('#saveBtnText').text(isEdit ? 'Save changes' : 'Create Contact');
}

/* ─────────── DOM shortcuts ───────────────────────── */
const $table = $('#contacts-table');
const $modal = $('#exampleModalScrollable');
const $form = $('#contactForm')[0];
const $companyVis = $('#companyDisplay');   // read-only visible text
const $companyHid = $('#companyId');        // hidden <input name="company">

let dt, editingId = null;
const token = localStorage.getItem('access');

/* ========== initialise DataTable ================== */
$(function () {
    if (!token) return (location.href = '/');

    dt = $table.DataTable({
        ajax: {
            url: '/api/contacts/',
            headers: {Authorization: `Bearer ${token}`},
            dataSrc: j => Array.isArray(j) ? j : j.results
        },
        columns: [
            {data: 'full_name', defaultContent: '—'},
            {data: 'company_name', defaultContent: '—'},
            {data: 'phone_number', defaultContent: '—'},
            {data: 'mobile_number', defaultContent: '—'},
            {
                data: null, orderable: false, searchable: false, className: 'text-center',
                render: (_, __, row) => `
          <div class="d-flex justify-content-center gap-1">
            <button class="btn btn-sm btn-outline-primary edit-contact"
                    data-id="${row.id}" title="Edit">
                <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger delete-contact"
                    data-id="${row.id}" title="Delete">
                <i class="bi bi-trash"></i>
            </button>
          </div>`
            }
        ],
        order: [[0, 'asc']],
        pageLength: 25,
        responsive: true
    });
});

/* ========== helpers ================================= */
function resetForm() {
    $form.reset();
    $companyVis.val('');
    $companyHid.val('');
    editingId = null;
    setMode(false);
}

/* open modal in “create” mode */
$('[data-bs-target="#exampleModalScrollable"]').on('click', resetForm);

/* ─────── company search modal ------------------------ */
$('#btnCompanySearch').on('click', () => $('#companySearchModal').modal('show'));

$('#companySearchInput').on('keyup', doCompanySearch);
$('#companySearchBtn').on('click', doCompanySearch);

async function doCompanySearch() {
    const q = $('#companySearchInput').val().trim();
    if (!q) return;
    const r = await fetch(`/api/companies/?search=${encodeURIComponent(q)}`,
        {headers: {Authorization: `Bearer ${token}`}});
    if (!r.ok) {
        alert('Search failed');
        return;
    }
    const data = await r.json();
    const list = Array.isArray(data) ? data : data.results;

    const $tbody = $('#companySearchBody').empty();
    list.forEach(c => {
        $('<tr>')
            .append(`<td>${c.id}</td><td>${c.name}</td>`)
            .css('cursor', 'pointer')
            .on('click', () => selectCompany(c))
            .appendTo($tbody);
    });
}

function selectCompany(c) {
    $companyVis.val(c.name);
    $companyHid.val(c.id);      // this value will be submitted
    $('#companySearchModal').modal('hide');
}

$('#btnClearCompany').on('click', () => {
    $companyVis.val('');
    $companyHid.val('');
});

/* ------------ EDIT -------------------------------- */
$table.on('click', '.edit-contact', async function () {
  const id = this.dataset.id;
  try {
    const r = await fetch(`/api/contacts/${id}/`,
        { headers:{ Authorization:`Bearer ${token}` }});
    if (!r.ok) throw await r.text();
    const data = await r.json();

    /* populate ordinary inputs */
    Object.entries(data).forEach(([k,v])=>{
      const el = $form.elements.namedItem(k);
      if (el) el.value = v ?? '';
    });

    /* fill company selector */
    if (data.company) {
      $companyVis.val(data.company_name);
      $companyHid.val(data.company);
    } else {
      $companyVis.val('');
      $companyHid.val('');
    }

    editingId = id;
    setMode(true);
    new bootstrap.Modal($modal[0]).show();
  } catch (err) {
    alert('Could not load record: ' + err);
  }
});

/* ------------ DELETE ------------------------------ */
$table.on('click', '.delete-contact', function () {
  const id = this.dataset.id;
  if (!confirm(`Delete contact #${id}?`)) return;

  fetch(`/api/contacts/${id}/`, {
    method :'DELETE',
    headers:{ Authorization:`Bearer ${token}` }
  }).then(r=> r.ok
      ? (toast('Deleted'), dt.ajax.reload(null,false))
      : r.text().then(t=>alert('Error: '+t)));
});

/* ------------ CREATE / UPDATE --------------------- */
$('#saveOdFormBtn').on('click', async e=>{
  e.preventDefault();
  if(!$form.checkValidity()){ $form.reportValidity(); return; }

  const fd = new FormData($form);
  /* inject (nullable) company id */
  const companyVal = $companyHid.val().trim();
  fd.set('company', companyVal ? parseInt(companyVal, 10) : null);

  const payload = Object.fromEntries(fd.entries());

  const url  = editingId ? `/api/contacts/${editingId}/` : '/api/contacts/';
  const opts = {
    method : editingId ? 'PATCH' : 'POST',
    headers: { 'Content-Type':'application/json',
               Authorization:`Bearer ${token}` },
    body   : JSON.stringify(payload)
  };

  const r   = await fetch(url, opts);
  const txt = await r.text();
  const data = (()=>{ try{return JSON.parse(txt);}catch{return txt;} })();

  if (r.ok) {
    bootstrap.Modal.getInstance($modal[0]).hide();
    resetForm();
    dt.ajax.reload(null,false);
    toast(editingId ? 'Updated' : 'Created');
  } else {
    alert('Error '+r.status+': '+(data.detail || txt.slice(0,300)));
  }
});

