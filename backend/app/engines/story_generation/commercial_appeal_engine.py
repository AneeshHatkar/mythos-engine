from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CommercialAppealReport,
    DialogueBeat,
    GenerationContract,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class CommercialAppealEngine:
    """Scores audience pull without making the story generic.

    This engine estimates whether a planned scene has:
    - strong hook
    - emotional investment
    - character appeal
    - relationship appeal
    - stakes clarity
    - world uniqueness
    - scene momentum
    - continuation pull

    It is not a replacement for originality. It helps identify why a scene
    would make someone keep reading/watching/playing.
    """

    engine_name = "story_generation.commercial_appeal_engine"

    def evaluate_commercial_appeal(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        prose_style_profile: Dict[str, Any] | None = None,
        story_context: Dict[str, Any] | None = None,
        world_detail_pack: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        prose_style_profile = prose_style_profile or {}
        story_context = story_context or {}
        world_detail_pack = world_detail_pack or {}

        hook_strength = self._hook_strength(blueprint=blueprint, scene_beats=scene_beats)
        emotional_investment = self._emotional_investment(
            blueprint=blueprint,
            scene_beats=scene_beats,
            dialogue_beats=dialogue_beats,
            story_context=story_context,
        )
        character_appeal = self._character_appeal(story_context=story_context, blueprint=blueprint)
        relationship_appeal = self._relationship_appeal(
            blueprint=blueprint,
            relationship_beats=relationship_beats,
            dialogue_beats=dialogue_beats,
        )
        stakes_clarity = self._stakes_clarity(blueprint=blueprint)
        world_uniqueness = self._world_uniqueness(
            blueprint=blueprint,
            world_detail_pack=world_detail_pack,
            prose_style_profile=prose_style_profile,
        )
        scene_momentum = self._scene_momentum(scene_beats=scene_beats, blueprint=blueprint)
        continuation_pull = self._continuation_pull(blueprint=blueprint, scene_beats=scene_beats)
        adaptation_potential = self._adaptation_potential(
            contract=contract,
            blueprint=blueprint,
            world_detail_pack=world_detail_pack,
            relationship_beats=relationship_beats,
        )

        overall = self._weighted_average(
            {
                "hook_strength": hook_strength,
                "emotional_investment": emotional_investment,
                "character_appeal": character_appeal,
                "relationship_appeal": relationship_appeal,
                "stakes_clarity": stakes_clarity,
                "world_uniqueness": world_uniqueness,
                "scene_momentum": scene_momentum,
                "continuation_pull": continuation_pull,
                "adaptation_potential": adaptation_potential,
            }
        )

        report = CommercialAppealReport(
            report_id=f"commercial_report_{blueprint.scene_id}",
            overall_score=overall,
            hook_strength=hook_strength,
            emotional_investment=emotional_investment,
            character_appeal=character_appeal,
            relationship_appeal=relationship_appeal,
            stakes_clarity=stakes_clarity,
            world_uniqueness=world_uniqueness,
            scene_momentum=scene_momentum,
            continuation_pull=continuation_pull,
            adaptation_potential=adaptation_potential,
            improvement_suggestions=self._improvement_suggestions(
                hook_strength=hook_strength,
                emotional_investment=emotional_investment,
                character_appeal=character_appeal,
                relationship_appeal=relationship_appeal,
                stakes_clarity=stakes_clarity,
                world_uniqueness=world_uniqueness,
                scene_momentum=scene_momentum,
                continuation_pull=continuation_pull,
                adaptation_potential=adaptation_potential,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "commercial_appeal_report": report,
            "commercial_appeal_report_dict": report.model_dump(mode="json"),
            "audience_positioning": self._audience_positioning(
                contract=contract,
                report=report,
                blueprint=blueprint,
            ),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.scene_draft_engine",
                "payload_keys": [
                    "commercial_appeal_report",
                    "prose_style_profile",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_beats",
                    "relationship_beats",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def validate_commercial_appeal_report(self, *, report: CommercialAppealReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.report_id:
            blockers.append("report_id missing")
        else:
            passed.append("report_id_present")

        score_fields = [
            report.overall_score,
            report.hook_strength,
            report.emotional_investment,
            report.character_appeal,
            report.relationship_appeal,
            report.stakes_clarity,
            report.world_uniqueness,
            report.scene_momentum,
            report.continuation_pull,
            report.adaptation_potential,
        ]

        if all(0.0 <= score <= 1.0 for score in score_fields):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more appeal scores out of bounds")

        if report.overall_score >= 0.65:
            passed.append("commercial_appeal_usable")
        else:
            warnings.append("commercial appeal score is low")

        if report.improvement_suggestions:
            passed.append("improvement_suggestions_present")
        else:
            warnings.append("no improvement suggestions generated")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def build_appeal_improvement_plan(self, *, report: CommercialAppealReport) -> Dict[str, Any]:
        priority = "low"
        if report.overall_score < 0.50:
            priority = "high"
        elif report.overall_score < 0.70:
            priority = "medium"

        return {
            "success": True,
            "engine_name": self.engine_name,
            "priority": priority,
            "ready_for_drafting": report.overall_score >= 0.55,
            "suggestions": report.improvement_suggestions,
            "lowest_dimensions": self._lowest_dimensions(report=report),
        }

    def summarize_commercial_appeal(self, *, report: CommercialAppealReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "report_id": report.report_id,
                "overall_score": report.overall_score,
                "strongest_dimension": self._strongest_dimension(report=report),
                "weakest_dimension": self._lowest_dimensions(report=report)[0]["dimension"],
                "suggestion_count": len(report.improvement_suggestions),
                "draft_ready": report.overall_score >= 0.55,
            },
        }

    def _hook_strength(self, *, blueprint: SceneBlueprint, scene_beats: List[SceneBeat]) -> float:
        score = 0.20

        if blueprint.opening_image:
            score += 0.15
        if blueprint.ending_hook:
            score += 0.25
        if blueprint.secret_pressure:
            score += 0.15
        if any(beat.beat_type == "ending_hook" for beat in scene_beats):
            score += 0.10
        if any(beat.tension_value >= 0.8 for beat in scene_beats):
            score += 0.15

        return self._bounded(score)

    def _emotional_investment(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat],
        story_context: Dict[str, Any],
    ) -> float:
        score = 0.20

        if blueprint.emotional_turn:
            score += 0.20
        if story_context.get("emotional_pressure"):
            score += 0.20
        if any(beat.emotional_state for beat in scene_beats):
            score += 0.15
        if any(beat.emotion or beat.subtext for beat in dialogue_beats):
            score += 0.15
        if blueprint.relationship_pressure:
            score += 0.10

        return self._bounded(score)

    def _character_appeal(self, *, story_context: Dict[str, Any], blueprint: SceneBlueprint) -> float:
        active_cast = story_context.get("active_cast", [])
        score = 0.20

        if blueprint.pov_character_id:
            score += 0.15
        if active_cast:
            score += 0.15
        if any(item.get("goals") for item in active_cast):
            score += 0.15
        if any(item.get("psychology") for item in active_cast):
            score += 0.15
        if any(item.get("voice_profile") for item in active_cast):
            score += 0.15
        if any(item.get("role_tags") for item in active_cast):
            score += 0.10

        return self._bounded(score)

    def _relationship_appeal(
        self,
        *,
        blueprint: SceneBlueprint,
        relationship_beats: List[RelationshipBeat],
        dialogue_beats: List[DialogueBeat],
    ) -> float:
        score = 0.15

        if blueprint.relationship_pressure:
            score += 0.20
        if relationship_beats:
            score += 0.20
        if any(beat.romantic_tension > 0.3 for beat in relationship_beats):
            score += 0.10
        if any(beat.betrayal_risk > 0.5 for beat in relationship_beats):
            score += 0.15
        if any(beat.relationship_effect for beat in dialogue_beats):
            score += 0.15

        return self._bounded(score)

    def _stakes_clarity(self, *, blueprint: SceneBlueprint) -> float:
        score = 0.20

        if blueprint.scene_objective:
            score += 0.20
        if blueprint.stakes:
            score += 0.25
        if blueprint.opposition:
            score += 0.10
        if blueprint.secret_pressure:
            score += 0.10
        if blueprint.ending_hook:
            score += 0.10

        return self._bounded(score)

    def _world_uniqueness(
        self,
        *,
        blueprint: SceneBlueprint,
        world_detail_pack: Dict[str, Any],
        prose_style_profile: Dict[str, Any],
    ) -> float:
        score = 0.15

        if blueprint.required_world_details:
            score += 0.20
        if world_detail_pack.get("specificity_score", 0.0) >= 0.6:
            score += 0.25
        if world_detail_pack.get("law_and_rule_anchors"):
            score += 0.10
        if world_detail_pack.get("ritual_anchors"):
            score += 0.10
        if prose_style_profile.get("world_detail_usage_rules"):
            score += 0.10

        return self._bounded(score)

    def _scene_momentum(self, *, scene_beats: List[SceneBeat], blueprint: SceneBlueprint) -> float:
        score = 0.15

        beat_types = [beat.beat_type for beat in scene_beats]
        if "choice" in beat_types:
            score += 0.20
        if "consequence" in beat_types:
            score += 0.20
        if "secret_pressure" in beat_types or blueprint.secret_pressure:
            score += 0.10
        if "relationship_pressure" in beat_types or blueprint.relationship_pressure:
            score += 0.10
        if scene_beats and scene_beats[-1].tension_value >= scene_beats[0].tension_value:
            score += 0.15

        return self._bounded(score)

    def _continuation_pull(self, *, blueprint: SceneBlueprint, scene_beats: List[SceneBeat]) -> float:
        score = 0.15

        if blueprint.ending_hook:
            score += 0.30
        if blueprint.secret_pressure:
            score += 0.15
        if any(beat.beat_type == "ending_hook" for beat in scene_beats):
            score += 0.15
        if any(beat.beat_type == "consequence" for beat in scene_beats):
            score += 0.10
        if blueprint.relationship_pressure:
            score += 0.10

        return self._bounded(score)

    def _adaptation_potential(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        world_detail_pack: Dict[str, Any],
        relationship_beats: List[RelationshipBeat],
    ) -> float:
        score = 0.15

        if contract.selected_format.value in {"screenplay", "movie", "game_scene", "scene"}:
            score += 0.15
        if blueprint.location_id:
            score += 0.10
        if blueprint.required_world_details:
            score += 0.15
        if world_detail_pack.get("sensory_detail_hints"):
            score += 0.15
        if relationship_beats:
            score += 0.10
        if blueprint.ending_hook:
            score += 0.10

        return self._bounded(score)

    def _improvement_suggestions(self, **scores: float) -> List[str]:
        suggestions = []

        if scores["hook_strength"] < 0.65:
            suggestions.append("Strengthen the opening image or ending hook.")
        if scores["emotional_investment"] < 0.65:
            suggestions.append("Make the emotional turn more specific and visible through behavior.")
        if scores["character_appeal"] < 0.65:
            suggestions.append("Add clearer character goal, wound, voice, or contradiction.")
        if scores["relationship_appeal"] < 0.65:
            suggestions.append("Increase relationship tension, betrayal risk, longing, or repair stakes.")
        if scores["stakes_clarity"] < 0.65:
            suggestions.append("Clarify what is lost if the scene objective fails.")
        if scores["world_uniqueness"] < 0.65:
            suggestions.append("Add more concrete world rules, rituals, locations, or institutions.")
        if scores["scene_momentum"] < 0.65:
            suggestions.append("Add a clear choice and consequence beat.")
        if scores["continuation_pull"] < 0.65:
            suggestions.append("End with a stronger unanswered question or unresolved pressure.")
        if scores["adaptation_potential"] < 0.65:
            suggestions.append("Add more visual, performable, or interactive story elements.")

        return suggestions

    def _audience_positioning(
        self,
        *,
        contract: GenerationContract,
        report: CommercialAppealReport,
        blueprint: SceneBlueprint,
    ) -> Dict[str, Any]:
        genres = contract.tone_contract.get("genres", [])
        tone_tags = contract.tone_contract.get("tone_tags", [])

        likely_audience = []
        if "dark_academy" in genres:
            likely_audience.append("dark academia / mystery readers")
        if "romance" in genres or report.relationship_appeal >= 0.7:
            likely_audience.append("relationship-driven story readers")
        if report.world_uniqueness >= 0.7:
            likely_audience.append("worldbuilding-focused fantasy/sci-fi readers")
        if report.continuation_pull >= 0.7:
            likely_audience.append("serial / binge readers")
        if contract.selected_format.value in {"screenplay", "movie"}:
            likely_audience.append("cinematic story viewers")

        if not likely_audience:
            likely_audience.append("general speculative fiction audience")

        return {
            "likely_audience": likely_audience,
            "genre_tags": genres,
            "tone_tags": tone_tags,
            "commercial_positioning_note": self._positioning_note(report=report, blueprint=blueprint),
        }

    def _positioning_note(self, *, report: CommercialAppealReport, blueprint: SceneBlueprint) -> str:
        strongest = self._strongest_dimension(report=report)
        if strongest == "world_uniqueness":
            return "The scene's strongest commercial angle is its specific world identity."
        if strongest == "relationship_appeal":
            return "The scene's strongest commercial angle is the character relationship pressure."
        if strongest == "continuation_pull":
            return "The scene's strongest commercial angle is making the audience want the next scene."
        if strongest == "emotional_investment":
            return "The scene's strongest commercial angle is emotional investment."
        return "The scene has balanced commercial appeal if drafting preserves specificity."

    def _weighted_average(self, scores: Dict[str, float]) -> float:
        weights = {
            "hook_strength": 0.14,
            "emotional_investment": 0.15,
            "character_appeal": 0.13,
            "relationship_appeal": 0.12,
            "stakes_clarity": 0.12,
            "world_uniqueness": 0.12,
            "scene_momentum": 0.10,
            "continuation_pull": 0.08,
            "adaptation_potential": 0.04,
        }

        total = sum(scores[key] * weights[key] for key in scores)
        return round(self._bounded(total), 3)

    def _lowest_dimensions(self, *, report: CommercialAppealReport) -> List[Dict[str, Any]]:
        values = self._dimension_values(report=report)
        return sorted(values, key=lambda item: item["score"])

    def _strongest_dimension(self, *, report: CommercialAppealReport) -> str:
        values = self._dimension_values(report=report)
        return max(values, key=lambda item: item["score"])["dimension"]

    def _dimension_values(self, *, report: CommercialAppealReport) -> List[Dict[str, Any]]:
        return [
            {"dimension": "hook_strength", "score": report.hook_strength},
            {"dimension": "emotional_investment", "score": report.emotional_investment},
            {"dimension": "character_appeal", "score": report.character_appeal},
            {"dimension": "relationship_appeal", "score": report.relationship_appeal},
            {"dimension": "stakes_clarity", "score": report.stakes_clarity},
            {"dimension": "world_uniqueness", "score": report.world_uniqueness},
            {"dimension": "scene_momentum", "score": report.scene_momentum},
            {"dimension": "continuation_pull", "score": report.continuation_pull},
            {"dimension": "adaptation_potential", "score": report.adaptation_potential},
        ]

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)
