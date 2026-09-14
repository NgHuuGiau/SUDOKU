import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture(autouse=True)
def isolate_runtime_data(monkeypatch):
    """Keep persistence tests away from the developer's real game data."""
    with TemporaryDirectory(dir=Path(__file__).parent) as data_dir:
        monkeypatch.setenv("SUDOKU_DATA_DIR", os.fspath(data_dir))
        yield
