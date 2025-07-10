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
function setMode(edit) {
  $('#modalTitle').text(edit ? 'Edit Contact' : 'Create New Contact');
  $('#saveBtnText').text(edit ? 'Save changes' : 'Create Contact');
}

/* ───────── DataTable + CRUD ─────────────────────── */
const $table = $('#contacts-table');
const $modal = $('#exampleModalScrollable');
const $form  = $('#contactForm')[0];

let dt, editingId = null;
const token = localStorage.getItem('access');

/* ------------ init table -------------------------- */
$(function () {
  if (!token) return (location.href = '/');

  dt = $table.DataTable({
    ajax: {
      url     : '/api/contacts/',
      headers : { Authorization: `Bearer ${token}` },
      dataSrc : j => Array.isArray(j) ? j : j.results
    },
    columns: [
      { data:'full_name',     defaultContent:'—' },
      { data:'company_name',  defaultContent:'—' },
      { data:'phone_number',  defaultContent:'—' },
      { data:'mobile_number', defaultContent:'—' },
      {                                   // Actions
        data:null, orderable:false, searchable:false, className:'text-center',
        render:(_,__,row)=>`
          <button class="btn btn-sm btn-outline-primary edit-contact"
                  data-id="${row.id}" title="Edit">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger  delete-contact"
                  data-id="${row.id}" title="Delete">
            <i class="bi bi-trash"></i>
          </button>`
      }
    ],
    order      : [[0,'asc']],   // sort by Full Name
    pageLength : 25,
    responsive : true
  });
});

/* ------------ helpers ----------------------------- */
function resetForm(){
  $form.reset();
  editingId = null;
  setMode(false);
}

$('[data-bs-target="#exampleModalScrollable"]').on('click', resetForm);

/* ------------ EDIT -------------------------------- */
$table.on('click','.edit-contact', async function () {
  const id = this.dataset.id;
  try{
    const r = await fetch(`/api/contacts/${id}/`,
                          { headers:{Authorization:`Bearer ${token}`} });
    if (!r.ok) throw await r.text();
    const data = await r.json();

    Object.entries(data).forEach(([k,v])=>{
      const el = $form.elements.namedItem(k);
      if (el) el.value = v ?? '';
    });

    editingId = id;
    setMode(true);
    new bootstrap.Modal($modal[0]).show();
  }catch(err){ alert('Could not load record: '+err); }
});

/* ------------ DELETE ------------------------------ */
$table.on('click','.delete-contact',function(){
  const id = this.dataset.id;
  if (!confirm('Delete contact #'+id+' ?')) return;

  fetch(`/api/contacts/${id}/`,
        { method:'DELETE', headers:{Authorization:`Bearer ${token}`} })
    .then(r=> r.ok
           ? (toast('Deleted'), dt.ajax.reload(null,false))
           : r.text().then(t=>alert('Error: '+t)));
});

/* ------------ CREATE / UPDATE --------------------- */
$('#saveOdFormBtn').on('click', async e=>{
  e.preventDefault();
  if(!$form.checkValidity()){ $form.reportValidity(); return; }

  const payload = Object.fromEntries(new FormData($form));
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

  if(r.ok){
    bootstrap.Modal.getInstance($modal[0]).hide();
    resetForm();
    dt.ajax.reload(null,false);
    toast(editingId ? 'Updated' : 'Created');
  }else{
    alert('Error '+r.status+': '+(data.detail||txt.slice(0,300)));
  }
});
