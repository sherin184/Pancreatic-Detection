export function ConfidenceGauge({ value = 0 }) {
  const percent = Math.round(value * 100);
  return <div className="gauge-wrap"><div className="gauge" style={{ '--value': `${percent}%` }}><div className="gauge-inner"><strong>{percent}%</strong><span>confidence</span></div></div></div>;
}
