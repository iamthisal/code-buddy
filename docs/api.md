# API

All endpoints are under `/api/v1`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Health status |
| GET | `/templates` | Supported site types |
| POST | `/projects` | Create from `{ "prompt": "..." }` |
| GET | `/projects` | List projects |
| GET | `/projects/{id}` | Read current specification, validation, and preview URL |
| POST | `/projects/{id}/refine` | Edit with `{ "instruction": "..." }` |
| GET | `/projects/{id}/versions` | List version specifications |
| POST | `/projects/{id}/restore/{version}` | Copy an earlier version as the latest |
| GET | `/projects/{id}/preview/{filename}` | Serve generated `index.html`, `styles.css`, or `script.js` |
| GET | `/projects/{id}/export` | Download the current static site ZIP |

Unknown resources return 404. Unsupported edit commands return 422 with a `detail` object containing a code and message. FastAPI returns its standard 422 validation response for invalid request bodies.
