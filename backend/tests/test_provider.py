from app.engine.schema import AppSpec
from app.providers import create_spec


class BrokenProvider:
    def suggest(self, prompt: str):
        raise ValueError("Bad JSON")


class FixedProvider:
    def suggest(self, prompt: str):
        return AppSpec(name="Fixed")


class InvalidProvider:
    def suggest(self, prompt: str):
        return {"name": "Unsafe", "theme": {"primary": "javascript:alert(1)"}}


def test_provider_failure_falls_back_to_rules():
    assert create_spec("A bakery called Crumb", BrokenProvider()).name == "Crumb"


def test_valid_provider_spec_is_used():
    assert create_spec("A bakery called Crumb", FixedProvider()).name == "Fixed"


def test_invalid_provider_spec_falls_back_to_rules():
    spec = create_spec("A bakery called Crumb", InvalidProvider())
    assert spec.name == "Crumb"
    assert spec.theme.primary.startswith("#")
