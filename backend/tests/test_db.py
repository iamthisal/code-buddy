import pytest
from app.db import Base, Project, Version
from sqlalchemy import CheckConstraint, UniqueConstraint, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_version_numbers_are_unique_and_positive():
    assert any(isinstance(item, UniqueConstraint) and item.name == "uq_project_version" for item in Version.__table__.constraints)
    assert any(isinstance(item, CheckConstraint) and item.name == "ck_version_number_positive" for item in Version.__table__.constraints)
    assert any(isinstance(item, CheckConstraint) and item.name == "ck_project_version_positive" for item in Project.__table__.constraints)


def test_sqlite_enforces_version_constraints():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        project = Project(name="Test", prompt="Test")
        session.add(project)
        session.flush()
        session.add(Version(project_id=project.id, number=1, instruction="first", spec_json="{}"))
        session.commit()
        session.add(Version(project_id=project.id, number=1, instruction="duplicate", spec_json="{}"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.add(Version(project_id=project.id, number=0, instruction="invalid", spec_json="{}"))
        with pytest.raises(IntegrityError):
            session.commit()
    engine.dispose()
