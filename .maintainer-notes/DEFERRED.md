# DEFERRED

Known issues not fixed now. Each entry is self-contained: what the issue is, where to find it, and why it was deferred.

---

## Analyzer

### decouple alias patterns not detected

`visualpy/analyzer/ast_parser.py` — `_extract_secrets`

`from decouple import config as cfg` (aliased import) and `import decouple as dc; dc.config(...)` (module alias) are not detected. Secrets accessed via these patterns are silently missed.

Fix: build an alias map during import extraction and consult it in secret detection.

Deferred: rare in real projects. Acceptable tradeoff for simpler implementation.

---

## Templates / Frontend

### Step-by-Step section hides silently if phase grouping fails

`visualpy/templating.py` — `script_render_context`

If `group_steps_by_phase` raises, the fallback is `phase_groups = []`, which makes the
"Step by Step" accordion section disappear from business view with no message — an empty
result is indistinguishable from "this script has no steps."

Deferred (not a regression): this matches the project's documented best-effort error
strategy (log to stderr, degrade rather than crash), and `group_steps_by_phase` is a
deterministic pass over already-parsed steps, so a raise is unlikely. Showing an explicit
"could not group steps" notice is a UX/product-copy decision for a future pass.

---

## Deployment

## Analyzer (cont.)

### Unwired interface params — `source` and `project_root`

`visualpy/analyzer/triggers.py` — `detect_triggers(tree, source)` declares `source` but never reads it.
`visualpy/analyzer/cross_file.py` — `resolve_connections(scripts, project_root)` declares `project_root` but never reads it.

Both are passed by all ~14 call sites. They look like reserved slots for planned features (cron-text detection from the raw source; sub-package import resolution against the project root) but were never wired up — an implementation oversight, not deliberate API design.

Fix: implement the intended use (regex/text cron detection in `triggers`; root-relative module resolution in `cross_file`) rather than removing the params. Next sprint.

### `_check_schedule` over-detects `.do()` as a cron trigger

`visualpy/analyzer/triggers.py` — `_check_schedule`

Any `.do()` method call fires a "cron" trigger, with no guard on the receiver chain. `todo.do()`, `session.do()`, etc. produce false cron triggers.

Fix: require the `schedule.every()...` chain (or a `schedule` import) before treating `.do()` as a scheduler call.

Deferred: heuristic precision issue; low false-positive rate on real automation code. Behavior-preservation needs care (don't lose real `schedule` detections).

### `ast.walk` BFS-order reliance

`visualpy/analyzer/ast_parser.py`

A comment relies on `ast.walk` traversal order, but the stdlib documents `ast.walk` as having no specified order (current behavior is a CPython implementation detail).

Fix: make the dependent logic order-independent, or sort explicitly. Low risk today; flagged so it isn't a silent breakage on a future Python.

---

## Summarizer

### `_call_llm` collapses all failures into a silent `None`

`visualpy/summarizer/llm.py` — `_call_llm`

A broad `except Exception` turns every failure (rate limit, bad key, empty `choices[]`, programmer error) into one silent `None` with a generic warning. Callers can't distinguish transient from fatal.

Fix: narrow to litellm's exception hierarchy (for the pinned version) and surface auth/config failures distinctly from transient ones.

Deferred: needs verification of the litellm exception classes for the pinned version before narrowing.

---

## Packaging

### `static/` is outside the package — non-editable installs break

`pyproject.toml` (no `package-data` / `package` entry for `static/`)

`static/` (CSS, JS, vendored assets) lives outside the `visualpy` package. Editable installs work, but a built/non-editable install ships without it: `serve` loads no CSS and `export` raises a RuntimeError on the first missing asset.

Fix: include `static/` via `package-data` (or move it under the package) and resolve it with `importlib.resources` rather than a filesystem path relative to `__file__`. Its own focused change — touches packaging + asset-path resolution in `server.py` and `export.py`.

---

## Resolved in S9

- **`step_detail.html` Alpine isolation** — step detail is now pre-rendered per view mode (business/technical) into embedded JSON and injected by JS; the live-toggle isolation bug is gone.
- **CDN/SRI dependency** — Tailwind, Mermaid, and Alpine are vendored in `static/vendor/`; the served app and the export both run fully offline, so the CDN subresource-integrity concern no longer applies.

---

