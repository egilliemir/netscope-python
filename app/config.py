"""
config.py - Reusable configuration constants for Netscope.

Central place for default values used across the project.
"""

# Socket timeout in seconds for each port connection attempt
DEFAULT_TIMEOUT = 0.5

# Socket timeout in seconds for banner reads (kept short to avoid slowing scans)
BANNER_TIMEOUT = 1.0

# Maximum number of threads for concurrent port scanning
MAX_WORKERS = 100

# Path to the log file
LOG_FILE = "logs/app.log"

# Path to the scan history file
SCANS_FILE = "data/scans.json"