# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `visualpy export` command — builds a single self-contained HTML file with all assets inlined; opens with no server, no Python, and no internet (works fully offline)
- Deterministic data-journey narrative in business view — a one-sentence "reads from … → processes → writes to …" summary that works without LLM summaries
- Humanized script titles in business view (e.g. `client_intake.py` → "Client Intake")
- Anti-pattern detection — deterministic code quality analysis: print spam, phase imbalance, error handling bulk, missing error handling, heavy transforms
- Health scoring — script cards show colored health badges (clean/minor issues/has issues/needs attention)
- Context-aware pattern insights — `explain_pattern()` gives teaching notes at normal pattern counts and constructive critique at high counts; exception-safe fallback
- Anti-pattern callout cards on script pages with severity-colored icons (red/amber/blue)
- Phase proportion percentage on accordion headers when >40% of total steps
- Credential deduplication in overview business view
- Condition simplification — business view cleans dict access and .get() patterns from if-conditions
- Risk annotations — per-phase "what could go wrong?" warnings piggybacked on existing LLM calls (zero extra cost)
- Data flow narrative — LLM-generated "data journey" callout (e.g., "Reads from Google Sheets → enriches via API → updates sheet")
- Per-phase LLM summaries — contextual 1-2 sentence descriptions for each business phase (Setup, Processing, Storage, etc.)
- Contextual step descriptions — LLM-generated unique descriptions replacing repeated generic phrasing
- Step deduplication — identical business descriptions collapsed into expandable "Description (N locations)" groups
- Phase summaries shown in accordion headers with blue left-border styling
- Step detail panel shows contextual description when available (falls back to deterministic translation)
- Business/Technical view toggle — switch between plain-English and developer views (persisted in localStorage)
- Business-language translation engine — plain-English step descriptions, triggers, secrets, and connection types
- Business-mode Mermaid diagrams — pre-rendered flow variants (detailed/compact × technical/business)
- Translated UI labels: "External Service" not "API Call", "Runs daily at midnight" not "0 0 * * *", "AWS credentials" not "AWS_SECRET_ACCESS_KEY"
- Per-step error isolation in business mode — one bad translation doesn't kill the whole diagram
- Phase inference — steps grouped by business intent (Setup, Processing, Storage, Safety checks, Reporting) instead of function names
- Pedagogical diagram — simple 3-5 phase pipeline replaces large flowcharts in business view
- Progressive disclosure — business view shows summary first, phase accordions, then collapsed technical diagram
- Compact mode for script flow diagrams — long functions collapse to summary nodes
- Importance scoring — overview sorted by connectivity, entry points, and services, with a "key" badge on top scripts
- LLM-generated plain-English summaries via litellm (BYOK — bring your own key); `--summarize` flag on `analyze`, `serve`, and `export`
- Per-script summaries, per-project executive summary, and model override via `VISUALPY_MODEL`
- `--from-json` — reuse a saved analysis (summaries and phase descriptions included) without re-scanning or repeating LLM calls
- Graceful degradation when litellm is not installed or no API key is set
- Dockerfile + docker-compose for public demo deployment (pre-baked LLM summaries)
- README, CONTRIBUTING, CODE_OF_CONDUCT (Contributor Covenant v2.1), and SECURITY policy
- GitHub issue templates, pull request template, and CI pipeline (tests on push and PR)
- CHANGELOG (this file, retroactive)

### Changed

- Plain-English business view — anti-pattern callouts, phase labels ("Getting ready", "Safety checks", …), and trigger descriptions rewritten for non-technical readers; raw variable names and file paths no longer appear in business view
- Frontend assets (Tailwind, Mermaid, Alpine) are now bundled with the package and served locally — the tool works offline, with no CDN dependency

### Removed

- HTMX dependency — step detail is now embedded directly in the page (no server round-trip)

## [0.1.0] - 2026-04-01

### Added

- **Web UI** — `visualpy serve /path` opens browser-based visualization
- Mermaid.js project dependency graph (left-to-right, scripts as nodes)
- Mermaid.js per-script flow diagrams (top-to-bottom, steps grouped by function)
- 6 step type shapes with colors: API call, file I/O, database, decision, output, transform
- Entry point highlighting in project graph
- Click-to-navigate: script node to flow view, step to detail panel
- Dark mode with Tailwind CSS and Alpine.js, persisted in localStorage
- HTMX step detail panel with inputs, outputs, and line numbers
- FastAPI server with app factory pattern and pre-computed project graph
- Script cards with service badges, step counts, entry point indicators
- Services and secrets inventory panels
- Global exception handler with graceful fallback
- Transform detection: comprehensions, 16 builtin transforms, string methods
- Inputs/outputs enrichment from assignments, open() modes, decision conditions
- File I/O false positive fix (serialization methods guarded by module)
- Cross-file structured detection using step inputs/outputs
- Analysis engine: `visualpy analyze /path` outputs structured JSON
- AST-based step detection for 6 step types
- Service mapping for 45+ Python libraries
- Cross-script connection resolution (imports, shared files, common services)
- Trigger detection (cron, webhook, CLI, import)
- Function signature parsing for main() type hints
- CLI with `analyze` and `serve` commands
- 140 tests with ~2.4s runtime
- Repo skeleton with models, fixtures, and dependency configuration

<!-- Links will be added when the first release is tagged -->
<!-- [Unreleased]: https://github.com/alexmavro/visualpy/compare/v0.1.0...HEAD -->
<!-- [0.1.0]: https://github.com/alexmavro/visualpy/releases/tag/v0.1.0 -->
