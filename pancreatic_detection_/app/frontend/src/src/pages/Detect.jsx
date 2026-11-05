import { FileText, LockKeyhole, UserRound } from 'lucide-react';
import { useContext, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FilePreview } from '../components/upload/FilePreview';
import { ImageDropzone } from '../components/upload/ImageDropzone';
import { UploadProgress } from '../components/upload/UploadProgress';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { ResultsContext } from '../context/ResultsContext';
import { usePrediction } from '../hooks/usePrediction';
import { useUpload } from '../hooks/useUpload';

export function Detect() {
  const inputRef = useRef(null); const navigate = useNavigate(); const { file, previewUrl, selectFile } = useUpload(); const { predict, loading, error, warning } = usePrediction(); const { addRecord } = useContext(ResultsContext); const [validation, setValidation] = useState(''); const [patientId, setPatientId] = useState(''); const [notes, setNotes] = useState('');
  const onFile = (nextFile) => { if (!nextFile) return; if (!['image/jpeg', 'image/jpg', 'image/png'].includes(nextFile.type) || nextFile.size > 10 * 1024 * 1024) return setValidation('Please choose a JPG or PNG image smaller than 10 MB.'); setValidation(''); selectFile(nextFile); };
  const analyze = async () => { if (!file) return setValidation('Select an image before analyzing.'); const result = await predict(file); if (result) { addRecord({ fileName: file.name, label: result.prediction.label, confidence: result.prediction.confidence, patientId: patientId || 'Not provided', notes }); navigate('/results', { state: { ...result, previewUrl } }); } };
  return <><div className="page-intro"><span className="overline">New analysis</span><h1>Analyze a pancreatic scan</h1><p>Upload a de-identified image to begin a guided analysis.</p></div><div className="detect-grid"><Card className="upload-card"><div className="section-heading"><div><h2>Scan image</h2><p>Only JPG, JPEG, and PNG files are accepted.</p></div><LockKeyhole size={19} /></div>{file ? <FilePreview file={file} previewUrl={previewUrl} onReplace={() => inputRef.current?.click()} onRemove={() => selectFile(null)} /> : <ImageDropzone onFile={onFile} error={validation} />}<input ref={inputRef} type="file" accept=".jpg,.jpeg,.png" hidden onChange={(event) => onFile(event.target.files?.[0])} /><UploadProgress visible={loading} />{error && <div className="alert error" role="alert">{error}</div>}{warning && <div className="alert warning" role="status">{warning}</div>}<Button className="full-width" onClick={analyze} disabled={loading || !file}>{loading ? 'Analyzing…' : 'Analyze image'}</Button></Card><Card className="details-card"><div className="section-heading"><div><h2>Optional context</h2><p>Add context without storing patient data.</p></div></div><label><span><UserRound size={15} /> Patient ID</span><input value={patientId} onChange={(event) => setPatientId(event.target.value)} placeholder="e.g. Research-014" /></label><label><span><FileText size={15} /> Notes</span><textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows="5" placeholder="Add non-identifying notes…" /></label><div className="privacy-note"><LockKeyhole size={16} /><span>Context is kept in memory only and is cleared when this session ends.</span></div></Card></div></>;
}
