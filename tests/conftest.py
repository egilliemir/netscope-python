import json
import pytest

from app.api import app


@pytest.fixture()
def tmp_scans_file(tmp_path, monkeypatch):
    """Redirect storage to a temporary JSON file so tests never touch production data."""
    path = str(tmp_path / "scans.json")
    monkeypatch.setattr("app.storage.SCANS_FILE", path)
    return path


@pytest.fixture()
def seeded_scans_file(tmp_scans_file):
    """A temp scans file pre-loaded with two sample records."""
    records = [
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "host": "10.0.0.1",
            "start_port": 1,
            "end_port": 100,
            "open_ports": [22, 80],
        },
        {
            "timestamp": "2026-01-02T00:00:00+00:00",
            "host": "10.0.0.2",
            "start_port": 400,
            "end_port": 500,
            "open_ports": [443],
        },
    ]
    with open(tmp_scans_file, "w", encoding="utf-8") as f:
        json.dump(records, f)
    return tmp_scans_file
