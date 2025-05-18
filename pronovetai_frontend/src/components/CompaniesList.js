// src/components/CompaniesList.js
import React, { useEffect, useState, useMemo } from "react";
import {authFetch} from "../api";
import TopNav from "./TopNav";
import {
  useTable,
  useSortBy,
  usePagination,
  useGlobalFilter
} from "react-table";

// Global search input component
const GlobalFilter = ({ filter, setFilter }) => (
  <input
    value={filter || ""}
    onChange={e => setFilter(e.target.value || undefined)}
    placeholder="Search companies..."
    className="border border-gray-300 p-2 rounded w-1/2"
  />
);

const CompaniesList = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch companies on mount
  useEffect(() => {
    async function load() {
      try {
        const res = await authFetch('/companies/');
        if (!res.ok) throw new Error('Fetch failed');
        const data = await res.json();
        setCompanies(data);
      } catch {
        setError('Error fetching buildings');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Define table columns
  const columns = useMemo(
    () => [
      { Header: "Name", accessor: "name" },
      {
        Header: "Address",
        accessor: row =>
          row.address
            ? `${row.address.street_address}, ${row.address.city}`
            : "No address",
        id: "address"
      },
      { Header: "Industry", accessor: "industry" },
      {
        Header: "Building",
        accessor: row => (row.building ? row.building.name : "N/A"),
        id: "building"
      }
    ],
    []
  );

  const data = useMemo(() => companies, [companies]);

  // Create table instance
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,               // current page rows
    prepareRow,
    state,
    setGlobalFilter,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize
  } = useTable(
    { columns, data, initialState: { pageIndex: 0, pageSize: 10 } },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const { globalFilter, pageIndex, pageSize } = state;

  if (loading) return <div className="container mx-auto p-4">Loading...</div>;
  if (error)   return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">
          Companies ({data.length})
        </h1>

        {/* Search & Total Count */}
        <div className="mb-4 flex justify-between items-center">
          <GlobalFilter filter={globalFilter} setFilter={setGlobalFilter} />
          <div className="text-lg">Total Records: {data.length}</div>
        </div>

        <div className="overflow-x-auto">
          <table
            {...getTableProps()}
            className="min-w-full bg-white border rounded"
          >
            <thead className="bg-gray-200">
              {headerGroups.map(headerGroup => (
                <tr {...headerGroup.getHeaderGroupProps()}>
                  {headerGroup.headers.map(column => (
                    <th
                      {...column.getHeaderProps(column.getSortByToggleProps())}
                      className="py-2 px-4 border text-left cursor-pointer"
                    >
                      {column.render("Header")}
                      <span>
                        {column.isSorted
                          ? column.isSortedDesc
                            ? " 🔽"
                            : " 🔼"
                          : ""}
                      </span>
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
                      <td
                        {...cell.getCellProps()}
                        className="py-2 px-4"
                      >
                        {cell.render("Cell")}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex justify-between items-center mt-4">
          <div>
            <button
              onClick={() => gotoPage(0)}
              disabled={!canPreviousPage}
              className="px-3 py-1 bg-gray-300 rounded mr-2 disabled:opacity-50"
            >
              {"<<"}
            </button>
            <button
              onClick={() => previousPage()}
              disabled={!canPreviousPage}
              className="px-3 py-1 bg-gray-300 rounded disabled:opacity-50"
            >
              Previous
            </button>
          </div>
          <span>
            Page{" "}
            <strong>
              {pageIndex + 1} of {pageOptions.length}
            </strong>
          </span>
          <div>
            <button
              onClick={() => nextPage()}
              disabled={!canNextPage}
              className="px-3 py-1 bg-gray-300 rounded mr-2 disabled:opacity-50"
            >
              Next
            </button>
            <button
              onClick={() => gotoPage(pageCount - 1)}
              disabled={!canNextPage}
              className="px-3 py-1 bg-gray-300 rounded disabled:opacity-50"
            >
              {">>"}
            </button>
          </div>
          <select
            value={pageSize}
            onChange={e => setPageSize(Number(e.target.value))}
            className="border p-2 rounded"
          >
            {[10, 20, 50].map(size => (
              <option key={size} value={size}>
                Show {size}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default CompaniesList;
