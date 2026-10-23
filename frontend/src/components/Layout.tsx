// Layout Component
import { ReactNode } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';

interface LayoutProps {
  children?: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/prompts', label: 'Prompts' },
    { path: '/evaluation', label: 'Evaluation' },
    { path: '/settings', label: 'Settings' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)] sticky top-0 z-50">
        <div className="container">
          <div className="flex items-center justify-between h-16">
            <NavLink to="/" className="text-xl font-bold text-[var(--color-primary)]" aria-label="Prism Hub Home">
              Prism Hub
            </NavLink>
            <nav className="flex items-center gap-6" aria-label="Main navigation">
              {navItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `text-sm font-medium transition-colors ${
                      isActive
                        ? 'text-[var(--color-primary)]'
                        : 'text-[var(--color-text-muted)] hover:text-[var(--color-text)]'
                    }`
                  }
                  aria-current={location.pathname === item.path ? 'page' : undefined}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1 container py-6" role="main">
        {children ?? <Outlet />}
      </main>
      <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-4">
        <div className="container text-center text-sm text-[var(--color-text-muted)]">
          Prism Hub &mdash; Ryan Vo ryandtvo@gmail.com | AI & Machine Learning
        </div>
      </footer>
    </div>
  );
}