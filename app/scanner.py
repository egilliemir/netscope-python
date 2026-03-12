"""
scanner.py – Core TCP port scanning logic.

Provides functions to check individual ports and scan a range of ports
on a given host using concurrent TCP connect attempts.
"""

import socket
from concurrent.futures import ThreadPoolExecutor

from app.config import DEFAULT_TIMEOUT, MAX_WORKERS


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


def scan_range(host: str, start_port: int, end_port: int) -> list[int]:
    """
    Scan every port in the inclusive range [start_port, end_port]
    concurrently using a thread pool.

    Returns a sorted list of open ports.
    """
    ports = range(start_port, end_port + 1)

    # Use ThreadPoolExecutor to scan many ports at once.
    # Each thread calls scan_port for a single port number.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # submit all scan_port calls and pair each future with its port
        results = executor.map(lambda p: (p, scan_port(host, p)), ports)

    # Collect only the ports that came back as open
    open_ports = sorted(port for port, is_open in results if is_open)
    return open_ports
