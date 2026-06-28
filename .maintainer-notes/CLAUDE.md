# visualpy

Auto-visualise Python automations for non-technical stakeholders.
Drop a folder of Python scripts, get a visual breakdown of what they do, how they connect, and what they need. No execution required.

## Quick start

```bash
cd /root/multi/visualpy
source .venv/bin/activate
pip install -e ".[dev]"      # first time only
visualpy --help
visualpy analyze /path/to/folder
visualpy analyze /path/to/folder --summarize  # LLM summaries (needs API key)
visualpy serve /path/to/folder --summarize
visualpy serve                                # upload mode — drag-and-drop in browser
visualpy export /path/to/folder -o out.html   # single self-contained offline HTML file
pytest -m "not slow"         # 498 tests, ~9s
```

### Sprint state (post-Portfolio-Roadmap close, 2026-06-27) — demo, landing, presentation mode, sovereignty report shipped.

498 tests. All core features deterministic. Default model: `groq/llama-3.3-70b-versatile`. Detail: `.maintainer-notes/sprints/sprint-portfolio-roadmap-2026-06-27.md`. Handoff: `.maintainer-notes/sprints/NEXT-SESSION-S-PORTFOLIO.md`.

## Project structure

```
visualpy/
├── README.md               # Badges, personas, quick start, features
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── visualpy/
│   ├── cli.py              # CLI + build_project()
│   ├── models.py           # Core dataclasses + STEP_TYPE_STYLES
│   ├── mermaid.py          # Mermaid syntax generation
│   ├── translate.py        # Business-language translation
│   ├── sovereignty.py      # Sovereignty Report (data egress)
│   ├── templating.py       # Jinja globals + context builders
│   ├── server.py           # FastAPI web UI
│   ├── ratelimit.py        # Per-IP rate limiter
│   ├── export.py           # Offline HTML export
│   ├── demo_data.py        # Packaged demo project
│   ├── demo/               # 10 .py files for demo
│   ├── analyzer/
│   ├── summarizer/
│   └── templates/
│       └── partials/
│           └── sovereignty.html
├── tests/
├── static/
│   ├── js/
│   ├── vendor/
│   └── img/
├── pyproject.toml
├── Dockerfile
├── docker-compose*.yml
└── .maintainer-notes/      # Internal
```

## Tech stack

- **Backend:** FastAPI + uvicorn
- **Analysis:** Python `ast` module (stdlib, zero deps for core analysis)
- **Frontend:** Alpine.js + Mermaid.js, vendored locally in `static/vendor/` (served app + export both work offline; no CDN). Step detail is embedded JSON, not HTMX.
- **LLM summaries:** litellm (optional, BYOK) — `pip install visualpy[llm]`
- **Static export:** `visualpy export` → one self-contained offline HTML file (`export.py` + `templating.py`)
- **Tests:** pytest (498 tests, ~9s)
- **License:** MIT

## Strategic direction

**North Star:** visualpy is a static analysis tool that turns Python automation scripts into visual, business-readable breakdowns. Non-technical stakeholders can see what scripts do, how they connect, and what they need — without reading code or running anything. The tool serves double duty as an OSS portfolio piece and a presentation layer for video content.

**The Gap (pre-sprint state — addressed below):**
- No built-in demo
- Landing page was a bare upload zone with no value proposition
- No presentation mode
- No Sovereignty Report
- LLM default model was tied to an expired Gemini key

All shipped in this sprint. Detail: `.maintainer-notes/sprints/sprint-portfolio-roadmap-2026-06-27.md`.
**Roadmap:**
| Sprint | Name | Value delivered | Status |
|--------|------|-----------------|--------|
| S0 | Strategic Docs | Fresh sessions can onboard without re-deriving the vision | Done |
| A | The Demo Returns | One-click "Try the Demo" | Done |
| B | The First Moment | Landing page sells value before asking for input | Done |
| C | The Showcase | Presentation mode + 3-state viewMode + shared Mermaid render | Done |
| D | The Proof | Sovereignty Report — verifies what data leaves your machine | Done |
## Sprint history

