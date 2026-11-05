import { Navbar } from './Navbar';

export function PageContainer({ children }) {
  return <div className="site-shell"><Navbar /><main className="page-container">{children}</main></div>;
}
