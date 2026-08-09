from collections import Counter

from .normalizer import tokens

INTENTS = {
    "store": "shop store catalog sell products ecommerce product purchase",
    "booking": "booking appointment schedule reserve reservation salon spa clinic service",
    "waitlist": "waitlist signup launch coming soon early access",
    "menu": "menu restaurant cafe bakery food dishes drinks",
    "landing": "landing portfolio agency business company service homepage",
}


def classify(prompt: str) -> list[tuple[str, float]]:
    words = Counter(tokens(prompt))
    scores = {}
    for intent, examples in INTENTS.items():
        lexicon = set(tokens(examples))
        scores[intent] = sum(words[word] for word in lexicon)
    total = sum(scores.values())
    if total == 0:
        return [("landing", 1.0)]
    return sorted(((key, value / total) for key, value in scores.items()), key=lambda x: -x[1])
