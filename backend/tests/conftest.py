import os
import tempfile
from pathlib import Path


_test_db_dir = tempfile.TemporaryDirectory(prefix="siteforge-tests-")
_test_db_path = Path(_test_db_dir.name) / "siteforge.db"
os.environ["SITEFORGE_DATABASE_URL"] = f"sqlite:///{_test_db_path.as_posix()}"


def pytest_unconfigure():
    from app.db import engine

    engine.dispose()
    _test_db_dir.cleanup()
