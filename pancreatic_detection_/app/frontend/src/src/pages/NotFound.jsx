import { Link } from 'react-router-dom';
export function NotFound() { return <div className="empty-state page-empty"><span className="overline">404</span><h1>That page is not here</h1><p>Return to the overview to continue.</p><Link className="button button-primary" to="/">Back to overview</Link></div>; }
