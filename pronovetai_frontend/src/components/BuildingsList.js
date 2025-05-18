import React, { useEffect, useState, useMemo } from "react";
import { authFetch} from "../api";
import TopNav from "./TopNav";
import {
  useTable,
  useSortBy,
  usePagination,
  useGlobalFilter
} from "react-table";

// Global filter component
const GlobalFilter = ({ filter, setFilter }) => (
  <input
    value={filter || ""}
    onChange={e => setFilter(e.target.value || undefined)}
    placeholder="Search by Building Name"
    className="border border-gray-300 p-2 rounded w-1/2"
  />
);

const BuildingsList = () => {
  const [buildings, setBuildings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch buildings on mount
  useEffect(() => {
    async function load() {
      try {
        const res = await authFetch('/buildings/');
        if (!res.ok) throw new Error('Fetch failed');
        const data = await res.json();
        setBuildings(data);
      } catch {
        setError('Error fetching buildings');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Accessor for contact name
  const getContactName = building => {
    if (building.contacts && building.contacts.length) {
      const owner = building.contacts.find(c => c.contact_type === "owner");
      const contact = owner || building.contacts[0];
      return `${contact.first_name || ""} ${contact.last_name || ""}`.trim();
    }
    return "N/A";
  };

  // Define columns
  const columns = useMemo(
    () => [
      {
        Header: "Building Name",
        accessor: "name"
      },
      {
        Header: "Address",
        accessor: row =>
          row.address
            ? `${row.address.street_address}, ${row.address.city}`
            : "No address",
        id: "address"
      },
      {
        Header: "Type",
        accessor: "building_type"
      },
      {
        Header: "Contact",
        accessor: getContactName,
        id: "contact"
      },
      {
        Header: "Grade",
        accessor: "grade"
      },
      {
        Header: "PEZA Certified",
        accessor: row => (row.is_peza_certified ? "Yes" : "No"),
        id: "peza"
      },
      {
        Header: "Strata",
        accessor: row => (row.is_strata ? "Yes" : "No"),
        id: "strata"
      }
    ],
    []
  );

  const data = useMemo(() => buildings, [buildings]);

  // Create table instance
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    page,
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
    {
      columns,
      data,
      initialState: { pageIndex: 0, pageSize: 10 }
    },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const { globalFilter, pageIndex, pageSize } = state;

  if (loading) return <div className="container mx-auto p-4">Loading...</div>;
  if (error) return <div className="container mx-auto p-4 text-red-600">{error}</div>;

  return (
    <div>
      <TopNav />
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Buildings ({data.length})</h1>

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
                      {...column.getHeaderProps(
                        column.getSortByToggleProps()
                      )}
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

        <div className="flex justify-between items-center mt-4">
          <div>
            <button
              onClick={() => gotoPage(0)}
              disabled={!canPreviousPage}
              className="px-3 py-1 bg-gray-300 rounded mr-2 disabled:opacity-50"
            >
              {'<<'}
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
            Page{' '}
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
              {'>>'}
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

export default BuildingsList;
