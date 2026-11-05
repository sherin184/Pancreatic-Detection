import { BookOpen, CircleAlert, Gauge, Layers3 } from 'lucide-react';

export function About() {
  const cards = [['Model architecture', 'ResNet50 + CBAM', 'A convolutional neural network with channel and spatial attention modules.', Layers3], ['Input standardization', '224 × 224 pixels', 'Uploaded RGB images are transformed using the project’s evaluation pipeline.', BookOpen], ['Evaluation', 'Research metrics', 'Reported metrics are available from the connected backend when evaluation artifacts exist.', Gauge], ['Limitations', 'Not a diagnosis', 'Performance can vary across scanners, populations, acquisition protocols, and image quality.', CircleAlert]];
  return <><div className="page-intro"><span className="overline">About the project</span><h1>Built for careful exploration</h1><p>Understand what the model does, where it helps, and where expert judgment remains essential.</p></div><div className="about-grid">{cards.map(([title, value, copy, Icon]) => <article className="about-card" key={title}><Icon size={21} /><span className="overline">{title}</span><h2>{value}</h2><p>{copy}</p></article>)}</div></>;
}
