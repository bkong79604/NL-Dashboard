import {
  BarChart, Bar, LineChart, Line,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#a855f7", "#14b8a6"];

export default function ResultChart({ chartType, columns, rows, rowCount }) {
  if (!rows.length) return <p className="text-gray-500 text-sm mt-2">No data to display.</p>;

  const labelKey = columns[0];
  const valueKeys = columns.slice(1);

  return (
    <div className="mt-3">
      <div className="text-xs text-gray-500 mb-2">{rowCount} row{rowCount !== 1 ? "s" : ""} returned</div>
      <ResponsiveContainer width="100%" height={320}>
        {chartType === "bar" ? (
          <BarChart data={rows} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={labelKey} tick={{ fontSize: 12 }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {valueKeys.map((key, i) => (
              <Bar key={key} dataKey={key} fill={COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
            ))}
          </BarChart>
        ) : chartType === "line" ? (
          <LineChart data={rows} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey={labelKey} tick={{ fontSize: 12 }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {valueKeys.map((key, i) => (
              <Line key={key} type="monotone" dataKey={key} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        ) : chartType === "pie" ? (
          <PieChart>
            <Pie
              data={rows}
              dataKey={valueKeys[0]}
              nameKey={labelKey}
              cx="50%"
              cy="50%"
              outerRadius={120}
              label={({ name, percent }) => `${name} (${(percent * 100).toFixed(1)}%)`}
            >
              {rows.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        ) : null}
      </ResponsiveContainer>
    </div>
  );
}
