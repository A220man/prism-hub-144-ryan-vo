// Dashboard Page
import { HealthCheck } from '../components/HealthCheck';

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text)]">Dashboard</h1>
        <p className="text-[var(--color-text-muted)] mt-1">Prism Hub - Jailbreak prompt management for AI models</p>
      </div>

      <HealthCheck />

      <div className="grid gap-6 md:grid-cols-3">
        <div className="card p-6">
          <h3 className="font-semibold text-[var(--color-text)] mb-2">Quick Actions</h3>
          <div className="space-y-3">
            <a href="/prompts" className="btn btn-primary w-full">Manage Prompts</a>
            <a href="/evaluation" className="btn btn-outline w-full">Run Evaluation</a>
            <a href="/settings" className="btn btn-outline w-full">Settings</a>
          </div>
        </div>

        <div className="card p-6 md:col-span-2">
          <h3 className="font-semibold text-[var(--color-text)] mb-2">About Prism Hub</h3>
          <p className="text-[var(--color-text-muted)] mb-4">
            Prism Hub is a tool for managing jailbreak prompts across different AI models.
            It allows you to store, organize, and test prompts per model, with a default
            prompt targeting the Chinese model "小码辣" (Xiao Ma La).
          </p>
          <h4 className="font-medium text-[var(--color-text)] mb-2">Key Features</h4>
          <ul className="space-y-1 text-[var(--color-text-muted)]">
            <li>• Per-model prompt storage with default selection</li>
            <li>• Import/export prompts in JSON format</li>
            <li>• Search and filter prompts by model, tags, content</li>
            <li>• AI/ML evaluation workflow with baseline metrics</li>
            <li>• LLM adapter supporting OpenAI, Anthropic, Gemini, Ollama</li>
            <li>• OIDC authentication with Keycloak (SAML broker support)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}