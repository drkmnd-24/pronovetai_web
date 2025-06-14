// src/components/BuildingsList.js
import React, { useEffect, useMemo, useState, useCallback } from 'react';
import { useTable, useSortBy, usePagination, useGlobalFilter } from 'react-table';
import { useNavigate } from 'react-router-dom';
import TopNav from './TopNav';
import { authFetch } from '../api';
import { Edit2, Trash2 } from 'lucide-react';

/* ––––– global search input ––––– */
function GlobalFilter({ filter, setFilter }) {
  return (
    <input
      className="border border-gray-300 p-2 rounded w-1/2"
      placeholder="Search by building name"
      value={filter || ''}
      onChange={e => setFilter(e.target.value || undefined)}
    />
  );
}

/* ––––– main component ––––– */
export default function BuildingsList() {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  /* fetch once on mount */
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

  /* handle edit navigation */
  const handleEdit = useCallback(building => {
    navigate(`/buildings/${building.id}/edit`);
  }, [navigate]);

  /* handle delete action */
  const handleDelete = useCallback(async building => {
    if (!window.confirm('Are you sure you want to delete this building?')) return;
    try {
      await authFetch({ method: 'delete', url: `buildings/${building.id}/` });
      setBuildings(prev => prev.filter(b => b.id !== building.id));
    } catch {
      alert('Failed to delete building');
    }
  }, []);

  /* helper for prettifying contacts */
  const contactName = b => {
    if (!b.contacts?.length) return 'N/A';
    const owner = b.contacts.find(c => c.contact_type === 'owner');
    const c = owner || b.contacts[0];
    return `${c.first_name || ''} ${c.last_name || ''}`.trim() || c.email || 'N/A';
  };

  /* columns definition (memoised) */
  const columns = useMemo(() => [
    { Header: 'Building', accessor: 'name' },
    {
      Header: 'Address',
      accessor: row =>
        row.address
          ? `${row.address.street_address || ''}, ${row.address.city || ''}`.replace(/^, /, '') || 'No address'
          : 'No address',
      id: 'address'
    },
    { Header: 'Type', accessor: 'building_type' },
    { Header: 'Contact', accessor: contactName, id: 'contact' },
    { Header: 'Grade', accessor: 'grade' },
    { Header: 'PEZA', accessor: r => (r.is_peza_certified ? 'Yes' : 'No'), id: 'peza' },
    { Header: 'Strata', accessor: r => (r.is_strata ? 'Yes' : 'No'), id: 'strata' },
    {
      Header: 'Actions',
      id: 'actions',
      Cell: ({ row }) => (
        <div className="flex space-x-2">
          <button
            onClick={() => handleEdit(row.original)}
            aria-label="Edit building"
            className="p-1 hover:bg-gray-100 rounded"
          >
            <Edit2 className="w-5 h-5 text-blue-600 hover:text-blue-800" />
          </button>
          <button
            onClick={() => handleDelete(row.original)}
            aria-label="Delete building"
            className="p-1 hover:bg-gray-100 rounded"
          >
            <Trash2 className="w-5 h-5 text-red-600 hover:text-red-800" />
          </button>
        </div>
      )
    }
  ], [handleEdit, handleDelete]);

  const data = useMemo(() => buildings, [buildings]);

  /* react-table instance */
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    state,
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
    setGlobalFilter
  } = useTable(
    { columns, data, initialState: { pageSize: 10 } },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const { pageIndex, pageSize, globalFilter } = state;

  /* ––– render ––– */
  if (loading) return <Centered>Loading…</Centered>;
  if (error) return <Centered className="text-red-600">{error}</Centered>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Buildings ({data.length})</h1>

        {/* search + record count */}
        <div className="mb-4 flex justify-between items-center">
          <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter} />
          <span className="text-lg">Total Records: {data.length}</span>
        </div>

        {/* table */}
        <div className="overflow-x-auto">
          <table {...getTableProps()} className="min-w-full bg-white border rounded">
            <thead className="bg-gray-200">
              {headerGroups.map(hg => (
                <tr {...hg.getHeaderGroupProps()}>
                  {hg.headers.map(col => (
                    <th
                      {...col.getHeaderProps(col.getSortByToggleProps())}
                      className="py-2 px-4 border text-left cursor-pointer select-none"
                    >
                      {col.render('Header')}
                      {col.isSorted ? (col.isSortedDesc ? ' 🔽' : ' 🔼') : ''}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody {...getTableBodyProps()}>
              {page.map(row => {
                prepareRow(row);
                return (
                  <tr {...row.getRowProps()} className="border-t">
                    {row.cells.map(cell => (
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
            <NavButton onClick={() => gotoPage(0)} disabled={!canPreviousPage}>{'<<'}</NavButton>
            <NavButton onClick={previousPage} disabled={!canPreviousPage}>Previous</NavButton>
          </div>

          <span>
            Page <strong>{pageIndex + 1} of {pageOptions.length}</strong>
          </span>

          <div>
            <NavButton onClick={nextPage} disabled={!canNextPage}>Next</NavButton>
            <NavButton onClick={() => gotoPage(pageCount - 1)} disabled={!canNextPage}>{'>>'}</NavButton>
          </div>

          <select
            className="border p-2 rounded"
            value={pageSize}
            onChange={e => setPageSize(Number(e.target.value))}
          >
            {[10, 20, 50].map(s => <option key={s} value={s}>Show {s}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}

/* small helpers */
const NavButton = ({ children, ...rest }) => (
  <button
    {...rest}
    className="px-3 py-1 bg-gray-300 rounded mr-2 disabled:opacity-50"
  >
    {children}
  </button>
);

function Centered({ children, className = '' }) {
  return <div className={`container mx-auto p-4 text-center ${className}`}>{children}</div>;
}
