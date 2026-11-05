import { RefreshCw, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';

export function FilePreview({ file, previewUrl, onReplace, onRemove }) {
  return <div className="file-preview"><img src={previewUrl} alt="Selected CT scan preview" /><div className="file-meta"><div><strong>{file.name}</strong><span>{(file.size / 1024 / 1024).toFixed(2)} MB · {file.type || 'image'}</span></div><div className="inline-actions"><Button variant="secondary" onClick={onReplace}><RefreshCw size={16} /> Replace</Button><Button variant="ghost" onClick={onRemove} aria-label="Remove selected image"><Trash2 size={16} /></Button></div></div></div>;
}
