import { useRef, useState } from 'react';

function ImageUploader({ file, previewUrl, onFileSelect, onAnalyze, loading }) {
  const inputRef = useRef(null);
  const [dragActive, setDragActive] = useState(false);

  const validateFile = (nextFile) => {
    if (!nextFile) return;
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(nextFile.type)) {
      alert('Please upload a JPG or PNG image.');
      return;
    }
    if (nextFile.size > 10 * 1024 * 1024) {
      alert('Please upload an image smaller than 10 MB.');
      return;
    }
    onFileSelect(nextFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragActive(false);
    const nextFile = event.dataTransfer.files?.[0];
    validateFile(nextFile);
  };

  return (
    <div className="uploader-wrap">
      <div
        className={`dropzone ${dragActive ? 'drag-active' : ''}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".jpg,.jpeg,.png"
          hidden
          onChange={(event) => validateFile(event.target.files?.[0])}
        />

        {previewUrl ? (
          <div className="preview-box">
            <img src={previewUrl} alt="Uploaded CT preview" />
            <div className="preview-actions">
              <button type="button" className="secondary-button" onClick={() => inputRef.current?.click()}>
                Replace Image
              </button>
              <button type="button" className="secondary-button danger" onClick={() => onFileSelect(null)}>
                Remove
              </button>
            </div>
          </div>
        ) : (
          <div className="dropzone-inner">
            <div className="upload-icon">⬆</div>
            <h2>Upload CT Image</h2>
            <p>Drag and drop an image here</p>
            <button type="button" className="primary-button" onClick={() => inputRef.current?.click()}>
              Browse Image
            </button>
            <small>Supported: JPG / JPEG / PNG</small>
          </div>
        )}
      </div>

      {file && (
        <button type="button" className="primary-button analyze-button" onClick={onAnalyze} disabled={loading}>
          {loading ? 'Analyzing image...' : 'Analyze Image'}
        </button>
      )}
    </div>
  );
}

export default ImageUploader;
