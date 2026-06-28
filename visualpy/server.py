"""FastAPI server — serves web UI for visual exploration."""

from __future__ import annotations

import shutil
import sys
import tempfile
import traceback
from pathlib import Path, PurePosixPath

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from visualpy.cli import build_project
from visualpy.models import AnalyzedProject
from visualpy.ratelimit import check_rate_limit
from visualpy.templating import (
    project_render_context,
    register_globals,
    script_render_context,
    step_details_json,
)

_PACKAGE_DIR = Path(__file__).parent
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"
_STATIC_DIR = _PACKAGE_DIR.parent / "static"

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_TOTAL_SIZE = 100 * 1024 * 1024
MAX_FILE_COUNT = 500


def _set_project(app: FastAPI, project: AnalyzedProject, tmp_dir: Path | None = None) -> None:
    old_tmp = getattr(app.state, "upload_tmp", None)
    if old_tmp and Path(old_tmp).exists():
        shutil.rmtree(old_tmp, ignore_errors=True)
    app.state.project = project
    app.state.scripts_by_path = {s.path: s for s in project.scripts}
    app.state.upload_tmp = str(tmp_dir) if tmp_dir else None


def create_app(project: AnalyzedProject | None = None) -> FastAPI:
    app = FastAPI(title="visualpy", docs_url=None, redoc_url=None)
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
    register_globals(templates.env)

    app.state.project = None
    app.state.scripts_by_path = {}
    app.state.upload_tmp = None

    if project is not None:
        _set_project(app, project)

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
        print(
            f"[visualpy] Unhandled {type(exc).__name__} at {request.url}: {exc}\n"
            + traceback.format_exc(),
            file=sys.stderr,
        )
        return templates.TemplateResponse(
            request,
            "error.html",
            context={"message": "Something went wrong rendering this page.", "code": 500},
            status_code=500,
        )

    @app.get("/", response_class=HTMLResponse)
    async def overview(request: Request):
        if app.state.project is None:
            return templates.TemplateResponse(request, "landing.html", context={})
        return templates.TemplateResponse(
            request,
            "overview.html",
            context=project_render_context(app.state.project, static=False),
        )

    @app.get("/landing", response_class=HTMLResponse)
    async def landing(request: Request):
        return templates.TemplateResponse(request, "landing.html", context={})

    @app.get("/demo")
    async def load_demo(request: Request):
        from visualpy.demo_data import load_demo_project
        project = load_demo_project()
        if project is None:
            return templates.TemplateResponse(
                request, "error.html", context={"code": 500, "message": "Demo data could not be loaded."}
            )
        _set_project(app, project)
        return RedirectResponse(url="/")

    @app.get("/health")
    async def health():
        return JSONResponse({"status": "ok"})

    @app.post("/upload")
    async def upload(request: Request, files: list[UploadFile] = File(default=[])):
        rate_resp = check_rate_limit(request)
        if rate_resp is not None:
            return rate_resp

        if not files:
            return JSONResponse({"error": "No files received."}, status_code=400)
        if len(files) > MAX_FILE_COUNT:
            return JSONResponse(
                {"error": f"Too many files (max {MAX_FILE_COUNT})."},
                status_code=400,
            )

        tmp_dir = Path(tempfile.mkdtemp(prefix="visualpy_"))
        total_size = 0
        saved = 0

        try:
            for upload_file in files:
                filename = upload_file.filename or ""
                if not filename.endswith(".py"):
                    continue

                rel = PurePosixPath(filename)
                if ".." in rel.parts or rel.is_absolute():
                    continue

                content = await upload_file.read()
                if len(content) > MAX_FILE_SIZE:
                    continue
                total_size += len(content)
                if total_size > MAX_TOTAL_SIZE:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
                    return JSONResponse(
                        {"error": f"Total upload too large (max {MAX_TOTAL_SIZE // (1024*1024)}MB)."},
                        status_code=400,
                    )

                dest = tmp_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(content)
                saved += 1
        except OSError as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print(f"[visualpy] Upload I/O error ({type(exc).__name__}): {exc}", file=sys.stderr)
            return JSONResponse({"error": "Failed to save uploaded files."}, status_code=500)

        if saved == 0:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return JSONResponse({"error": "No Python files found in the upload."}, status_code=400)

        try:
            new_project = build_project(tmp_dir)
            if new_project is None:
                shutil.rmtree(tmp_dir, ignore_errors=True)
                return JSONResponse({"error": "No Python files could be analyzed."}, status_code=400)
            _set_project(app, new_project, tmp_dir)
        except Exception as exc:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            print(
                f"[visualpy] Analysis error ({type(exc).__name__}): {exc}\n"
                + traceback.format_exc(),
                file=sys.stderr,
            )
            return JSONResponse({"error": "Analysis failed. Check the server logs."}, status_code=500)

        return JSONResponse({"success": True, "scripts": len(new_project.scripts)})

    @app.get("/script/{path:path}", response_class=HTMLResponse)
    async def script_view(request: Request, path: str):
        if app.state.project is None:
            return RedirectResponse("/")
        script = app.state.scripts_by_path.get(path)
        if script is None:
            return templates.TemplateResponse(
                request,
                "error.html",
                context={"message": f"Script not found: {path}", "code": 404},
                status_code=404,
            )
        context = script_render_context(script, static=False)
        context["project"] = app.state.project
        context["step_details_json"] = step_details_json(templates.env, [script])
        return templates.TemplateResponse(request, "script.html", context=context)

    return app
