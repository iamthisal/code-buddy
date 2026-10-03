import io
import os
import time
import zipfile
from contextlib import asynccontextmanager
from math import ceil

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError

from .db import Base, Project, SessionLocal, Version, engine
from .engine.catalog import list_templates
from .engine.diff import diff_specs
from .engine.generator import generate
from .engine.refiner import refine
from .engine.schema import AppSpec
from .engine.validator import validate
from .events import record_event
from .providers import create_spec
from .rate_limit import RateLimiter


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="SiteForge API", version="0.1.0", lifespan=lifespan)
limiter = RateLimiter(limit=int(os.getenv("SITEFORGE_RATE_LIMIT", "30")))
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("SITEFORGE_CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_error(_request, exc: RequestValidationError):
    fields = [{"field": ".".join(str(part) for part in error["loc"]), "message": error["msg"]} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": {"code": "validation_error", "message": "Invalid request", "fields": fields}})


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)


class RefineRequest(BaseModel):
    instruction: str = Field(min_length=3, max_length=500)


def check_rate(request: Request) -> None:
    client = request.client.host if request.client else "unknown"
    if not limiter.allow(client, time.monotonic()):
        raise HTTPException(status_code=429, detail={"code": "rate_limited", "message": "Too many generation requests"}, headers={"Retry-After": str(ceil(limiter.window_seconds))})


def not_found() -> HTTPException:
    return HTTPException(status_code=404, detail={"code": "not_found", "message": "Project or version not found"})


def current(db, project: Project) -> Version:
    version = db.scalar(select(Version).where(Version.project_id == project.id, Version.number == project.current_version))
    if version is None:
        raise not_found()
    return version


def detail(db, project: Project) -> dict:
    version = current(db, project)
    spec = AppSpec.model_validate_json(version.spec_json)
    files = generate(spec)
    report = validate(spec, files)
    return {
        "id": project.id, "name": project.name, "prompt": project.prompt,
        "current_version": project.current_version, "spec": spec.model_dump(),
        "validation": report.model_dump() | {"valid": report.valid},
        "preview_url": f"/api/v1/projects/{project.id}/preview/index.html?v={project.current_version}",
    }


@app.get("/api/v1/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail={"code": "database_unavailable", "message": "Database is unavailable"}) from exc
    return {"status": "ok"}


@app.get("/api/v1/templates")
def templates():
    return [template.model_dump() for template in list_templates()]


@app.post("/api/v1/projects", status_code=201)
def create_project(request: PromptRequest, _rate: None = Depends(check_rate)):
    spec = create_spec(request.prompt)
    with SessionLocal() as db:
        project = Project(name=spec.name, prompt=request.prompt, current_version=1)
        db.add(project)
        db.flush()
        db.add(Version(project_id=project.id, number=1, instruction=request.prompt, spec_json=spec.model_dump_json()))
        db.commit()
        db.refresh(project)
        record_event("project_created", project_id=project.id, version=1)
        return detail(db, project)


@app.get("/api/v1/projects")
def list_projects(response: Response, limit: int = Query(default=100, ge=1, le=100), offset: int = Query(default=0, ge=0), q: str | None = Query(default=None, min_length=1, max_length=120)):
    with SessionLocal() as db:
        query = select(Project)
        count_query = select(func.count()).select_from(Project)
        if q:
            predicate = Project.name.contains(q, autoescape=True)
            query = query.where(predicate)
            count_query = count_query.where(predicate)
        response.headers["X-Total-Count"] = str(db.scalar(count_query) or 0)
        projects = db.scalars(query.order_by(Project.id.desc()).limit(limit).offset(offset)).all()
        return [{"id": p.id, "name": p.name, "current_version": p.current_version, "created_at": p.created_at} for p in projects]


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: int):
    with SessionLocal() as db:
        project = db.get(Project, project_id)
        if project is None:
            raise not_found()
        return detail(db, project)


@app.post("/api/v1/projects/{project_id}/refine")
def refine_project(project_id: int, request: RefineRequest, _rate: None = Depends(check_rate)):
    with SessionLocal() as db:
        project = db.get(Project, project_id)
        if project is None:
            raise not_found()
        try:
            spec = refine(AppSpec.model_validate_json(current(db, project).spec_json), request.instruction)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail={"code": "unsupported_edit", "message": str(exc)}) from exc
        next_number = (db.scalar(select(Version.number).where(Version.project_id == project_id).order_by(Version.number.desc())) or 0) + 1
        db.add(Version(project_id=project_id, number=next_number, instruction=request.instruction, spec_json=spec.model_dump_json()))
        project.name = spec.name
        project.current_version = next_number
        db.commit()
        record_event("project_refined", project_id=project_id, version=next_number)
        return detail(db, project)


