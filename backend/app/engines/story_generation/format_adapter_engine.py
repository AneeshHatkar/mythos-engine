from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    FormatAdaptationPlan,
    GeneratedChapter,
    GenerationContract,
    LongFormContinuationAnchor,
    PlotOutline,
    StoryFormat,
)


class FormatAdapterEngine:
    """Builds format-specific adaptation plans.

    This prevents the same story plan from being written in one generic style.
    The adapter tells later generators how to write differently for novels,
    chapters, screenplays, movies, series episodes, game scenes, and long arcs.
    """

    engine_name = "story_generation.format_adapter_engine"

    FORMAT_PRESETS: Dict[str, Dict[str, Any]] = {
        "scene": {
            "structure_rules": {
                "unit_type": "single_scene",
                "requires_opening_image": True,
                "requires_scene_turn": True,
                "requires_ending_hook": True,
            },
            "prose_rules": {
                "internality": "moderate",
                "paragraph_density": "balanced",
                "sensory_detail": "medium",
                "description_style": "scene-specific",
            },
            "dialogue_rules": {
                "dialogue_density": "balanced",
                "speaker_tags": "prose",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "setup_pressure_choice_consequence_hook",
                "act_breaks": 0,
                "cliffhanger_required": False,
            },
            "continuity_rules": {
                "must_preserve_open_loops": True,
                "must_track_scene_delta": True,
            },
            "required_sections": ["opening image", "pressure beat", "choice/consequence", "hook"],
            "forbidden_patterns": ["episode act cards", "camera-only prose", "choice menu only"],
        },
        "novel": {
            "structure_rules": {
                "unit_type": "novel_prose",
                "requires_chapter_arc": True,
                "requires_interiority": True,
                "requires_scene_sequence": True,
            },
            "prose_rules": {
                "internality": "high",
                "paragraph_density": "rich",
                "sensory_detail": "high",
                "description_style": "literary-concrete",
            },
            "dialogue_rules": {
                "dialogue_density": "moderate",
                "speaker_tags": "novelistic",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "emotional-escalation-with-reflection",
                "act_breaks": 0,
                "cliffhanger_required": False,
            },
            "continuity_rules": {
                "must_preserve_character_memory": True,
                "must_preserve_world_rules": True,
                "must_track_chapter_delta": True,
            },
            "required_sections": ["chapter opening", "interior conflict", "external pressure", "chapter turn"],
            "forbidden_patterns": ["screenplay camera directions", "flat summary-only prose", "game UI choices"],
        },
        "chapter": {
            "structure_rules": {
                "unit_type": "chapter",
                "requires_scene_sequence": True,
                "requires_chapter_turn": True,
                "requires_next_chapter_hook": True,
            },
            "prose_rules": {
                "internality": "medium_high",
                "paragraph_density": "varied",
                "sensory_detail": "medium_high",
                "description_style": "chapter-driven",
            },
            "dialogue_rules": {
                "dialogue_density": "balanced",
                "speaker_tags": "prose",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "multi-scene escalation",
                "act_breaks": 0,
                "cliffhanger_required": True,
            },
            "continuity_rules": {
                "must_preserve_open_loops": True,
                "must_update_chapter_memory": True,
            },
            "required_sections": ["chapter title", "scene sequence", "chapter consequence", "next hook"],
            "forbidden_patterns": ["screenplay-only formatting", "disconnected scenes"],
        },
        "screenplay": {
            "structure_rules": {
                "unit_type": "screenplay_scene",
                "requires_scene_heading": True,
                "requires_action_lines": True,
                "requires_dialogue_blocks": True,
            },
            "prose_rules": {
                "internality": "none",
                "paragraph_density": "short_action_lines",
                "sensory_detail": "visual_only",
                "description_style": "performable",
            },
            "dialogue_rules": {
                "dialogue_density": "high",
                "speaker_tags": "screenplay",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "visual-beat-dialogue-turn",
                "act_breaks": 0,
                "cliffhanger_required": False,
            },
            "continuity_rules": {
                "must_preserve_scene_objective": True,
                "must_preserve_visible_action": True,
            },
            "required_sections": ["scene heading", "action", "dialogue", "transition/hook"],
            "forbidden_patterns": ["internal monologue", "novelistic exposition", "unfilmable feelings"],
        },
        "movie": {
            "structure_rules": {
                "unit_type": "film_sequence",
                "requires_visual_sequence": True,
                "requires_set_piece_or_turn": True,
                "requires_performable_action": True,
            },
            "prose_rules": {
                "internality": "none",
                "paragraph_density": "cinematic_blocks",
                "sensory_detail": "visual_and_sound",
                "description_style": "cinematic",
            },
            "dialogue_rules": {
                "dialogue_density": "medium_high",
                "speaker_tags": "screenplay_like",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "sequence-escalation-payoff",
                "act_breaks": 3,
                "cliffhanger_required": False,
            },
            "continuity_rules": {
                "must_preserve_visual_motifs": True,
                "must_preserve_major_payoffs": True,
            },
            "required_sections": ["sequence purpose", "visual escalation", "turn", "payoff/hook"],
            "forbidden_patterns": ["deep internal narration", "unfilmable exposition"],
        },
        "game_scene": {
            "structure_rules": {
                "unit_type": "interactive_scene",
                "requires_player_choice": True,
                "requires_branching_outcomes": True,
                "requires_state_change": True,
            },
            "prose_rules": {
                "internality": "low_to_medium",
                "paragraph_density": "interactive_blocks",
                "sensory_detail": "actionable",
                "description_style": "player-facing",
            },
            "dialogue_rules": {
                "dialogue_density": "choice_aware",
                "speaker_tags": "npc_dialogue",
                "subtext_required": True,
            },
            "pacing_rules": {
                "shape": "setup-choice-consequence-state-update",
                "act_breaks": 0,
                "cliffhanger_required": False,
            },
            "continuity_rules": {
                "must_preserve_player_agency": True,
                "must_emit_state_delta": True,
                "must_track_branch_consequence": True,
            },
            "required_sections": ["scene setup", "NPC exchange", "choice options", "state delta"],
            "forbidden_patterns": ["single fixed outcome only", "passive prose-only chapter"],
        },
        "multi_book_arc": {
            "structure_rules": {
                "unit_type": "series_arc",
                "requires_book_level_arcs": True,
                "requires_foreshadowing_registry": True,
                "requires_payoff_registry": True,
            },
            "prose_rules": {
                "internality": "summary_plus_key_samples",
                "paragraph_density": "outline_blocks",
                "sensory_detail": "selective",
                "description_style": "arc-level",
            },
            "dialogue_rules": {
                "dialogue_density": "sample_only",
                "speaker_tags": "minimal",
                "subtext_required": False,
            },
            "pacing_rules": {
                "shape": "book-by-book-escalation",
                "act_breaks": "per_book",
                "cliffhanger_required": True,
            },
            "continuity_rules": {
                "must_preserve_series_memory": True,
                "must_track_long_payoffs": True,
                "must_track_character_evolution": True,
            },
            "required_sections": ["series premise", "book arcs", "character evolution", "long payoffs"],
            "forbidden_patterns": ["single-scene-only output", "untracked foreshadowing"],
        },
    }

    def build_format_adaptation_plan(
        self,
        *,
        target_format: StoryFormat | str,
        source_id: str,
        generation_contract: GenerationContract | None = None,
        chapter: GeneratedChapter | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        plot_outline: PlotOutline | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}
        format_key = target_format.value if isinstance(target_format, StoryFormat) else str(target_format)

        preset = self.FORMAT_PRESETS.get(format_key, self.FORMAT_PRESETS["scene"])

        plan = FormatAdaptationPlan(
            adaptation_plan_id=f"format_plan_{source_id}_{format_key}",
            source_id=source_id,
            target_format=format_key,
            structure_rules=self._structure_rules(
                preset=preset,
                generation_contract=generation_contract,
                chapter=chapter,
                continuation_anchor=continuation_anchor,
            ),
            prose_rules=self._prose_rules(preset=preset, generation_contract=generation_contract),
            dialogue_rules=self._dialogue_rules(preset=preset, generation_contract=generation_contract),
            pacing_rules=self._pacing_rules(preset=preset, chapter=chapter, continuation_anchor=continuation_anchor),
            continuity_rules=self._continuity_rules(
                preset=preset,
                chapter=chapter,
                continuation_anchor=continuation_anchor,
                plot_outline=plot_outline,
                story_context=story_context,
            ),
            required_sections=list(preset["required_sections"]),
            forbidden_patterns=list(preset["forbidden_patterns"]),
            adaptation_notes=self._adaptation_notes(
                format_key=format_key,
                chapter=chapter,
                continuation_anchor=continuation_anchor,
            ),
            warnings=self._warnings(format_key=format_key, generation_contract=generation_contract, chapter=chapter),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "format_adaptation_plan": plan,
            "format_adaptation_plan_dict": plan.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.episode_structure_engine",
                "payload_keys": [
                    "format_adaptation_plan",
                    "generated_chapter",
                    "continuation_anchor",
                    "plot_outline",
                    "generation_contract",
                    "story_context",
                ],
            },
        }

    def adapt_text_skeleton(
        self,
        *,
        plan: FormatAdaptationPlan,
        source_text: str,
    ) -> Dict[str, Any]:
        if plan.target_format == "screenplay":
            adapted = self._screenplay_skeleton(plan=plan, source_text=source_text)
        elif plan.target_format == "game_scene":
            adapted = self._game_scene_skeleton(plan=plan, source_text=source_text)
        elif plan.target_format == "movie":
            adapted = self._movie_skeleton(plan=plan, source_text=source_text)
        elif plan.target_format == "multi_book_arc":
            adapted = self._multi_book_skeleton(plan=plan, source_text=source_text)
        elif plan.target_format in {"novel", "chapter"}:
            adapted = self._novel_chapter_skeleton(plan=plan, source_text=source_text)
        else:
            adapted = self._scene_skeleton(plan=plan, source_text=source_text)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "adapted_text_skeleton": adapted,
        }

    def validate_format_plan(self, *, plan: FormatAdaptationPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not plan.adaptation_plan_id:
            blockers.append("adaptation_plan_id missing")
        else:
            passed.append("adaptation_plan_id_present")

        if plan.target_format:
            passed.append("target_format_present")
        else:
            blockers.append("target format missing")

        if plan.structure_rules:
            passed.append("structure_rules_present")
        else:
            blockers.append("structure rules missing")

        if plan.prose_rules:
            passed.append("prose_rules_present")
        else:
            blockers.append("prose rules missing")

        if plan.dialogue_rules:
            passed.append("dialogue_rules_present")
        else:
            blockers.append("dialogue rules missing")

        if plan.continuity_rules:
            passed.append("continuity_rules_present")
        else:
            warnings.append("continuity rules missing")

        if plan.required_sections:
            passed.append("required_sections_present")
        else:
            warnings.append("required sections missing")

        if plan.warnings:
            warnings.extend(plan.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_format_plan(self, *, plan: FormatAdaptationPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "adaptation_plan_id": plan.adaptation_plan_id,
                "source_id": plan.source_id,
                "target_format": plan.target_format,
                "unit_type": plan.structure_rules.get("unit_type"),
                "internality": plan.prose_rules.get("internality"),
                "dialogue_density": plan.dialogue_rules.get("dialogue_density"),
                "pacing_shape": plan.pacing_rules.get("shape"),
                "required_section_count": len(plan.required_sections),
                "forbidden_pattern_count": len(plan.forbidden_patterns),
                "warning_count": len(plan.warnings),
            },
        }

    def _structure_rules(
        self,
        *,
        preset: Dict[str, Any],
        generation_contract: GenerationContract | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> Dict[str, Any]:
        rules = dict(preset["structure_rules"])

        if generation_contract:
            rules["contract_selected_format"] = generation_contract.selected_format.value
            rules["contract_id"] = generation_contract.generation_contract_id

        if chapter:
            rules["source_chapter_id"] = chapter.chapter_id
            rules["source_scene_count"] = len(chapter.scene_ids)

        if continuation_anchor:
            rules["source_anchor_id"] = continuation_anchor.anchor_id
            rules["open_loop_count"] = len(continuation_anchor.open_loops)

        return rules

    def _prose_rules(self, *, preset: Dict[str, Any], generation_contract: GenerationContract | None) -> Dict[str, Any]:
        rules = dict(preset["prose_rules"])

        if generation_contract:
            rules["tone_tags"] = generation_contract.tone_contract.get("tone_tags", [])
            rules["genre_tags"] = generation_contract.tone_contract.get("genres", [])

        return rules

    def _dialogue_rules(self, *, preset: Dict[str, Any], generation_contract: GenerationContract | None) -> Dict[str, Any]:
        rules = dict(preset["dialogue_rules"])

        if generation_contract:
            rules["contract_dialogue_density"] = generation_contract.tone_contract.get("dialogue_density")

        return rules

    def _pacing_rules(
        self,
        *,
        preset: Dict[str, Any],
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> Dict[str, Any]:
        rules = dict(preset["pacing_rules"])

        if chapter:
            rules["source_word_count"] = len(chapter.chapter_text.split())
            rules["source_open_loop_count"] = len(chapter.open_loops)

        if continuation_anchor:
            rules["next_hook_count"] = len(continuation_anchor.next_chapter_hooks)
            rules["active_causal_count"] = len(continuation_anchor.active_causal_ids)

        return rules

    def _continuity_rules(
        self,
        *,
        preset: Dict[str, Any],
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        plot_outline: PlotOutline | None = None,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        rules = dict(preset["continuity_rules"])

        if chapter:
            rules["must_preserve_character_ids"] = chapter.used_character_ids
            rules["must_preserve_relationship_ids"] = chapter.used_relationship_ids
            rules["must_preserve_secret_ids"] = chapter.used_secret_ids
            rules["must_preserve_causal_ids"] = chapter.used_causal_ids

        if continuation_anchor:
            rules["active_open_loop_ids"] = [loop.get("loop_id") for loop in continuation_anchor.open_loops]
            rules["continuity_reminders"] = continuation_anchor.continuity_reminders

        if plot_outline:
            rules["plot_outline_id"] = plot_outline.outline_id
            rules["required_plot_character_ids"] = plot_outline.continuity_requirements.get("required_character_ids", [])
            rules["required_plot_relationship_ids"] = plot_outline.continuity_requirements.get("required_relationship_ids", [])
            rules["required_plot_secret_ids"] = plot_outline.continuity_requirements.get("required_secret_ids", [])
            rules["required_plot_causal_ids"] = plot_outline.continuity_requirements.get("required_causal_ids", [])
            rules["plot_open_loop_ids"] = plot_outline.continuity_requirements.get("open_loop_ids", [])
            rules["plot_next_hooks"] = plot_outline.next_outline_hooks

        if story_context.get("story_context_id"):
            rules["story_context_id"] = story_context["story_context_id"]

        return rules

    def _adaptation_notes(
        self,
        *,
        format_key: str,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        notes = [f"Adapt source material for {format_key} without changing canon facts."]

        if format_key == "screenplay":
            notes.append("Use visible action only; avoid inner narration.")
        elif format_key == "novel":
            notes.append("Increase interiority, sensory detail, and prose rhythm.")
        elif format_key == "chapter":
            notes.append("Preserve chapter flow and next-chapter hook.")
        elif format_key == "game_scene":
            notes.append("Add player-facing choices and explicit state deltas.")
        elif format_key == "multi_book_arc":
            notes.append("Convert local events into book-level foreshadowing and payoff structure.")
        elif format_key == "movie":
            notes.append("Prioritize visual sequence logic and performable action.")

        if chapter:
            notes.append(f"Source chapter {chapter.chapter_id} has {len(chapter.scene_ids)} scene(s).")

        if continuation_anchor:
            notes.append(f"Continuation anchor has {len(continuation_anchor.open_loops)} open loop(s).")

        return notes

    def _warnings(
        self,
        *,
        format_key: str,
        generation_contract: GenerationContract | None,
        chapter: GeneratedChapter | None,
    ) -> List[str]:
        warnings: List[str] = []

        if format_key not in self.FORMAT_PRESETS:
            warnings.append(f"Unknown format {format_key}; default scene preset used.")

        if generation_contract and generation_contract.allowed_formats:
            allowed = [item.value for item in generation_contract.allowed_formats]
            if format_key not in allowed:
                warnings.append(f"Target format {format_key} is not in generation contract allowed formats: {allowed}.")

        if chapter and chapter.quality_summary.get("failed_scene_count", 0) > 0:
            warnings.append("Source chapter includes failed-quality scenes; adaptation may need revision first.")

        return warnings

    def _screenplay_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "INT./EXT. LOCATION - TIME\n\n"
            "ACTION: Convert the source scene into visible, performable action.\n\n"
            "CHARACTER\n"
            "Dialogue should carry subtext without inner narration.\n\n"
            f"CONTINUITY TO PRESERVE: {', '.join(plan.continuity_rules.get('must_preserve_causal_ids', []))}\n"
        )

    def _movie_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "FILM SEQUENCE PURPOSE\n"
            "Convert the source into visual sequence logic.\n\n"
            "VISUAL ESCALATION\n"
            "Each beat must be performable, visible, and tied to consequence.\n\n"
            "SET PIECE / TURN\n"
            "Identify the scene turn, reversal, or cinematic payoff.\n\n"
            f"CONTINUITY TO PRESERVE: {', '.join(plan.continuity_rules.get('must_preserve_causal_ids', []))}\n"
        )

    def _game_scene_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "SCENE SETUP\n"
            "Describe actionable player-facing situation.\n\n"
            "NPC DIALOGUE\n"
            "Use subtext and relationship state.\n\n"
            "PLAYER CHOICES\n"
            "1. Push for truth.\n"
            "2. Protect the secret.\n"
            "3. Delay and gather evidence.\n\n"
            "STATE DELTAS\n"
            f"Track: {', '.join(plan.continuity_rules.get('must_preserve_secret_ids', []))}\n"
        )

    def _multi_book_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "SERIES PREMISE IMPACT\n"
            "Explain how this material affects the larger saga.\n\n"
            "BOOK-LEVEL ARCS\n"
            "Book 1: Setup.\nBook 2: Complication.\nBook 3: Payoff.\n\n"
            "FORESHADOWING / PAYOFF REGISTRY\n"
            f"Open loops: {', '.join(plan.continuity_rules.get('active_open_loop_ids', []))}\n"
        )

    def _novel_chapter_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "# Adapted Chapter Draft Skeleton\n\n"
            "Opening image with interior pressure.\n\n"
            "Scene sequence with sensory detail, character thought, and subtext.\n\n"
            "Chapter turn and unresolved hook.\n"
        )

    def _scene_skeleton(self, *, plan: FormatAdaptationPlan, source_text: str) -> str:
        return (
            "# Adapted Scene Draft Skeleton\n\n"
            "Opening image.\n\n"
            "Pressure beat.\n\n"
            "Choice and consequence.\n\n"
            "Ending hook.\n"
        )

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
