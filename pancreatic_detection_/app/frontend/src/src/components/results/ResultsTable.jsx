import { Trash2 } from 'lucide-react';

export function ResultsTable({ records, onDelete }) {
  if (!records.length) return <div className="empty-state"><h3>No saved analyses yet</h3><p>Your in-memory analysis history will appear here.</p></div>;
  return <div className="table-wrap"><table><thead><tr><th>Date</th><th>File</th><th>Result</th><th>Confidence</th><th aria-label="Actions" /></tr></thead><tbody>{records.map((record) => <tr key={record.id}><td>{new Date(record.createdAt).toLocaleDateString()}</td><td>{record.fileName}</td><td>{record.label}</td><td>{Math.round(record.confidence * 100)}%</td><td><button className="icon-button" onClick={() => onDelete(record.id)} aria-label={`Delete ${record.fileName}`}><Trash2 size={16} /></button></td></tr>)}</tbody></table></div>;
}
