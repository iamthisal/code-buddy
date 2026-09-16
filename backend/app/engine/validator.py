import re
from html.parser import HTMLParser

from .schema import AppSpec, ValidationIssue, ValidationReport


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.headings: list[int] = []
        self.labels: set[str] = set()
        self.inputs: set[str] = set()
        self.title_count = 0
        self.main_count = 0
        self.issues: list[ValidationIssue] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.title_count += 1
        if tag == "main":
            self.main_count += 1
        if any(name.lower().startswith("on") for name in values):
            self.issues.append(ValidationIssue(level="error", code="inline_handler", message="Inline event handlers are not allowed"))
        element_id = values.get("id")
        href = values.get("href")
        label_for = values.get("for")
        if element_id:
            if element_id in self.ids:
                self.issues.append(ValidationIssue(level="error", code="duplicate_id", message=f"Duplicate id {element_id}"))
            self.ids.add(element_id)
        if tag == "a" and href and href.startswith("#"):
            self.links.append(href[1:])
        if tag in {"a", "link"} and href and re.match(r"\s*javascript\s*:", href, re.I):
            self.issues.append(ValidationIssue(level="error", code="unsafe_url", message="JavaScript URLs are not allowed"))
        if tag == "a" and values.get("target") == "_blank" and "noopener" not in (values.get("rel") or "").split():
            self.issues.append(ValidationIssue(level="error", code="unsafe_blank_target", message="New-tab links need rel=noopener"))
        if tag == "img" and "alt" not in values:
            self.issues.append(ValidationIssue(level="error", code="missing_alt", message="Image needs alt text"))
        if tag == "label" and label_for:
            self.labels.add(label_for)
        if tag in {"input", "textarea", "select"} and element_id:
            self.inputs.add(element_id)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))


def contrast(first: str, second: str) -> float:
    def luminance(color: str) -> float:
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))

    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def validate(spec: AppSpec, files: dict[str, str]) -> ValidationReport:
    parser = SiteParser()
    parser.feed(files["index.html"])
    issues = parser.issues
    for target in parser.links:
        if target and target not in parser.ids:
            issues.append(ValidationIssue(level="error", code="dead_anchor", message=f"Missing #{target}"))
    if parser.headings.count(1) != 1:
        issues.append(ValidationIssue(level="error", code="heading", message="Exactly one H1 is required"))
    if parser.title_count != 1:
        issues.append(ValidationIssue(level="error", code="title", message="Exactly one document title is required"))
    if parser.main_count != 1:
        issues.append(ValidationIssue(level="error", code="main_landmark", message="Exactly one main landmark is required"))
    for previous, current in zip(parser.headings, parser.headings[1:]):
        if current > previous + 1:
            issues.append(ValidationIssue(level="error", code="heading_order", message="Heading levels must not be skipped"))
            break
    for input_id in parser.inputs - parser.labels:
        issues.append(ValidationIssue(level="error", code="missing_label", message=f"Input {input_id} needs a label"))
    for filename, maximum in (("index.html", 500_000), ("styles.css", 200_000), ("script.js", 100_000)):
        if len(files[filename].encode("utf-8")) > maximum:
            issues.append(ValidationIssue(level="error", code="size", message=f"{filename} exceeds its size limit"))
    colors = (spec.theme.primary, spec.theme.background, spec.theme.text)
    for color in colors:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            issues.append(ValidationIssue(level="error", code="color", message="Invalid theme color"))
    if all(re.fullmatch(r"#[0-9a-fA-F]{6}", color) for color in colors):
        if contrast(spec.theme.background, spec.theme.text) < 4.5:
            issues.append(ValidationIssue(level="error", code="contrast", message="Text and background need more contrast"))
        if contrast(spec.theme.primary, "#ffffff") < 4.5:
            issues.append(ValidationIssue(level="error", code="hero_contrast", message="Hero and white text need more contrast"))
    return ValidationReport(issues=issues)