See `docs/PLAN-v1-transparency-layer.md` for original plan + market research + architecture.
Current status in `.maintainer-notes/status.md`. Sprint reports: S1–S8 legacy location deleted; S8.5+ in `.maintainer-notes/sprints/` (gitignored).

Sprint 3 ("The Community") added: README, CONTRIBUTING.md, issue templates (YAML forms), PR template, CI workflow, CHANGELOG, CODE_OF_CONDUCT, SECURITY. Zero Python code changes.

Sprint 4 ("The Voice") added: LLM-generated plain-English summaries via litellm (BYOK). `--summarize` CLI flag for both `analyze` and `serve`. Per-script summaries, project executive summary. Graceful degradation (no key = no summaries, not an error). 32 new tests.

Sprint 5 ("The Scaling Fix") added: Compact mode for flow diagrams (functions >8 steps → summary nodes, 82% reduction on 445-step scripts). Compact/Detailed toggle on script pages. Importance scoring for overview sorting + "key" badges. 20 new tests.

Sprint 5.5 ("The Demo") added: `--from-json` flag for `serve` (load pre-computed analysis), Dockerfile + docker-compose for public demo, live at https://visualpy.lexi-energy.com with pre-baked LLM summaries. 4 new tests.

Sprint 6 ("The Translation") added: Business/Technical view toggle (Alpine.js, localStorage-persisted). New `translate.py` module with deterministic plain-English translations for step descriptions, triggers, secrets, connection types. All templates render dual business/technical text via `x-show`. Mermaid diagrams pre-rendered in 4 variants (detailed/compact x tech/business). Jinja2 globals eliminate 3x duplicated type label dicts. 89 new tests.

Sprint 6.5 ("The Reframe") added: Phase inference (`infer_phase()`) groups steps by business intent (Setup, Processing, Storage, Error Handling, Reporting) instead of function names. Pedagogical diagram (`pedagogical_flow()`) shows 3-5 phase pipeline replacing 50-node flowcharts in business view. Layout restructured: summary → phase pipeline → phase accordions → collapsed tech diagram. Progressive disclosure via `<details>` elements. 43 new tests.

Sprint 7 ("The Teacher") added: Per-phase LLM summaries (1 call per phase, shown in accordion headers). Contextual step descriptions (unique per step, replaces "Handles potential errors" x9). Step deduplication (`deduplicate_steps()`, collapses identical descriptions into expandable groups). Robust JSON parser for LLM responses (handles fences, thinking tokens, partial results). 42 new tests.

Sprint 7.5 ("The Teacher II") added: Pattern insights (`explain_pattern()`, deterministic teaching explanations for dedup groups — zero LLM cost). Risk annotations (per-phase "what could go wrong?" piggybacked on existing LLM calls). Data flow narrative (`summarize_data_flow()`, 1-sentence data journey per script). Exception-safe wrappers on all template-facing functions. Accessibility improvements (role="note", sr-only labels). 46 new tests.

## Analysis pipeline

```
cli.py _build_project(path) → AnalyzedProject
  ├── scanner.scan_project(path)
  │     ├── Walk folder, find .py files (skip __pycache__, .venv, .git, etc.)
  │     └── For each file: ast_parser.analyze_file() → AnalyzedScript
  │           ├── service_map.detect_services() → services
  │           ├── triggers.detect_triggers() → triggers
  │           └── signatures.parse_signature() → main() type hints
  ├── _enrich_io(steps, tree) → populate step.inputs/outputs from assignments + open() modes
  ├── cross_file.resolve_connections(scripts) → connections
  └── Assemble AnalyzedProject

cli.py analyze(path) → JSON output
cli.py serve(path)  → create_app(project) → uvicorn
cli.py serve()      → create_app() → uvicorn (upload mode, no pre-loaded project)

With --summarize:
  cli.py _summarize_project(project) → mutates in place
    ├── For each script: summarizer.summarize_script(script) → script.summary
    ├── For each script: summarizer.summarize_phases(script) → script.phase_summaries, script.contextual_steps, script.phase_risks
    ├── For each script: summarizer.summarize_data_flow(script) → script.data_flow
    └── summarizer.summarize_project(project) → project.summary
    Uses litellm.completion() → model-agnostic (Gemini, OpenAI, Anthropic, etc.)
    Model chain: explicit param → VISUALPY_MODEL env → openrouter/deepseek/deepseek-v4-flash:free
    Phase summarization: 1 LLM call per phase (not per step), JSON structured output
```

