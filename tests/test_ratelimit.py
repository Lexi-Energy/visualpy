"""Tests for the in-memory rate limiter."""

import time
from unittest.mock import patch

import pytest

from visualpy import ratelimit
from visualpy.ratelimit import check_rate_limit, reset


class FakeClient:
    def __init__(self, host):
        self.host = host


class FakeRequest:
    def __init__(self, ip="127.0.0.1", forwarded=None):
        self.client = FakeClient(ip)
        self._headers = {}
        if forwarded:
            self._headers["x-forwarded-for"] = forwarded

    @property
    def headers(self):
        return self._headers


@pytest.fixture(autouse=True)
def _clean():
    reset()
    yield
    reset()


def test_allows_requests_under_limit():
    req = FakeRequest("10.0.0.1")
    for _ in range(5):
        assert check_rate_limit(req) is None


def test_blocks_at_limit():
    req = FakeRequest("10.0.0.2")
    for _ in range(5):
        check_rate_limit(req)
    resp = check_rate_limit(req)
    assert resp is not None
    assert resp.status_code == 429


def test_different_ips_independent():
    for _ in range(5):
        check_rate_limit(FakeRequest("10.0.0.3"))
    assert check_rate_limit(FakeRequest("10.0.0.4")) is None


def test_ban_at_threshold():
    req = FakeRequest("10.0.0.5")
    with patch.object(ratelimit, "UPLOAD_LIMIT", 100):
        for _ in range(15):
            check_rate_limit(req)
        resp = check_rate_limit(req)
    assert resp is not None
    assert resp.status_code == 429
    assert "blocked" in resp.body.decode().lower()


def test_ban_expires():
    req = FakeRequest("10.0.0.6")
    with patch.object(ratelimit, "UPLOAD_LIMIT", 100), \
         patch.object(ratelimit, "BAN_DURATION", 1):
        for _ in range(15):
            check_rate_limit(req)
        check_rate_limit(req)

    time.sleep(1.1)
    assert check_rate_limit(req) is None


def test_x_forwarded_for_uses_rightmost():
    req = FakeRequest("10.0.0.7", forwarded="spoofed.ip, 203.0.113.50")
    for _ in range(5):
        check_rate_limit(req)
    resp = check_rate_limit(req)
    assert resp is not None

    req_spoofed = FakeRequest("10.0.0.7", forwarded="different.spoof, 203.0.113.50")
    assert check_rate_limit(req_spoofed) is not None


def test_reset_clears_state():
    req = FakeRequest("10.0.0.8")
    for _ in range(5):
        check_rate_limit(req)
    reset()
    assert check_rate_limit(req) is None
