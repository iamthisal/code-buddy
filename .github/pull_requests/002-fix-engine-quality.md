# fix: improve prompt interpretation

## Summary

Make short and messy business prompts produce clearer, safer specifications.

## Changes

- Remove control characters and favor explicit page phrases in intent ranking.
- Extract quoted names, hex theme colors, and labeled local phone numbers.
- Keep supplied contact details visible even when other sections are requested.
- Keep the new name extraction path type-safe.

## Testing

- 65 backend tests pass, including the 25-prompt corpus.
- Ruff and mypy pass.

## Checklist

- [x] Focused regressions included
- [x] Backend checks pass
- [x] No credentials or generated files added

Linked issue: SiteForge prompt quality.
