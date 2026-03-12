# Netscope

A concurrent CLI TCP port scanner written in Python (standard library only).

## Features

- Scan a range of TCP ports on any host
- **Concurrent scanning** using `ThreadPoolExecutor` for speed
- **Dual logging** to console and `logs/app.log`
- Uses only the Python standard library — no external dependencies
- Clean, readable terminal output

## Usage

```bash
python main.py --host <target> --start <start_port> --end <end_port>
```

### Example

```bash
python main.py --host 127.0.0.1 --start 20 --end 80
```

### Example Output

```
2026-03-12 14:00:01 | INFO     | Scan started on 127.0.0.1 [ports 20-80]
[OPEN] Port 22
[OPEN] Port 80

Scan complete: 2 open port(s) found in 1.34s.
2026-03-12 14:00:02 | INFO     | Scan finished: 2 open port(s) in 1.34s
```

If no ports are open:

```
2026-03-12 14:00:01 | INFO     | Scan started on 127.0.0.1 [ports 20-80]
No open ports found in the given range.
2026-03-12 14:00:02 | INFO     | Scan finished: 0 open port(s) in 1.18s
```

## Logging

Every scan is logged to **`logs/app.log`** with timestamps, levels, and messages.
The log file is created automatically on first run.

Log format:

```
2026-03-12 14:00:01 | INFO     | Scan started on 127.0.0.1 [ports 20-80]
2026-03-12 14:00:02 | INFO     | Scan finished: 2 open port(s) in 1.34s
2026-03-12 14:05:00 | ERROR    | Port numbers must be between 1 and 65535.
```

## Configuration

Defaults are defined in `app/config.py`:

| Constant          | Default      | Description                        |
| ----------------- | ------------ | ---------------------------------- |
| `DEFAULT_TIMEOUT` | `0.5`        | Socket timeout per port (seconds)  |
| `MAX_WORKERS`     | `100`        | Thread pool size for scanning      |
| `LOG_FILE`        | `logs/app.log` | Path to the log file             |

## Project Structure

```
netscope-python/
├── app/
│   ├── __init__.py
│   ├── scanner.py      # Concurrent port scanning logic
│   ├── config.py       # Configuration constants
│   ├── utils.py        # Logger setup
│   ├── services.py
│   └── storage.py
├── data/
│   └── scans.json
├── tests/
│   └── test_scanner.py
├── logs/
│   └── app.log         # Auto-generated log file
├── main.py              # CLI entry point
├── requirements.txt
├── README.md
└── .gitignore
```
