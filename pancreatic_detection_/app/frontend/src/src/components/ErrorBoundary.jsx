import { Component } from 'react';
import { Link } from 'react-router-dom';

export class ErrorBoundary extends Component {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <div className="empty-state page-empty"><h1>Something went wrong</h1><p>Refresh the page or return to the overview to continue.</p><Link className="button button-primary" to="/">Return to overview</Link></div>;
    }
    return this.props.children;
  }
}
