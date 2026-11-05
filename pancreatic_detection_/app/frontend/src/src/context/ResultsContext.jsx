import { createContext, useMemo, useState } from 'react';

export const ResultsContext = createContext({ records: [], addRecord: () => {}, removeRecord: () => {} });

export function ResultsProvider({ children }) {
  const [records, setRecords] = useState([]);
  const addRecord = (record) => setRecords((current) => [{ ...record, id: crypto.randomUUID(), createdAt: new Date().toISOString() }, ...current]);
  const removeRecord = (id) => setRecords((current) => current.filter((record) => record.id !== id));
  const value = useMemo(() => ({ records, addRecord, removeRecord }), [records]);
  return <ResultsContext.Provider value={value}>{children}</ResultsContext.Provider>;
}
