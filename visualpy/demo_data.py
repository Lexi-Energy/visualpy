"""Packaged demo project — loads the agentic_workflows scripts."""

from pathlib import Path

from visualpy.cli import build_project
from visualpy.models import AnalyzedProject

_DEMO_DIR = Path(__file__).parent / "demo"
_cache: AnalyzedProject | None = None


def load_demo_project() -> AnalyzedProject | None:
    global _cache
    if _cache is None:
        _cache = build_project(_DEMO_DIR)
    return _cache