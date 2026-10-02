import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# The application logger is configured on import; keep test logs out of the project.
os.environ["SUDOKU_DATA_DIR"] = os.fspath(Path(__file__).parent / ".pytest-runtime-data")

import persistence


@pytest.fixture(autouse=True)
def isolate_runtime_data(monkeypatch):
    """Keep persistence tests away from the developer's real game data."""
    # System temp, NOT the repo dir: OneDrive sync locks files mid-test and
    # causes random I/O flakes (same family as the .pytest_cache lock).
    with TemporaryDirectory(prefix="sudoku_test_") as data_dir:
        monkeypatch.setenv("SUDOKU_DATA_DIR", os.fspath(data_dir))
        monkeypatch.setattr(persistence, "LEGACY_DATA_DIR", Path(data_dir))
        yield
