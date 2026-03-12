# Netscope

A simple CLI TCP port scanner written in Python.

## Features

- Scan a range of TCP ports on any host
- Uses standard-library `socket` - no external dependencies
- Clean, readable output

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
Scanning 127.0.0.1 from port 20 to 80...

[OPEN] Port 22
[OPEN] Port 80

Scan complete: 2 open port(s) found.
```

If no ports are open:

```
Scanning 127.0.0.1 from port 20 to 80...

No open ports found in the given range.
```

## Project Structure

```
netscope-python/
├── app/
│   ├── __init__.py
│   ├── scanner.py      # Core scanning logic
│   ├── services.py
│   ├── storage.py
│   ├── utils.py
│   └── config.py
├── data/
│   └── scans.json
├── tests/
│   └── test_scanner.py
├── logs/
│   └── app.log
├── main.py              # CLI entry point
├── requirements.txt
├── README.md
└── .gitignore
```
