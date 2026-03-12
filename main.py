"""
main.py – CLI entry point for Netscope, a simple TCP port scanner.

Usage:
    python main.py --host <target> --start <port> --end <port>
"""

import argparse
import sys

from app.scanner import scan_range


def parse_args() -> argparse.Namespace:
    """Parse and validate command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Netscope – A simple TCP port scanner."
    )
    parser.add_argument("--host", required=True, help="Target host (IP or hostname)")
    parser.add_argument("--start", type=int, required=True, help="Start port (1-65535)")
    parser.add_argument("--end", type=int, required=True, help="End port (1-65535)")
    return parser.parse_args()


def validate_ports(start: int, end: int) -> None:
    """Ensure port numbers are within the valid TCP range and ordered correctly."""
    if not (1 <= start <= 65535) or not (1 <= end <= 65535):
        print("Error: Port numbers must be between 1 and 65535.")
        sys.exit(1)
    if start > end:
        print("Error: Start port must be less than or equal to end port.")
        sys.exit(1)


def main() -> None:
    args = parse_args()
    validate_ports(args.start, args.end)

    print(f"Scanning {args.host} from port {args.start} to {args.end}...\n")

    open_ports = scan_range(args.host, args.start, args.end)

    # Print results
    if open_ports:
        for port in open_ports:
            print(f"[OPEN] Port {port}")
        print(f"\nScan complete: {len(open_ports)} open port(s) found.")
    else:
        print("No open ports found in the given range.")


if __name__ == "__main__":
    main()
