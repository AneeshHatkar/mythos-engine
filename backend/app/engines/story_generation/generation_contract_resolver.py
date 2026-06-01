from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import (
    GenerationContract,
    GenerationMode,
    HandoffReference,
    StoryFormat,
    StoryIntent,
)


class GenerationContractResolver:
    """Builds the strict contract every Chunk 5 generation run must obey.

    This is the bridge between:
    - user intent from StoryIntentInterpreter
    - generation mode from GenerationModeController
    - Chunk 4 handoff/generation-control payloads
    - story validation requirements

    The contract prevents generic/hardcoded generation by making the generator
    explicitly obey characters, world rules, secrets, consequences, causality,
    format rules, quality thresholds, and provenance requirements.
    """

    engine_name = "story_generation.generation_contract_resolver"

    DEFAULT_QUALITY_THRESHOLDS = {
        "overall_score": 0.70,
        "user_intent_match": 0.75,
        "character_specificity": 0.70,
        "voice_consistency": 0.70,
        "emotional_depth": 0.65,
        "causal_coherence": 0.75,
        "knowledge_correctness": 0.85,
        "relationship_progression": 0.65,
        "world_specificity": 0.70,
        "format_adherence": 0.80,
        "anti_genericity": 0.70,
        "originality_safety": 0.90,
    }

    FORMAT_CONTRACTS = {
        StoryFormat.scene: {
            "requires_scene_purpose": True,
            "requires_ending_hook": True,
            "allows_internality": True,
            "requires_format_label": False,
        },
        StoryFormat.novel: {
            "requires_scene_purpose": True,
            "requires_chapter_or_scene_structure": True,
            "allows_internality": True,
            "requires_continuation_anchor": True,
        },
        StoryFormat.chapter: {
            "requires_chapter_objective": True,
            "requires_scene_sequence": True,
            "requires_ending_hook": True,
            "requires_continuation_anchor": True,
        },
        StoryFormat.screenplay: {
            "requires_scene_heading": True,
            "requires_action_lines": True,
            "requires_dialogue_blocks": True,
            "minimize_internal_monologue": True,
            "requires_visual_specificity": True,
        },
        StoryFormat.movie: {
            "requires_cinematic_beats": True,
            "requires_visual_specificity": True,
            "minimize_internal_monologue": True,
        },
        StoryFormat.series_episode: {
            "requires_a_plot_b_plot": True,
            "requires_act_breaks": True,
            "requires_episode_hook": True,
            "requires_season_continuity": True,
        },
        StoryFormat.season_outline: {
            "requires_episode_ladder": True,
            "requires_midseason_turn": True,
            "requires_finale_payoff": True,
            "requires_character_arc_progression": True,
        },
        StoryFormat.multi_book_arc: {
            "requires_book_arc_map": True,
            "requires_open_loop_registry": True,
            "requires_long_form_continuity": True,
            "requires_payoff_plan": True,
        },
        StoryFormat.game_scene: {
            "requires_choice_points": True,
            "requires_branch_outcomes": True,
            "requires_state_delta_preview": True,
        },
        StoryFormat.comic_scene: {
            "requires_panel_beats": True,
            "requires_visual_specificity": True,
            "minimize_internal_monologue": True,
        },
        StoryFormat.short_story: {
            "requires_compressed_arc": True,
            "requires_clear_turn": True,
            "requires_resolution_or_hook": True,
        },
        StoryFormat.treatment: {
            "requires_summary_beats": True,
            "requires_character_arc_summary": True,
            "requires_market_positioning": True,
        },
    }

    def resolve_contract(
        self,
        *,
        intent: StoryIntent,
        mode_decision: Dict[str, Any],
        handoff_payload: Optional[Dict[str, Any]] = None,
        generation_control_payload: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        handoff_payload = handoff_payload or {}
        generation_control_payload = generation_control_payload or {}
        overrides = overrides or {}

        selected_format = StoryFormat(mode_decision.get("selected_format", intent.desired_format.value))
        selected_mode = GenerationMode(mode_decision.get("selected_mode", intent.generation_mode.value))

        handoff_reference = self._build_handoff_reference(
            intent=intent,
            handoff_payload=handoff_payload,
            generation_control_payload=generation_control_payload,
        )

        allowed_character_ids = self._extract_allowed_characters(handoff_payload)
        required_character_ids = self._merge_unique(
            intent.required_character_ids,
            generation_control_payload.get("required_character_ids", []),
            handoff_payload.get("selected_character_ids", []),
        )

        if not required_character_ids and allowed_character_ids:
            required_character_ids = allowed_character_ids[: min(5, len(allowed_character_ids))]

        contract = GenerationContract(
            generation_contract_id=overrides.get("generation_contract_id", f"contract_{intent.intent_id}"),
            story_intent_id=intent.intent_id,
            handoff_reference=handoff_reference,
            allowed_formats=self._allowed_formats_for_mode(selected_mode),
            selected_format=selected_format,
            required_character_ids=required_character_ids,
            allowed_character_ids=allowed_character_ids,
            forbidden_character_ids=self._merge_unique(
                generation_control_payload.get("forbidden_character_ids", []),
                overrides.get("forbidden_character_ids", []),
            ),
            required_world_rule_ids=self._merge_unique(
                handoff_payload.get("required_world_rule_ids", []),
                generation_control_payload.get("required_world_rule_ids", []),
                self._extract_world_rule_ids(handoff_payload),
            ),
            required_secret_ids=self._merge_unique(
                handoff_payload.get("linked_secret_ids", []),
                generation_control_payload.get("required_secret_ids", []),
            ),
            forbidden_secret_reveals=self._merge_unique(
                generation_control_payload.get("forbidden_secret_reveals", []),
                self._secret_reveal_blocks_from_intent(intent),
            ),
            required_causal_node_ids=self._merge_unique(
                handoff_payload.get("causal_node_ids", []),
                generation_control_payload.get("required_causal_node_ids", []),
            ),
            required_consequence_ids=self._merge_unique(
                handoff_payload.get("consequence_ids", []),
                generation_control_payload.get("required_consequence_ids", []),
            ),
            required_relationship_ids=self._merge_unique(
                handoff_payload.get("relationship_ids", []),
                generation_control_payload.get("required_relationship_ids", []),
                self._extract_relationship_ids(handoff_payload),
            ),
            tone_contract=self._build_tone_contract(intent=intent, generation_control_payload=generation_control_payload),
            format_contract=self._build_format_contract(
                selected_format=selected_format,
                selected_mode=selected_mode,
                generation_control_payload=generation_control_payload,
            ),
            quality_thresholds=self._build_quality_thresholds(generation_control_payload, overrides),
            originality_rules=self._build_originality_rules(intent=intent, generation_control_payload=generation_control_payload),
            validation_required=True,
            provenance_required=True,
        )

        warnings = self._build_warnings(
            intent=intent,
            contract=contract,
            selected_mode=selected_mode,
            handoff_payload=handoff_payload,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "generation_contract": contract,
            "generation_contract_dict": contract.model_dump(mode="json"),
            "selected_mode": selected_mode.value,
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.handoff_package_loader",
                "payload_keys": [
                    "generation_contract",
                    "handoff_reference",
                    "required_character_ids",
                    "required_world_rule_ids",
                    "required_secret_ids",
                    "required_causal_node_ids",
                    "required_consequence_ids",
                ],
            },
        }

    def validate_contract(self, *, contract: GenerationContract) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not contract.generation_contract_id:
            blockers.append("generation_contract_id is required")
        else:
            passed.append("generation_contract_id_present")

        if not contract.story_intent_id:
            blockers.append("story_intent_id is required")
        else:
            passed.append("story_intent_id_present")

        if contract.validation_required:
            passed.append("validation_required")

        if contract.provenance_required:
            passed.append("provenance_required")

        if not contract.required_character_ids and not contract.allowed_character_ids:
            warnings.append("contract has no character constraints")

        if not contract.format_contract:
            warnings.append("format contract is empty")
        else:
            passed.append("format_contract_present")

        if not contract.quality_thresholds:
            warnings.append("quality thresholds are empty")
        else:
            passed.append("quality_thresholds_present")

        if not contract.originality_rules:
            warnings.append("originality rules are empty")
        else:
            passed.append("originality_rules_present")

        if contract.selected_format not in contract.allowed_formats and contract.allowed_formats:
            warnings.append("selected format is not listed in allowed formats")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def explain_contract(self, *, contract: GenerationContract) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "generation_contract_id": contract.generation_contract_id,
            "explanation": {
                "selected_format": contract.selected_format.value,
                "character_rules": {
                    "required": contract.required_character_ids,
                    "allowed_count": len(contract.allowed_character_ids),
                    "forbidden": contract.forbidden_character_ids,
                },
                "world_rules": contract.required_world_rule_ids,
                "knowledge_rules": {
                    "required_secret_ids": contract.required_secret_ids,
                    "forbidden_secret_reveals": contract.forbidden_secret_reveals,
                },
                "causality_rules": {
                    "required_causal_node_ids": contract.required_causal_node_ids,
                    "required_consequence_ids": contract.required_consequence_ids,
                },
                "relationship_rules": contract.required_relationship_ids,
                "quality_thresholds": contract.quality_thresholds,
                "originality_rules": contract.originality_rules,
            },
            "why_it_matters": [
                "The draft generator must follow this contract instead of inventing disconnected prose.",
                "Validators use this contract to check format, knowledge, causality, continuity, and originality.",
                "Provenance records should point back to this contract.",
            ],
        }

    def _build_handoff_reference(
        self,
        *,
        intent: StoryIntent,
        handoff_payload: Dict[str, Any],
        generation_control_payload: Dict[str, Any],
    ) -> HandoffReference:
        return HandoffReference(
            simulation_id=handoff_payload.get("simulation_id", generation_control_payload.get("simulation_id", "sim_unknown")),
            run_id=handoff_payload.get("run_id", generation_control_payload.get("run_id")),
            handoff_package_id=handoff_payload.get("handoff_package_id"),
            scene_payload_id=handoff_payload.get("scene_payload_id"),
            plot_payload_id=handoff_payload.get("plot_payload_id"),
            dialogue_payload_id=handoff_payload.get("dialogue_payload_id"),
            generation_control_payload_id=generation_control_payload.get("generation_control_payload_id"),
            quality_report_id=handoff_payload.get("quality_report_id"),
            anti_genericity_report_id=handoff_payload.get("anti_genericity_report_id"),
            benchmark_report_id=handoff_payload.get("benchmark_report_id"),
        )

    def _extract_allowed_characters(self, handoff_payload: Dict[str, Any]) -> List[str]:
        candidates = []
        candidates.extend(handoff_payload.get("selected_character_ids", []))
        candidates.extend(handoff_payload.get("active_character_ids", []))

        cast = handoff_payload.get("cast", {})
        if isinstance(cast, dict):
            candidates.extend(cast.get("character_ids", []))
            candidates.extend(cast.get("selected_character_ids", []))

        character_context = handoff_payload.get("character_context", {})
        if isinstance(character_context, dict):
            candidates.extend(character_context.keys())

        return self._merge_unique(candidates)

    def _extract_world_rule_ids(self, handoff_payload: Dict[str, Any]) -> List[str]:
        world_context = handoff_payload.get("world_context", {})
        if isinstance(world_context, dict):
            rules = world_context.get("world_rules", {})
            if isinstance(rules, dict):
                return list(rules.keys())
            if isinstance(rules, list):
                return [str(item) for item in rules]
        return []

    def _extract_relationship_ids(self, handoff_payload: Dict[str, Any]) -> List[str]:
        relationship_context = handoff_payload.get("relationship_context", {})
        if isinstance(relationship_context, dict):
            return list(relationship_context.keys())
        return []

    def _secret_reveal_blocks_from_intent(self, intent: StoryIntent) -> List[str]:
        blocked = []

        for item in intent.forbidden_elements:
            if "secret" in item or "reveal" in item or "spoiler" in item:
                blocked.append(item)

        if "mystery" in intent.genres and "secret_reveal" not in intent.required_plot_beats:
            blocked.append("major_mystery_solution_until_planned_reveal")

        return blocked

    def _allowed_formats_for_mode(self, mode: GenerationMode) -> List[StoryFormat]:
        mapping = {
            GenerationMode.quick_scene: [StoryFormat.scene],
            GenerationMode.full_scene: [StoryFormat.scene, StoryFormat.novel],
            GenerationMode.dialogue_only: [StoryFormat.scene, StoryFormat.screenplay, StoryFormat.novel],
            GenerationMode.chapter: [StoryFormat.chapter, StoryFormat.novel],
            GenerationMode.novel_outline: [StoryFormat.novel, StoryFormat.multi_book_arc],
            GenerationMode.movie_scene: [StoryFormat.movie, StoryFormat.screenplay],
            GenerationMode.screenplay_scene: [StoryFormat.screenplay],
            GenerationMode.series_episode: [StoryFormat.series_episode],
            GenerationMode.season_outline: [StoryFormat.season_outline],
            GenerationMode.multi_book_arc: [StoryFormat.multi_book_arc, StoryFormat.novel],
            GenerationMode.interactive_game_scene: [StoryFormat.game_scene],
            GenerationMode.rewrite_existing: list(StoryFormat),
            GenerationMode.continue_story: list(StoryFormat),
            GenerationMode.compare_drafts: list(StoryFormat),
            GenerationMode.export_bundle: list(StoryFormat),
        }
        return mapping.get(mode, [StoryFormat.scene])

    def _build_tone_contract(
        self,
        *,
        intent: StoryIntent,
        generation_control_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "tone_tags": self._merge_unique(intent.tone_tags, generation_control_payload.get("tone_tags", [])),
            "genres": self._merge_unique(intent.genres, generation_control_payload.get("genres", [])),
            "pov_preference": intent.pov_preference or generation_control_payload.get("pov_preference"),
            "target_length": intent.target_length or generation_control_payload.get("target_length"),
            "dialogue_density": intent.dialogue_density,
            "worldbuilding_density": intent.worldbuilding_density,
            "romance_intensity": intent.romance_intensity,
            "action_intensity": intent.action_intensity,
            "tragedy_intensity": intent.tragedy_intensity,
            "comedy_intensity": intent.comedy_intensity,
            "commercial_target": intent.commercial_target,
            "audience_type": intent.audience_type,
        }

    def _build_format_contract(
        self,
        *,
        selected_format: StoryFormat,
        selected_mode: GenerationMode,
        generation_control_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        base = dict(self.FORMAT_CONTRACTS.get(selected_format, {}))
        base["selected_mode"] = selected_mode.value
        base["selected_format"] = selected_format.value

        extra = generation_control_payload.get("format_contract", {})
        if isinstance(extra, dict):
            base.update(extra)

        return base

    def _build_quality_thresholds(
        self,
        generation_control_payload: Dict[str, Any],
        overrides: Dict[str, Any],
    ) -> Dict[str, float]:
        thresholds = dict(self.DEFAULT_QUALITY_THRESHOLDS)

        for source in [
            generation_control_payload.get("quality_thresholds", {}),
            overrides.get("quality_thresholds", {}),
        ]:
            if isinstance(source, dict):
                for key, value in source.items():
                    try:
                        thresholds[key] = max(0.0, min(1.0, float(value)))
                    except (TypeError, ValueError):
                        continue

        return thresholds

    def _build_originality_rules(
        self,
        *,
        intent: StoryIntent,
        generation_control_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        rules = {
            "no_raw_source_text": True,
            "no_excessive_imitation": True,
            "abstract_style_only": True,
            "copy_risk_threshold": 0.10,
            "avoid_generic_phrases": True,
            "must_use_world_specific_details": True,
            "must_use_character_specific_voice": True,
            "forbidden_elements": intent.forbidden_elements,
        }

        extra = generation_control_payload.get("originality_rules", {})
        if isinstance(extra, dict):
            rules.update(extra)

        return rules

    def _build_warnings(
        self,
        *,
        intent: StoryIntent,
        contract: GenerationContract,
        selected_mode: GenerationMode,
        handoff_payload: Dict[str, Any],
    ) -> List[str]:
        warnings = []

        if contract.handoff_reference.simulation_id == "sim_unknown":
            warnings.append("No simulation_id found; contract can still be built but Chunk 4 linkage is weak.")

        if not contract.required_character_ids:
            warnings.append("No required characters found; downstream cast selection must choose relevant characters.")

        if selected_mode in {GenerationMode.multi_book_arc, GenerationMode.season_outline}:
            warnings.append("Long-form mode requires continuation anchors, open loop registry, and payoff tracking.")

        if intent.preferred_character_count and intent.preferred_character_count >= 100:
            warnings.append("Huge entity pool detected; scaling controller must rank and filter before drafting.")

        if not contract.required_causal_node_ids and handoff_payload:
            warnings.append("Handoff payload has no causal nodes; causal continuity validator may have limited signal.")

        return warnings

    def _merge_unique(self, *items: Any) -> List[str]:
        result: List[str] = []
        seen = set()

        def add(value: Any) -> None:
            if value is None:
                return
            if isinstance(value, str):
                candidates = [value]
            elif isinstance(value, (list, tuple, set)):
                candidates = list(value)
            else:
                candidates = [str(value)]

            for candidate in candidates:
                if candidate is None:
                    continue
                text = str(candidate)
                if text and text not in seen:
                    seen.add(text)
                    result.append(text)

        for item in items:
            add(item)

        return result