## Web UI architecture

```
server.py create_app(project=None) → FastAPI
  ├── If project: pre-loaded mode (overview + script views immediately)
  ├── If no project: upload mode (landing page with drag-and-drop)
  ├── GET /          → project loaded ? overview.html : landing.html
  ├── GET /landing   → landing.html (always available, for re-upload)
  ├── POST /upload   → save .py files to temp dir → build_project() → app.state (rate-limited)
  ├── GET /script/{path} → script.html (redirects to / if no project)
  └── GET /health    → {"status": "ok"}

Static export (no server): `export.py build_static_html(project)` renders `export.html` —
overview + every script body inlined, vendored assets inlined, same-document JS navigation.

mermaid.py (pure functions, no HTTP):
  ├── project_graph() → Mermaid LR graph (scripts as nodes, connections as edges)
  ├── script_flow()   → Mermaid TB graph (steps grouped by function, sequential edges)
  │     └── compact=True → functions >threshold steps collapse to summary nodes
  ├── importance_score() → heuristic ranking (connections + entry + services + steps)
  ├── _compact_function_node() → single summary node for collapsed functions
  ├── _step_node()    → step type → Mermaid shape + classDef
  ├── _sanitize_id()  → safe node IDs
  └── _escape_label() → escape special chars, truncate before escaping
```

translate.py (pure functions, no HTTP):
  ├── BUSINESS_LABELS / TECHNICAL_LABELS  → step type label dicts
  ├── translate_step(step) → plain-English step description from type + service + description
  ├── translate_trigger(trigger) → human-readable trigger (cron → "Runs daily at midnight")
  ├── translate_secret(secret) → grouped credential labels (AWS_* → "AWS credentials")
  ├── translate_connection(conn_type) → business verbs ("import" → "uses")
  ├── deduplicate_steps(steps) → [(description, [steps])] grouped by translate_step() output
  ├── explain_pattern(desc, steps) → teaching insight for dedup groups (exception-safe, context-aware: critiques at high counts)
  ├── detect_antipatterns(script) → list[dict] of code quality findings (exception-safe, deterministic, zero LLM)
  ├── compute_health(script) → {"score", "color", "findings"} health summary (exception-safe)
  ├── infer_phase(step) → business phase from type + description (setup/processing/storage/error_handling/reporting)
  ├── group_steps_by_phase(steps) → [(phase_key, label, steps)] ordered by PHASE_ORDER
  └── PHASE_LABELS / PHASE_ORDER → phase display names and canonical ordering

**Frontend stack (vendored in `static/vendor/`, no build step, works offline):** Tailwind CSS + Alpine.js + Mermaid.js (UMD). No HTMX — step detail is embedded JSON rendered by `static/js/script_view.js`.

**Step type → Mermaid shape:** api_call=rectangle/blue, file_io=parallelogram/green, db_op=cylinder/purple, decision=diamond/orange, output=stadium/gray, transform=subroutine/teal

**Interactivity:** Click script node → navigate to script view (served: `/script/` URL; export: same-document `showScript()`). Click step node → JS looks up embedded step-detail JSON and injects the variant for the current view mode (re-injects on toggle). Dark mode + Business/Technical toggle persisted in localStorage (default: Business). `securityLevel: 'loose'` for Mermaid click callbacks.

**Business view (Sprint 6+6.5):** Completely different layout from technical view. Business shows: summary card → pedagogical phase pipeline (3-5 blocks) → phase-grouped step accordions → services/credentials inline → collapsed tech diagram. Technical view is unchanged grid layout. All controlled via `x-show="viewMode === 'business'"` / `=== 'technical'`. Phase inference (`infer_phase()`) is deterministic, keyword-based, runs at render time (no model changes). `pedagogical_flow()` generates simple Mermaid LR diagram. Step detail is pre-rendered per view mode (business + technical), embedded as JSON, and re-injected live on view-mode toggle. Business view has a separate step detail panel (`step-detail-biz`) from technical view.

