from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root():
    """Health-check returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "NetScope API is running"}


# ---------------------------------------------------------------------------
# POST /scan
# ---------------------------------------------------------------------------

@patch("app.api.save_scan")
@patch("app.api.scan_range", return_value=[22, 80])
def test_scan_success(mock_scan_range, mock_save_scan):
    """POST /scan returns open ports and persists the record."""
    payload = {"host": "10.0.0.1", "start_port": 20, "end_port": 80}
    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["host"] == "10.0.0.1"
    assert data["open_ports"] == [22, 80]
    assert "timestamp" in data
    mock_scan_range.assert_called_once_with("10.0.0.1", 20, 80)
    mock_save_scan.assert_called_once()


@patch("app.api.save_scan")
@patch("app.api.scan_range", return_value=[])
def test_scan_no_open_ports(mock_scan_range, mock_save_scan):
    """POST /scan returns an empty list when no ports are open."""
    payload = {"host": "10.0.0.1", "start_port": 100, "end_port": 200}
    response = client.post("/scan", json=payload)

    assert response.status_code == 200
    assert response.json()["open_ports"] == []


def test_scan_invalid_port_range():
    """POST /scan rejects start_port > end_port with 422."""
    payload = {"host": "10.0.0.1", "start_port": 100, "end_port": 50}
    response = client.post("/scan", json=payload)
    assert response.status_code == 422


def test_scan_port_out_of_bounds():
    """POST /scan rejects port numbers outside 1-65535."""
    payload = {"host": "10.0.0.1", "start_port": 0, "end_port": 80}
    response = client.post("/scan", json=payload)
    assert response.status_code == 422


def test_scan_missing_host():
    """POST /scan rejects a request without a host field."""
    payload = {"start_port": 1, "end_port": 100}
    response = client.post("/scan", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /stats
# ---------------------------------------------------------------------------

@patch("app.api.get_scan_stats", return_value={
    "total_scans": 3,
    "unique_hosts": 2,
    "total_open_ports_found": 5,
})
def test_stats(mock_stats):
    """GET /stats returns the expected statistics payload."""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_scans"] == 3
    assert data["unique_hosts"] == 2
    assert data["total_open_ports_found"] == 5
