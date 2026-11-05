export function UploadProgress({ visible }) {
  return visible ? <div className="progress-wrap" aria-live="polite"><div className="progress-label"><span>Analyzing scan</span><span>Processing securely…</span></div><div className="progress-track"><div className="progress-bar" /></div></div> : null;
}