**Error handling strategy:** Best-effort with warnings. One bad file never kills the pipeline — unreadable files, syntax errors, permission issues, and oversized files (>10MB) are skipped with warnings to stderr. Symlink loops are detected and avoided.

**Step types:** `api_call`, `file_io`, `db_op`, `transform`, `decision`, `output`

**Transform detection (Sprint 1.5):** Comprehensions (list/dict/set with expression snippets), builtin transforms (`sorted`, `map`, `filter`, `int`, `len`, etc.), string methods (`.split`, `.join`, `.strip`, `.lower`, etc.). Noisy methods removed: `.format()`, `.keys()`, `.values()`, `.items()`, `.update()`, `.pop()`, `.remove()`.

**Inputs/outputs enrichment (Sprint 1.5):** Post-processing pass `_enrich_io()` populates `Step.inputs` and `Step.outputs` from assignment targets, open() file paths (mode-aware: read→inputs, write→outputs, unknown→both), and decision condition variables. Cross-file uses structured step.inputs/outputs for file I/O connections (with description-parsing fallback).

## Steal Like an Artist

All reference repos at `/root/reference-repos/`. Full research in `docs/PLAN-v1-transparency-layer.md` → "What We Steal".

### Patterns adopted (Sprint 1)

| Pattern | Source (license) | Applied to | What we took |
|---------|-----------------|------------|-------------|
| `ast.unparse()` for readable conditions | pyflowchart (MIT) | `ast_parser.py` | Human-readable `if`/`for`/`while` descriptions |
| `ast.NodeVisitor` subclass | staticfg (Apache-2.0) | `ast_parser.py` | `_StepCollector` class structure |
| Call resolution (`Attribute` vs `Name`) | code2flow (MIT) | `ast_parser.py` | `_classify_call()` dispatch pattern |
| Zero-code-change philosophy | VizTracer (Apache-2.0) | everything | No decorators, no config — just point at folder |

### Patterns adopted (Sprint 2)

| Pattern | Source (license) | Applied to | What we took |
|---------|-----------------|------------|-------------|
| Data as JS constant, no runtime API calls | emerge (MIT) | `server.py` | Pre-compute project graph at startup, embed in template |
| Module separation (render/UI/data) | emerge (MIT) | `mermaid.py` + `server.py` + templates | Pure generation vs routing vs display |
| Dark mode via CSS toggle + localStorage | emerge (MIT) | `base.html` | Tailwind `dark:` classes + Alpine.js toggle |
| Function subgraphs (NodesGroup pattern) | pyflowchart (MIT) | `script_flow()` | Steps grouped into Mermaid subgraphs by function_name |
| Direction hints (TB/LR) | pyflowchart (MIT) | `mermaid.py` | Project graph = LR, script flows = TB |
| Three-tier hierarchy | code2flow (MIT) | `project_graph()` | Directory-based subgraph grouping |
| Leaf/trunk entry point styling | code2flow (MIT) | `project_graph()` | `classDef entry` for entry point scripts |
| Click-to-navigate | code2flow (MIT) | `project_graph()` | Click script node → navigate to script view |

### Patterns researched but not yet adopted

- **D3 force layout** (emerge) — charge=-500, link distance=20px, canvas rendering, Louvain clustering. Ready for Cytoscape.js upgrade path (S12+).
- **TransparentNode** (pyflowchart) — invisible connector nodes for empty branches. Not needed with Mermaid's built-in subgraph handling.
- **Subset filtering** (code2flow) — `--target-function + --upstream-depth + --downstream-depth`. Studied in S5 (BFS depth traversal), deferred to S6+.
- **Orphan trimming** (code2flow) — remove nodes with no edges. Partially implemented (overview hides graph for single-script projects).

### Patterns adopted (Sprint 4)

