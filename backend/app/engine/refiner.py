import re

from .schema import AppSpec, Item
from .slots import COLORS


def refine(spec: AppSpec, command: str) -> AppSpec:
    updated = spec.model_copy(deep=True)
    lower = command.lower().strip()
    changed = False
    if re.search(r"\b(make it dark|dark mode|dark theme)\b", lower):
        updated.theme.background, updated.theme.text = "#142127", "#f5f7f7"
        changed = True
    if re.search(r"\b(make it light|light mode|light theme)\b", lower):
        updated.theme.background, updated.theme.text = "#ffffff", "#17252b"
        changed = True
    color = re.search(r"(?:primary )?color (?:to |is )?(#[0-9a-fA-F]{6}|\w+)", lower)
    if color:
        value = color.group(1)
        if value in COLORS or re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            updated.theme.primary = COLORS.get(value, value)
            changed = True
    font = re.search(r"\b(?:change |set )?font (?:to )?(serif|sans)\b", lower)
    if font:
        updated.theme.font = "serif" if font.group(1) == "serif" else "sans"
        changed = True
    rename = re.search(r"\brename (?:it |the site |to )?(?:to )?(.+?)(?:[.!]|$)", command, re.I)
    if rename:
        updated.name = rename.group(1).strip()[:120]
        updated.tagline = f"Welcome to {updated.name}"
        changed = True
    tagline = re.search(r"\b(?:change|set) (?:the )?tagline to (.+)$", command, re.I)
    if tagline:
        updated.tagline = tagline.group(1).strip().strip('"\'')
        changed = True
    description = re.search(r"\b(?:change|set) (?:the )?description to (.+)$", command, re.I)
    if description:
        updated.description = description.group(1).strip().strip('"\'')
        changed = True
    email = re.search(r"\b(?:change|set) (?:contact )?email to ([\w.+-]+@[\w.-]+\.[a-zA-Z]{2,})\b", command, re.I)
    if email:
        updated.contact_email = email.group(1)
        if "contact" not in updated.sections:
            updated.sections.append("contact")
        changed = True
    phone = re.search(r"\b(?:change|set) (?:contact )?phone to ([+\d()\s-]+)$", command, re.I)
    if phone:
        number = phone.group(1).strip()
        if not 8 <= len(re.sub(r"\D", "", number)) <= 15:
            raise ValueError("Phone numbers need 8 to 15 digits")
        updated.contact_phone = number
        if "contact" not in updated.sections:
            updated.sections.append("contact")
        changed = True
    for action, section in re.findall(r"\b(add|remove)\s+(features|pricing|testimonials|faq|contact)\b", lower):
        if action == "add" and section not in updated.sections:
            updated.sections.append(section)
            changed = True
        elif action == "remove" and section in updated.sections:
            updated.sections.remove(section)
            changed = True
    product = re.search(r"\badd (?:product |item )?([\w][\w\s-]{1,60}?)\s+(?:at|for)\s+(\$\s?\d+(?:\.\d{1,2})?)", command, re.I)
    if product:
        updated.items.append(Item(name=product.group(1).strip().title(), price=product.group(2).replace(" ", "")))
        changed = True
    if not changed or updated == spec:
        raise ValueError("Try changing the color, adding a section, renaming, or adding a priced item")
    return AppSpec.model_validate(updated.model_dump())
