import { Route, Routes } from 'react-router-dom';
import { About } from './pages/About';
import { Detect } from './pages/Detect';
import { History } from './pages/History';
import { Home } from './pages/Home';
import { NotFound } from './pages/NotFound';
import { Results } from './pages/Results';

export function AppRoutes() {
  return <Routes><Route path="/" element={<Home />} /><Route path="/detect" element={<Detect />} /><Route path="/results" element={<Results />} /><Route path="/history" element={<History />} /><Route path="/about" element={<About />} /><Route path="*" element={<NotFound />} /></Routes>;
}