| Pattern | Source (license) | Applied to | What we took |
|---------|-----------------|------------|-------------|
| Objective → Instructions → Expected Output prompts | codebase-digest (MIT) | `summarizer/llm.py` | Prompt structure for script + project summaries |
| Optional dep import inside function body | aider-repomap (Apache-2.0) | `summarizer/llm.py` | litellm imported at call time, not module level |

### Patterns adopted (Sprint 5)

| Pattern | Source (license) | Applied to | What we took |
|---------|-----------------|------------|-------------|
| Simplification toggle | pyflowchart (MIT) | `mermaid.py` | Concept of collapsing nodes to summaries; extended from 1-line if/loop to function-level |
| Importance ranking | aider-repomap (Apache-2.0) | `mermaid.py` + `server.py` | Connectivity-based ranking; simplified from full PageRank to heuristic (0 new deps) |

### Patterns adopted (Sprint 6)

| Pattern | Source (license) | Applied to | What we took |
|---------|-----------------|------------|-------------|
| Simplified view toggle | pyflowchart (MIT) | `translate.py` + templates | Concept of business vs technical views; extended from node-level to full UI toggle |

### S7 "The Teacher" — LLM explanation layer (DONE)

Sprint 7 added contextual LLM explanations to replace generic template phrases.

**Delivered:**
1. **Per-phase LLM summaries** — 1-2 sentence summaries per business phase, shown in accordion headers
2. **Contextual step descriptions** — LLM generates unique descriptions per step (aware of surrounding context)
3. **Step deduplication** — `deduplicate_steps()` collapses identical `translate_step()` output into expandable groups

**Technical:**
- `summarize_phases()` orchestrates one LLM call per phase via `_build_phase_prompt()` + `_parse_phase_response()`
- Partial success: 2 of 3 phases succeed → partial results returned
- JSON parser handles markdown fences, Gemini thinking prefixes, invalid JSON
- `AnalyzedScript.phase_summaries` (dict[str, str]) and `.contextual_steps` (dict[int, str]) — both nullable, backward compatible
- `deduplicate_steps()` in translate.py — groups by `translate_step()` output, preserves first-occurrence order
- Templates: contextual description preferred, falls back to deterministic `translate_step()`
- 42 new tests (370 total)

### S7.5 "The Teacher II" — Teaching moments (DONE)

- `explain_pattern()` in translate.py — deterministic teaching insights for dedup groups (zero LLM cost)
- Risk annotations — per-phase "what could go wrong?" piggybacked on existing phase LLM calls
- `summarize_data_flow()` — 1 LLM call per script for "data journey" narrative
- `AnalyzedScript.phase_risks` (dict[str, str]) and `.data_flow` (str) — both nullable, backward compatible
- Exception-safe: `explain_pattern` wraps inner logic in try/except, `summarize_data_flow` catches prompt-building errors
- 46 new tests (416 total)

### S8 "The Critic" — Anti-pattern detection + UX overhaul (DONE)

- `detect_antipatterns(script)` — deterministic code quality detection (print spam, phase imbalance, error handling bulk, no error handling, transform heavy). Zero LLM cost.
- `compute_health(script)` — aggregates findings into health score (clean/minor/has issues/needs attention) with color coding
- `explain_pattern()` now context-aware — critiques at high counts (>10 prints → "Excessive output", >5 try/except → "Repetitive error handling")
- `_humanize_condition()` — cleans dict access and .get() patterns from business view conditions
- Health badges on overview script cards (colored dot + issue count, business view only)
- Anti-pattern callout cards on script pages (severity-colored: red/amber/blue with icons)
- Phase proportion % on accordion headers when >40%
- Credential dedup in overview business view (PandaDoc 4x → 1x)
- Exception-safe with stderr logging on all template-facing functions
- No model changes — all computed at render time
- 31 new tests (447 total)

### S8.5 "Cleanup + Foundation" — Structural debt, analyzer accuracy, repo hygiene (DONE)

