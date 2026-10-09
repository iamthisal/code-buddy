# feat: expand catalog edits through chat

## Summary

Let project owners maintain common content and catalog fields without regenerating their site.

## Changes

- Edit the site description and contact phone.
- Rename, remove, and reprice existing products while retaining the site name.
- Reject duplicate products instead of silently adding a second catalog entry.

## Testing

- 81 backend tests pass, including focused refiner regressions.
- Ruff and mypy pass.
- Frontend package installation remains blocked by npm registry access in this environment.

## Checklist

- [x] Backend checks pass
- [ ] Frontend test and build gate

Linked issue: SiteForge catalog maintenance.
