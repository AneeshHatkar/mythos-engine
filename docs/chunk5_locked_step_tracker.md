# Chunk 5 Locked Roadmap Tracker

This file is the source-of-truth tracker for Chunk 5.  
No future Chunk 5 step should be renamed, skipped, replaced, or reordered without updating this tracker.

## Current status rule

- **DONE** means the locked step has a main implementation and tests.
- **PARTIAL** means supporting code exists, but the locked step still needs its official module/tests or final alignment.
- **NOT STARTED** means no dedicated implementation yet.
- **SUPPORTING / EARLY** means the module was added ahead of the locked step and should be reused, not deleted.

---

## Locked Chunk 5 List

| Step | Locked name | Status | Main files / notes |
|---|---|---|---|
| 5.1 | Story Generation Schemas + Chunk 5 Design Contract | DONE | `backend/app/schemas/story_generation.py` |
| 5.2 | Story Intent Interpreter | DONE | `story_intent_interpreter.py` |
| 5.3 | Generation Mode Controller | DONE | `generation_mode_controller.py` |
| 5.4 | Generation Contract Resolver | DONE | `generation_contract_resolver.py` |
| 5.5 | Handoff Package Loader | DONE | `handoff_package_loader.py` |
| 5.6 | Story Context Builder | DONE | `story_context_builder.py` |
| 5.7 | World Detail Injection Engine | DONE | `world_detail_injection_engine.py` |
| 5.8 | Scene Blueprint Engine | DONE | `scene_blueprint_engine.py` |
| 5.9 | Scene Beat Planner | DONE | `scene_beat_planner.py` |
| 5.10 | Dialogue Beat Engine | DONE | `dialogue_beat_engine.py` |
| 5.11 | Character Voice Engine | DONE | `character_voice_engine.py` |
| 5.12 | Emotional Subtext Engine | DONE | `emotional_subtext_engine.py` |
| 5.13 | Relationship Beat Engine | DONE | `relationship_beat_engine.py` |
| 5.14 | Knowledge Boundary Validator | DONE | `knowledge_boundary_validator.py` |
| 5.15 | Causal Continuity Validator | DONE | `causal_continuity_validator.py` |
| 5.16 | Consequence Payoff Engine | DONE | `consequence_payoff_engine.py` |
| 5.17 | Constraint Satisfaction Engine | DONE | `constraint_satisfaction_engine.py` |
| 5.18 | Prose Style Engine | DONE | `prose_style_engine.py` |
| 5.19 | Commercial Story Potential Heuristic | DONE | Implemented as `commercial_appeal_engine.py` |
| 5.20 | Scene Draft Generator | DONE | Implemented as `scene_draft_engine.py` |
| 5.21 | Dialogue Draft Generator | DONE | Implemented as `dialogue_line_generator.py` |
| 5.22 | Prose Draft Assembler | DONE | Implemented as `scene_assembly_engine.py` |
| 5.23 | Chapter Generator | DONE | `chapter_generator.py` |
| 5.24 | Plot Outline Generator | NOT STARTED | Resume here after audit |
| 5.25 | Long-Form Continuation Anchor | DONE / VERIFY | `long_form_continuation_anchor.py` added early |
| 5.26 | Format Adapter Engine | DONE / VERIFY | `format_adapter_engine.py` added early |
| 5.27 | Screenplay / Movie Formatter | NOT STARTED | Needs dedicated formatter |
| 5.28 | Series / Season Formatter | PARTIAL | `series_episode_structure_engine.py` supports this, formatter still needed |
| 5.29 | Game / Interactive Scene Formatter | NOT STARTED | Needs dedicated formatter |
| 5.30 | Multi-World / Multi-Cast Scaling Controller | NOT STARTED | Needs dedicated scaling controller |
| 5.31 | Adaptive Story Pattern Engine | NOT STARTED | Needs adaptive pattern engine |
| 5.32 | Story Quality Scorer | PARTIAL | `scene_quality_gate.py` + `multi_scene_pacing_engine.py` support this |
| 5.33 | Story Anti-Genericity Validator | NOT STARTED | Needs story-level anti-genericity validator |
| 5.34 | Story Continuity Validator | PARTIAL | validators + pacing support this, dedicated story-level validator needed |
| 5.35 | Originality / Copy-Risk Guard | NOT STARTED | Needs copy-risk guard |
| 5.36 | Story Revision Engine | PARTIAL | `chapter_expansion_engine.py` supports this |
| 5.37 | Draft Comparison Engine | NOT STARTED | Needs comparison engine |
| 5.38 | Generation Improvement Loop | PARTIAL | expansion + quality support this, dedicated loop needed |
| 5.39 | Story Provenance Engine | NOT STARTED | Needs provenance engine |
| 5.40 | Generated Scene Delta Extractor | NOT STARTED | Needs delta extractor |
| 5.41 | Story Memory Update Contract | PARTIAL | `long_form_memory_bridge.py` supports this, official contract still needed |
| 5.42 | Story Generation Orchestrator | NOT STARTED | Needs orchestrator |
| 5.43 | Story Generation API Routes | NOT STARTED | Needs API routes |
| 5.44 | Story Export Store | NOT STARTED | Needs export store |
| 5.45 | Story Benchmark Pack | NOT STARTED | Needs benchmark pack |
| 5.46 | Story Smoke Test | NOT STARTED | Needs smoke test |
| 5.47 | Learning Feedback Adapter | NOT STARTED | Needs learning feedback adapter |
| 5.48 | Chunk 1-5 Integration Verifier | PARTIAL | This audit script supports it; final locked verifier still needed |
| 5.49 | README Update + Full Verification | NOT STARTED | Needs README/docs update and final full verification |
| 5.50 | Push to GitHub | NOT STARTED | Final push after verification |

---

## Supporting engines added early

These files are useful and should not be deleted. They must be mapped into locked steps.

| Supporting engine | Purpose | Locked step it supports |
|---|---|---|
| `scene_quality_gate.py` | Scene-level quality checks before chapter flow | 5.32, 5.34 |
| `chapter_expansion_engine.py` | Plans richer chapter expansion | 5.36, 5.38 |
| `multi_scene_pacing_engine.py` | Checks pacing across connected scenes | 5.32, 5.34 |
| `long_form_memory_bridge.py` | Converts chapters into structured memory updates | 5.41 |
| `series_episode_structure_engine.py` | Builds episode act/plot-lane structure | 5.28 |
| `format_adapter_engine.py` | Format-aware writing rules | 5.26, 5.27, 5.28, 5.29 |

---

## Resume point

The next locked step is:

**5.24 — Plot Outline Generator**

Do not jump to memory store, API routes, LLM calls, or final verification until the locked sequence reaches those steps.
