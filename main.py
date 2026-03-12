"""
main.py – CLI entry point for Netscope, a concurrent TCP port scanner.

Usage:
    python main.py --host <target> --start <port> --end <port>
"""

import argparse
import sys
import time

from app.scanner import scan_range
from app.utils import setup_logger

# Initialize the project-wide logger
logger = setup_logger()


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Netscope – A concurrent TCP port scanner."
    )
    parser.add_argument("--host", required=True, help="Target host (IP or hostname)")
    parser.add_argument("--start", type=int, required=True, help="Start port (1-65535)")
    parser.add_argument("--end", type=int, required=True, help="End port (1-65535)")
    return parser.parse_args()


def validate_ports(start: int, end: int) -> None:
    """Ensure port numbers are within the valid TCP range and ordered correctly."""
    if not (1 <= start <= 65535) or not (1 <= end <= 65535):
        logger.error("Port numbers must be between 1 and 65535.")
        sys.exit(1)
    if start > end:
        logger.error("Start port must be less than or equal to end port.")
        sys.exit(1)


def main() -> None:
    args = parse_args()
    validate_ports(args.start, args.end)

    logger.info("Scan started on %s [ports %d-%d]", args.host, args.start, args.end)
    start_time = time.time()

    try:
        open_ports = scan_range(args.host, args.start, args.end)
    except Exception as exc:
        logger.error("Scan failed: %s", exc)
        sys.exit(1)

    elapsed = time.time() - start_time

    # Print a clean user-facing summary
    if open_ports:
        for port in open_ports:
            print(f"[OPEN] Port {port}")
        print(f"\nScan complete: {len(open_ports)} open port(s) found in {elapsed:.2f}s.")
    else:
        print("No open ports found in the given range.")

    logger.info("Scan finished: %d open port(s) in %.2fs", len(open_ports), elapsed)


if __name__ == "__main__":
    main()
