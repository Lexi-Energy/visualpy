"""Tests for the self-contained static HTML export."""

from __future__ import annotations

import json

from visualpy.export import build_static_html
from visualpy.models import AnalyzedProject, AnalyzedScript, ScriptConnection, Service, Step, Trigger


def _project() -> AnalyzedProject:
    a = AnalyzedScript(
        path="fetch_leads.py",
        is_entry_point=True,
        steps=[
            Step(line_number=3, type="api_call", description="requests.get()",
                 function_name="fetch", service=Service(name="HTTP Client", library="requests")),
            Step(line_number=8, type="file_io", description="open('leads.csv', 'w')", outputs=["leads.csv"]),
        ],
        services=[Service(name="HTTP Client", library="requests")],
        secrets=["API_KEY"],
        triggers=[Trigger(type="cli", detail="__main__ guard")],
    )
    b = AnalyzedScript(
        path="clean/transform.py",
        steps=[Step(line_number=2, type="transform", description="sorted()")],
    )
    return AnalyzedProject(
        path="/tmp/demo",
        scripts=[a, b],
        connections=[ScriptConnection(source="fetch_leads.py", target="clean/transform.py",
                                      type="import", detail="a imports b")],
        services=[Service(name="HTTP Client", library="requests")],
        secrets=["API_KEY"],
        entry_points=["fetch_leads.py"],
    )


def test_export_is_single_html_document():
    html = build_static_html(_project())
    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert html.rstrip().endswith("</html>")


def test_export_has_no_external_resource_loads():
    """The whole point: it renders offline. No external script/style loads."""
    import re

    html = build_static_html(_project())
    external = re.findall(r'(?:src|href)="https?://[^"]+"', html)
    assert external == [], f"export should be self-contained, found: {external}"


def test_export_inlines_vendor_assets():
    html = build_static_html(_project())
    assert "tailwind.config" in html
    assert "globalThis[\"mermaid\"]" in html or "mermaid" in html
    assert "Alpine" in html  # alpine bundle inlined


def test_export_embeds_all_script_bodies():
    html = build_static_html(_project())
    start = html.index('<script id="script-bodies" type="application/json">') + len(
        '<script id="script-bodies" type="application/json">'
    )
    end = html.index("</script>", start)
    bodies = json.loads(html[start:end])
    assert set(bodies) == {"fetch_leads.py", "clean/transform.py"}


def test_export_embeds_step_details():
    html = build_static_html(_project())
    start = html.index('<script id="step-details" type="application/json">') + len(
        '<script id="step-details" type="application/json">'
    )
    end = html.index("</script>", start)
    details = json.loads(html[start:end])
    assert "fetch_leads.py::3" in details
    assert set(details["fetch_leads.py::3"]) == {"business", "technical"}


def test_export_uses_same_document_navigation():
    html = build_static_html(_project())
    assert "showScript" in html
    assert "showOverview" in html
    assert "/script/" not in html  # no server-route navigation
    assert "/partials/" not in html  # no HTMX round-trips


def test_export_business_view_has_no_raw_filename_headline():
    """A humanized title travels into the export, not the .py filename."""
    html = build_static_html(_project())
    assert "Fetch Leads" in html
