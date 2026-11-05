import { ArrowRight, ScanSearch, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card } from '../components/ui/Card';

export function Home() {
  const steps = [
    ['01', 'Upload securely', 'Choose a JPG or PNG scan. Files stay in the active session and are never stored in your browser.'],
    ['02', 'Analyze patterns', 'Our trained model evaluates the image and returns class probabilities in seconds.'],
    ['03', 'Review with context', 'Use the attention map and confidence details to understand what influenced the result.'],
  ];

  return (
    <>
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">
            <Sparkles size={15} /> Research-grade image intelligence
          </span>
          <h1>
            Clarity for every <span>pancreatic scan.</span>
          </h1>
          <p className="hero-lede">
            Pancreatic Insight helps research teams explore image-level patterns with fast, explainable AI-assisted analysis.
          </p>
          <div className="hero-actions">
            <Link className="button button-primary" to="/detect">
              Start an analysis <ArrowRight size={17} />
            </Link>
            <Link className="text-link" to="/about">
              Learn about the model
            </Link>
          </div>
        </div>

        <div className="hero-art">
          <div className="scan-orb">
            <ScanSearch size={42} />
          </div>
          <div className="floating-card">
            <span className="pulse-dot" /> Model ready <strong>ResNet50 + CBAM</strong>
          </div>
        </div>
      </section>

      <section className="stats-grid">
        <div>
          <strong>2</strong>
          <span>Supported classes</span>
        </div>
        <div>
          <strong>224px</strong>
          <span>Standardized input</span>
        </div>
        <div>
          <strong>100%</strong>
          <span>Local session privacy</span>
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <span className="overline">A considered workflow</span>
            <h2>From scan to insight in three steps</h2>
          </div>
        </div>
        <div className="steps-grid">
          {steps.map(([number, title, copy]) => (
            <Card key={number} className="step-card">
              <span className="step-number">{number}</span>
              <h3>{title}</h3>
              <p>{copy}</p>
            </Card>
          ))}
        </div>
      </section>
    </>
  );
}