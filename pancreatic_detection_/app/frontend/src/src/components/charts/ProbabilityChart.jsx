import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export function ProbabilityChart({ probabilities = {} }) {
  const data = Object.entries(probabilities).map(([label, value]) => ({ label, value: Number((value * 100).toFixed(1)) }));
  return <div className="probability-chart"><div className="section-heading"><div><span className="overline">Class probabilities</span><h2>Confidence by class</h2></div></div><div className="chart-area"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}><XAxis type="number" domain={[0, 100]} hide /><YAxis type="category" dataKey="label" width={110} tickLine={false} axisLine={false} /><Tooltip formatter={(value) => [`${value}%`, 'Probability']} /><Bar dataKey="value" radius={[0, 6, 6, 0]}>{data.map((entry, index) => <Cell key={entry.label} fill={index === 0 ? '#13a89e' : '#ef9b55'} />)}</Bar></BarChart></ResponsiveContainer></div></div>;
}
