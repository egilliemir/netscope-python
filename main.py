"""
main.py – CLI entry point for Netscope, a concurrent TCP port scanner.

Usage:
    python main.py --host <target> --start <port> --end <port>
    python main.py --stats
"""

import argparse
import sys
import time
from datetime import datetime, timezone

from app.scanner import scan_range
from app.storage import save_scan, get_scan_stats
from app.utils import setup_logger

# Initialize the project-wide logger
logger = setup_logger()


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Netscope – A concurrent TCP port scanner."
    )
    # --stats mode (no scan, just show statistics)
    parser.add_argument("--stats", action="store_true",
                        help="Show scan history statistics and exit")
    # Scan arguments (required only when not using --stats)
    parser.add_argument("--host", help="Target host (IP or hostname)")
    parser.add_argument("--start", type=int, help="Start port (1-65535)")
    parser.add_argument("--end", type=int, help="End port (1-65535)")
    return parser.parse_args()


def validate_ports(start: int, end: int) -> None:
    """Ensure port numbers are within the valid TCP range and ordered correctly."""
    if not (1 <= start <= 65535) or not (1 <= end <= 65535):
        logger.error("Port numbers must be between 1 and 65535.")
        sys.exit(1)
    if start > end:
        logger.error("Start port must be less than or equal to end port.")
        sys.exit(1)


def print_stats() -> None:
    """Print scan history statistics to the terminal."""
    stats = get_scan_stats()
    print("Scan statistics")
    print("---------------")
    print(f"Total scans: {stats['total_scans']}")
    print(f"Unique hosts: {stats['unique_hosts']}")
    print(f"Total open ports found: {stats['total_open_ports_found']}")


def main() -> None:
    args = parse_args()

    # If --stats flag is set, show statistics and exit
    if args.stats:
        print_stats()
        return

    # For scanning mode, host/start/end are required
    if not args.host or args.start is None or args.end is None:
        logger.error("--host, --start, and --end are required for scanning.")
        sys.exit(1)

    validate_ports(args.start, args.end)

    logger.info("Scan started on %s [ports %d-%d]", args.host, args.start, args.end)
    start_time = time.time()

    try:
        results = scan_range(args.host, args.start, args.end)
    except Exception as exc:
        logger.error("Scan failed: %s", exc)
        sys.exit(1)

    elapsed = time.time() - start_time

    # Print a clean user-facing summary
    if results:
        for entry in results:
            print(f"[OPEN] Port {entry['port']}  service: {entry['service']}")
        print(f"\nScan complete: {len(results)} open port(s) found in {elapsed:.2f}s.")
    else:
        print("No open ports found in the given range.")

    # Save the scan record to history
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": args.host,
        "start_port": args.start,
        "end_port": args.end,
        "results": results,
    }
    save_scan(record)
    logger.info("Scan finished: %d open port(s) in %.2fs", len(results), elapsed)


if __name__ == "__main__":
    main()