- Alpine `biz: boolean` → `viewMode: string` across all templates — S10 foundation
- File I/O connections directional (writer→reader); sub-package imports; dotted-import service attribution; decouple secrets
- `_SKIP_DIRS` → `visualpy/analyzer/_constants.py`; `collect_local_modules` with `os.walk(followlinks=False)`
- Dict-of-variants loop in `server.py`; Mermaid `<br/>` → `\n`
- Standalone `docker-compose.yml`; prod config gitignored; demo redeployed
- Fixture data scrub (third-party names); `pyrightconfig.json`; Pyright fixes
- .maintainer-notes/DEFERRED.md created (3 items + Gemini key)
- 8 new tests (455 total)
- Detail: `.maintainer-notes/sprints/sprint8.5-cleanup-foundation-2026-05-06.md`

### S9.5 "The Upload" — drag-and-drop folder upload + rate limiter (DONE)

- `visualpy serve` (no args) → landing page with drag-and-drop zone. `POST /upload` → temp dir → `build_project()` → app.state.
- `visualpy/ratelimit.py` — per-IP rate limiter (5/10min, ban at 15). Config via `VISUALPY_RATE_*` env vars.
- `build_project()` extracted from `cli._build_project()` as shared function (server + CLI).
- Default model: `openrouter/deepseek/deepseek-v4-flash:free`. `VISUALPY_MODEL` override still works.
- Double-render bug fixed: `overview_body.html` tech graph `class="mermaid"` → `class="mermaid-deferred"`.
- Internal docs moved to `.maintainer-notes/` (gitignored).
- QC hardening: X-Forwarded-For rightmost IP, narrowed except to `OSError`, tracebacks in error handlers, JS `.catch()` on upload promises.
- 17 new tests (498 total).
- Detail: `.maintainer-notes/sprints/sprint9.5-the-upload-2026-06-25.md`

### S9 "The Share + Literacy" — offline static export + non-dev business view (DONE)

- `visualpy export <path> -o out.html` → one self-contained, fully offline HTML file (overview + all scripts, same-document JS nav). `export.py` + `export.html`.
- HTMX removed: step detail pre-rendered (business + technical) into embedded JSON; served app + export share one rendering path via `templating.py` and `static/js/*.js`.
- Assets vendored to `static/vendor/` (Tailwind, Mermaid UMD, Alpine) — served app offline too.
- Mia literacy fixes: humanized titles, deterministic `data_flow_fallback()`, jargon-free callouts, renamed phase labels, no raw identifiers in business view.
- Resolved + removed two DEFERRED items (step_detail Alpine isolation; CDN SRI). 478 tests.
- Detail: `.maintainer-notes/sprints/sprint9-the-share-and-literacy-2026-05-28.md`

### Patterns to steal — by upcoming sprint

See "Strategic direction" section above for full sprint detail. Reference repos (all at `/root/reference-repos/`):

| Sprint | Reference | What to study |
|--------|-----------|---------------|
| **S9 (Share + Literacy)** | emerge (MIT) | `emerge/output/html/emerge.html` — 500-line self-contained pattern |
| S9 | codebase-digest | File hashing for summary cache invalidation |
| **S9.5 (The Proof)** | — | Original — no direct reference. LangFuse trace UI for accountability framing inspiration only |
| **S10 (The Presenter)** | Reveal.js patterns | Keyboard nav, fullscreen, presentation-mode HTML conventions |
| **S11 (Intelligence)** | emerge (MIT) | `emerge/output/export.py` — TF-IDF impl |
| **S12 (Platform)** | emerge / aider-repomap / LangFuse | D3 force layout, tree-sitter multi-language, annotation UI |

### Key files to study per sprint

**Sprint 2 (The Face) — already researched:**
- `emerge/output/html/emerge.html` — self-contained HTML template (500 lines)
- `emerge/resources/js/emerge_main.js` — D3 force sim setup, state, menu (1002 lines)
- `emerge/resources/js/emerge_graph.js` — canvas rendering, node/edge styling (533 lines)
- `emerge/output/export.py` — Python → JS data export (530 lines)
- `pyflowchart/node.py` — TransparentNode, NodesGroup, connection model
- `pyflowchart/ast_node.py` — Try/except structure, simplification toggles
- `code2flow/model.py` — Group/Node/Edge hierarchy, to_dot() output
- `code2flow/engine.py` — map_it() pipeline, subset filtering, orphan trimming

