from unittest.mock import patch, MagicMock

from app.scanner import scan_port, scan_range, grab_banner


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
# grab_banner
# ---------------------------------------------------------------------------

@patch("app.scanner.socket.socket")
def test_grab_banner_returns_first_line(mock_socket_class):
    """grab_banner returns the first line of the received data."""
    sock_instance = MagicMock()
    sock_instance.recv.return_value = b"SSH-2.0-OpenSSH_8.9\r\nProtocol info"
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=sock_instance)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    result = grab_banner("127.0.0.1", 22)
    assert result == "SSH-2.0-OpenSSH_8.9"


@patch("app.scanner.socket.socket")
def test_grab_banner_empty_response(mock_socket_class):
    """grab_banner returns 'unknown' when the service sends no data."""
    sock_instance = MagicMock()
    sock_instance.recv.return_value = b""
    mock_socket_class.return_value.__enter__ = MagicMock(return_value=sock_instance)
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    assert grab_banner("127.0.0.1", 80) == "unknown"


@patch("app.scanner.socket.socket")
def test_grab_banner_socket_error(mock_socket_class):
    """grab_banner returns 'unknown' when a connection error occurs."""
    import socket
    mock_socket_class.return_value.__enter__ = MagicMock(
        side_effect=socket.timeout("timed out")
    )
    mock_socket_class.return_value.__exit__ = MagicMock(return_value=False)

    assert grab_banner("127.0.0.1", 80) == "unknown"


# ---------------------------------------------------------------------------
# scan_range
# ---------------------------------------------------------------------------

@patch("app.scanner.grab_banner", return_value="test-service")
@patch("app.scanner.scan_port")
def test_scan_range_returns_open_ports_sorted(mock_scan_port, mock_grab_banner):
    """scan_range returns open port dicts sorted by port number."""
    def fake_scan(host, port):
        return port in (22, 25)

    mock_scan_port.side_effect = fake_scan

    result = scan_range("10.0.0.1", 20, 25)

    assert result == [
        {"port": 22, "status": "open", "service": "test-service"},
        {"port": 25, "status": "open", "service": "test-service"},
    ]
    assert mock_scan_port.call_count == 6  # ports 20..25
    assert mock_grab_banner.call_count == 2  # only for open ports


@patch("app.scanner.grab_banner")
@patch("app.scanner.scan_port")
def test_scan_range_no_open_ports(mock_scan_port, mock_grab_banner):
    """scan_range returns an empty list when all ports are closed."""
    mock_scan_port.return_value = False

    result = scan_range("10.0.0.1", 100, 105)

    assert result == []
    mock_grab_banner.assert_not_called()


@patch("app.scanner.grab_banner", return_value="nginx")
@patch("app.scanner.scan_port")
def test_scan_range_single_port(mock_scan_port, mock_grab_banner):
    """scan_range works correctly with a single-port range."""
    mock_scan_port.return_value = True

    result = scan_range("10.0.0.1", 443, 443)

    assert result == [{"port": 443, "status": "open", "service": "nginx"}]
    mock_scan_port.assert_called_once_with("10.0.0.1", 443)
    mock_grab_banner.assert_called_once_with("10.0.0.1", 443)