@app.get("/api/v1/projects/{project_id}/versions")
def list_versions(project_id: int):
    with SessionLocal() as db:
        if db.get(Project, project_id) is None:
            raise not_found()
        versions = db.scalars(select(Version).where(Version.project_id == project_id).order_by(Version.number.desc())).all()
        return [{"number": v.number, "instruction": v.instruction, "created_at": v.created_at, "spec": AppSpec.model_validate_json(v.spec_json).model_dump()} for v in versions]


@app.post("/api/v1/projects/{project_id}/restore/{version_number}")
def restore(project_id: int, version_number: int):
    with SessionLocal() as db:
        project = db.get(Project, project_id)
        source = db.scalar(select(Version).where(Version.project_id == project_id, Version.number == version_number))
        if project is None or source is None:
            raise not_found()
        next_number = (db.scalar(select(Version.number).where(Version.project_id == project_id).order_by(Version.number.desc())) or 0) + 1
        db.add(Version(project_id=project_id, number=next_number, instruction=f"Restored version {version_number}", spec_json=source.spec_json))
        project.current_version = next_number
        project.name = AppSpec.model_validate_json(source.spec_json).name
        db.commit()
        record_event("project_restored", project_id=project_id, version=next_number, source_version=version_number)
        return detail(db, project)


@app.get("/api/v1/projects/{project_id}/versions/{version_number}/diff")
def version_diff(project_id: int, version_number: int):
    with SessionLocal() as db:
        selected = db.scalar(select(Version).where(Version.project_id == project_id, Version.number == version_number))
        previous = db.scalar(select(Version).where(Version.project_id == project_id, Version.number == version_number - 1))
        if selected is None or (version_number > 1 and previous is None):
            raise not_found()
        changes = diff_specs(AppSpec.model_validate_json(previous.spec_json), AppSpec.model_validate_json(selected.spec_json)) if previous else {}
        return {"version": version_number, "changes": changes}


@app.get("/api/v1/projects/{project_id}/preview/{filename}")
def preview(project_id: int, filename: str, v: int | None = Query(default=None, ge=1)):
    if filename not in {"index.html", "styles.css", "script.js"}:
        raise not_found()
    with SessionLocal() as db:
        project = db.get(Project, project_id)
        if project is None:
            raise not_found()
        version = db.scalar(select(Version).where(Version.project_id == project_id, Version.number == v)) if v else current(db, project)
        if version is None:
            raise not_found()
        files = generate(AppSpec.model_validate_json(version.spec_json), asset_suffix=f"?v={version.number}")
    media = {"index.html": "text/html", "styles.css": "text/css", "script.js": "text/javascript"}[filename]
    headers = {
        "Content-Security-Policy": "default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; form-action 'none'; base-uri 'none'",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
        "Referrer-Policy": "no-referrer",
    }
    return Response(files[filename], media_type=media, headers=headers)


@app.get("/api/v1/projects/{project_id}/export")
def export_project(project_id: int):
    with SessionLocal() as db:
        project = db.get(Project, project_id)
        if project is None:
            raise not_found()
        files = generate(AppSpec.model_validate_json(current(db, project).spec_json))
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, content.encode("utf-8"))
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="siteforge-{project_id}.zip"'})
