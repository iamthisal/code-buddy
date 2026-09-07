import re
import unicodedata


def normalize(prompt: str) -> str:
    clean = unicodedata.normalize("NFKC", prompt)
    clean = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", clean)
    return re.sub(r"\s+", " ", clean).strip()


def tokens(prompt: str) -> list[str]:
    return re.findall(r"[\w]+", normalize(prompt).lower())
