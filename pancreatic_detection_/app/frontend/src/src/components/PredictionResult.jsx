function PredictionResult({ result }) {
  const percentage = Math.round((result.confidence || 0) * 100);
  const predictedClass = result.predicted_class || result.prediction;

  return (
    <div className="result-card">
      <p className="section-label">AI Analysis Result</p>
      <h2>Model Prediction: {predictedClass}</h2>
      <div className="confidence-box">
        <span>Confidence</span>
        <strong>{percentage}%</strong>
      </div>
      <div className="probability-list">
        {Object.entries(result.probabilities || {}).map(([label, value]) => (
          <div key={label} className="probability-row">
            <span>{label}</span>
            <strong>{(value * 100).toFixed(1)}%</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default PredictionResult;
