# Architecture

The browser editor uses React and Vite. It calls FastAPI `/api/v1` endpoints. SQLAlchemy stores projects and immutable version specifications in SQLite. The current version number points to the active specification. Preview assets are generated from that specification on request; no user-supplied file path is written to disk.

The deterministic engine runs `normalizer -> intent -> slots -> planner -> generator -> validator`. The refiner parses a constrained command grammar, copies the current specification, changes supported fields, and generates the next version. Jinja2 autoescaping keeps text out of markup. Theme values are restricted to known colors or validated hex values. The preview route only accepts three fixed filenames and sets a restrictive Content Security Policy.

`SITEFORGE_LLM_PROVIDER=groq` with `GROQ_API_KEY` enables optional structured specification suggestions. Provider output is parsed as `AppSpec` and falls back to the deterministic planner on errors. It never writes code or files.

The exported ZIP contains `index.html`, `styles.css`, and `script.js`. They are static and can be hosted anywhere. Forms are previews without a submission backend.
