import json
from pathlib import Path

from pydantic import BaseModel

from .schema import Kind


class TemplateDescriptor(BaseModel):
    id: Kind
    name: str
    description: str


def list_templates() -> list[TemplateDescriptor]:
    path = Path(__file__).with_name("catalog.json")
    return [TemplateDescriptor.model_validate(item) for item in json.loads(path.read_text(encoding="utf-8"))]
