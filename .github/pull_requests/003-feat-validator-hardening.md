# feat: harden generated-site validation

## Summary

Catch accessibility, document structure, and link safety defects before preview or export.

## Changes

- Check labels on all form controls, including textareas and selects.
- Reject JavaScript links, inline event handlers, and unprotected new-tab links.
- Require one title and main landmark.
- Enforce byte-size limits for HTML, CSS, and JavaScript.

## Testing

- 71 backend tests pass; each new validation rule has a regression.
- Ruff and mypy pass.

## Checklist

- [x] Generated sites still validate without errors
- [x] Backend checks pass

Linked issue: SiteForge generated-site quality.
