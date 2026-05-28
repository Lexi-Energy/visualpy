"""Build a single self-contained HTML file from an analysed project.

The output embeds all assets (Tailwind, Mermaid, Alpine, the view JS) and all
analysis data, so it renders fully offline with no server and no Python at view
time. Navigation between the overview and each script is same-document JS.
"""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from visualpy.models import AnalyzedProject
from visualpy.templating import (
    TEMPLATES_DIR,
    _embed_json,
    project_render_context,
    register_globals,
    script_render_context,
    step_details_json,
)

_PACKAGE_DIR = Path(__file__).parent
_STATIC_DIR = _PACKAGE_DIR.parent / "static"
_VENDOR_DIR = _STATIC_DIR / "vendor"


def _read_asset(path: Path) -> str:
    """Read a JS/CSS asset, neutralising any literal ``</script>`` (any case) so it
    can be safely inlined inside a <script> element."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(
            f"visualpy export could not read bundled asset {path.name!r} ({exc}). "
            "Try reinstalling visualpy so its static assets are present."
        ) from exc
    return re.sub(r"</(script)", r"<\\/\1", text, flags=re.IGNORECASE)


def build_static_html(project: AnalyzedProject) -> str:
    """Render the full project to one self-contained, offline HTML document."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    register_globals(env)

    body_template = env.get_template("partials/script_body.html")
    script_bodies: dict[str, str] = {}
    for script in project.scripts:
        ctx = script_render_context(script, static=True)
        ctx["project"] = project
        script_bodies[script.path] = body_template.render(**ctx)

    context = project_render_context(project, static=True)
    context.update(
        project_name=Path(project.path).name or project.path,
        step_details_json=step_details_json(env, project.scripts),
        script_bodies_json=_embed_json(script_bodies),
        tailwind_js=_read_asset(_VENDOR_DIR / "tailwind.js"),
        mermaid_js=_read_asset(_VENDOR_DIR / "mermaid.min.js"),
        alpine_js=_read_asset(_VENDOR_DIR / "alpine.min.js"),
        style_css=_read_asset(_STATIC_DIR / "css" / "style.css"),
        mermaid_boot_js=_read_asset(_STATIC_DIR / "js" / "mermaid_boot.js"),
        script_view_js=_read_asset(_STATIC_DIR / "js" / "script_view.js"),
        overview_view_js=_read_asset(_STATIC_DIR / "js" / "overview_view.js"),
        export_controller_js=_read_asset(_STATIC_DIR / "js" / "export_controller.js"),
    )
    return env.get_template("export.html").render(**context)
