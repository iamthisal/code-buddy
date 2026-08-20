from .schema import AppSpec


def diff_specs(before: AppSpec, after: AppSpec) -> dict[str, dict[str, object]]:
    old = before.model_dump()
    new = after.model_dump()
    changes: dict[str, dict[str, object]] = {}
    for field in ("name", "kind", "tagline", "description", "sections", "items", "contact_email", "contact_phone"):
        if old[field] != new[field]:
            changes[field] = {"before": old[field], "after": new[field]}
    for field in ("primary", "background", "text", "font"):
        if old["theme"][field] != new["theme"][field]:
            changes[f"theme.{field}"] = {"before": old["theme"][field], "after": new["theme"][field]}
    return changes
