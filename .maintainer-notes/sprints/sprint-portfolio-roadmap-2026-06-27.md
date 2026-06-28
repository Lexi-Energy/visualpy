# Sprint: Portfolio Roadmap (Sprints 0/A/B/C/D)

**Close date:** 2026-06-27
**Tests:** 498 passing (unchanged — no new unit tests added)
**Files changed:** 18 files, +251/-148 lines

## What was delivered

### Sprint 0 — Strategic Documentation
- CLAUDE.md strategic direction section rewritten: North Star / Current State / The Gap / Roadmap. Sprint-by-sprint history preserved below.
- status.md restructured: top 30 lines are scannable current-state summary; sprint history archived below `## History` separator.
- DEFERRED.md cleaned: removed Dockerfile provider lock, frontend foundation (S10 coordination), and `explain_pattern` jargon entries — all addressed by this plan.
- ROADMAP.md was created per plan, then removed at Alex's request — she doesn't want public roadmaps with unconfident wording.

### Sprint A — The Demo Returns
- `visualpy/demo/` — 10 `.py` files copied from `tests/fixtures/agentic_workflows/` (no `webhooks.json`)
- `visualpy/demo_data.py` — lazy-cached `load_demo_project()` calling `build_project(_DEMO_DIR)`
- `GET /demo` route in `server.py` — loads demo project, sets `app.state`, redirects to overview
- "Try the Demo" button on landing page — loads pre-built 10-script project, no upload needed
- `pyproject.toml` package-data updated: includes `demo/*.py`

### Sprint B — The First Moment
- Landing page redesigned: hero headline ("See what Python automations actually do.") + sub + preview SVG + upload zone + "Try the Demo" side by side + trust line
- `aggregate_data_flow()` in `translate.py` — generates one-line-per-script data journey across all scripts, deduplicated
- Overview page: project header is now split layout — left = counts (scripts/services/credentials/entry points), right = aggregated data flow
- Post-upload nudge — dismissible banner with localStorage persistence, guides users to Simple view and export

### Sprint C — The Showcase
- **viewMode three-state fix** — `getViewMode()` and `isBusinessView()` in `mermaid_boot.js`. All direct localStorage reads in JS replaced. Toggle button cycles business → technical → business; presentation mode shows "Exit Presentation" label.
- **Shared `renderMermaidElement`** — extracted to `mermaid_boot.js`. Replaced 3 duplicates in `script_view.js`, `overview_view.js`, and export paths.
- **Presentation mode** — keyboard arrow navigation through phases, Escape to exit, sidebar + nav left side hide in presentation mode, main content gets wider typography. `presentation.js` handles all keyboard interactions.
- **`STEP_TYPE_STYLES`** — canonical source in `models.py` with `tailwind`/`border`/`hex` per step type. `mermaid.py` classDefs built dynamically from it. `script_card.html` and `script_body.html` `step_badge_classes` macro and color legend use the same source.
- **Tech-debt fixes:** `_call_llm` exception logging includes exception type name. `compute_health` import restored in templating.py (was accidentally dropped).
- **LLM default switched** — `DEFAULT_MODEL` from `openrouter/deepseek/deepseek-v4-flash:free` to `groq/llama-3.3-70b-versatile`. Free LLM options documented in README with setup instructions for Groq, Gemini, OpenRouter, Ollama.

### Sprint D — Sovereignty Report
- `SovereigntyReport` dataclass on `AnalyzedProject` — verdict, external_services, local_operations, credentials_used, data_egress_count
- `compute_sovereignty_report()` in new `visualpy/sovereignty.py` — deterministic, aggregates from existing analysis data (services, secrets, steps). Empty project → verdict "local". Project with only file I/O → "local". Any api_call step → "external" or "mixed". Guards against empty-string credential matches.
- `sovereignty.html` partial template — verdict banner (green/amber/red), external services list with credential attribution, local processing list, credential attribution with per-script transmission.
- Included in `overview_body.html` (business view only). Available in JSON export and offline HTML export.
- Wired in `build_project()` — computed after project assembly. Available in `_project_from_dict()` deserialization.

## What was tried and rejected

- **Putting `compute_sovereignty_report` in translate.py** — translate.py is 800+ lines already. Moved to its own module per the project's "small focused modules" convention.
- **ROADMAP.md** — created per plan, deleted at Alex's request. All strategic docs stay internal.
- **QC review agents** — launched `code-reviewer` and `silent-failure-hunter` as per the QC cycle doc. Both used expensive models (Opus hardcoded in agent definitions) and were cancelled. Alex will fix the model override issue herself. Going forward: no agent launches for QC.
- **SVG preview replacement** — the `overview-preview.svg` is a hand-coded placeholder with manual coordinates. It's rough. Alex noted it for a future design sprint.

## Mid-sprint corrections

- ROADMAP.md was created and then removed — Alex doesn't want public roadmaps
- `/demo` route landed at wrong indentation (module level instead of inside `create_app`) — caught by test suite
- `compute_health` import was accidentally dropped from `templating.py` when adding `aggregate_data_flow` — caught by export test
- `data_flow_fallback` was dropped from `register_globals` — caught by export test
- `SovereigntyReport` dataclass was accidentally defined in models.py with `from typing import Literal` out of order — caught by ruff
- `overview_body.html` had leftover lines from old project header after split-layout edit — caught by visual inspection
- Presentation mode sidebar hiding and `export.html` toggle were missed in initial Sprint C — caught by advisory mid-sprint
- `has_file_io`/`has_transform` variables in `sovereignty.py` were scoped per-script (bug) — caught by advisory. Fixed to use set accumulation.
- Empty-string substring match in credential detection — caught by advisory. Added `if k:` guard.

## Verification

498 tests pass. Key acceptance checks:
- `compute_sovereignty_report` on agentic_workflows → verdict "mixed", 8 services, 52 egress calls, 2 credentials attributed
- Sovereignty in JSON export and offline HTML
- Demo loads via `/demo` route
- Export works end-to-end with sovereignty data
