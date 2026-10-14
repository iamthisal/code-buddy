# API

All endpoints are under `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Health status |
| GET | `/templates` | Supported site types |
| POST | `/projects` | Create from `{ "prompt": "..." }` |
| GET | `/projects` | List projects; `q`, `limit`, and `offset` filter and page results; `X-Total-Count` reports matches |
| GET | `/projects/{id}` | Read current specification, validation, and preview URL |
| POST | `/projects/{id}/refine` | Edit with `{ "instruction": "...", "base_version": 1 }`; `base_version` detects stale edits |
| GET | `/projects/{id}/versions` | List version specifications; supports `limit` and `offset` |
| POST | `/projects/{id}/restore/{version}` | Copy an earlier version as the latest |
| GET | `/projects/{id}/versions/{version}/diff` | Compare a version with its predecessor |
| GET | `/projects/{id}/versions/{left}/compare/{right}` | Compare any two versions |
| GET | `/projects/{id}/preview/{filename}` | Serve generated `index.html`, `styles.css`, or `script.js`; `v` selects a saved version |
| GET | `/projects/{id}/export` | Download a static site ZIP; `version` selects a saved version |

Unknown resources return 404. Unsupported edit commands and invalid request bodies return 422. Errors use a `detail` object with a code and message; validation errors also include a `fields` list.
Stale refinements return 409 with the `version_conflict` code. Preview responses use a restrictive Content Security Policy, `nosniff`, and `no-store`.
Create and refine requests are limited to 30 per client per minute by default; `SITEFORGE_RATE_LIMIT=0` disables the limit.
`/health` checks database connectivity and returns 503 when SQLite is unavailable. Project creation, refinement, and restore emit structured events without prompt text.
