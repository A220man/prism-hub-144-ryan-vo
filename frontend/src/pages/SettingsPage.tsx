// Settings Page
import { useState, useEffect } from 'react';
import { useToast } from '../components/Toast';

interface Settings {
  llm_provider: string;
  llm_model: string;
  llm_base_url: string;
  llm_api_key: string;
  oidc_issuer_url: string;
  oidc_client_id: string;
  demo_mode: boolean;
}

const DEFAULT_SETTINGS: Settings = {
  llm_provider: 'openai-compatible',
  llm_model: 'gpt-4o-mini',
  llm_base_url: '',
  llm_api_key: '',
  oidc_issuer_url: 'http://127.0.0.1:8080/realms/prism-hub',
  oidc_client_id: 'prism-hub-frontend',
  demo_mode: true,
};

const PROVIDERS = [
  { value: 'openai-compatible', label: 'OpenAI Compatible (OpenAI, LiteLLM, OpenRouter, Ollama)' },
  { value: 'anthropic', label: 'Anthropic (Claude)' },
  { value: 'gemini', label: 'Google Gemini' },
  { value: 'ollama', label: 'Ollama (Local)' },
];

export function SettingsPage() {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState(false);
  const { showToast } = useToast();

  useEffect(() => {
    // Load from localStorage
    const stored = localStorage.getItem('prism-hub-settings');
    if (stored) {
      try {
        setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(stored) });
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  const handleChange = (key: keyof Settings, value: string | boolean) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem('prism-hub-settings', JSON.stringify(settings));
    setSaved(true);
    showToast('Settings saved', 'success');
  };

  const handleTestConnection = async () => {
    showToast('Connection test not implemented in demo mode', 'info');
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]">Settings</h1>
        <p className="text-[var(--color-text-muted)] mt-1">Configure LLM providers, authentication, and application behavior</p>
      </div>

      {/* LLM Provider */}
      <div className="card p-6">
        <h3 className="font-semibold text-[var(--color-text)] mb-4">LLM Provider</h3>
        <div className="space-y-4">
          <div>
            <label className="label" htmlFor="llm_provider">Provider</label>
            <select
              id="llm_provider"
              className="input"
              value={settings.llm_provider}
              onChange={(e) => handleChange('llm_provider', e.target.value)}
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>{p.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="llm_model">Model</label>
            <input
              id="llm_model"
              type="text"
              className="input"
              placeholder="e.g., gpt-4o-mini, claude-3-sonnet, gemini-pro"
              value={settings.llm_model}
              onChange={(e) => handleChange('llm_model', e.target.value)}
            />
          </div>
          <div>
            <label className="label" htmlFor="llm_base_url">Base URL (Optional)</label>
            <input
              id="llm_base_url"
              type="url"
              className="input"
              placeholder="https://api.openai.com/v1 or http://localhost:11434/v1"
              value={settings.llm_base_url}
              onChange={(e) => handleChange('llm_base_url', e.target.value)}
            />
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              Leave blank for provider defaults. For Ollama, use <code>http://localhost:11434/v1</code>.
            </p>
          </div>
          <div>
            <label className="label" htmlFor="llm_api_key">API Key</label>
            <input
              id="llm_api_key"
              type="password"
              className="input"
              placeholder="Enter API key (stored locally only)"
              value={settings.llm_api_key}
              onChange={(e) => handleChange('llm_api_key', e.target.value)}
              autoComplete="off"
            />
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              Keys are stored in browser localStorage only. Never sent to this application's backend.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="btn btn-outline" onClick={handleTestConnection} disabled={!settings.llm_api_key}>
              Test Connection
            </button>
          </div>
        </div>
      </div>

      {/* Authentication */}
      <div className="card p-6">
        <h3 className="font-semibold text-[var(--color-text)] mb-4">Authentication (Keycloak OIDC)</h3>
        <div className="space-y-4">
          <div>
            <label className="label" htmlFor="oidc_issuer_url">Issuer URL</label>
            <input
              id="oidc_issuer_url"
              type="url"
              className="input"
              value={settings.oidc_issuer_url}
              onChange={(e) => handleChange('oidc_issuer_url', e.target.value)}
            />
            <p className="text-sm text-[var(--color-text-muted)] mt-1">
              Keycloak realm URL, e.g., <code>http://127.0.0.1:8080/realms/prism-hub</code>
            </p>
          </div>
          <div>
            <label className="label" htmlFor="oidc_client_id">Client ID</label>
            <input
              id="oidc_client_id"
              type="text"
              className="input"
              value={settings.oidc_client_id}
              onChange={(e) => handleChange('oidc_client_id', e.target.value)}
            />
          </div>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.demo_mode}
                onChange={(e) => handleChange('demo_mode', e.target.checked)}
              />
              <span>Demo Mode (bypass authentication for local development)</span>
            </label>
          </div>
          <p className="text-sm text-[var(--color-warning)]">
            ⚠ Demo mode MUST be disabled in production. The backend will refuse to start with demo mode enabled in production.
          </p>
        </div>
      </div>

      {/* Save Button */}
      <div className="card p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-[var(--color-text)]">Save Configuration</p>
            <p className="text-sm text-[var(--color-text-muted)]">
              Settings are stored in browser localStorage for frontend configuration.
              Backend settings are configured via environment variables.
            </p>
          </div>
          <button className="btn btn-primary" onClick={handleSave} disabled={saved}>
            {saved ? 'Saved ✓' : 'Save Settings'}
          </button>
        </div>
      </div>

      {/* Environment Variables Reference */}
      <div className="card p-6">
        <h3 className="font-semibold text-[var(--color-text)] mb-4">Backend Environment Variables</h3>
        <p className="text-sm text-[var(--color-text-muted)] mb-4">
          Configure these in <code>.env</code> or Docker environment:
        </p>
        <div className="bg-[var(--color-bg)] p-4 rounded-lg font-mono text-sm overflow-x-auto">
          <pre>{`# Application
APP_NAME=Prism Hub
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./prism_hub.db

# OIDC / Keycloak
OIDC_ISSUER_URL=http://keycloak:8080/realms/prism-hub
OIDC_CLIENT_ID=prism-hub-backend
OIDC_CLIENT_SECRET=your-secret
OIDC_AUDIENCE=prism-hub-api

# LLM
LLM_PROVIDER=openai-compatible
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=
LLM_API_KEY=

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Demo Mode (MUST be false in production)
DEMO_MODE=false`}</pre>
        </div>
      </div>
    </div>
  );
}