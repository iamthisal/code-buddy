# feat: improve project API reliability

## Summary

Make project browsing predictable and static output easier to cache, compare, and review.

## Changes

- Add bounded pagination, literal name search, and total-count headers to project listings.
- Include Retry-After when generation is rate limited.
- Make exported ZIP bytes stable across repeated downloads.
- Keep preview responses out of caches and referrer headers.

## Testing

- 74 backend tests pass; new list and export behavior has API regressions.
- Ruff and mypy pass.

## Checklist

- [x] Existing editor list response remains an array
- [x] Backend checks pass

Linked issue: SiteForge API reliability.
