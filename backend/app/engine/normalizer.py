import re
import unicodedata


def normalize(prompt: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", prompt)).strip()


def tokens(prompt: str) -> list[str]:
    return re.findall(r"[\w]+", normalize(prompt).lower())
