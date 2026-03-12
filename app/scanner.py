"""
scanner.py – Core TCP port scanning logic.

Provides functions to check individual ports and scan a range of ports
on a given host using plain TCP connect attempts (no threads).
"""

import socket


def scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
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
    Scan every port in the inclusive range [start_port, end_port] and
    return a list of ports that are open.
    """
    open_ports: list[int] = []
    for port in range(start_port, end_port + 1):
        if scan_port(host, port):
            open_ports.append(port)
    return open_ports