**Sprint 4 (The Voice) — already researched:**
- `codebase-digest/prompt_library/` — 70 prompt templates, Objective → Instructions → Expected Output structure
- `codebase-digest/codebase_digest/app.py` — token counting with tiktoken, file consolidation
- `aider-repomap/aider/repomap.py` — binary search token budgeting, PageRank, tree-sitter
- `aider-repomap/aider/special.py` — important file detection patterns

### Reference repos by sprint

- **S1 (Engine):** pyflowchart, code2flow, staticfg, pydeps — DONE
- **S2 (Face):** emerge (HTML/D3), pyflowchart (node hierarchy), code2flow (graph org), Mermaid.js (CDN) — DONE
- **S3 (Community):** chonkie (YAML issue forms, CONTRIBUTING tone), aider (CONTRIBUTING completeness), pyan (badges, modern FOSS practices) — DONE
- **S4 (Voice):** codebase-digest (prompt structure), aider-repomap (optional dep import pattern) — DONE
- **S5 (Scaling Fix):** pyflowchart (simplify toggle), aider-repomap (PageRank), code2flow (subset filtering, studied), pyan (depth control, studied) — DONE
- **S6 (Translation):** pyflowchart (simplified view toggle) — DONE
- **S9 (Export):** emerge (self-contained HTML), codebase-digest (file hashing)
- **S11 (Intelligence):** emerge (TF-IDF keyword extraction)
- **S12 (Platform):** emerge (D3 force layout), aider-repomap (tree-sitter), LangFuse (three-view paradigm)

## Gotchas

