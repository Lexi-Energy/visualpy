"""FastAPI server — serves web UI for visual exploration."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from visualpy.models import AnalyzedProject
from visualpy.templating import (
    project_render_context,
    register_globals,
    script_render_context,
    step_details_json,
)

_PACKAGE_DIR = Path(__file__).parent
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"
_STATIC_DIR = _PACKAGE_DIR.parent / "static"


def create_app(project: AnalyzedProject) -> FastAPI:
    """Build a FastAPI application pre-loaded with analysis results."""
    app = FastAPI(title="visualpy", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
    register_globals(templates.env)

    # Fallback diagrams for error cases.
    app.state.project = project
    app.state.scripts_by_path = {s.path: s for s in project.scripts}

    if _STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    else:
        print(
            f"[visualpy] Warning: static directory not found at {_STATIC_DIR}, "
            "CSS will not load",
            file=sys.stderr,
        )

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception):
        print(f"[visualpy] Error handling {request.url}: {exc}", file=sys.stderr)
        return templates.TemplateResponse(
            request,
            "error.html",
            context={"message": "Something went wrong rendering this page.", "code": 500},
            status_code=500,
        )

    @app.get("/", response_class=HTMLResponse)
    async def overview(request: Request):
        return templates.TemplateResponse(
            request,
            "overview.html",
            context=project_render_context(project),
        )

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    @app.get("/script/{path:path}", response_class=HTMLResponse)
    async def script_view(request: Request, path: str):
        script = app.state.scripts_by_path.get(path)
        if script is None:
            return templates.TemplateResponse(
                request,
                "error.html",
                context={"message": f"Script not found: {path}", "code": 404},
                status_code=404,
            )
        context = script_render_context(script)
        context["project"] = project
        context["step_details_json"] = step_details_json(templates.env, [script])
        return templates.TemplateResponse(request, "script.html", context=context)

    return app
