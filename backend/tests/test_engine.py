import pytest
from app.engine.generator import generate
from app.engine.intent import classify
from app.engine.normalizer import normalize
from app.engine.planner import plan
from app.engine.refiner import refine
from app.engine.validator import validate


def test_normalizer_and_classifier():
    assert normalize("  a   bakery\n ") == "a bakery"
    assert classify("A restaurant menu with food")[0][0] == "menu"


@pytest.mark.parametrize("prompt,kind", [
    ("A restaurant menu for Little Table", "menu"),
    ("A shop selling products called North Goods", "store"),
    ("A booking page for a salon called Juniper", "booking"),
    ("A waitlist for a launch called Bright", "waitlist"),
    ("An agency landing page called Orbit", "landing"),
])
def test_site_types(prompt, kind):
    assert plan(prompt).kind == kind


def test_bakery_generation_is_deterministic_and_valid():
    spec = plan("A bakery selling cupcakes and custom cakes, pink theme, with FAQ")
    assert spec.theme.primary == "#c34878"
    assert "faq" in spec.sections
    files = generate(spec)
    assert files == generate(spec)
    assert validate(spec, files).valid
    assert "<h1>Welcome to Your Bakery</h1>" in files["index.html"]


def test_refinement_creates_new_spec_without_mutating_original():
    original = plan("A bakery called Crumb")
    updated = refine(original, "make it dark and add pricing")
    assert original.theme.background == "#ffffff"
    assert updated.theme.background != original.theme.background
    assert "pricing" in updated.sections
    assert validate(updated, generate(updated)).valid


def test_unsafe_text_is_escaped():
    spec = plan("A bakery called <script>alert(1)</script>")
    html = generate(spec)["index.html"]
    assert "<script>alert(1)</script>" not in html


def test_unknown_edit_is_rejected():
    with pytest.raises(ValueError):
        refine(plan("A bakery"), "write me a poem")


def test_font_change():
    assert refine(plan("A bakery"), "change font to serif").theme.font == "serif"


def test_refiner_rejects_no_op():
    with pytest.raises(ValueError):
        refine(plan("A bakery with FAQ"), "add FAQ")


def test_refiner_changes_tagline():
    spec = refine(plan("A bakery called Crumb"), 'set tagline to "Fresh every day"')
    assert spec.tagline == "Fresh every day"
