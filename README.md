# NetScope

> A fast, concurrent TCP port scanner with service banner detection, a REST API, structured scan history, and a full CI/CD pipeline.

[![CI](https://github.com/egilliemir/netscope-python/actions/workflows/tests.yml/badge.svg)](https://github.com/egilliemir/netscope-python/actions/workflows/tests.yml)

---

## Table of Contents

- [Introduction](#introduction)
- [Why This Project](#why-this-project)
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI Scanning](#cli-scanning)
  - [Scan Statistics](#scan-statistics)
  - [FastAPI Server](#fastapi-server)
  - [Swagger Docs](#swagger-docs)
  - [Docker](#docker)
- [API Endpoints](#api-endpoints)
- [Sample Output](#sample-output)
- [Configuration](#configuration)
- [Testing](#testing)
- [CI/CD](#cicd)
- [Roadmap](#roadmap)

---

## Introduction

NetScope is a Python-based network diagnostics tool that scans TCP port ranges on any host, identifies open ports, and attempts to read service banners to determine what is running on each port. It ships with a CLI for local use and a FastAPI REST interface for programmatic or remote access. All scan results are persisted to a JSON file for historical querying and statistics.

---

## Why This Project

Network reconnaissance and port scanning are foundational skills in both security engineering and DevOps. NetScope was built as a clean, well-tested reference implementation to demonstrate:

- Concurrent I/O with `ThreadPoolExecutor`
- FastAPI design patterns with Pydantic validation
- Structured persistence without a database dependency
- Testable architecture with full mock coverage
- Professional CI/CD workflows with GitHub Actions

---

## Features

- **Concurrent TCP scanning** — scans hundreds of ports in parallel using `ThreadPoolExecutor`
- **Service banner grabbing** — attempts to read banners from open ports to identify running services (SSH, HTTP, FTP, etc.)
- **REST API** — FastAPI interface with automatic request validation and interactive Swagger docs
- **Scan history** — every scan is saved to `data/scans.json` with timestamps, host, port range, and results
- **Statistics endpoint** — aggregated totals across all historical scans
- **Dual logging** — logs written to both the console and `logs/app.log`
- **Docker support** — runs as a containerised API service on port 8081
- **Pytest test suite** — unit and integration tests with mocked sockets and coverage reporting on core modules
- **GitHub Actions CI** — automated test runs with pip caching on every push and pull request

---

## Architecture Overview

```
User / Client
     │
     ├── CLI (main.py)
     │       │
     │       └──► scanner.scan_range()
     │                   │
     │                   ├── scan_port()      ← TCP connect probe
     │                   └── grab_banner()    ← Service banner read
     │
     └── HTTP (FastAPI)
             │
             └──► POST /scan ──► scanner.scan_range()
             └──► GET  /stats──► storage.get_scan_stats()

Both paths write results through:
    storage.save_scan() ──► data/scans.json
```

---

## Project Structure

```
netscope-python/
├── .github/
│   └── workflows/
│       └── tests.yml       # GitHub Actions CI pipeline
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI application and endpoints
│   ├── config.py           # Centralised configuration constants
│   ├── scanner.py          # Concurrent TCP scanning and banner grabbing
│   ├── storage.py          # JSON scan persistence and statistics
│   └── utils.py            # Logger setup
├── data/
│   └── scans.json          # Auto-generated scan history
├── logs/
│   └── app.log             # Auto-generated log file
├── tests/
│   ├── conftest.py         # Shared pytest fixtures
│   ├── test_api.py         # FastAPI endpoint tests
│   ├── test_scanner.py     # Scanner and banner unit tests
│   └── test_storage.py     # Storage and statistics tests
├── Dockerfile
├── .dockerignore
├── main.py                 # CLI entry point
├── requirements.txt
└── README.md
```

---

## Installation

**Prerequisites:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/egilliemir/netscope-python.git
cd netscope-python

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### CLI Scanning

Scan a range of TCP ports on any host:

```bash
python main.py --host <target> --start <start_port> --end <end_port>
```

**Example:**

```bash
python main.py --host 127.0.0.1 --start 20 --end 100
```

**Output:**

```
[OPEN] Port 22  service: SSH-2.0-OpenSSH_8.9
[OPEN] Port 80  service: unknown

Scan complete: 2 open port(s) found in 1.42s.
```

If no ports are open:

```
No open ports found in the given range.
```

### Scan Statistics

View aggregated statistics from all historical scans:

```bash
python main.py --stats
```

```
Scan statistics
---------------
Total scans      : 5
Unique hosts     : 2
Total open ports : 9
```

### FastAPI Server

Start the development server:

```bash
python -m uvicorn app.api:app --reload
```

The API is available at `http://127.0.0.1:8000`.

### Swagger Docs

Interactive API documentation is auto-generated by FastAPI and available at:

```
http://127.0.0.1:8000/docs
```

Use the Swagger UI to explore and execute all endpoints directly from your browser without any additional tooling.

### Docker

Build and run the containerised API service:

```bash
# Build the image
docker build -t netscope-python .

# Run the container (API exposed on port 8081)
docker run -p 8081:8081 netscope-python
```

Access the API and docs:

```
http://127.0.0.1:8081
http://127.0.0.1:8081/docs
```

---

## API Endpoints

| Method | Path     | Description                          |
|--------|----------|--------------------------------------|
| `GET`  | `/`      | Health check                         |
| `POST` | `/scan`  | Run a TCP port scan                  |
| `GET`  | `/stats` | Return aggregated scan statistics    |

### `GET /`

```bash
curl http://127.0.0.1:8000/
```

```json
{ "message": "NetScope API is running" }
```

### `POST /scan`

**Request body:**

| Field        | Type    | Required | Description                        |
|--------------|---------|----------|------------------------------------|
| `host`       | string  | yes      | Target IP address or hostname      |
| `start_port` | integer | yes      | First port to scan (1 – 65535)     |
| `end_port`   | integer | yes      | Last port to scan (≥ `start_port`) |

```bash
curl -X POST http://127.0.0.1:8000/scan \
  -H "Content-Type: application/json" \
  -d '{"host": "127.0.0.1", "start_port": 20, "end_port": 100}'
```

**Response:**

```json
{
  "timestamp": "2026-03-13T12:00:01.123456+00:00",
  "host": "127.0.0.1",
  "start_port": 20,
  "end_port": 100,
  "results": [
    { "port": 22, "status": "open", "service": "SSH-2.0-OpenSSH_8.9" },
    { "port": 80, "status": "open", "service": "unknown" }
  ]
}
```

### `GET /stats`

```bash
curl http://127.0.0.1:8000/stats
```

```json
{
  "total_scans": 5,
  "unique_hosts": 2,
  "total_open_ports_found": 9
}
```

---

## Sample Output

**CLI scan with banner grabbing:**

```
2026-03-13 12:00:01 | INFO | Scan started on 192.168.1.1 [ports 1-1024]
[OPEN] Port 22   service: SSH-2.0-OpenSSH_8.9p1
[OPEN] Port 25   service: 220 mail.example.com ESMTP Postfix
[OPEN] Port 80   service: unknown
[OPEN] Port 443  service: unknown

Scan complete: 4 open port(s) found in 2.17s.
2026-03-13 12:00:03 | INFO | Scan finished: 4 open port(s) in 2.17s
```

**Log file (`logs/app.log`):**

```
2026-03-13 12:00:01 | INFO  | Scan started on 192.168.1.1 [ports 1-1024]
2026-03-13 12:00:03 | INFO  | Scan finished: 4 open port(s) in 2.17s
2026-03-13 12:05:00 | ERROR | Port numbers must be between 1 and 65535.
```

---

## Configuration

All defaults are defined in `app/config.py` and can be changed there:

| Constant          | Default           | Description                              |
|-------------------|-------------------|------------------------------------------|
| `DEFAULT_TIMEOUT` | `0.5`             | Socket connect timeout per port (seconds)|
| `BANNER_TIMEOUT`  | `1.0`             | Socket read timeout for banner grabbing  |
| `MAX_WORKERS`     | `100`             | Thread pool size for concurrent scanning |
| `LOG_FILE`        | `logs/app.log`    | Path to the log file                     |
| `SCANS_FILE`      | `data/scans.json` | Path to the scan history file            |

---

## Testing

Run the full test suite:

```bash
python -m pytest -v
```

Run with coverage reporting:

```bash
python -m pytest --cov=app --cov-report=term-missing -v
```

The test suite covers:

- `scan_port` — open, closed, and error cases with mocked sockets
- `grab_banner` — successful banner read, empty response, and timeout
- `scan_range` — open port collection, sorting, and banner integration
- `load_scans` / `save_scan` / `get_scan_stats` — all storage paths using `tmp_path` fixtures
- FastAPI endpoints — `GET /`, `POST /scan`, `GET /stats` with mocked scanner and storage layers

---

## CI/CD

GitHub Actions runs the full test suite automatically on every push and pull request.

Workflow: `.github/workflows/tests.yml`

Steps:
1. Check out the repository
2. Set up Python 3.11
3. Restore pip dependency cache (keyed on `requirements.txt`)
4. Install all dependencies including `pytest-cov`
5. Run `python -m pytest --cov=app --cov-report=term-missing -v`

---

## Roadmap

- [ ] UDP port scanning support
- [ ] OS fingerprinting via TTL analysis
- [ ] Output to CSV and HTML report formats
- [ ] Rate limiting and scan throttling options
- [ ] Authentication layer for the REST API
- [ ] WebSocket endpoint for real-time scan progress
- [ ] `--top-ports` shortcut for the most common 100 ports
