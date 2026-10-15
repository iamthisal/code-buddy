from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schema import AppSpec

TEMPLATES = Path(__file__).parent / "templates"
ENV = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "j2"]))


def generate(spec: AppSpec) -> dict[str, str]:
    html = ENV.get_template("index.html.j2").render(spec=spec)
    css = ENV.get_template("styles.css.j2").render(spec=spec)
    js = (TEMPLATES / "script.js").read_text(encoding="utf-8")
    return {"index.html": html, "styles.css": css, "script.js": js}
