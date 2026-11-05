export function adaptPrediction(payload) {
  return {
    label: payload.predicted_class || payload.prediction || 'Unknown',
    confidence: Number(payload.confidence || 0),
    probabilities: payload.probabilities || {},
    modelName: payload.model_name || 'ResNet50 + CBAM',
    device: payload.device || '—',
  };
}

export function imageDataUrl(value) {
  return value ? (value.startsWith('data:') ? value : `data:image/png;base64,${value}`) : '';
}
