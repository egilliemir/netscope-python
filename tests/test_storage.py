import json

from app.storage import load_scans, save_scan, get_scan_stats


# ---------------------------------------------------------------------------
# load_scans
# ---------------------------------------------------------------------------

def test_load_scans_file_missing(tmp_scans_file):
    """Returns an empty list when the file does not exist."""
    assert load_scans() == []


def test_load_scans_file_empty(tmp_scans_file):
    """Returns an empty list when the file exists but is empty."""
    with open(tmp_scans_file, "w") as f:
        f.write("")
    assert load_scans() == []


def test_load_scans_invalid_json(tmp_scans_file):
    """Returns an empty list when the file contains invalid JSON."""
    with open(tmp_scans_file, "w") as f:
        f.write("{broken json")
    assert load_scans() == []


def test_load_scans_valid(seeded_scans_file):
    """Returns the correct list of records from a valid file."""
    scans = load_scans()
    assert len(scans) == 2
    assert scans[0]["host"] == "10.0.0.1"


# ---------------------------------------------------------------------------
# save_scan
# ---------------------------------------------------------------------------

def test_save_scan_creates_file(tmp_scans_file):
    """save_scan creates the file and writes the first record."""
    record = {
        "timestamp": "2026-03-12T00:00:00+00:00",
        "host": "10.0.0.1",
        "start_port": 1,
        "end_port": 10,
        "open_ports": [22],
    }
    save_scan(record)

    with open(tmp_scans_file, "r") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["host"] == "10.0.0.1"


def test_save_scan_appends(seeded_scans_file):
    """save_scan appends to existing records without overwriting."""
    new_record = {
        "timestamp": "2026-03-12T12:00:00+00:00",
        "host": "10.0.0.3",
        "start_port": 80,
        "end_port": 90,
        "open_ports": [],
    }
    save_scan(new_record)

    with open(seeded_scans_file, "r") as f:
        data = json.load(f)
    assert len(data) == 3
    assert data[2]["host"] == "10.0.0.3"


# ---------------------------------------------------------------------------
# get_scan_stats
# ---------------------------------------------------------------------------

def test_get_scan_stats_empty(tmp_scans_file):
    """Returns zeroed stats when there are no scans."""
    stats = get_scan_stats()
    assert stats == {
        "total_scans": 0,
        "unique_hosts": 0,
        "total_open_ports_found": 0,
    }


def test_get_scan_stats_with_data(seeded_scans_file):
    """Returns correct stats from seeded records."""
    stats = get_scan_stats()
    assert stats["total_scans"] == 2
    assert stats["unique_hosts"] == 2
    assert stats["total_open_ports_found"] == 3  # [22, 80] + [443]
