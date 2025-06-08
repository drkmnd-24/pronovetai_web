// src/pages/UnitList.js
import React, {
  useEffect,
  useState,
  useCallback,
  useRef,
  useMemo,
} from 'react';
import {
  useTable,
  usePagination,
  useSortBy,
  useGlobalFilter,
} from 'react-table';
import TopNav from './TopNav';
import { authFetch } from '../api';

/* ---------- global search (placeholder) ---------- */
const GlobalFilter = ({ filter, setFilter }) => (
  <input
    value={filter || ''}
    onChange={e => setFilter(e.target.value || undefined)}
    placeholder="Search units…"
    className="border border-gray-300 p-2 rounded w-1/2"
  />
);

export default function UnitList() {
  /* ---------- column definitions ---------- */
  const columns = useMemo(
    () => [
      { Header: 'Unit', accessor: 'name' },
      { Header: 'Building', accessor: 'building_name' },
      { Header: 'Floor', accessor: 'floor' },
      { Header: 'Marketing', accessor: 'marketing_status' },
      { Header: 'Vacancy', accessor: 'vacancy_status' },
      {
        Header: 'Foreclosed',
        accessor: row => (row.foreclosed ? 'Yes' : 'No'),
        id: 'foreclosed',
      },
    ],
    [],
  );

  /* ---------- state ---------- */
  const [data, setData] = useState([]);
  const [total, setTotal] = useState(0);      // grand total from API
  const [pageCount, setPageCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const fetchIdRef = useRef(0);               // cancel stale requests

  /* ---------- fetch one page from the API ---------- */
  const fetchPage = useCallback(async ({ pageIndex, pageSize }) => {
    const fetchId = ++fetchIdRef.current;
    setLoading(true);
    try {
      const url = `units/?page=${pageIndex + 1}&page_size=${pageSize}`;
      const { data: payload } = await authFetch({ url, method: 'get' });

      if (fetchId !== fetchIdRef.current) return; // newer request exists
      setData(payload.results);
      setTotal(payload.count);
      setPageCount(Math.ceil(payload.count / pageSize));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* ---------- table instance ---------- */
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
    prepareRow,
    state: { pageIndex, pageSize, globalFilter },
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    canNextPage,
    canPreviousPage,
    pageOptions,
  } = useTable(
    {
      columns,
      data,
      manualPagination: true,  // server-side
      manualGlobalFilter: true,
      manualSortBy: true,
      pageCount,
      initialState: { pageIndex: 0, pageSize: 10 },
    },
    useGlobalFilter,
    useSortBy,
    usePagination,
  );

  /* reload when pageIndex / pageSize change */
  useEffect(() => {
    fetchPage({ pageIndex, pageSize });
  }, [fetchPage, pageIndex, pageSize]);

  /* ---------- render ---------- */
  return (
    <div className="min-h-screen flex flex-col">
      <TopNav />

      <main className="container mx-auto p-4 flex-1">
        <h1 className="text-2xl font-bold mb-4">
          Units&nbsp;
          <span className="text-sm text-gray-500">
            ({total.toLocaleString()} total)
          </span>
        </h1>

        <div className="mb-4 flex justify-between items-center">
          <GlobalFilter
            filter={globalFilter}
            setFilter={() => {
              /* hook up server search when ready */
            }}
          />
        </div>

        <div className="overflow-x-auto">
          <table
            {...getTableProps()}
            className="min-w-full bg-white border rounded"
          >
            <thead className="bg-gray-200">
              {headerGroups.map(hg => (
                <tr {...hg.getHeaderGroupProps()}>
                  {hg.headers.map(col => (
                    <th
                      {...col.getHeaderProps(col.getSortByToggleProps())}
                      className="py-2 px-4 border text-left cursor-pointer whitespace-nowrap"
                    >
                      {col.render('Header')}
                      {col.isSorted && (col.isSortedDesc ? ' 🔽' : ' 🔼')}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>

            <tbody {...getTableBodyProps()}>
              {loading && (
                <tr>
                  <td
                    colSpan={columns.length}
                    className="p-6 text-center"
                  >
                    Loading…
                  </td>
                </tr>
              )}

              {!loading &&
                page.map(row => {
                  prepareRow(row);
                  return (
                    <tr
                      {...row.getRowProps()}
                      className="border-t even:bg-gray-50"
                    >
                      {row.cells.map(cell => (
                        <td
                          {...cell.getCellProps()}
                          className="py-2 px-4"
                        >
                          {cell.render('Cell')}
                        </td>
                      ))}
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>

        {/* ---------- pagination ---------- */}
        <div className="flex flex-wrap justify-between items-center gap-3 mt-4">
          <div className="space-x-1">
            <button
              type="button"
              onClick={() => gotoPage(0)}
              disabled={!canPreviousPage}
              className="px-2 py-1 border rounded disabled:opacity-40"
            >
              ⏮
            </button>
            <button
              type="button"
              onClick={previousPage}
              disabled={!canPreviousPage}
              className="px-3 py-1 border rounded disabled:opacity-40"
            >
              Prev
            </button>
            <button
              type="button"
              onClick={nextPage}
              disabled={!canNextPage}
              className="px-3 py-1 border rounded disabled:opacity-40"
            >
              Next
            </button>
            <button
              type="button"
              onClick={() => gotoPage(pageCount - 1)}
              disabled={!canNextPage}
              className="px-2 py-1 border rounded disabled:opacity-40"
            >
              ⏭
            </button>
          </div>

          <span>
            Page&nbsp;
            <strong>
              {pageIndex + 1} / {pageOptions.length || 1}
            </strong>
          </span>

          <select
            value={pageSize}
            onChange={e => setPageSize(Number(e.target.value))}
            className="border p-1 rounded"
          >
            {[10, 20, 50, 100].map(sz => (
              <option key={sz} value={sz}>
                Show {sz}
              </option>
            ))}
          </select>
        </div>
      </main>
    </div>
  );
}
