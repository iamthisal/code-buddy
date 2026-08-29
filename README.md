# SiteForge

SiteForge turns a short business description into a responsive website you can preview, edit, version, and export. It works without an AI key: a deterministic parser creates an `AppSpec`, and Jinja2 renders static HTML, CSS, and JavaScript. An optional Groq provider may suggest an `AppSpec`; invalid responses fall back to the rule-based planner.

## Run locally

Requirements: Python 3.12+, uv, Node.js 22+, npm.

```sh
uv sync --extra dev
cd frontend && npm install && cd ..
make dev
```

Open http://localhost:5173. The API runs at http://localhost:8000. On Windows without Make, run `uv run uvicorn app.main:app --app-dir backend --reload --port 8000` and `npm run dev --prefix frontend` in separate terminals. `docker compose up --build` starts both services with a persistent SQLite volume.

Use `make test` for backend and frontend tests. The frontend build is `make build`. Copy `.env.example` to `.env` to configure the database, CORS, or optional Groq provider. The default provider uses no network or API key.

## Current scope

The engine supports landing, store, booking, waitlist, and menu layouts, named color themes, contact details, FAQ, pricing, and priced items. Refinement understands light/dark themes, primary color and font changes, section additions/removals, renaming, and adding priced items. Each successful edit creates a new version; restore creates a new version from an older specification. Booking and waitlist forms in exported sites are demonstration forms and do not store submissions.

The previous LangGraph prototype remains in `agent/` for reference. Its code-writing path is not used by SiteForge.

See [architecture](docs/architecture.md), [API](docs/api.md), and [adding a site type](docs/adding-a-template.md).
