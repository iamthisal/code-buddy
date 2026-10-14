# test: strengthen SiteForge review gates

## Summary

Keep backend verification isolated and cover important fallback, persistence, and preview contracts.

## Changes

- Run pytest against a temporary SQLite database and close it cleanly on Windows.
- Verify malformed provider output falls back to the deterministic planner.
- Exercise SQLite version constraints and preview security responses.
- Document current version APIs and local review commands.

## Testing

- 84 backend tests pass.
- Ruff and mypy pass.
- Frontend package installation remains blocked by npm registry access in this environment.

## Checklist

- [x] Backend checks pass
- [ ] Frontend test and build gate

Linked issue: SiteForge quality gates.
