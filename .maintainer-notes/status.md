---
## Current state

**498 tests** passing. Sprint state: post-S9.5 close (2026-06-25).

| What | Status |
|------|--------|
| CLI analyze / serve / export | Stable |
| Drag-and-drop folder upload | Shipped |
| Offline static export | Shipped |
| Business/Technical view toggle | Shipped |
| Mermaid project graphs + script flows | Shipped |
| Phase inference + pedagogical diagrams | Shipped |
| Anti-pattern detection + health scoring | Shipped |
| LLM summaries (BYOK, opt-in) | Shipped — default: DeepSeek V4 Flash |
| Rate limiter on upload endpoint | Shipped |
| **Demo** (try without uploading) | Sprint A |
| **Landing page value proposition** | Sprint B |
| **Presentation mode** (YouTube recording) | Sprint C |
| **Sovereignty Report** | Sprint D |
| Demo site (visualpy.lexi-energy.com) | Down — needs rebuild |

### Known issues
- Flow diagram scaling: compact mode helps large scripts but no zoom/pan controls
- UI language: mostly solved via Business/Technical toggle + LLM phase summaries
- See `.maintainer-notes/DEFERRED.md` for full deferred list

## History

## What Sprint 8 delivered

- **Anti-pattern detection** — `detect_antipatterns(script)` detects 5 code quality issues: print spam (>3 print() without logging), phase imbalance (>50%), error handling bulk (>5 try/except), no error handling (>10 steps, API/IO present), transform heavy (>15 identical transforms). Zero LLM cost.
- **Health scoring** — `compute_health(script)` aggregates findings into score: clean (green), minor issues (yellow), has issues (amber), needs attention (red). Shown as colored badges on overview cards.
- **Context-aware critiques** — `explain_pattern()` now shifts from praise to critique at high counts: >10 "Displays message" → "Excessive output — N print() calls; consider logging"; >5 "Handles potential errors" → "Repetitive error handling — extract a shared helper"
- **Business view condition cleanup** — `_humanize_condition()` transforms dict access and .get() patterns: `item['matched'] and (not item.get('needs_review'))` → `item matched and not item needs review`
- **Anti-pattern callouts on script page** — severity-colored cards (red/amber/blue) with icons between Data Journey and Step by Step
- **Phase proportion %** — accordion headers show amber percentage when phase has >40% of steps
- **Credential dedup** — overview business view deduplicates translated labels (PandaDoc 4x → 1x); technical view unchanged
- **Exception-safe with logging** — all template-facing functions log to stderr on failure instead of silent swallow
- **31 new tests** (447 total) — anti-pattern detection (14), health scoring (5), context-aware explain_pattern (5), condition simplification (3), server rendering (5), modified 2 existing tests

## What Sprint 7.5 delivered

- **Pattern insights** — `explain_pattern()` generates deterministic teaching explanations for dedup groups (e.g., 20x print → "Status logging — tracks workflow progress across 20 checkpoints")
- **Risk annotations** — per-phase "what could go wrong?" warnings piggybacked on existing phase LLM calls (zero extra cost); shown as amber callout
- **Data flow narrative** — `summarize_data_flow()` generates 1-sentence "data journey" per script (e.g., "Reads leads from Google Sheets → enriches via AnyMailFinder → updates sheet")
- **Exception safety** — `explain_pattern()` wrapped in try/except (never crashes template), `summarize_data_flow` catches prompt-building errors
- **Accessibility** — risk annotations have `role="note"` + sr-only "Risk:" prefix for screen readers
- **Model changes** — `AnalyzedScript.phase_risks` (dict[str, str]) and `.data_flow` (str) — both nullable, backward compatible
- **46 new tests** (416 total) — pattern insights (17), risk parsing/integration (10), data flow prompt/integration (8), server rendering (5), CLI roundtrip (4), review-driven edge cases (2)

## What Sprint 7 delivered