- **PyPI name conflict** — `visualpy` is taken on PyPI (unrelated package). Need a different name for distribution, or contact the owner. README quick start uses `git clone` + `pip install -e .` for now.
- `python-multipart` in pyproject.toml is unused — FastAPI needs it for Form/UploadFile but we don't use those. Remove when convenient.
- System Python is externally managed — always activate `.venv` first
- Reference repos at `/root/reference-repos/` — pyan is GPL-2.0, study patterns only, never copy code
- Test fixtures: `tests/fixtures/hello.py` (unit), `tests/fixtures/agentic_workflows/` (integration, 10 real scripts)
- `db_op` steps guarded by `_DB_OBJECTS` set to avoid false positives on common methods like `.add()`, `.find()`
- `file_io` serialization methods (`.dump`, `.load`) guarded by `_FILE_IO_MODULES`; pathlib methods (`.read_text`) always file_io
- `_TRANSFORM_METHODS` trimmed for noise — no `.format()`, `.keys()`, `.values()`, `.items()`, `.update()`, `.pop()`, `.remove()`
- `_looks_like_file_path` requires actual file extension (not just any dot) to prevent false cross-file connections
- Mermaid node IDs: `_sanitize_id()` replaces non-alphanumeric with `_`, prepends `n_` — must be unique
- Mermaid labels: `_escape_label()` truncates BEFORE escaping to prevent split escape sequences
- Starlette 1.0 `TemplateResponse` API: `(request, name, context={...})` — NOT the old `(name, {"request": request, ...})` form
- `securityLevel: 'loose'` required for Mermaid `click ... call` callbacks
- `static/` directory is outside the package — works with editable install but needs `package_data` for built packages
- Server tests use `@pytest.mark.anyio` + `AsyncClient` with `ASGITransport` — no live server needed
- `litellm.suppress_debug_info = True` required before calls — litellm prints to stdout otherwise, polluting JSON output
- `max_tokens=2048` (not 200) — Gemini 2.5 Flash uses thinking tokens that count against max_tokens; 200 left only ~8 text tokens
- LLM response `content` can be `None` (Gemini thinking, safety filters) — always check before `.strip()`
- `VISUALPY_MODEL` env var overrides default model (`openrouter/deepseek/deepseek-v4-flash:free`); litellm reads provider-specific keys automatically
- Do NOT set temperature < 1.0 for Gemini 3 models — causes infinite loops (litellm defaults to 1.0, keep it)
- Step detail: `step_detail.html` renders by a `mode` param (business|technical), not Alpine `x-show`. `templating.render_step_details()` pre-renders both variants per step into JSON embedded in the page (`step-details` script tag, keyed `path::line`). `static/js/script_view.js` `showStepDetail()` injects the variant for the current view mode and re-injects on toggle (the old isolation bug is gone). No `/partials/step` route, no HTMX.
- Offline assets: `static/vendor/` holds Tailwind (Play CDN JIT script), Mermaid UMD (`mermaid.min.js`, sets `globalThis.mermaid` — UMD chosen over ESM so it inlines as one file), Alpine. `base.html` loads them from `/static/vendor`; `export.py` inlines them. Re-fetch/update via the `jsdelivr`/`cdn.tailwindcss.com` URLs in the S9 report.
- Static export: one script body is injected into `#view-script` at a time (so fixed diagram IDs never collide); `showScript()`/`showOverview()` in `static/js/export_controller.js`. `mermaid.project_graph(static=True)` emits `call showScript(...)` instead of `/script/` URLs.
- Mermaid diagrams in business mode: server pre-renders variants via dict-of-variants loop in `server.py`. If business flow fails, falls back to technical flow (not error placeholder). Per-step isolation in `_step_node()` catches translate errors for individual steps.
- Alpine view-mode state: `viewMode: string` (`'business'` | `'technical'` | `'presentation'`), NOT `biz: boolean`. localStorage key is `viewMode`. `'presentation'` is valid but unused until S10.
- `collect_local_modules()` (ast_parser.py) uses `os.walk(followlinks=False)` — symlink-safe. `_SKIP_DIRS` is a single source of truth in `visualpy/analyzer/_constants.py`, imported by both scanner and ast_parser.
- `from google.cloud import storage` pattern: `_extract_imports` emits `"google.cloud.storage"` (only for dotted modules — `"." in node.module` guard prevents `os.path` noise). `_match_service` matches via suffix `svc.library.endswith(f".{obj_name}")`.
- File I/O connections are directional: `_extract_file_paths` returns `(reads, writes)`; `_find_file_io_connections` emits writer→reader only. Fallback (description parsing) is reads-only — `open()` no-mode defaults to read.
- Default model: `groq/llama-3.3-70b-versatile`. Set `GROQ_API_KEY` env var at runtime for LLM summaries. `VISUALPY_MODEL` overrides the model. No API keys baked into the Docker image — summaries are computed at runtime or skip gracefully.
- `docker-compose.yml` is standalone (port 8123, no external network). Production runs `docker-compose.prod.yml` (gitignored, caddy_net). Rebuild: `docker-compose -f docker-compose.prod.yml up --build -d` from repo root.

## Conventions

- Python 3.12+, pyproject.toml, pytest
- `pytest -m "not slow"` before any push
- CLAUDE.md and .maintainer-notes/status.md are always gitignored
- No AI attribution in commits
- Author: `alexmavro` / `258596309+alexmavro@users.noreply.github.com`

## Notes

- Sprint reports S1–S8: legacy `/root/multi/visualpy_notes/` deleted (not recoverable)
- Sprint reports S8.5+: `<repo>/.maintainer-notes/sprints/` (gitignored, per memory rule)
Latest sprint report: `.maintainer-notes/sprints/sprint-portfolio-roadmap-2026-06-27.md`
Next session handoff: `.maintainer-notes/sprints/NEXT-SESSION-S-PORTFOLIO.md` (superseded handoffs in `.maintainer-notes/sprints/archive/`)
- Screenshots: `.maintainer-notes/sprints/screenshots/` (8 PNGs — overview, dark mode, script views, step detail)
- .maintainer-notes/status.md + CLAUDE.md + .maintainer-notes/DEFERRED.md are gitignored
- Remote: https://github.com/alexmavro/visualpy
- Demo: https://visualpy.lexi-energy.com (Docker on caddy_net, pre-baked summaries)
