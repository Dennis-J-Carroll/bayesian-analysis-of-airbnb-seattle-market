"""Fixtures that run the real app in a subprocess for the browser tests."""

import subprocess
import sys
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SHARED_PORT = 8765
COLD_PORT = 8766


def _healthy(port: int) -> bool:
    try:
        with urllib.request.urlopen(
            f"http://localhost:{port}/_stcore/health", timeout=2
        ) as resp:
            return resp.read().decode().strip() == "ok"
    except OSError:
        return False


@contextmanager
def running_app(port: int, timeout: float = 60.0):
    """Start `streamlit run app.py` on `port`; always terminate it on exit."""
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + timeout
        while not _healthy(port):
            if proc.poll() is not None:
                raise RuntimeError(f"streamlit exited early ({proc.returncode})")
            if time.monotonic() > deadline:
                raise RuntimeError(f"app not healthy on :{port} after {timeout}s")
            time.sleep(0.5)
        yield f"http://localhost:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture(scope="session")
def app_url():
    with running_app(SHARED_PORT) as url:
        yield url


@pytest.fixture()
def cold_app_url():
    """A freshly started server per test (its own port, never the shared one)."""
    with running_app(COLD_PORT) as url:
        yield url


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            yield b
        finally:
            b.close()
