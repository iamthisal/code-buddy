import re
from typing import cast

from .intent import classify
from .normalizer import normalize
from .schema import AppSpec, Kind, Theme
from .slots import extract


def plan(prompt: str) -> AppSpec:
    clean = normalize(prompt)
    if not clean:
        raise ValueError("Describe your business to get started")
    slots = extract(clean)
    if slots["name"] == "Your Business":
        industry = re.search(r"\b(bakery|cafe|restaurant|salon|studio|shop|store|agency|clinic)\b", clean, re.I)
        if industry:
            slots["name"] = f"Your {industry.group(1).title()}"
    kind = cast(Kind, classify(clean)[0][0])
    if re.search(r"\bbaker(y|ies)\b", clean, re.I):
        kind = "menu" if kind == "landing" else kind
    theme = Theme(primary=slots["color"])
    if slots["dark"]:
        theme.background, theme.text = "#142127", "#f5f7f7"
    name = slots["name"]
    return AppSpec(
        name=name, kind=kind, industry=kind, tagline=f"Welcome to {name}",
        description=(clean[0].upper() + clean[1:])[:500], items=slots["items"],
        sections=slots["sections"], contact_email=slots["email"],
        contact_phone=slots["phone"], theme=theme,
    )
