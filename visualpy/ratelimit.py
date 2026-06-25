"""In-memory per-IP rate limiter with temporary ban for the upload endpoint."""

from __future__ import annotations

import os
import time

from fastapi import Request
from fastapi.responses import JSONResponse


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        import sys
        print(f"[visualpy] Warning: {name}={raw!r} is not a valid integer, using default {default}", file=sys.stderr)
        return default


UPLOAD_LIMIT = _int_env("VISUALPY_RATE_LIMIT", 5)
UPLOAD_WINDOW = _int_env("VISUALPY_RATE_WINDOW", 600)
BAN_THRESHOLD = _int_env("VISUALPY_BAN_THRESHOLD", 15)
BAN_DURATION = _int_env("VISUALPY_BAN_DURATION", 3600)

_requests: dict[str, list[float]] = {}
_banned: dict[str, float] = {}


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def _prune(ip: str, now: float) -> list[float]:
    cutoff = now - UPLOAD_WINDOW
    timestamps = _requests.get(ip, [])
    timestamps = [t for t in timestamps if t > cutoff]
    if timestamps:
        _requests[ip] = timestamps
    else:
        _requests.pop(ip, None)
    return timestamps


def check_rate_limit(request: Request) -> JSONResponse | None:
    ip = _client_ip(request)
    now = time.monotonic()

    ban_expires = _banned.get(ip)
    if ban_expires is not None:
        if now < ban_expires:
            remaining = int(ban_expires - now)
            return JSONResponse(
                {"error": f"Too many requests. Try again in {remaining // 60 + 1} minutes."},
                status_code=429,
            )
        del _banned[ip]

    timestamps = _prune(ip, now)

    if len(timestamps) >= BAN_THRESHOLD:
        _banned[ip] = now + BAN_DURATION
        _requests.pop(ip, None)
        return JSONResponse(
            {"error": f"Too many requests. You are temporarily blocked for {BAN_DURATION // 60} minutes."},
            status_code=429,
        )

    if len(timestamps) >= UPLOAD_LIMIT:
        oldest = min(timestamps)
        retry_in = max(0, int(oldest + UPLOAD_WINDOW - now))
        return JSONResponse(
            {"error": f"Upload limit reached. Try again in {retry_in // 60 + 1} minutes."},
            status_code=429,
        )

    _requests.setdefault(ip, []).append(now)
    return None


def reset() -> None:
    _requests.clear()
    _banned.clear()
