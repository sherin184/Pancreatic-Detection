import { useCallback, useEffect, useState } from 'react';

export function useUpload() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');

  const selectFile = useCallback((nextFile) => {
    setFile(nextFile || null);
    setPreviewUrl(nextFile ? URL.createObjectURL(nextFile) : '');
  }, []);

  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl]);
  return { file, previewUrl, selectFile };
}
