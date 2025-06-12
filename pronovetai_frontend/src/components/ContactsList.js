// src/components/ContactsList.js          ← replace entire file
import React, { useEffect, useState, useMemo } from 'react';
import TopNav   from './TopNav';
import { authFetch } from '../api';
import {
  useTable,
  usePagination,
  useSortBy,
  useGlobalFilter,
} from 'react-table';

const GlobalFilter = ({ filter, setFilter }) => (
  <input
    value={filter || ''}
    onChange={e => setFilter(e.target.value || undefined)}
    placeholder="Search contacts…"
    className="border border-gray-300 p-2 rounded w-1/2"
  />
);

export default function ContactsList() {
  const [contacts, setContacts] = useState([]);
  const [loading,  setLoading] = useState(true);
  const [error,    setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const { data } = await authFetch({ url: 'contacts/', method: 'get' });
        setContacts(data);
      } catch (err) {
        console.error(err);
        setError('Error fetching contacts');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const columns = useMemo(() => [
    { Header: 'Name', accessor: 'full_name' },
    { Header: 'Company', accessor: 'company_name', Cell: ({ value }) => value || '—' },
    { Header: 'Title', accessor: 'title', Cell: ({ value }) => value || '—' },
    { Header: 'Position', accessor: 'position', Cell: ({ value }) => value || '—' },
    { Header: 'Email', accessor: 'email', Cell: ({ value }) => value || '—' },
    { Header: 'Phone', accessor: 'phone_number', Cell: ({ value }) => value || '—' },
    { Header: 'Mobile', accessor: 'mobile_number', Cell: ({ value }) => value || '—' },
    { Header: 'Fax', accessor: 'fax_number', Cell: ({ value }) => value || '—' },
  ], []);

  const {
    getTableProps, getTableBodyProps, headerGroups, page, prepareRow,
    state: { pageIndex, pageSize, globalFilter },
    setGlobalFilter, canPreviousPage, canNextPage,
    pageOptions, gotoPage, nextPage, previousPage, setPageSize,
  } = useTable(
    { columns, data: contacts, initialState: { pageIndex: 0, pageSize: 10 } },
    useGlobalFilter,
    useSortBy,
    usePagination,
  );

  if (loading) return <div className="p-4">Loading…</div>;
  if (error)   return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div className="min-h-screen flex flex-col">
      <TopNav />

      <div className="container mx-auto p-4 flex-1">
        <h1 className="text-2xl font-bold mb-4">
          Contacts&nbsp;<span className="text-gray-500 text-sm">({contacts.length})</span>
        </h1>

        <div className="mb-4 flex justify-between items-center">
          <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter} />
          <div className="text-lg">Total: {contacts.length}</div>
        </div>

        <div className="overflow-x-auto">
          <table {...getTableProps()} className="min-w-full bg-white border rounded">
            <thead className="bg-gray-200">
              {headerGroups.map(hg => (
                <tr {...hg.getHeaderGroupProps()}>
                  {hg.headers.map(col => (
                    <th
                      {...col.getHeaderProps(col.getSortByToggleProps())}
                      className="py-2 px-4 border text-left cursor-pointer"
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

        {/* pagination */}
        <div className="flex justify-between items-center mt-4 gap-4">
          <div className="space-x-2">
            <button onClick={() => gotoPage(0)} disabled={!canPreviousPage} className="btn-pager">{'<<'}</button>
            <button onClick={previousPage} disabled={!canPreviousPage} className="btn-pager">Prev</button>
            <button onClick={nextPage} disabled={!canNextPage}     className="btn-pager">Next</button>
            <button onClick={() => gotoPage(pageOptions.length - 1)} disabled={!canNextPage} className="btn-pager">{'>>'}</button>
          </div>

          <span>
            Page&nbsp;<strong>{pageIndex + 1} / {pageOptions.length}</strong>
          </span>

          <select
            value={pageSize}
            onChange={e => setPageSize(Number(e.target.value))}
            className="border p-1 rounded"
          >
            {[10, 20, 50, 100].map(sz => (
              <option key={sz} value={sz}>Show {sz}</option>
            ))}
          </select>
        </div>
      </div>

      <style jsx="true">{`
        .btn-pager { @apply px-3 py-1 bg-gray-300 rounded disabled:opacity-50; }
      `}</style>
    </div>
  );
}
