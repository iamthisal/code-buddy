# feat: complete saved-version workflows

## Summary

Make historical versions inspectable and exportable while protecting concurrent edits.

## Changes

- Honor version parameters on preview HTML, CSS, and JavaScript.
- Pin preview asset URLs to the displayed version.
- Export a selected version and page long version histories.
- Reject stale refinements with a version conflict.
- Compare any two saved specifications.

## Testing

- 75 backend tests pass, including historical asset and conflict regressions.
- Ruff and mypy pass.
- Frontend package installation remains blocked by npm registry access in this environment.

## Checklist

- [x] Backend checks pass
- [ ] Frontend test and build gate

Linked issue: SiteForge version history.
