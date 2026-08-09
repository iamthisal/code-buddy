import re

from .normalizer import normalize
from .schema import Item

COLORS = {
    "pink": "#c34878", "green": "#287a54", "blue": "#2568a8",
    "red": "#b53641", "orange": "#a9581c", "purple": "#7951a1",
    "black": "#252525", "teal": "#256f68", "yellow": "#886009",
}


def extract(prompt: str) -> dict:
    clean = normalize(prompt)
    lower = clean.lower()
    name_pattern = r"([\w][\w '&-]{1,45}?)(?=\s+(?:that|with|selling|offering|in)\b|[,.;]|$)"
    match = re.search(r"(?:called|named)\s+" + name_pattern, clean, re.I)
    if match is None:
        match = re.search(r"\bfor\s+" + name_pattern, clean, re.I)
    name = match.group(1).strip() if match else "Your Business"
    if name.lower() in {"a", "an", "the", "me", "my", "website"}:
        name = "Your Business"
    email = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", clean)
    phone = re.search(r"(?:\+\d[\d\s()-]{7,}\d)", clean)
    color = next((value for word, value in COLORS.items() if re.search(rf"\b{word}\b", lower)), "#256f68")
    sections = [key for key in ("features", "pricing", "testimonials", "faq", "contact") if re.search(rf"\b{key}\b", lower)]
    if not sections:
        sections = ["features", "contact"]
    items = []
    for item, price in re.findall(r"([\w][\w\s-]{1,35}?)\s+(?:at|for)\s+(\$\s?\d+(?:\.\d{1,2})?)", clean, re.I):
        name_part = re.split(r"\b(?:selling|and|offers?|including)\b", item, flags=re.I)[-1].strip()
        if name_part:
            items.append(Item(name=name_part.title(), price=price.replace(" ", "")))
    return {
        "name": name, "color": color, "email": email.group() if email else "",
        "phone": phone.group() if phone else "", "sections": sections,
        "items": items[:12], "dark": bool(re.search(r"\bdark\b", lower)),
    }
