import { motion } from 'framer-motion';

const Table = ({ columns, data, onRowClick }) => {
  return (
    <div className="bg-white rounded-2xl overflow-hidden border-2 border-gray-200 shadow-lg">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gradient-to-r from-gray-50 to-gray-100 border-b-2 border-gray-200">
            <tr>
              {columns.map((column, idx) => (
                <th
                  key={idx}
                  className="px-6 py-4 text-left text-sm font-black text-gray-900 uppercase tracking-wider"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y-2 divide-gray-200">
            {data.map((row, rowIdx) => (
              <motion.tr
                key={rowIdx}
                whileHover={{ backgroundColor: 'rgba(249, 250, 251, 1)' }}
                onClick={() => onRowClick?.(row)}
                className={`transition-colors ${onRowClick ? 'cursor-pointer' : ''}`}
              >
                {columns.map((column, colIdx) => (
                  <td key={colIdx} className="px-6 py-4 text-sm font-bold text-gray-900">
                    {column.render ? column.render(row) : row[column.accessor]}
                  </td>
                ))}
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Table;
