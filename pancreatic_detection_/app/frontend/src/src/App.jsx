import { BrowserRouter } from 'react-router-dom';
import { ErrorBoundary } from './components/ErrorBoundary';
import { PageContainer } from './components/layout/PageContainer';
import { ResultsProvider } from './context/ResultsContext';
import { ThemeProvider } from './context/ThemeContext';
import { AppRoutes } from './routes';

export default function App() {
  return <BrowserRouter><ErrorBoundary><ThemeProvider><ResultsProvider><PageContainer><AppRoutes /></PageContainer></ResultsProvider></ThemeProvider></ErrorBoundary></BrowserRouter>;
}
