import io
import json
import logging
import zipfile

from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError


def test_project_lifecycle():
    with TestClient(app) as client:
        created = client.post("/api/v1/projects", json={"prompt": "A bakery called Crumb with FAQ"})
        assert created.status_code == 201
        project = created.json()
        project_id = project["id"]
        assert project["validation"]["valid"]
        assert client.get(f"/api/v1/projects/{project_id}/preview/index.html").status_code == 200
        refined = client.post(f"/api/v1/projects/{project_id}/refine", json={"instruction": "make it dark and add pricing"})
        assert refined.status_code == 200
        assert refined.json()["current_version"] == 2
        diff = client.get(f"/api/v1/projects/{project_id}/versions/2/diff")
        assert set(diff.json()["changes"]) == {"sections", "theme.background", "theme.text"}
        restored = client.post(f"/api/v1/projects/{project_id}/restore/1")
        assert restored.status_code == 200
        assert restored.json()["current_version"] == 3
        assert restored.json()["spec"]["theme"]["background"] == "#ffffff"
        archive = client.get(f"/api/v1/projects/{project_id}/export")
        assert archive.status_code == 200
        with zipfile.ZipFile(io.BytesIO(archive.content)) as bundle:
            assert set(bundle.namelist()) == {"index.html", "styles.css", "script.js"}


def test_bad_requests_and_preview_path():
    with TestClient(app) as client:
        invalid = client.post("/api/v1/projects", json={"prompt": ""})
        assert invalid.status_code == 422
        assert invalid.json()["detail"]["code"] == "validation_error"
        assert client.get("/api/v1/projects/999999").status_code == 404
        assert client.get("/api/v1/projects/1/preview/unknown").status_code == 404


def test_template_endpoint_returns_catalog_metadata():
    with TestClient(app) as client:
        templates = client.get("/api/v1/templates").json()
        assert len(templates) == 5
        assert all(template["description"] for template in templates)


def test_health_reports_database_failure(monkeypatch):
    from app import main

    def fail():
        raise OperationalError("SELECT 1", {}, Exception("offline"))

    with TestClient(app) as client:
        monkeypatch.setattr(main.engine, "connect", fail)
        response = client.get("/api/v1/health")
        assert response.status_code == 503
        assert response.json()["detail"]["code"] == "database_unavailable"


def test_generation_is_rate_limited(monkeypatch):
    from app import main
    from app.rate_limit import RateLimiter

    monkeypatch.setattr(main, "limiter", RateLimiter(limit=1))
    with TestClient(app) as client:
        assert client.post("/api/v1/projects", json={"prompt": "A bakery called One"}).status_code == 201
        blocked = client.post("/api/v1/projects", json={"prompt": "A bakery called Two"})
        assert blocked.status_code == 429
        assert blocked.json()["detail"]["code"] == "rate_limited"


def test_create_logs_project_id_without_prompt(caplog):
    with TestClient(app) as client, caplog.at_level(logging.INFO, logger="siteforge.events"):
        client.post("/api/v1/projects", json={"prompt": "A bakery called Private Name"})
    event = json.loads(caplog.records[-1].message)
    assert event["event"] == "project_created"
    assert "prompt" not in event


def test_project_list_supports_pagination():
    with TestClient(app) as client:
        client.post("/api/v1/projects", json={"prompt": "A bakery called Page One"})
        client.post("/api/v1/projects", json={"prompt": "A bakery called Page Two"})
        first = client.get("/api/v1/projects?limit=1&offset=0").json()
        second = client.get("/api/v1/projects?limit=1&offset=1").json()
        assert len(first) == len(second) == 1
        assert first[0]["id"] > second[0]["id"]


def test_project_search_treats_wildcards_literally():
    with TestClient(app) as client:
        client.post("/api/v1/projects", json={"prompt": "A bakery called Searchable Place"})
        matches = client.get("/api/v1/projects?q=Searchable%20Place").json()
        assert any(item["name"] == "Searchable Place" for item in matches)
        assert client.get("/api/v1/projects?q=Searchable%25Place").json() == []
