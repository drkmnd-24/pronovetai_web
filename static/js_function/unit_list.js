$(document).ready(function () {
    const token = localStorage.getItem('access');
    if (!token) {
        location.href = '/';
        return;
    }

    $('#units-table').DataTable({
        ajax: {
            url: '/api/units/',
            headers: {Authorization: `Bearer ${token}`},
            dataSrc: json => Array.isArray(json) ? json : json.results,
            error: xhr => alert(`Could not load units (${xhr.status} ${xhr.statusText})`)
        },
        columns: [
            {data: 'name'},
            {data: 'building_name', defaultContent: '—'},
            {data: 'floor', defaultContent: '—'},
            {data: 'marketing_status_display', defaultContent: '—'},
            {data: 'vacancy_status_display', defaultContent: '—'},
            {
                data: 'foreclosed',
                render: d => d
                    ? '<span class="badge bg-danger">Yes</span>'
                    : '<span class="badge bg-success">No</span>',
                className: 'text-center'
            }
        ],
        pageLength: 25,
        lengthMenu: [25, 50, 100],
        responsive: true
    });
});