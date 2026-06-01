from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CausalContinuityReport,
    ConsequencePayoffPlan,
    ConstraintSatisfactionReport,
    DialogueBeat,
    GenerationContract,
    KnowledgeBoundaryReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class ConstraintSatisfactionEngine:
    """Checks whether the planned story unit satisfies the generation contract.

    This is the final planning gate before prose/dialogue generation.
    It makes sure the scene plan obeys the user request, format rules,
    character requirements, knowledge boundaries, causality, consequence payoff,
    relationship beats, emotional beats, world details, and originality rules.
    """

    engine_name = "story_generation.constraint_satisfaction_engine"

    def evaluate_constraints(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        knowledge_report: KnowledgeBoundaryReport | None = None,
        causal_report: CausalContinuityReport | None = None,
        payoff_plan: ConsequencePayoffPlan | None = None,
        story_context: Dict[str, Any] | None = None,
        world_detail_pack: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        story_context = story_context or {}
        world_detail_pack = world_detail_pack or {}

        failed_constraints: List[str] = []
        warnings: List[str] = []

        required_characters_present = self._required_characters_present(contract=contract, blueprint=blueprint)
        if not required_characters_present:
            failed_constraints.append("required characters missing from blueprint")

        forbidden_elements_avoided = self._forbidden_elements_avoided(contract=contract, blueprint=blueprint, dialogue_beats=dialogue_beats)
        if not forbidden_elements_avoided:
            failed_constraints.append("forbidden elements appear in planned scene")

        requested_format_followed = self._requested_format_followed(contract=contract)
        if not requested_format_followed:
            failed_constraints.append("selected format is not allowed by contract")

        requested_tone_followed = self._requested_tone_followed(contract=contract, blueprint=blueprint, scene_beats=scene_beats)
        if not requested_tone_followed:
            warnings.append("tone signal is weak in current plan")

        emotional_beats_included = self._emotional_beats_included(story_context=story_context, scene_beats=scene_beats, dialogue_beats=dialogue_beats)
        if not emotional_beats_included:
            warnings.append("emotional beat signal is weak")

        relationship_beats_included = bool(relationship_beats) or bool(blueprint.relationship_pressure)
        if not relationship_beats_included:
            warnings.append("relationship beat signal is weak")

        ending_hook_included = bool(blueprint.ending_hook) or any(beat.beat_type == "ending_hook" for beat in scene_beats)
        if not ending_hook_included:
            warnings.append("ending hook missing")

        knowledge_rules_obeyed = True if knowledge_report is None else knowledge_report.valid
        if not knowledge_rules_obeyed:
            failed_constraints.append("knowledge boundary report is invalid")

        causal_rules_obeyed = True if causal_report is None else causal_report.valid
        if not causal_rules_obeyed:
            failed_constraints.append("causal continuity report is invalid")

        consequence_payoff_included = self._consequence_payoff_included(payoff_plan=payoff_plan, scene_beats=scene_beats)
        if not consequence_payoff_included and payoff_plan and payoff_plan.source_consequence_ids:
            warnings.append("consequence payoff is incomplete or delayed")

        world_details_included = bool(blueprint.required_world_details) or bool(world_detail_pack.get("law_and_rule_anchors"))
        if not world_details_included:
            warnings.append("world-specific details missing")

        report = ConstraintSatisfactionReport(
            report_id=f"constraint_report_{blueprint.scene_id}",
            satisfied=not failed_constraints,
            required_characters_present=required_characters_present,
            forbidden_elements_avoided=forbidden_elements_avoided,
            requested_format_followed=requested_format_followed,
            requested_tone_followed=requested_tone_followed,
            emotional_beats_included=emotional_beats_included,
            relationship_beats_included=relationship_beats_included,
            ending_hook_included=ending_hook_included,
            knowledge_rules_obeyed=knowledge_rules_obeyed,
            failed_constraints=failed_constraints,
            warnings=warnings,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "constraint_report": report,
            "constraint_report_dict": report.model_dump(mode="json"),
            "extra_checks": {
                "causal_rules_obeyed": causal_rules_obeyed,
                "consequence_payoff_included": consequence_payoff_included,
                "world_details_included": world_details_included,
            },
            "handoff_to_next_engine": {
                "next_engine": "story_generation.prose_style_engine",
                "payload_keys": [
                    "constraint_report",
                    "generation_contract",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_beats",
                    "relationship_beats",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def build_constraint_repair_plan(
        self,
        *,
        report: ConstraintSatisfactionReport,
        extra_checks: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        extra_checks = extra_checks or {}
        repairs: List[str] = []

        for failed in report.failed_constraints:
            if "required characters" in failed:
                repairs.append("Add missing required characters to the scene blueprint and active cast.")
            elif "forbidden elements" in failed:
                repairs.append("Remove forbidden elements from blueprint/dialogue plan.")
            elif "format" in failed:
                repairs.append("Switch selected format or update allowed format contract.")
            elif "knowledge" in failed:
                repairs.append("Run safe reveal plan and add missing knowledge setup.")
            elif "causal" in failed:
                repairs.append("Run causal repair plan and add missing cause/effect beats.")
            else:
                repairs.append(f"Repair failed constraint: {failed}")

        if not report.requested_tone_followed:
            repairs.append("Strengthen tone anchors in scene beats and prose style profile.")

        if not report.emotional_beats_included:
            repairs.append("Add emotional turn and emotional subtext instructions.")

        if not report.relationship_beats_included:
            repairs.append("Add relationship pressure and relationship state shift.")

        if not report.ending_hook_included:
            repairs.append("Add ending hook beat.")

        if extra_checks.get("consequence_payoff_included") is False:
            repairs.append("Add consequence payoff beat or open-loop delayed payoff entry.")

        if extra_checks.get("world_details_included") is False:
            repairs.append("Inject concrete world details from world detail pack.")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_for_generation": report.satisfied and not repairs,
            "repair_count": len(self._unique(repairs)),
            "repairs": self._unique(repairs),
        }

    def validate_constraint_report(self, *, report: ConstraintSatisfactionReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.report_id:
            blockers.append("report_id missing")
        else:
            passed.append("report_id_present")

        if report.satisfied:
            passed.append("constraints_satisfied")
        else:
            blockers.extend(report.failed_constraints)

        if report.required_characters_present:
            passed.append("required_characters_present")

        if report.forbidden_elements_avoided:
            passed.append("forbidden_elements_avoided")

        if report.requested_format_followed:
            passed.append("requested_format_followed")

        if report.knowledge_rules_obeyed:
            passed.append("knowledge_rules_obeyed")

        if report.warnings:
            warnings.extend(report.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_constraint_report(self, *, report: ConstraintSatisfactionReport, extra_checks: Dict[str, Any] | None = None) -> Dict[str, Any]:
        extra_checks = extra_checks or {}
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "report_id": report.report_id,
                "satisfied": report.satisfied,
                "failed_constraint_count": len(report.failed_constraints),
                "warning_count": len(report.warnings),
                "required_characters_present": report.required_characters_present,
                "forbidden_elements_avoided": report.forbidden_elements_avoided,
                "requested_format_followed": report.requested_format_followed,
                "knowledge_rules_obeyed": report.knowledge_rules_obeyed,
                "causal_rules_obeyed": extra_checks.get("causal_rules_obeyed"),
                "consequence_payoff_included": extra_checks.get("consequence_payoff_included"),
                "world_details_included": extra_checks.get("world_details_included"),
            },
        }

    def _required_characters_present(self, *, contract: GenerationContract, blueprint: SceneBlueprint) -> bool:
        required = set(contract.required_character_ids)
        present = set(blueprint.active_character_ids)
        return required.issubset(present)

    def _forbidden_elements_avoided(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        dialogue_beats: List[DialogueBeat],
    ) -> bool:
        forbidden = contract.originality_rules.get("forbidden_elements", [])
        if not forbidden:
            forbidden = []

        text = " ".join(
            [
                blueprint.scene_purpose or "",
                blueprint.scene_objective or "",
                blueprint.ending_hook or "",
                " ".join(blueprint.stakes),
                " ".join(blueprint.secret_pressure),
                " ".join(blueprint.relationship_pressure),
                " ".join(blueprint.required_world_details),
                " ".join(
                    [
                        " ".join(
                            [
                                beat.surface_meaning or "",
                                beat.hidden_meaning or "",
                                beat.subtext or "",
                            ]
                        )
                        for beat in dialogue_beats
                    ]
                ),
            ]
        ).lower()

        for item in forbidden:
            if str(item).lower() in text:
                return False

        return True

    def _requested_format_followed(self, *, contract: GenerationContract) -> bool:
        if not contract.allowed_formats:
            return True
        return contract.selected_format in contract.allowed_formats

    def _requested_tone_followed(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
    ) -> bool:
        tone_tags = contract.tone_contract.get("tone_tags", [])
        if not tone_tags:
            return True

        text = " ".join(
            [
                blueprint.scene_purpose or "",
                blueprint.scene_objective or "",
                blueprint.emotional_turn or "",
                blueprint.ending_hook or "",
                " ".join(blueprint.stakes),
                " ".join(beat.purpose for beat in scene_beats),
            ]
        ).lower()

        # Tone can be explicit or implied by pressure words.
        tone_markers = {
            "tense": ["pressure", "risk", "harder", "confront", "consequence"],
            "dark": ["cost", "secret", "betrayal", "fear", "judgment"],
            "tragic": ["loss", "cost", "grief", "betrayal", "cannot"],
            "romantic": ["longing", "care", "almost", "trust", "silence"],
            "epic": ["fate", "war", "kingdom", "world", "saga"],
        }

        for tone in tone_tags:
            lowered = str(tone).lower()
            if lowered in text:
                return True
            if any(marker in text for marker in tone_markers.get(lowered, [])):
                return True

        return False

    def _emotional_beats_included(
        self,
        *,
        story_context: Dict[str, Any],
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat],
    ) -> bool:
        if story_context.get("emotional_pressure"):
            return True

        if any(beat.emotional_state for beat in scene_beats):
            return True

        if any(beat.emotion for beat in dialogue_beats):
            return True

        return False

    def _consequence_payoff_included(
        self,
        *,
        payoff_plan: ConsequencePayoffPlan | None,
        scene_beats: List[SceneBeat],
    ) -> bool:
        if payoff_plan is None:
            return True

        if not payoff_plan.source_consequence_ids:
            return True

        has_consequence_beat = any(beat.beat_type == "consequence" for beat in scene_beats)
        has_obligation = bool(payoff_plan.payoff_obligations)
        has_required_beats_missing = bool(payoff_plan.required_scene_beats)

        return has_consequence_beat and has_obligation and not has_required_beats_missing

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
