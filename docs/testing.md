# Testing

Run the backend gate from the repository root:

```sh
uv run pytest backend/tests -q
uv run ruff check backend
uv run mypy backend/app --ignore-missing-imports
```

The pytest suite sets `SITEFORGE_DATABASE_URL` to a temporary SQLite file before importing the app. It disposes the engine and removes that file at the end of the run, so tests do not modify the local `siteforge.db`.

Run the frontend gate after installing dependencies:

```sh
npm install --prefix frontend
npm test --prefix frontend
npm run build --prefix frontend
```

CI runs both gates on pushes and pull requests. The backend suite covers specification parsing, generation and validation, provider fallback, database constraints, API lifecycle, version history, preview security, and export. Frontend checks require npm registry access.