- **Per-phase LLM summaries** — `summarize_phases()` orchestrates one LLM call per phase, returns structured JSON with phase summary + per-step descriptions
- **Contextual step descriptions** — LLM generates unique descriptions aware of surrounding context; replaces generic "Handles potential errors" x9
- **Step deduplication** — `deduplicate_steps()` in translate.py groups identical `translate_step()` output; template renders "Description (N locations)" with expandable list
- **Robust JSON parser** — `_parse_phase_response()` handles markdown fences, Gemini thinking prefixes, truncated JSON, unknown line numbers
- **Partial success** — if 2 of 3 phases succeed, returns partial results (not all-or-nothing)
- **Model changes** — `AnalyzedScript.phase_summaries` (dict[str, str]) and `.contextual_steps` (dict[int, str]) — both nullable, backward compatible
- **CLI integration** — phase summarization in `_summarize_project()`, JSON roundtrip with int key conversion in `_project_from_dict()`
- **Template integration** — phase summaries in accordion headers (blue left border), contextual descriptions preferred over deterministic, deduplication with expandable groups
- **42 new tests** (370 total) — prompt building, JSON parsing, deduplication, server rendering, CLI roundtrip

## What Sprint 2 delivered

- **Mermaid generation engine** (`mermaid.py`) — pure functions for project graphs (LR) and script flows (TB)
- **6 step type shapes** — api_call (rectangle/blue), file_io (parallelogram/green), db_op (cylinder/purple), decision (diamond/orange), output (stadium/gray), transform (subroutine/teal)
- **FastAPI server** (`server.py`) — app factory with pre-computed project graph, Jinja2 templates, HTMX step detail fragments
- **Project overview** — dependency graph, script cards, services/secrets inventory panels
- **Per-script flow view** — steps grouped by function (NodesGroup pattern from pyflowchart), sequential edges within functions, click-to-detail via HTMX (HTMX replaced in S9 — step detail is now embedded JSON)
- **Dark mode** — Tailwind `dark:` classes + Alpine.js toggle persisted in localStorage
- **CLI `serve` command** — analyze once at startup, uvicorn with error handling
- **Entry point highlighting** — green border on entry point scripts in project graph
- **Click navigation** — click script node → navigate to script view, click step → show detail panel
- **Error handling** — global exception handler, graceful project graph fallback, styled 404 fragments, port-in-use friendly message

## What Sprint 1.5 delivered

- **Transform detection** — list/dict/set comprehensions (with expression snippets), 16 builtin transforms (`sorted`, `map`, `filter`, `int`, `len`, etc.), string methods (`.split`, `.join`, `.strip`, `.lower`, etc.)
- **Inputs/outputs enrichment** — `_enrich_io()` post-processing populates `Step.inputs`/`Step.outputs` from assignments, open() modes, decision conditions
- **file_io false positive fix** — split into `_SERIALIZATION_METHODS` (module-guarded) + `_PATHLIB_IO_METHODS` (always file_io)
- **Cross-file structured detection** — uses step.inputs/outputs instead of brittle description parsing
- **Noise reduction** — removed `.format()`, `.keys()`, `.values()`, `.items()`, `.update()`, `.pop()`, `.remove()` from transform methods
- **`_looks_like_file_path`** — tightened to require actual file extension

## Known issues (future sprint)

- **Flow diagram scaling (partially solved)** — Sprint 5 compact mode reduces 445-step scripts by 82%. Still no zoom/pan controls or collapsible subgraphs for the detailed view. Subset filtering (click function → show only its context) deferred to S6+.
- **UI language (mostly solved)** — Sprint 6 added Business/Technical toggle. Sprint 7 added LLM per-phase summaries and contextual step descriptions. Remaining: "what does this do?" per function group, interactive Q&A.

## What Sprint 3 delivered

- **README rewrite** — badges, "Who is this for?" personas, quick start, features, roadmap, acknowledgments
- **CONTRIBUTING.md** — non-dev-friendly guide with first-person section headers ("I found something broken", "I have an idea", "I have a question")
- **Issue templates** — 3 YAML form templates (bug report, feature request, question) with warm descriptions and minimal required fields
- **PR template** — what/how-to-test fields, checklist, hidden welcome comment for first-timers
- **GitHub Actions CI** — tests on push to main and PRs (ubuntu-latest, Python 3.12)
- **CHANGELOG.md** — retroactive Keep a Changelog format for Sprints 0–2
- **CODE_OF_CONDUCT.md** — Contributor Covenant v2.1
- **SECURITY.md** — responsible disclosure policy, threat surface documentation

## What Sprint 4 delivered

