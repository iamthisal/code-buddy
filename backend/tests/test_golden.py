import json
from pathlib import Path

import pytest
from app.engine.generator import generate
from app.engine.planner import plan
from app.engine.validator import validate

CASES = json.loads((Path(__file__).parent / "golden" / "cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_prompt_corpus(case):
    spec = plan(case["prompt"])
    assert spec.kind == case["kind"]
    assert spec.name == case["name"]
    files = generate(spec)
    assert validate(spec, files).valid
    assert files == generate(spec)
