import { useState } from 'react';
import { Maximize2 } from 'lucide-react';
import { imageDataUrl } from '../../services/adapters';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';

export function HeatmapViewer({ gradCam, previewUrl }) {
  const [view, setView] = useState('overlay');
  const [opacity, setOpacity] = useState(75);
  const source = gradCam ? { original: imageDataUrl(gradCam.original_image), heatmap: imageDataUrl(gradCam.heatmap_image), overlay: imageDataUrl(gradCam.overlay_image) } : null;
  return <Card className="heatmap-card"><div className="section-heading"><div><span className="overline">Explainability</span><h2>Attention map</h2></div><Button variant="ghost" aria-label="Expand attention map"><Maximize2 size={17} /></Button></div><div className="heatmap-stage">{source ? <img src={source[view]} alt={`${view} model attention visualization`} style={{ opacity: opacity / 100 }} /> : previewUrl ? <img src={previewUrl} alt="Selected scan" /> : <div className="empty-visual">Attention visualization will appear after analysis.</div>}</div><div className="heatmap-controls"><div className="segmented">{['original', 'heatmap', 'overlay'].map((item) => <button key={item} className={view === item ? 'selected' : ''} onClick={() => setView(item)} disabled={!source}>{item}</button>)}</div><label>Overlay opacity <input type="range" min="0" max="100" value={opacity} onChange={(event) => setOpacity(event.target.value)} disabled={!source} /></label></div></Card>;
}
