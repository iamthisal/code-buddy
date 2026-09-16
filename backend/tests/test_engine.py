import pytest
from app.engine.catalog import list_templates
from app.engine.diff import diff_specs
from app.engine.generator import generate
from app.engine.intent import classify
from app.engine.normalizer import normalize
from app.engine.planner import plan
from app.engine.refiner import refine
from app.engine.slots import extract
from app.engine.validator import validate


def test_normalizer_and_classifier():
    assert normalize("  a   bakery\n ") == "a bakery"
    assert classify("A restaurant menu with food")[0][0] == "menu"


def test_normalizer_removes_control_characters():
    assert normalize("A\x00 bakery\x1f\nsite") == "A bakery site"


def test_explicit_page_type_beats_incidental_business_word():
    assert classify("A booking page for a store called Juniper")[0][0] == "booking"


def test_quoted_business_name_is_extracted():
    assert plan("A bakery called 'Red Fern' with FAQ").name == "Red Fern"


def test_explicit_hex_theme_color_is_extracted():
    assert plan("A bakery called Crumb with color #1a5b3c").theme.primary == "#1a5b3c"


def test_labeled_local_phone_number_is_extracted():
    assert plan("A bakery called Crumb, phone: 555-123-4567").contact_phone == "555-123-4567"


def test_contact_information_is_not_hidden_by_section_request():
    spec = plan("A bakery called Crumb with FAQ, email hello@example.com")
    assert "contact" in spec.sections
    assert "hello@example.com" in generate(spec)["index.html"]


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


def test_refiner_updates_contact_email():
    spec = refine(plan("A bakery"), "set contact email to hello@example.com")
    assert spec.contact_email == "hello@example.com"
    assert "contact" in spec.sections


def test_extracts_multiple_priced_items_without_prompt_prefix():
    items = extract("A bakery selling cupcakes at $5 and cakes for $20")["items"]
    assert [(item.name, item.price) for item in items] == [("Cupcakes", "$5"), ("Cakes", "$20")]


def test_extracts_shorthand_prices():
    items = extract("A bakery selling cupcakes $5 and custom cakes $25")["items"]
    assert [(item.name, item.price) for item in items] == [("Cupcakes", "$5"), ("Custom Cakes", "$25")]


def test_priced_items_are_visible_when_only_faq_was_requested():
    spec = plan("A bakery selling cupcakes at $5 with FAQ")
    assert "features" in spec.sections
    assert "Cupcakes" in generate(spec)["index.html"]


def test_unnamed_industry_does_not_become_a_literal_name():
    assert plan("Build a site for a bakery with FAQ").name == "Your Bakery"


def test_validator_rejects_duplicate_ids():
    spec = plan("A bakery with features")
    files = generate(spec)
    files["index.html"] = files["index.html"].replace('id="features"', 'id="top"')
    assert "duplicate_id" in {issue.code for issue in validate(spec, files).issues}


def test_validator_rejects_skipped_heading_levels():
    spec = plan("A bakery with features")
    files = generate(spec)
    files["index.html"] = files["index.html"].replace("<h2>", "<h4>", 1)
    assert "heading_order" in {issue.code for issue in validate(spec, files).issues}


def test_validator_checks_textarea_labels():
    spec = plan("A booking page for a salon")
    files = generate(spec)
    files["index.html"] = files["index.html"].replace("</form>", '<textarea id="notes"></textarea></form>')
    assert "missing_label" in {issue.code for issue in validate(spec, files).issues}


def test_validator_rejects_javascript_links():
    spec = plan("A bakery")
    files = generate(spec)
    files["index.html"] += '<a href="javascript:alert(1)">Open</a>'
    assert "unsafe_url" in {issue.code for issue in validate(spec, files).issues}


def test_template_catalog_covers_all_site_types():
    assert {template.id for template in list_templates()} == {"landing", "store", "booking", "waitlist", "menu"}


def test_diff_reports_changed_fields_only():
    before = plan("A bakery called Crumb")
    after = refine(before, "make it dark and add FAQ")
    changes = diff_specs(before, after)
    assert set(changes) == {"sections", "theme.background", "theme.text"}
    assert changes["theme.background"]["before"] == "#ffffff"
