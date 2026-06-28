"""Shared Jinja2 setup used by both the live server and the static export.

Keeping the global registration and step-detail pre-rendering in one place means
the served UI and the exported HTML file render identical content from one source.
"""

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

from jinja2 import Environment

from visualpy.mermaid import importance_score, pedagogical_flow, project_graph, script_flow
from visualpy.models import AnalyzedProject, AnalyzedScript, STEP_TYPE_STYLES
from visualpy.translate import (
    BUSINESS_LABELS,
    PHASE_LABELS,
    TECHNICAL_LABELS,
    TECHNICAL_LABELS_SHORT,
    compute_health,
    aggregate_data_flow,
    data_flow_fallback,
    deduplicate_steps,
    detect_antipatterns,
    explain_pattern,
    group_steps_by_phase,
    humanize_filename,
    infer_phase,
    translate_connection,
    translate_secret,
    translate_step,
    translate_trigger,
)

TEMPLATES_DIR = Path(__file__).parent / "templates"

_STEP_DETAIL_TEMPLATE = "partials/step_detail.html"


def register_globals(env: Environment) -> None:
    """Register the translation helpers every template relies on."""
    env.globals.update(
        biz_labels=BUSINESS_LABELS,
        tech_labels=TECHNICAL_LABELS,
        tech_labels_short=TECHNICAL_LABELS_SHORT,
        phase_labels=PHASE_LABELS,
        translate_step=translate_step,
        translate_trigger=translate_trigger,
        translate_secret=translate_secret,
        translate_connection=translate_connection,
        humanize_filename=humanize_filename,
        aggregate_data_flow=aggregate_data_flow,
        data_flow_fallback=data_flow_fallback,
        infer_phase=infer_phase,
        group_steps_by_phase=group_steps_by_phase,
        deduplicate_steps=deduplicate_steps,
        explain_pattern=explain_pattern,
        detect_antipatterns=detect_antipatterns,
        compute_health=compute_health,
        step_type_styles=STEP_TYPE_STYLES,
    )


def step_detail_key(path: str, line: int) -> str:
    """Stable key for the embedded step-detail lookup (path + line)."""
    return f"{path}::{line}"


def render_step_details(env: Environment, scripts: list[AnalyzedScript]) -> dict[str, dict[str, str]]:
    """Pre-render every step's detail panel, both business and technical variants.

    The result is embedded in the page so step detail works with no server round-trip
    (and offline in the static export). Keyed by ``path::line``; each value holds the
    rendered HTML for each view mode so the client can swap variants on toggle.
    """
    template = env.get_template(_STEP_DETAIL_TEMPLATE)
    details: dict[str, dict[str, str]] = {}
    for script in scripts:
        contextual = script.contextual_steps or {}
        for step in script.steps:
            key = step_detail_key(script.path, step.line_number)
            ctx = {
                "step": step,
                "script_path": script.path,
                "contextual_desc": contextual.get(step.line_number),
            }
            details[key] = {
                "business": template.render(mode="business", **ctx),
                "technical": template.render(mode="technical", **ctx),
            }
    return details


def step_details_json(env: Environment, scripts: list[AnalyzedScript]) -> str:
    """JSON-encoded step-detail map, safe to embed in a <script> tag.

    `<`, `>`, `&` are unicode-escaped so a step description can never break out
    of the surrounding <script> element.
    """
    return _embed_json(render_step_details(env, scripts))


def _embed_json(obj: object) -> str:
    """JSON-encode and escape angle brackets / ampersands for safe <script> embedding."""
    raw = json.dumps(obj)
    return raw.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


_FLOW_FALLBACK = 'graph TB\n  error["Flow generation failed for this script"]'
_GRAPH_FALLBACK = 'graph LR\n  error["Graph generation failed"]'


def _safe(fn, fallback, label):
    """Call a diagram generator, returning *fallback* (and logging) on failure."""
    try:
        return fn()
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        print(f"[visualpy] Warning: {label}: {exc}", file=sys.stderr)
        return fallback


def script_render_context(script: AnalyzedScript, *, static: bool = False) -> dict:
    """Build the full template context for one script body (server + export share this)."""
    flows = {
        "flow_detailed": _safe(lambda: script_flow(script), _FLOW_FALLBACK, f"detailed flow for {script.path}"),
        "flow_compact": _safe(lambda: script_flow(script, compact=True), _FLOW_FALLBACK, f"compact flow for {script.path}"),
        "flow_detailed_biz": _safe(lambda: script_flow(script, business=True), _FLOW_FALLBACK, f"business flow for {script.path}"),
        "flow_compact_biz": _safe(lambda: script_flow(script, compact=True, business=True), _FLOW_FALLBACK, f"business compact flow for {script.path}"),
    }
    # Business flows fall back to their technical counterparts on error.
    if flows["flow_detailed_biz"] == _FLOW_FALLBACK:
        flows["flow_detailed_biz"] = flows["flow_detailed"]
    if flows["flow_compact_biz"] == _FLOW_FALLBACK:
        flows["flow_compact_biz"] = flows["flow_compact"]

    flow_pedagogical = _safe(lambda: pedagogical_flow(script), _FLOW_FALLBACK, f"pedagogical flow for {script.path}")
    phase_groups = _safe(lambda: group_steps_by_phase(script.steps), [], f"phase grouping for {script.path}")

    total_steps = len(script.steps)
    return {
        "script": script,
        "flow": flows["flow_compact"] if total_steps > 30 else flows["flow_detailed"],
        "flow_pedagogical": flow_pedagogical,
        "phase_groups": phase_groups,
        "phase_summaries": script.phase_summaries or {},
        "contextual_steps": script.contextual_steps or {},
        "phase_risks": script.phase_risks or {},
        "data_flow": script.data_flow,
        "total_steps": total_steps,
        "default_compact": total_steps > 30,
        "static": static,
        **flows,
    }


def project_render_context(project: AnalyzedProject, *, static: bool = False) -> dict:
    """Build the template context for the overview body (server + export share this)."""
    scored = sorted(project.scripts, key=lambda s: importance_score(s, project), reverse=True)
    key_count = max(1, len(scored) // 3)
    key_paths = {s.path for s in scored[:key_count]}
    graph = _safe(lambda: project_graph(project, static=static), _GRAPH_FALLBACK, "project graph")
    graph_biz = _safe(
        lambda: project_graph(project, business=True, static=static),
        graph,
        "business project graph",
    )
    return {
        "project": project,
        "graph": graph,
        "graph_biz": graph_biz,
        "sorted_scripts": scored,
        "key_paths": key_paths,
        "static": static,
    }
