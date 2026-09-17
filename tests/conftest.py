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
    with TemporaryDirectory(dir=Path(__file__).parent) as data_dir:
        monkeypatch.setenv("SUDOKU_DATA_DIR", os.fspath(data_dir))
        monkeypatch.setattr(persistence, "LEGACY_DATA_DIR", Path(data_dir))
        yield
