import { ShieldCheck, TriangleAlert } from 'lucide-react';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';
import { ConfidenceGauge } from './ConfidenceGauge';

export function PredictionCard({ prediction }) {
  const risk = prediction.label.toLowerCase().includes('tumour') || prediction.label.toLowerCase().includes('tumor');
  return <Card className="prediction-card"><div className="section-heading"><div><span className="overline">Analysis complete</span><h2>Prediction summary</h2></div><Badge tone={risk ? 'risk' : 'safe'}>{risk ? <TriangleAlert size={15} /> : <ShieldCheck size={15} />}{risk ? 'Elevated risk' : 'Low risk'}</Badge></div><div className="prediction-main"><div><span className="muted-label">Predicted class</span><strong className="prediction-label">{prediction.label}</strong><p className="muted-copy">Model-generated classification based on the uploaded image. Highlighted regions show the areas that most influenced the prediction.</p></div><ConfidenceGauge value={prediction.confidence} /></div><div className="stat-strip"><div><span>Model</span><strong>{prediction.modelName}</strong></div><div><span>Inference device</span><strong>{prediction.device}</strong></div></div></Card>;
}
