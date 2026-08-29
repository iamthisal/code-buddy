from sqlalchemy import CheckConstraint, UniqueConstraint

from app.db import Project, Version


def test_version_numbers_are_unique_and_positive():
    assert any(isinstance(item, UniqueConstraint) and item.name == "uq_project_version" for item in Version.__table__.constraints)
    assert any(isinstance(item, CheckConstraint) and item.name == "ck_version_number_positive" for item in Version.__table__.constraints)
    assert any(isinstance(item, CheckConstraint) and item.name == "ck_project_version_positive" for item in Project.__table__.constraints)
