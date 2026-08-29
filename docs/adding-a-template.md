# Adding a site type

Site types are fixed and deterministic. A new type needs a schema value, classifier examples, catalog entry, rendering behavior, and tests.

1. Add the new value to `Kind` in `backend/app/engine/schema.py`.
2. Add its keyword examples to `INTENTS` in `backend/app/engine/intent.py`. Keep examples distinctive so short prompts rank predictably.
3. Add an entry with `id`, `name`, and `description` to `backend/app/engine/catalog.json`. `/api/v1/templates` reads this catalog.
4. Extend `backend/app/engine/templates/index.html.j2` and `styles.css.j2` for the type. All user text must remain inside Jinja expressions so autoescaping applies. Avoid external assets and scripts.
5. Add a varied prompt to `backend/tests/golden/cases.json` and a focused engine test for the type's distinctive behavior. The generated site must pass `validate` and remain byte-identical for the same `AppSpec`.
6. Add the type to the editor's template list in `frontend/src/App.tsx` and run the frontend tests and build.

Before merging, run `uv run pytest backend/tests`, `uv run ruff check backend`, `uv run mypy backend/app --ignore-missing-imports`, `npm test --prefix frontend`, and `npm run build --prefix frontend`.
