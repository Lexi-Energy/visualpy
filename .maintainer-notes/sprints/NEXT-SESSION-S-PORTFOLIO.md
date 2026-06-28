# Next session — post-portfolio roadmap

**State:** 498 tests, 18 files changed (+251/-148). All 5 sprints delivered.
All core features deterministic; LLM is purely additive enrichment.
Default model: `groq/llama-3.3-70b-versatile`.

## Current board

| What | Status |
|------|--------|
| Demo path (1-click "Try the Demo") | Shipped |
| Landing page redesign | Shipped (placeholder SVG) |
| Presentation mode (keyboard nav) | Shipped |
| viewMode three-state fix | Shipped |
| `STEP_TYPE_STYLES` canonical source | Shipped |
| Sovereignty Report | Shipped (verdict + service/credential attribution) |
| Groq default + free LLM docs | Shipped |
| README LLM docs | Shipped |
| Demo site (visualpy.lexi-energy.com) | Down — needs rebuild |
| SVG preview image | Placeholder — Alex flagged for redesign |
| QC agent model overrides | Alex fixing herself |

## Open questions

- **Screenshot vs real preview.** The `static/img/overview-preview.svg` is a hand-coded placeholder with manual coordinates — text shifts, cards cramped, doesn't scale. Replace with either a real browser screenshot or a server-generated dynamic preview. Alex noted for a future design sprint.
- **Dockerfile generalization.** Currently hardcodes `GEMINI_API_KEY` build arg. Needs to accept `LLM_API_KEY` + `VISUALPY_MODEL` for provider-agnostic builds. Deferred until a working API key is available for the demo site rebuild.
- **Demo site rebuild.** Needs working API key + generalized Dockerfile. Separately from the code work.

## Deferred items

Full list in `.maintainer-notes/DEFERRED.md`. This sprint cleared 3 entries (Dockerfile provider lock, frontend foundation, `explain_pattern` jargon). Key remaining:
- `decouple` alias patterns not detected in AST parser
- `_call_llm` broad except (added exception type logging but narrowing to litellm hierarchy deferred)
- `static/` outside package (non-editable installs break)
- `ast.walk` BFS-order reliance
- `_check_schedule` over-detects `.do()` as cron

## Sprint report

Detail: `.maintainer-notes/sprints/sprint-portfolio-roadmap-2026-06-27.md`.
