import json
import logging

from app.events import record_event


def test_event_logs_structured_fields_without_prompt(caplog):
    with caplog.at_level(logging.INFO, logger="siteforge.events"):
        record_event("project_created", project_id=7, version=1)
    assert json.loads(caplog.records[-1].message) == {"event": "project_created", "project_id": 7, "version": 1}
