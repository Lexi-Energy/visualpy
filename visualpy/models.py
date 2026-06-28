"""Data models for visualpy analysis output."""

from __future__ import annotations


from dataclasses import dataclass, field
from typing import Literal
StepType = Literal["api_call", "file_io", "db_op", "decision", "output", "transform"]

STEP_TYPE_STYLES: dict[str, dict[str, str]] = {
    "api_call":  {"tailwind": "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200",   "border": "border-blue-500",  "hex": "#3B82F6"},
    "file_io":   {"tailwind": "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200", "border": "border-green-600", "hex": "#22C55E"},
    "db_op":     {"tailwind": "bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200","border": "border-purple-500","hex": "#A855F7"},
    "decision":  {"tailwind": "bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200","border": "border-orange-500","hex": "#F97316"},
    "output":    {"tailwind": "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200",     "border": "border-gray-400",  "hex": "#6B7280"},
    "transform": {"tailwind": "bg-teal-100 dark:bg-teal-900 text-teal-800 dark:text-teal-200",     "border": "border-teal-500",  "hex": "#14B8A6"},
}


@dataclass
class Service:
    """An external service detected via imports."""

    name: str  # "Google Sheets"
    library: str  # "gspread"
    icon: str | None = None


@dataclass
class Trigger:
    """How a script gets invoked."""

    type: str  # "cron", "webhook", "cli", "manual", "import"
    detail: str  # "*/5 * * * *" or "POST /webhook/intake"


@dataclass
class Step:
    """A single operation within a script."""

    line_number: int
    type: str  # "api_call", "file_io", "db_op", "transform", "decision", "output"
    description: str  # "Fetches leads from Google Maps API"
    function_name: str | None = None
    service: Service | None = None
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)


@dataclass
class ScriptConnection:
    """A relationship between two scripts in a project."""

    source: str  # script path
    target: str  # script path
    type: str  # "import", "file_io", "subprocess", "trigger"
    detail: str  # "cleanup.py writes clean.csv -> upload.py reads clean.csv"


@dataclass
class AnalyzedScript:
    """Analysis result for a single Python file."""

    path: str  # relative to project root
    is_entry_point: bool = False
    steps: list[Step] = field(default_factory=list)
    imports_internal: list[str] = field(default_factory=list)
    imports_external: list[str] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    triggers: list[Trigger] = field(default_factory=list)
    signature: dict | None = None  # main() type hints
    summary: str | None = None  # LLM-generated plain English
    phase_summaries: dict[str, str] | None = None  # phase_key -> LLM summary
    contextual_steps: dict[int, str] | None = None  # line_number -> LLM description
    phase_risks: dict[str, str] | None = None  # phase_key -> risk annotation
    data_flow: str | None = None  # LLM-generated "data journey" narrative


@dataclass
class AnalyzedProject:
    """Analysis result for an entire project folder."""

    path: str
    scripts: list[AnalyzedScript] = field(default_factory=list)
    connections: list[ScriptConnection] = field(default_factory=list)
    services: list[Service] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    summary: str | None = None  # LLM-generated executive summary
    sovereignty: SovereigntyReport | None = None


@dataclass
class SovereigntyReport:
    """What data leaves the machine, which services receive it, and which credentials are involved."""

    verdict: str  # "local" | "external" | "mixed"
    external_services: list[dict]  # [{"service": "Google Sheets", "scripts": [...], "credential": "GOOGLE_API_KEY"}]
    local_operations: list[str]  # ["File reads/writes", "Local data transforms"]
    credentials_used: list[dict]  # [{"secret": "GOOGLE_API_KEY", "used_by": [...], "transmitted_to": [...]}]
    data_egress_count: int