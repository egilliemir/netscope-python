"""
scanner.py – Core TCP port scanning logic.

Provides functions to check individual ports, grab service banners,
and scan a range of ports concurrently using a thread pool.
"""

import socket
from concurrent.futures import ThreadPoolExecutor

from app.config import DEFAULT_TIMEOUT, BANNER_TIMEOUT, MAX_WORKERS


def scan_port(host: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """
    Test whether a single TCP port is open on the target host.

    Returns True if the port is open, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            # connect_ex returns 0 on success
            return result == 0
    except socket.error:
        return False


def grab_banner(host: str, port: int, timeout: float = BANNER_TIMEOUT) -> str:
    """
    Attempt to read a service banner from an open port.

    Opens a fresh connection and waits briefly for the service to emit an
    identification string (e.g. SSH, SMTP, FTP banners).  Returns the first
    readable line, capped at 128 characters.  Falls back to "unknown" when
    no banner is received or any error occurs.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            # Read up to 1024 bytes; many services emit a banner on connect
            data = sock.recv(1024)
        if data:
            banner = data.decode("utf-8", errors="ignore").strip()
            # Return only the first line, capped at 128 characters
            first_line = banner.splitlines()[0][:128] if banner else ""
            return first_line if first_line else "unknown"
    except Exception:
        pass
    return "unknown"


def scan_range(host: str, start_port: int, end_port: int) -> list[dict]:
    """
    Scan every port in the inclusive range [start_port, end_port]
    concurrently using a thread pool.

    Returns a sorted list of dicts for each open port::

        [{"port": int, "status": "open", "service": str}, ...]
    """
    def check_port(port: int) -> dict | None:
        # First confirm the port is open
        if not scan_port(host, port):
            return None
        # Port is open – try to identify the service via banner grabbing
        service = grab_banner(host, port)
        return {"port": port, "status": "open", "service": service}

    # Use ThreadPoolExecutor to probe many ports at once
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(check_port, range(start_port, end_port + 1))

    # Collect only open-port dicts and sort by port number
    return sorted(
        (r for r in results if r is not None),
        key=lambda r: r["port"],
    )