- **LLM summarizer engine** (`summarizer/llm.py`) — prompt builders + litellm wrapper with graceful degradation
- **Per-script summaries** — structured AST data (steps, services, triggers) fed to LLM, returns 1-2 sentence plain-English description
- **Per-project executive summary** — aggregates script summaries + connections into 2-3 sentence overview
- **`--summarize` CLI flag** — opt-in for both `analyze` and `serve` commands
- **BYOK model support** — default `gemini/gemini-2.5-flash`, override via `VISUALPY_MODEL` env var
- **Template integration** — summaries render in overview header, script cards, and script headers (all with `{% if %}` guards)
- **Graceful degradation** — no litellm → warning, no API key → warning per call, LLM failure → None, empty content → None
- **`litellm.suppress_debug_info`** — prevents litellm stdout pollution in JSON output
- **32 new tests** — prompt building (deterministic), graceful degradation (mocked), CLI flag, template rendering
- **Patterns stolen** — prompt structure from codebase-digest (MIT), optional dep import from aider-repomap (Apache-2.0)

## What Sprint 5 delivered

- **Compact mode** — functions with >8 steps collapse to single summary node showing step type breakdown (82% line reduction on 445-step scripts, 67% on 114-step scripts)
- **Compact/Detailed toggle** — button on script pages with >30 steps, defaults to compact for large scripts
- **Importance scoring** — scripts sorted by connectivity heuristic (connections + entry point + services + step count), top ~30% get "key" badge
- **20 new tests** — compact mode (10), importance scoring (5), server/UI (5)
- **Patterns stolen** — simplification toggle from pyflowchart (MIT), importance ranking concept from aider-repomap (Apache-2.0)

## What Sprint 5.5 delivered

- **`--from-json` CLI flag** — `visualpy serve --from-json analysis.json` loads pre-computed analysis (no API key at runtime)
- **`_project_from_dict()`** — deserializes `dataclasses.asdict()` output back into full model hierarchy
- **Dockerfile** — python:3.12-slim, editable install, pre-bakes LLM summaries at build time via `GEMINI_API_KEY` build arg
- **docker-compose.yml** — caddy_net external network (same pattern as all other sites)
- **Public demo** — live at https://visualpy.lexi-energy.com with pre-baked summaries on agentic_workflows fixture
- **4 new tests** — roundtrip deserialization, CLI roundtrip, missing file error, requires path/json validation

## What Sprint 6 delivered

- **`translate.py`** — deterministic translation engine: step descriptions, triggers, secrets, connection types → plain English. Zero LLM cost, zero new dependencies.
- **Business/Technical view toggle** — Alpine.js `biz` state in `base.html`, localStorage-persisted, default Business
- **Dual rendering** — all templates use `x-show="biz"` / `x-show="!biz"` for every user-visible label
- **4-way Mermaid flows** — server pre-renders detailed/compact × tech/business; JS `_getFlowSourceId()` selects correct variant
- **Business translations** — "API Call" → "External Service", "File I/O" → "Read/Write File", `0 0 * * *` → "Runs daily at midnight", `AWS_SECRET_ACCESS_KEY` → "AWS credentials"
- **Jinja2 globals** — `biz_labels`, `tech_labels`, `translate_step()`, `translate_trigger()`, `translate_secret()` eliminate 3× duplicated type label dicts
- **Error isolation** — per-step try/except in `_step_node()` for business mode; business flow falls back to technical on error; tracebacks logged
- **89 new tests** — translate.py (77), mermaid business mode (7), server business mode (5)
- **Patterns stolen** — simplified view toggle concept from pyflowchart (MIT)

## Roadmap

| Sprint | Name | Focus | Key patterns to steal |
|--------|------|-------|----------------------|
| **8.5** | Cleanup + Foundation | DONE — structural debt, analyzer accuracy, repo hygiene | — |
| **9** | The Share + Literacy | DONE — offline static export + non-dev literacy fixes | emerge, codebase-digest |
| **9.5** | The Proof | Digital Sovereignty Report — accountability pitch made visual | — |
| **10** | The Presenter | Fullscreen presentation mode — YouTube recording UX | Reveal.js |
| **11** | The Intelligence | TF-IDF keywords (no LLM), print-friendly view | emerge |
| **12** | The Platform | Annotations, HITL, diff view, Cytoscape.js upgrade, multi-language | emerge, aider-repomap, LangFuse |

**TODO:** Audit acknowledgments section — review which reference repos actually shaped the code vs. which were just studied. Decide who to feature in README before public launch.
