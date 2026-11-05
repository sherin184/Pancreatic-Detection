import { FileImage, UploadCloud } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { Button } from '../ui/Button';

export function ImageDropzone({ onFile, error }) {
  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop: (files) => onFile(files[0]),
    accept: { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] },
    maxSize: 10 * 1024 * 1024,
    multiple: false,
    noClick: true,
  });
  return <div {...getRootProps()} className={`dropzone ${isDragActive ? 'drag-active' : ''}`}><input {...getInputProps()} /><div className="drop-icon"><UploadCloud size={28} /></div><h2>{isDragActive ? 'Drop image to upload' : 'Upload a CT image'}</h2><p>Drag and drop a JPG or PNG file here</p><Button type="button" onClick={open}>Browse files</Button><span className="drop-hint"><FileImage size={14} /> Maximum size 10 MB</span>{error && <p className="field-error" role="alert">{error}</p>}</div>;
}
