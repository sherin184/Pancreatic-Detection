import { Download, RotateCcw } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { Link, useLocation } from 'react-router-dom';
import { ProbabilityChart } from '../components/charts/ProbabilityChart';
import { HeatmapViewer } from '../components/results/HeatmapViewer';
import { PredictionCard } from '../components/results/PredictionCard';
import { Button } from '../components/ui/Button';

export function Results() {
  const { state } = useLocation();
  if (!state?.prediction) return <div className="empty-state page-empty"><h2>No result to display</h2><p>Start an analysis to see model output.</p><Link className="button button-primary" to="/detect">Go to detection</Link></div>;
  const { prediction, gradCam, previewUrl, warning } = state;
  const download = () => { const pdf = new jsPDF(); pdf.setFontSize(18); pdf.text('Pancreatic Insight research report', 20, 25); pdf.setFontSize(12); pdf.text(`Prediction: ${prediction.label}`, 20, 45); pdf.text(`Confidence: ${Math.round(prediction.confidence * 100)}%`, 20, 55); pdf.text(`Model: ${prediction.modelName}`, 20, 65); pdf.setFontSize(10); pdf.text('For research and decision-support only. Not a clinical diagnosis.', 20, 85); pdf.save('pancreatic-insight-report.pdf'); };
  return <><div className="page-intro result-intro"><div><span className="overline">Analysis result</span><h1>Your scan insight</h1><p>Review the model output and visual explanation below.</p></div><div className="inline-actions"><Button variant="secondary" onClick={download}><Download size={17} /> Download report</Button><Link className="button button-primary" to="/detect"><RotateCcw size={17} /> New analysis</Link></div></div>{warning && <div className="alert warning" role="status">{warning}</div>}<div className="results-grid"><PredictionCard prediction={prediction} /><ProbabilityChart probabilities={prediction.probabilities} /><HeatmapViewer gradCam={gradCam} previewUrl={previewUrl} /></div></>;
}
