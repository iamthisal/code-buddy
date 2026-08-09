# feat: add deterministic SiteForge MVP

## Summary

Build a usable prompt-to-site flow on top of the original LangGraph prototype without requiring an AI API key.

## Changes

- Add pure engine modules for normalization, classification, slot extraction, planning, generation, validation, and refinement.
- Add SQLite-backed FastAPI projects, immutable versions, preview, restore, and ZIP export.
- Add a React editor with prompt entry, live preview, theme controls, history, validation, device widths, and export.
- Add Docker, Make targets, CI, test coverage, and setup/API/architecture docs.

## Testing

- Backend: 14 pytest tests pass.
- Ruff and mypy pass.
- Frontend test and build pending: npm registry returns 403 in this environment, and the alternate mirror times out.

## Checklist

- [x] Backend tests and static checks pass
- [ ] Frontend dependencies install, tests, and build pass
- [ ] Merge into develop after the frontend gate passes

Linked issue: initial SiteForge implementation request.
