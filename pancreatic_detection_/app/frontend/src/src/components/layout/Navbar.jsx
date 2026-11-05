import { Activity, Moon, Sun } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../../hooks/useTheme';

export function Navbar() {
  const { theme, toggleTheme } = useTheme();
  return <header className="navbar"><NavLink to="/" className="brand"><span className="brand-mark"><Activity size={20} /></span><span>Pancreatic<span className="brand-accent">Insight</span></span></NavLink><nav aria-label="Primary navigation">{[['/', 'Overview'], ['/detect', 'Detect'], ['/history', 'History'], ['/about', 'About']].map(([to, label]) => <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>{label}</NavLink>)}</nav><button className="theme-toggle" onClick={toggleTheme} aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}>{theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}</button></header>;
}
