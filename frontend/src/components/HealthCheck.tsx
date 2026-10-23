// Health Check Component
import { useEffect, useState } from 'react';
import { api, type HealthResponse } from '../api';

export function HealthCheck() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    async function fetchHealth() {
      try {
        const data = await api.getHealth();
        if (mounted) setHealth(data);
      } catch (err) {
        if (mounted) setError(err instanceof Error ? err.message : 'Failed to fetch health');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-[var(--color-text-muted)]">
        <div className="spinner" aria-hidden="true" />
        <span>Checking backend health...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-error" role="alert">
        <strong>Backend unavailable:</strong> {error}
      </div>
    );
  }

  if (!health) return null;

  const statusColor = health.status === 'healthy' ? 'text-[var(--color-success)]' : 'text-[var(--color-warning)]';
  const statusIcon = health.status === 'healthy' ? '✓' : '⚠';

  return (
    <div className="card p-4">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <span className={`${statusColor} text-2xl`} aria-hidden="true">{statusIcon}</span>
          <div>
            <h3 className="font-semibold text-[var(--color-text)]">Backend Status</h3>
            <p className="text-sm text-[var(--color-text-muted)]">
              {health.status === 'healthy' ? 'All systems operational' : 'Degraded - some services unavailable'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm text-[var(--color-text-muted)] flex-wrap">
          <span>Version: <code>{health.version}</code></span>
          <span>Env: <code>{health.environment}</code></span>
          <span>DB: <code>{health.database}</code></span>
          {health.demo_mode && <span className="badge badge-warning">Demo Mode</span>}
        </div>
      </div>
    </div>
  );
}