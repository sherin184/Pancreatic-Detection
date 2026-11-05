import { Download, Search } from 'lucide-react';
import { useContext, useMemo, useState } from 'react';
import { ResultsContext } from '../context/ResultsContext';
import { ResultsTable } from '../components/results/ResultsTable';
import { Button } from '../components/ui/Button';

export function History() {
  const { records, removeRecord } = useContext(ResultsContext); const [query, setQuery] = useState('');
  const filtered = useMemo(() => records.filter((record) => `${record.fileName} ${record.label}`.toLowerCase().includes(query.toLowerCase())), [records, query]);
  const exportCsv = () => { const csv = ['Date,File,Result,Confidence', ...filtered.map((record) => `${record.createdAt},${record.fileName},${record.label},${record.confidence}`)].join('\n'); const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' })); link.download = 'analysis-history.csv'; link.click(); };
  return <><div className="page-intro result-intro"><div><span className="overline">Session archive</span><h1>Analysis history</h1><p>Results are held in memory only and disappear when this session ends.</p></div><Button variant="secondary" onClick={exportCsv} disabled={!filtered.length}><Download size={17} /> Export CSV</Button></div><div className="toolbar"><label className="search-field"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search file or result" /></label><span className="muted-copy">{filtered.length} {filtered.length === 1 ? 'analysis' : 'analyses'}</span></div><ResultsTable records={filtered} onDelete={removeRecord} /></>;
}
