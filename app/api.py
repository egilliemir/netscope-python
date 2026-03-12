"""
api.py – FastAPI web interface for Netscope.

Provides REST endpoints to trigger scans and view statistics,
reusing the existing scanner and storage modules.

Run with:
    uvicorn app.api:app --reload
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

from app.scanner import scan_range
from app.storage import save_scan, get_scan_stats

app = FastAPI(title="Netscope API", version="1.0.0")


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    """JSON body accepted by POST /scan."""
    host: str
    start_port: int
    end_port: int

    @field_validator("start_port", "end_port")
    @classmethod
    def port_in_range(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @field_validator("end_port")
    @classmethod
    def end_gte_start(cls, v: int, info) -> int:
        start = info.data.get("start_port")
        if start is not None and v < start:
            raise ValueError("end_port must be >= start_port")
        return v


class ScanResponse(BaseModel):
    """JSON response returned by POST /scan."""
    timestamp: str
    host: str
    start_port: int
    end_port: int
    open_ports: list[int]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    """Health-check endpoint."""
    return {"message": "NetScope API is running"}


@app.post("/scan", response_model=ScanResponse)
def run_scan(request: ScanRequest):
    """Run a TCP port scan and persist the result."""
    open_ports = scan_range(request.host, request.start_port, request.end_port)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": request.host,
        "start_port": request.start_port,
        "end_port": request.end_port,
        "open_ports": open_ports,
    }

    save_scan(record)
    return record


@app.get("/stats")
def stats():
    """Return scan history statistics."""
    return get_scan_stats()
