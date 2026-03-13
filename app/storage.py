"""
storage.py - Scan result persistence and statistics.

Stores scan records in data/scans.json and provides
functions to load history and compute basic statistics.
"""

import json
import os

from app.config import SCANS_FILE


def load_scans() -> list[dict]:
    """
    Read all scan records from the JSON file.

    Returns an empty list if the file doesn't exist or is empty.
    """
    if not os.path.exists(SCANS_FILE):
        return []

    try:
        with open(SCANS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []


def save_scan(record: dict) -> None:
    """
    Append a scan record to the JSON file.

    Loads the existing list, appends the new record, and writes
    the whole list back so the file always contains valid JSON.
    """
    scans = load_scans()
    scans.append(record)

    # Ensure the data directory exists
    os.makedirs(os.path.dirname(SCANS_FILE), exist_ok=True)

    with open(SCANS_FILE, "w", encoding="utf-8") as f:
        json.dump(scans, f, indent=2)


def get_scan_stats() -> dict:
    """
    Calculate simple statistics from the scan history.

    Returns a dict with:
        - total_scans:  number of scans recorded
        - unique_hosts: number of distinct hosts scanned
        - total_open_ports_found: sum of open ports across all scans
    """
    scans = load_scans()

    unique_hosts = set()
    total_open = 0

    for scan in scans:
        unique_hosts.add(scan.get("host", ""))
        # Support both new format ("results") and legacy format ("open_ports")
        total_open += len(scan.get("results", scan.get("open_ports", [])))

    return {
        "total_scans": len(scans),
        "unique_hosts": len(unique_hosts),
        "total_open_ports_found": total_open,
    }