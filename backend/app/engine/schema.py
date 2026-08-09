from typing import Literal

from pydantic import BaseModel, Field

Kind = Literal["landing", "store", "booking", "waitlist", "menu"]
Section = Literal["features", "pricing", "testimonials", "faq", "contact"]


def default_sections() -> list[Section]:
    return ["features", "contact"]


class Item(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=300)
    price: str = Field(default="", max_length=30)


class Theme(BaseModel):
    primary: str = Field(default="#256f68", pattern=r"^#[0-9a-fA-F]{6}$")
    background: str = Field(default="#ffffff", pattern=r"^#[0-9a-fA-F]{6}$")
    text: str = Field(default="#17252b", pattern=r"^#[0-9a-fA-F]{6}$")
    font: Literal["sans", "serif"] = "sans"


class AppSpec(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: Kind = "landing"
    industry: str = Field(default="business", max_length=80)
    tone: str = Field(default="welcoming", max_length=80)
    tagline: str = Field(default="Made with care, just for you.", max_length=200)
    description: str = Field(default="Discover something worth sharing.", max_length=500)
    items: list[Item] = Field(default_factory=list)
    sections: list[Section] = Field(default_factory=default_sections, max_length=8)
    contact_email: str = Field(default="", max_length=200)
    contact_phone: str = Field(default="", max_length=50)
    theme: Theme = Field(default_factory=Theme)


class ValidationIssue(BaseModel):
    level: Literal["error", "warning"]
    code: str
    message: str


class ValidationReport(BaseModel):
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue.level == "error" for issue in self.issues)
