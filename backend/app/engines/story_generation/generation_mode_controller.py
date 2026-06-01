from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


class GenerationModeController:
    """Chooses and explains the correct generation mode for a story request.

    The controller keeps Chunk 5 from becoming one giant hardcoded generator.
    It routes requests into the correct downstream pipeline:
    scene, dialogue, chapter, outline, screenplay, episode, season, game,
    rewrite, continuation, comparison, or export.
    """

    engine_name = "story_generation.generation_mode_controller"

    MODE_PIPELINES = {
        GenerationMode.quick_scene: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "scene_blueprint",
            "scene_draft",
            "quality_check",
        ],
        GenerationMode.full_scene: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "scene_blueprint",
            "scene_beats",
            "dialogue_beats",
            "voice_instructions",
            "emotional_subtext",
            "relationship_beats",
            "draft_scene",
            "validate",
            "revise",
            "provenance",
            "memory_update_contract",
        ],
        GenerationMode.dialogue_only: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "dialogue_beats",
            "voice_instructions",
            "knowledge_boundary_check",
            "dialogue_draft",
            "validate_voice",
        ],
        GenerationMode.chapter: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "chapter_plan",
            "scene_sequence",
            "scene_drafts",
            "chapter_assembly",
            "continuity_validation",
            "memory_update_contract",
        ],
        GenerationMode.novel_outline: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "plot_outline",
            "subplot_map",
            "long_form_anchor",
            "continuity_plan",
        ],
        GenerationMode.movie_scene: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "cinematic_scene_blueprint",
            "screenplay_formatter",
            "visual_continuity_check",
        ],
        GenerationMode.screenplay_scene: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "screenplay_scene_blueprint",
            "screenplay_formatter",
            "format_validation",
        ],
        GenerationMode.series_episode: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "episode_plan",
            "a_b_plot_map",
            "act_breaks",
            "episode_formatter",
            "season_continuity_check",
        ],
        GenerationMode.season_outline: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "season_arc_plan",
            "episode_ladder",
            "midseason_turn",
            "finale_payoff",
        ],
        GenerationMode.multi_book_arc: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "saga_scale_plan",
            "book_arc_map",
            "long_form_anchor",
            "open_loop_registry",
            "payoff_plan",
        ],
        GenerationMode.interactive_game_scene: [
            "load_handoff",
            "resolve_contract",
            "build_context",
            "interactive_scene_plan",
            "choice_points",
            "branch_outcomes",
            "simulation_delta_preview",
        ],
        GenerationMode.rewrite_existing: [
            "load_existing_draft",
            "quality_check",
            "anti_genericity_check",
            "continuity_check",
            "rewrite_plan",
            "revised_draft",
            "comparison",
        ],
        GenerationMode.continue_story: [
            "load_previous_memory",
            "load_handoff",
            "resolve_contract",
            "continuation_anchor",
            "next_scene_or_chapter",
            "continuity_validation",
            "memory_update_contract",
        ],
        GenerationMode.compare_drafts: [
            "load_candidate_drafts",
            "quality_score",
            "continuity_score",
            "anti_genericity_score",
            "draft_comparison",
            "select_best",
        ],
        GenerationMode.export_bundle: [
            "load_selected_draft",
            "load_reports",
            "build_export_bundle",
            "write_export_files",
        ],
    }

    MODE_OUTPUTS = {
        GenerationMode.quick_scene: ["SceneDraft"],
        GenerationMode.full_scene: ["SceneDraft", "StoryProvenanceRecord", "StoryMemoryUpdateContract"],
        GenerationMode.dialogue_only: ["DialogueDraft"],
        GenerationMode.chapter: ["ChapterDraft", "StoryMemoryUpdateContract"],
        GenerationMode.novel_outline: ["PlotOutline", "LongFormContinuationAnchor"],
        GenerationMode.movie_scene: ["ScriptDraft"],
        GenerationMode.screenplay_scene: ["ScriptDraft"],
        GenerationMode.series_episode: ["SeriesEpisodeDraft"],
        GenerationMode.season_outline: ["SeasonArcDraft"],
        GenerationMode.multi_book_arc: ["MultiBookArcDraft"],
        GenerationMode.interactive_game_scene: ["InteractiveSceneDraft"],
        GenerationMode.rewrite_existing: ["RewritePlan", "SceneDraft"],
        GenerationMode.continue_story: ["SceneDraft", "ChapterDraft", "StoryMemoryUpdateContract"],
        GenerationMode.compare_drafts: ["DraftComparisonReport"],
        GenerationMode.export_bundle: ["StoryExportBundle"],
    }

    def choose_mode(
        self,
        *,
        intent: StoryIntent,
        available_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        available_context = available_context or {}

        requested_mode = intent.generation_mode
        selected_mode = self._resolve_mode_from_intent(intent=intent, available_context=available_context)

        confidence = self._confidence(intent=intent, selected_mode=selected_mode, requested_mode=requested_mode)
        warnings = self._warnings(intent=intent, selected_mode=selected_mode, available_context=available_context)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "intent_id": intent.intent_id,
            "requested_mode": requested_mode.value,
            "selected_mode": selected_mode.value,
            "selected_format": intent.desired_format.value,
            "confidence": confidence,
            "pipeline": self.MODE_PIPELINES[selected_mode],
            "expected_outputs": self.MODE_OUTPUTS[selected_mode],
            "warnings": warnings,
            "requires_handoff": self._requires_handoff(selected_mode),
            "requires_existing_draft": selected_mode in {
                GenerationMode.rewrite_existing,
                GenerationMode.compare_drafts,
                GenerationMode.export_bundle,
            },
            "requires_memory_anchor": selected_mode in {
                GenerationMode.continue_story,
                GenerationMode.chapter,
                GenerationMode.multi_book_arc,
                GenerationMode.season_outline,
            },
            "large_scale_mode": selected_mode in {
                GenerationMode.season_outline,
                GenerationMode.multi_book_arc,
                GenerationMode.novel_outline,
            } or bool(intent.preferred_character_count and intent.preferred_character_count >= 20),
        }

    def build_mode_plan(
        self,
        *,
        intent: StoryIntent,
        available_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        decision = self.choose_mode(intent=intent, available_context=available_context)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "mode_decision": decision,
            "execution_plan": [
                {
                    "step_index": index + 1,
                    "step_name": step,
                    "purpose": self._step_purpose(step),
                }
                for index, step in enumerate(decision["pipeline"])
            ],
            "handoff_to_next_engine": {
                "next_engine": "story_generation.generation_contract_resolver",
                "payload_keys": [
                    "story_intent",
                    "selected_mode",
                    "selected_format",
                    "pipeline",
                    "expected_outputs",
                ],
            },
        }

    def compare_modes(
        self,
        *,
        intent: StoryIntent,
        candidate_modes: Optional[List[GenerationMode]] = None,
    ) -> Dict[str, Any]:
        candidate_modes = candidate_modes or list(GenerationMode)
        rows = []

        for mode in candidate_modes:
            score = self._mode_fit_score(intent=intent, mode=mode)
            rows.append(
                {
                    "mode": mode.value,
                    "fit_score": score,
                    "expected_outputs": self.MODE_OUTPUTS[mode],
                    "pipeline_length": len(self.MODE_PIPELINES[mode]),
                    "recommended": False,
                }
            )

        rows.sort(key=lambda item: item["fit_score"], reverse=True)
        if rows:
            rows[0]["recommended"] = True

        return {
            "success": True,
            "engine_name": self.engine_name,
            "intent_id": intent.intent_id,
            "ranked_modes": rows,
            "best_mode": rows[0]["mode"] if rows else None,
        }

    def _resolve_mode_from_intent(
        self,
        *,
        intent: StoryIntent,
        available_context: Dict[str, Any],
    ) -> GenerationMode:
        prompt = intent.user_prompt.lower()

        if intent.generation_mode in {
            GenerationMode.rewrite_existing,
            GenerationMode.continue_story,
            GenerationMode.compare_drafts,
            GenerationMode.export_bundle,
        }:
            return intent.generation_mode

        if "dialogue only" in prompt or intent.generation_mode == GenerationMode.dialogue_only:
            return GenerationMode.dialogue_only

        if intent.desired_format == StoryFormat.screenplay:
            return GenerationMode.screenplay_scene

        if intent.desired_format == StoryFormat.movie:
            return GenerationMode.movie_scene

        if intent.desired_format == StoryFormat.series_episode:
            return GenerationMode.series_episode

        if intent.desired_format == StoryFormat.season_outline:
            return GenerationMode.season_outline

        if intent.desired_format == StoryFormat.multi_book_arc:
            return GenerationMode.multi_book_arc

        if intent.desired_format == StoryFormat.game_scene:
            return GenerationMode.interactive_game_scene

        if intent.desired_format == StoryFormat.chapter:
            return GenerationMode.chapter

        if intent.target_length == "very_long" or "thousands of pages" in prompt:
            return GenerationMode.multi_book_arc

        if intent.preferred_character_count and intent.preferred_character_count >= 20:
            return GenerationMode.multi_book_arc

        if intent.desired_format == StoryFormat.novel and intent.generation_mode == GenerationMode.chapter:
            return GenerationMode.chapter

        if intent.desired_format == StoryFormat.novel:
            return GenerationMode.novel_outline if "outline" in prompt else GenerationMode.chapter

        return intent.generation_mode or GenerationMode.full_scene

    def _confidence(
        self,
        *,
        intent: StoryIntent,
        selected_mode: GenerationMode,
        requested_mode: GenerationMode,
    ) -> float:
        score = 0.65

        if selected_mode == requested_mode:
            score += 0.2

        if intent.desired_format:
            score += 0.05

        if intent.genres:
            score += 0.05

        if intent.tone_tags:
            score += 0.05

        if intent.preferred_character_count and intent.preferred_character_count >= 20:
            if selected_mode in {GenerationMode.multi_book_arc, GenerationMode.season_outline, GenerationMode.novel_outline}:
                score += 0.05
            else:
                score -= 0.15

        return round(max(0.0, min(1.0, score)), 3)

    def _warnings(
        self,
        *,
        intent: StoryIntent,
        selected_mode: GenerationMode,
        available_context: Dict[str, Any],
    ) -> List[str]:
        warnings = []

        if selected_mode in {GenerationMode.rewrite_existing, GenerationMode.compare_drafts}:
            if not available_context.get("existing_draft_ids"):
                warnings.append("This mode expects existing draft IDs.")

        if selected_mode == GenerationMode.continue_story:
            if not available_context.get("memory_update_contract_id") and not available_context.get("continuation_anchors"):
                warnings.append("Continuation mode works best with story memory anchors.")

        if selected_mode in {GenerationMode.chapter, GenerationMode.multi_book_arc, GenerationMode.season_outline}:
            warnings.append("Long-form mode should generate through outlines, scenes, validation, and memory updates.")

        if intent.preferred_character_count and intent.preferred_character_count >= 100:
            warnings.append("Huge cast detected; downstream engines must rank, filter, cluster, and select relevant characters.")

        if not intent.genres:
            warnings.append("No genre detected; generation contract may need defaults.")

        return warnings

    def _requires_handoff(self, mode: GenerationMode) -> bool:
        return mode not in {
            GenerationMode.rewrite_existing,
            GenerationMode.compare_drafts,
            GenerationMode.export_bundle,
        }

    def _mode_fit_score(self, *, intent: StoryIntent, mode: GenerationMode) -> float:
        score = 0.1

        format_mode_map = {
            StoryFormat.screenplay: GenerationMode.screenplay_scene,
            StoryFormat.movie: GenerationMode.movie_scene,
            StoryFormat.series_episode: GenerationMode.series_episode,
            StoryFormat.season_outline: GenerationMode.season_outline,
            StoryFormat.multi_book_arc: GenerationMode.multi_book_arc,
            StoryFormat.game_scene: GenerationMode.interactive_game_scene,
            StoryFormat.chapter: GenerationMode.chapter,
            StoryFormat.scene: GenerationMode.full_scene,
        }

        format_specific_mode = format_mode_map.get(intent.desired_format)

        if mode == intent.generation_mode:
            # Default full_scene should not overpower a clearly requested format-specific mode.
            score += 0.25 if format_specific_mode and format_specific_mode != intent.generation_mode else 0.45

        if format_specific_mode == mode:
            score += 0.55

        if intent.target_length == "very_long" and mode == GenerationMode.multi_book_arc:
            score += 0.25

        if intent.preferred_character_count and intent.preferred_character_count >= 20:
            if mode in {GenerationMode.multi_book_arc, GenerationMode.season_outline, GenerationMode.novel_outline}:
                score += 0.2
            else:
                score -= 0.1

        if "dialogue" in intent.user_prompt.lower() and mode == GenerationMode.dialogue_only:
            score += 0.2

        return round(max(0.0, min(1.0, score)), 3)

    def _step_purpose(self, step: str) -> str:
        purposes = {
            "load_handoff": "Load Chunk 4 simulation handoff data.",
            "resolve_contract": "Merge user intent with simulation and format constraints.",
            "build_context": "Create a unified story context package.",
            "scene_blueprint": "Plan the scene before drafting prose.",
            "scene_beats": "Break scene into ordered causally meaningful beats.",
            "dialogue_beats": "Plan subtext-aware dialogue beats.",
            "voice_instructions": "Apply character-specific voice rules.",
            "emotional_subtext": "Translate emotional state into prose/dialogue behavior.",
            "relationship_beats": "Apply relationship pressure and expected movement.",
            "draft_scene": "Generate the scene draft.",
            "validate": "Run continuity, knowledge, format, and quality checks.",
            "revise": "Improve the draft based on validator feedback.",
            "provenance": "Record why and how the draft was generated.",
            "memory_update_contract": "Prepare story-to-simulation feedback candidates.",
            "chapter_plan": "Plan chapter structure and scene sequence.",
            "screenplay_formatter": "Format output as screenplay/script.",
            "season_arc_plan": "Plan long-form episodic structure.",
            "book_arc_map": "Map large story across books.",
            "choice_points": "Create interactive choice points.",
            "export_bundle": "Package selected outputs for export.",
        }

        return purposes.get(step, f"Run pipeline step: {step}.")
