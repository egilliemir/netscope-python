# Netscope

A concurrent TCP port scanner with both a **CLI** and a **REST API** (FastAPI).

## Features

- Scan a range of TCP ports on any host
- **Concurrent scanning** using `ThreadPoolExecutor` for speed
- **REST API** with FastAPI (`POST /scan`, `GET /stats`)
- **Docker support** for containerized deployment
- **Scan history** saved to `data/scans.json` with `--stats` support
- **Dual logging** to console and `logs/app.log`
- Clean, readable terminal output

## Installation

```bash
pip install -r requirements.txt
```

## CLI Usage

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

## Scan History and Statistics

Every scan result is automatically saved to **`data/scans.json`**.
Each record includes the timestamp, host, port range, and list of open ports.

To view statistics from past scans:

```bash
python main.py --stats
```

Example output:

```
Scan statistics
---------------
Total scans: 5
Unique hosts: 2
Total open ports found: 7
```

## REST API

Install dependencies first:

```bash
pip install -r requirements.txt
```

Start the API server:

```bash
python -m uvicorn app.api:app --reload
```

The API runs at `http://127.0.0.1:8000` by default.
Interactive docs are available at `http://127.0.0.1:8000/docs`.

### Endpoints

| Method | Path     | Description                    |
| ------ | -------- | ------------------------------ |
| GET    | `/`      | Health check                   |
| POST   | `/scan`  | Run a port scan                |
| GET    | `/stats` | View scan history statistics   |

### Example: POST /scan

```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1", "start_port": 20, "end_port": 80}'
```

Response:

```json
{
  "timestamp": "2026-03-12T14:00:01.123456+00:00",
  "host": "127.0.0.1",
  "start_port": 20,
  "end_port": 80,
  "open_ports": [22, 80]
}
```

## Docker

Build the image:

```bash
docker build -t netscope-python .
```

Run the container:

```bash
docker run -p 8081:8081 netscope-python
```

Open the API docs in your browser:

```
http://127.0.0.1:8081/docs
```

## Configuration

Defaults are defined in `app/config.py`:

| Constant          | Default          | Description                        |
| ----------------- | ---------------- | ---------------------------------- |
| `DEFAULT_TIMEOUT` | `0.5`            | Socket timeout per port (seconds)  |
| `MAX_WORKERS`     | `100`            | Thread pool size for scanning      |
| `LOG_FILE`        | `logs/app.log`   | Path to the log file               |
| `SCANS_FILE`      | `data/scans.json`| Path to the scan history file      |

## Project Structure

```
netscope-python/
├── app/
│   ├── __init__.py
│   ├── scanner.py      # Concurrent port scanning logic
│   ├── config.py       # Configuration constants
│   ├── utils.py        # Logger setup
│   ├── storage.py      # Scan persistence & stats
│   ├── api.py          # FastAPI web interface
│   └── services.py
├── data/
│   └── scans.json
├── tests/
│   └── test_scanner.py
├── logs/
│   └── app.log         # Auto-generated log file
├── main.py              # CLI entry point
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
└── .gitignore
```
