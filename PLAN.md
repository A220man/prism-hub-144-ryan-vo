# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI/React skeleton with auth and database

Status: done

Acceptance:
- FastAPI app starts and serves /health endpoint
- React frontend builds and loads
- SQLite database initializes with migrations
- OIDC Keycloak configuration present
- Docker compose runs backend, frontend, Keycloak, and DB
- Basic tests pass for backend and frontend

Implementation: `backend/app/main.py`, `backend/app/api/health.py`, `backend/app/api/prompts.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/security.py`, `backend/app/models/prompt.py`, `backend/app/services/prompt_service.py`, `backend/app/llm_adapters.py`, `backend/app/evaluate.py`, `backend/tests/test_health.py`, `backend/tests/test_prompts.py`, `backend/tests/test_llm_adapters.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/Layout.tsx`, `frontend/src/components/HealthCheck.tsx`, `frontend/src/components/Modal.tsx`, `frontend/src/components/Toast.tsx`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/PromptsPage.tsx`, `frontend/src/pages/EvaluationPage.tsx`, `frontend/src/pages/SettingsPage.tsx`, `frontend/src/api/client.ts`, `frontend/src/api/types.ts`, `frontend/src/styles/global.css`, `frontend/tests/App.test.tsx`, `frontend/tests/components.test.tsx`

Tests: `backend/tests/test_health.py`, `backend/tests/test_prompts.py`, `backend/tests/test_llm_adapters.py`, `frontend/src/App.test.tsx`, `frontend/src/components.test.tsx`

### jailbreak-engine — Jailbreak prompt engine with per-model prompt swapping

Status: planned

Acceptance:
- Store and retrieve jailbreak prompts per model
- Default prompt targets Chinese model '小码辣'
- LLM adapter supports OpenAI-compatible, Anthropic, Gemini, Ollama
- Deterministic offline core works without LLM key

### prompt-management — Prompt management UI with create/import/search/export

Status: planned

Acceptance:
- Dashboard lists prompts with pagination/filtering
- Create new prompt with model association
- Import prompts from JSON/file
- Search prompts by model, tag, content
- Export prompts to JSON

### evaluation-workflow — AI/ML evaluation workflow with baseline metrics

Status: planned

Acceptance:
- Run evaluation against test dataset
- Measure jailbreak success rate
- Report baseline and failure cases
- Reproducible evaluation command

