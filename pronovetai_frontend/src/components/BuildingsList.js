// src/components/BuildingsList.js
import React, { useEffect, useMemo, useState, useCallback } from 'react';
import {
  useTable,
  useSortBy,
  usePagination,
  useGlobalFilter,
} from 'react-table';
import TopNav from './TopNav';
import { authFetch } from '../api';
import { Edit2, Trash2 } from 'lucide-react';

/* -------------------------------------------------- */
/* Global filter (search)                             */
/* -------------------------------------------------- */
function GlobalFilter({ filter, setFilter }) {
  return (
    <input
      className="border border-gray-300 p-2 rounded w-1/2"
      placeholder="Search by building name"
      value={filter || ''}
      onChange={(e) => setFilter(e.target.value || undefined)}
    />
  );
}

/* -------------------------------------------------- */
/* Edit modal                                         */
/* -------------------------------------------------- */
function EditModal({ building, onClose, onSave }) {
  const [form, setForm] = useState({});

  /* populate form when modal opens */
  useEffect(() => {
    if (building) {
      setForm({
        building_name: building.name || '',
        building_grade: building.grade || '',
        building_peza: building.is_peza_certified || false,
        building_strata: building.is_strata || false,
        building_address_street: building.address?.street_address || '',
        building_address_brgy: building.address?.barangay || '',
        building_address_city: building.address?.city || '',
      });
    }
  }, [building]);

  const handleChange = (e) => {
    const { name, type, value, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      name: form.building_name,
      grade: form.building_grade,
      is_peza_certified: form.building_peza,
      is_strata: form.building_strata,
      address: {
        street_address: form.building_address_street,
        barangay: form.building_address_brgy,
        city: form.building_address_city,
      },
    };

    try {
      await authFetch({
        method: 'patch',
        url: `buildings/${building.id}/`,
        data: payload,
      });
      onSave({ ...building, ...payload });
      onClose();
    } catch {
      alert('Failed to update building');
    }
  };

  if (!building) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-lg max-h-screen overflow-y-auto">
        <h2 className="text-xl font-semibold mb-4">Edit Building</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium mb-1">Building Name</label>
            <input
              name="building_name"
              value={form.building_name}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>

          {/* Grade */}
          <div>
            <label className="block text-sm font-medium mb-1">Building Grade</label>
            <input
              name="building_grade"
              value={form.building_grade}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>

          {/* PEZA & Strata */}
          <div className="flex space-x-4">
            <label className="inline-flex items-center space-x-2">
              <input
                type="checkbox"
                name="building_peza"
                checked={form.building_peza}
                onChange={handleChange}
                className="h-4 w-4"
              />
              <span>PEZA Certified</span>
            </label>
            <label className="inline-flex items-center space-x-2">
              <input
                type="checkbox"
                name="building_strata"
                checked={form.building_strata}
                onChange={handleChange}
                className="h-4 w-4"
              />
              <span>Strata</span>
            </label>
          </div>

          {/* Address fields */}
          <div>
            <label className="block text-sm font-medium mb-1">Street</label>
            <input
              name="building_address_street"
              value={form.building_address_street}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Barangay</label>
            <input
              name="building_address_brgy"
              value={form.building_address_brgy}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">City</label>
            <input
              name="building_address_city"
              value={form.building_address_city}
              onChange={handleChange}
              className="w-full border border-gray-300 p-2 rounded"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 rounded"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded"
            >
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

/* -------------------------------------------------- */
/* Main component                                     */
/* -------------------------------------------------- */
export default function BuildingsList() {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);

  /* fetch data */
  useEffect(() => {
    (async () => {
      try {
        const { data } = await authFetch({ method: 'get', url: 'buildings/' });
        setBuildings(data);
      } catch {
        setError('Error fetching buildings');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  /* delete */
  const handleDelete = useCallback(async (building) => {
    if (!window.confirm('Are you sure you want to delete this building?')) return;
    try {
      await authFetch({ method: 'delete', url: `buildings/${building.id}/` });
      setBuildings((prev) => prev.filter((b) => b.id !== building.id));
    } catch {
      alert('Failed to delete building');
    }
  }, []);

  /* save after edit */
  const handleSave = (updated) => {
    setBuildings((prev) => prev.map((b) => (b.id === updated.id ? updated : b)));
  };

  /* table columns */
  const columns = useMemo(
    () => [
      { Header: 'Building Name', accessor: 'name' },
      { Header: 'Building Grade', accessor: 'grade' },
      {
        Header: 'PEZA',
        accessor: (r) => (r.is_peza_certified ? 'Yes' : 'No'),
        id: 'peza',
      },
      {
        Header: 'Strata',
        accessor: (r) => (r.is_strata ? 'Yes' : 'No'),
        id: 'strata',
      },
      {
        Header: 'Street',
        accessor: (r) => r.address?.street_address || '—',
        id: 'street',
      },
      {
        Header: 'Barangay',
        accessor: (r) => r.address?.barangay || '—',
        id: 'brgy',
      },
      {
        Header: 'City',
        accessor: (r) => r.address?.city || '—',
        id: 'city',
      },
      {
        Header: 'Actions',
        id: 'actions',
        Cell: ({ row }) => (
          <div className="flex space-x-2">
            <button
              onClick={() => setEditing(row.original)}
              className="p-1 hover:bg-gray-100 rounded"
              aria-label="Edit"
            >
              <Edit2 className="w-5 h-5 text-blue-600 hover:text-blue-800" />
            </button>
            <button
              onClick={() => handleDelete(row.original)}
              className="p-1 hover:bg-gray-100 rounded"
              aria-label="Delete"
            >
              <Trash2 className="w-5 h-5 text-red-600 hover:text-red-800" />
            </button>
          </div>
        ),
      },
    ],
    [handleDelete]
  );

  const data = useMemo(() => buildings, [buildings]);

  /* react-table instance */
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    // pagination helpers
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    setGlobalFilter,
    state,
  } = useTable(
    { columns, data, initialState: { pageSize: 10 } },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const { pageIndex, pageSize, globalFilter } = state;

  /* -------------------------------------------------- */
  /* Render                                             */
  /* -------------------------------------------------- */
  if (loading) return <Centered>Loading…</Centered>;
  if (error) return <Centered className="text-red-600">{error}</Centered>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">
          Buildings ({data.length})
        </h1>

        {/* search + record count */}
        <div className="mb-4 flex justify-between items-center">
          <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter} />
          <span>Total Records: {data.length}</span>
        </div>

        {/* table */}
        <div className="overflow-x-auto">
          <table
            {...getTableProps()}
            className="min-w-full bg-white border rounded"
          >
            <thead className="bg-gray-200">
              {headerGroups.map((hg) => (
                <tr {...hg.getHeaderGroupProps()}>
                  {hg.headers.map((col) => (
                    <th
                      {...col.getHeaderProps(col.getSortByToggleProps())}
                      className="py-2 px-4 border text-left cursor-pointer select-none"
                    >
                      {col.render('Header')}
                      {col.isSorted
                        ? col.isSortedDesc
                          ? ' 🔽'
                          : ' 🔼'
                        : ''}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody {...getTableBodyProps()}>
              {page.map((row) => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()} className="border-t">
                    {row.cells.map((cell) => (
                      <td {...cell.getCellProps()} className="py-2 px-4">
                        {cell.render('Cell')}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* pagination controls */}
        <div className="flex justify-between items-center mt-4">
          <div>
            <NavButton onClick={() => gotoPage(0)} disabled={!canPreviousPage}>
              {'<<'}
            </NavButton>
            <NavButton onClick={previousPage} disabled={!canPreviousPage}>
              Previous
            </NavButton>
          </div>

          <span>
            Page <strong>{pageIndex + 1}</strong> of{' '}
            <strong>{pageOptions.length}</strong>
          </span>

          <div>
            <NavButton onClick={nextPage} disabled={!canNextPage}>
              Next
            </NavButton>
            <NavButton
              onClick={() => gotoPage(pageCount - 1)}
              disabled={!canNextPage}
            >
              {'>>'}
            </NavButton>
          </div>

          <select
            className="border p-2 rounded"
            value={pageSize}
            onChange={(e) => setPageSize(Number(e.target.value))}
          >
            {[10, 20, 50].map((s) => (
              <option key={s} value={s}>
                Show {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* edit modal */}
      {editing && (
        <EditModal
          building={editing}
          onClose={() => setEditing(null)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

/* -------------------------------------------------- */
/* Small helpers                                      */
/* -------------------------------------------------- */
const NavButton = ({ children, ...rest }) => (
  <button
    {...rest}
    className="px-3 py-1 bg-gray-300 rounded mr-2 disabled:opacity-50"
  >
    {children}
  </button>
);

function Centered({ children, className = '' }) {
  return (
    <div className={`container mx-auto p-4 text-center ${className}`}>
      {children}
    </div>
  );
}
