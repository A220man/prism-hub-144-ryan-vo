# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure with FastAPI backend and React frontend
- SQLite database with SQLAlchemy ORM
- OIDC Keycloak integration with realm import
- Docker Compose for local development
- Health check endpoint
- Prompt CRUD API with pagination, filtering, import/export
- Role-based access control (admin, operator, analyst, viewer)
- LLM adapter abstraction (OpenAI-compatible, Anthropic, Gemini, Ollama)
- Deterministic offline evaluation framework
- React frontend with Dashboard, Prompts, Evaluation, Settings pages
- Responsive UI with Tailwind-like CSS variables
- Toast notifications, Modal dialogs, Loading states
- Comprehensive test suite (23 backend, 12 frontend tests)

### Changed
- None

### Fixed
- None

### Security
- Demo mode validation (refuses to start in production)
- JWT token validation with JWKS
- Role-based authorization on all data endpoints
- CORS configuration

## [1.0.0] - 2026-10-23

### Added
- Initial release of Prism Hub