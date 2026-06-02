export default function ResultTable({ columns, rows, rowCount }) {
  return (
    <div className="mt-3">
      <div className="text-xs text-gray-500 mb-2">{rowCount} row{rowCount !== 1 ? "s" : ""} returned</div>
      <div className="overflow-x-auto rounded-xl border border-gray-200">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-4 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50 transition-colors">
                {columns.map((col) => (
                  <td key={col} className="px-4 py-2 text-gray-800 whitespace-nowrap">
                    {row[col] === null || row[col] === undefined ? (
                      <span className="text-gray-400 italic">null</span>
                    ) : (
                      String(row[col])
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
