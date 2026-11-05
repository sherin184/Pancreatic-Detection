import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

function ProbabilityChart({ probabilities }) {
  if (!probabilities) return null;

  const chartData = Object.entries(probabilities).map(([label, value]) => ({
    label,
    value: Number((value * 100).toFixed(1)),
  }));

  return (
    <div className="chart-card">
      <p className="section-label">Class Probabilities</p>
      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis domain={[0, 100]} />
            <Tooltip formatter={(value) => [`${value}%`, 'Probability']} />
            <Bar dataKey="value" fill="#4c7ef3" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ProbabilityChart;
