// App Component
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { PromptsPage } from './pages/PromptsPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { SettingsPage } from './pages/SettingsPage';
import { ToastProvider } from './components/Toast';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="prompts" element={<PromptsPage />} />
        <Route path="evaluation" element={<EvaluationPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export function App() {
  return (
    <ToastProvider>
      <AppRoutes />
    </ToastProvider>
  );
}