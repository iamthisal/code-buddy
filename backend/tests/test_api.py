import io
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
        assert client.post("/api/v1/projects", json={"prompt": ""}).status_code == 422
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
