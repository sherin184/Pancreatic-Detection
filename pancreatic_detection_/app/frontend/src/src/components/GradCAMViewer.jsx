import { useState } from 'react';

function GradCAMViewer({ gradCam }) {
  const [view, setView] = useState('overlay');

  if (!gradCam) {
    return (
      <div className="gradcam-card empty-gradcam">
        <p className="section-label">Model Attention</p>
        <p>No attention visualization available yet.</p>
      </div>
    );
  }

  const sourceMap = {
    original: `data:image/png;base64,${gradCam.original_image}`,
    heatmap: `data:image/png;base64,${gradCam.heatmap_image}`,
    overlay: `data:image/png;base64,${gradCam.overlay_image}`,
  };

  return (
    <div className="gradcam-card">
      <div className="gradcam-header">
        <p className="section-label">Model Attention</p>
        <div className="view-toggle">
          {['original', 'heatmap', 'overlay'].map((key) => (
            <button
              key={key}
              type="button"
              className={view === key ? 'active' : ''}
              onClick={() => setView(key)}
            >
              {key.charAt(0).toUpperCase() + key.slice(1)}
            </button>
          ))}
        </div>
      </div>
      <img src={sourceMap[view]} alt={`Model attention ${view}`} className="gradcam-image" />
      <div className="gradcam-meta">
        <span>Prediction: {gradCam.prediction}</span>
        <span>Confidence: {(gradCam.confidence * 100).toFixed(1)}%</span>
      </div>
    </div>
  );
}

export default GradCAMViewer;
