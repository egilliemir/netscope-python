from unittest.mock import patch, MagicMock

from app.scanner import scan_port, scan_range


# ---------------------------------------------------------------------------
# scan_port
# ---------------------------------------------------------------------------

@patch("app.scanner.socket.socket")
def test_scan_port_open(mock_socket_class):
    """scan_port returns True when connect_ex returns 0 (port open)."""
    sock_instance = MagicMock()
    sock_instance.connect_ex.return_value = 0
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=sock_instance)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    assert scan_port("127.0.0.1", 80) is True


@patch("app.scanner.socket.socket")
def test_scan_port_closed(mock_socket_class):
    """scan_port returns False when connect_ex returns non-zero (port closed)."""
    sock_instance = MagicMock()
    sock_instance.connect_ex.return_value = 1
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=sock_instance)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    assert scan_port("127.0.0.1", 80) is False


@patch("app.scanner.socket.socket")
def test_scan_port_socket_error(mock_socket_class):
    """scan_port returns False when a socket error is raised."""
    import socket
    mock_socket_class.return_value.__enter__ = MagicMock(
        side_effect=socket.error("Connection refused")
    )
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    assert scan_port("127.0.0.1", 80) is False


# ---------------------------------------------------------------------------
# scan_range
# ---------------------------------------------------------------------------

@patch("app.scanner.scan_port")
def test_scan_range_returns_open_ports_sorted(mock_scan_port):
    """scan_range collects only open ports and returns them sorted."""
    # Simulate ports 20-25: only 22 and 25 are open
    def fake_scan(host, port):
        return port in (22, 25)

    mock_scan_port.side_effect = fake_scan

    result = scan_range("10.0.0.1", 20, 25)

    assert result == [22, 25]
    assert mock_scan_port.call_count == 6  # ports 20..25


@patch("app.scanner.scan_port")
def test_scan_range_no_open_ports(mock_scan_port):
    """scan_range returns an empty list when all ports are closed."""
    mock_scan_port.return_value = False

    result = scan_range("10.0.0.1", 100, 105)

    assert result == []


@patch("app.scanner.scan_port")
def test_scan_range_single_port(mock_scan_port):
    """scan_range works correctly with a single-port range."""
    mock_scan_port.return_value = True

    result = scan_range("10.0.0.1", 443, 443)

    assert result == [443]
    mock_scan_port.assert_called_once_with("10.0.0.1", 443)
