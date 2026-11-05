function ModelInfo({ info }) {
  const modelData = info || {
    model_name: 'ResNet50 + CBAM',
    device: 'CPU',
    input_size: 224,
    class_names: ['Normal', 'Pancreatic Tumour'],
  };

  return (
    <div className="info-card">
      <p className="section-label">Model Information</p>
      <ul>
        <li><strong>Model:</strong> {modelData.model_name || 'ResNet50 + CBAM'}</li>
        <li><strong>Framework:</strong> PyTorch</li>
        <li><strong>Input:</strong> {modelData.input_size || 224} × {modelData.input_size || 224}</li>
        <li><strong>Classes:</strong> {modelData.class_names?.join(' / ') || 'Normal / Pancreatic Tumour'}</li>
        <li><strong>Device:</strong> {modelData.device || 'CPU'}</li>
      </ul>
    </div>
  );
}

export default ModelInfo;
