export function Toast({ message, onClose }) {
  if (!message) return null;
  return <div className="toast" role="alert"><span>{message}</span><button onClick={onClose} aria-label="Dismiss notification">×</button></div>;
}
