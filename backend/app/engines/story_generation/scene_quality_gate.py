from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    CommercialAppealReport,
    SceneQualityReport,
)


class SceneQualityGate:
    """Evaluates assembled scene quality before chapter handoff.

    This quality gate prevents weak assembled scenes from silently moving into
    long-form generation. It checks length, specificity, characters, dialogue,
    secrets, causality, relationship pressure, and generic phrase risk.
    """

    engine_name = "story_generation.scene_quality_gate"

    GENERIC_PHRASES = [
        "heart skipped a beat",
        "little did they know",
        "a chill ran down",
        "for what felt like forever",
        "eyes widened",
        "time stood still",
        "everything changed",
        "in that moment",
        "without warning",
        "destiny awaited",
    ]

    def evaluate_scene_quality(
        self,
        *,
        assembled_scene: AssembledScene,
        commercial_report: CommercialAppealReport | None = None,
        prose_style_profile: Dict[str, Any] | None = None,
        min_word_count: int = 180,
    ) -> Dict[str, Any]:
        prose_style_profile = prose_style_profile or {}

        length_score = self._length_score(assembled_scene=assembled_scene, min_word_count=min_word_count)
        world_specificity_score = self._world_specificity_score(assembled_scene=assembled_scene)
        character_presence_score = self._character_presence_score(assembled_scene=assembled_scene)
        relationship_pressure_score = self._relationship_pressure_score(assembled_scene=assembled_scene)
        secret_pressure_score = self._secret_pressure_score(assembled_scene=assembled_scene)
        causal_trace_score = self._causal_trace_score(assembled_scene=assembled_scene)
        dialogue_presence_score = self._dialogue_presence_score(assembled_scene=assembled_scene)
        generic_phrase_risk = self._generic_phrase_risk(
            text=assembled_scene.assembled_text,
            prose_style_profile=prose_style_profile,
        )

        overall_score = self._overall_score(
            length_score=length_score,
            world_specificity_score=world_specificity_score,
            character_presence_score=character_presence_score,
            relationship_pressure_score=relationship_pressure_score,
            secret_pressure_score=secret_pressure_score,
            causal_trace_score=causal_trace_score,
            dialogue_presence_score=dialogue_presence_score,
            generic_phrase_risk=generic_phrase_risk,
            commercial_score=commercial_report.overall_score if commercial_report else None,
        )

        blockers = self._blockers(
            assembled_scene=assembled_scene,
            overall_score=overall_score,
            length_score=length_score,
            character_presence_score=character_presence_score,
            causal_trace_score=causal_trace_score,
        )
        warnings = self._warnings(
            assembled_scene=assembled_scene,
            world_specificity_score=world_specificity_score,
            relationship_pressure_score=relationship_pressure_score,
            secret_pressure_score=secret_pressure_score,
            dialogue_presence_score=dialogue_presence_score,
            generic_phrase_risk=generic_phrase_risk,
            commercial_report=commercial_report,
        )
        improvement_targets = self._improvement_targets(
            length_score=length_score,
            world_specificity_score=world_specificity_score,
            character_presence_score=character_presence_score,
            relationship_pressure_score=relationship_pressure_score,
            secret_pressure_score=secret_pressure_score,
            causal_trace_score=causal_trace_score,
            dialogue_presence_score=dialogue_presence_score,
            generic_phrase_risk=generic_phrase_risk,
            commercial_report=commercial_report,
        )

        report = SceneQualityReport(
            report_id=f"scene_quality_{assembled_scene.scene_id}",
            scene_id=assembled_scene.scene_id,
            passed=not blockers and overall_score >= 0.65,
            overall_score=overall_score,
            length_score=length_score,
            world_specificity_score=world_specificity_score,
            character_presence_score=character_presence_score,
            relationship_pressure_score=relationship_pressure_score,
            secret_pressure_score=secret_pressure_score,
            causal_trace_score=causal_trace_score,
            dialogue_presence_score=dialogue_presence_score,
            generic_phrase_risk=generic_phrase_risk,
            blockers=blockers,
            warnings=warnings,
            improvement_targets=improvement_targets,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_quality_report": report,
            "scene_quality_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.chapter_generator",
                "payload_keys": [
                    "assembled_scene",
                    "scene_quality_report",
                    "chapter_handoff_payload",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def build_quality_repair_plan(self, *, report: SceneQualityReport) -> Dict[str, Any]:
        repairs: List[str] = []

        for blocker in report.blockers:
            if "too short" in blocker.lower():
                repairs.append("Expand scene with sensory detail, causal consequence, and character reaction.")
            elif "characters" in blocker.lower():
                repairs.append("Add active characters and make their presence visible in the assembled text.")
            elif "causal" in blocker.lower():
                repairs.append("Reconnect scene to causal IDs and consequence obligations.")
            else:
                repairs.append(f"Repair blocker: {blocker}")

        for target in report.improvement_targets:
            if target == "world_specificity":
                repairs.append("Add concrete world rules, institutions, rituals, locations, or artifacts.")
            elif target == "relationship_pressure":
                repairs.append("Increase trust/resentment/betrayal/repair pressure in scene action or dialogue.")
            elif target == "secret_pressure":
                repairs.append("Make secret pressure visible without revealing forbidden information.")
            elif target == "dialogue_presence":
                repairs.append("Add dialogue lines that carry subtext and voice differentiation.")
            elif target == "generic_phrase_risk":
                repairs.append("Remove generic phrases and replace them with story-specific imagery.")
            elif target == "commercial_appeal":
                repairs.append("Strengthen hook, emotional investment, stakes, or continuation pull.")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_for_chapter_handoff": report.passed,
            "repair_count": len(self._unique(repairs)),
            "repairs": self._unique(repairs),
        }

    def validate_quality_report(self, *, report: SceneQualityReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.report_id:
            blockers.append("report_id missing")
        else:
            passed.append("report_id_present")

        if not report.scene_id:
            blockers.append("scene_id missing")
        else:
            passed.append("scene_id_present")

        scores = [
            report.overall_score,
            report.length_score,
            report.world_specificity_score,
            report.character_presence_score,
            report.relationship_pressure_score,
            report.secret_pressure_score,
            report.causal_trace_score,
            report.dialogue_presence_score,
            report.generic_phrase_risk,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more scores are out of bounds")

        if report.passed:
            passed.append("quality_gate_passed")
        else:
            warnings.append("quality gate did not pass")

        if report.blockers:
            blockers.extend(report.blockers)

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

    def summarize_quality_report(self, *, report: SceneQualityReport) -> Dict[str, Any]:
        weakest = self._weakest_dimension(report=report)
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "report_id": report.report_id,
                "scene_id": report.scene_id,
                "passed": report.passed,
                "overall_score": report.overall_score,
                "weakest_dimension": weakest["dimension"],
                "weakest_score": weakest["score"],
                "blocker_count": len(report.blockers),
                "warning_count": len(report.warnings),
                "improvement_target_count": len(report.improvement_targets),
            },
        }

    def _length_score(self, *, assembled_scene: AssembledScene, min_word_count: int) -> float:
        word_count = len(assembled_scene.assembled_text.split())
        return self._bounded(word_count / max(1, min_word_count))

    def _world_specificity_score(self, *, assembled_scene: AssembledScene) -> float:
        score = 0.0

        if assembled_scene.used_world_details:
            score += min(0.6, len(assembled_scene.used_world_details) * 0.15)

        text = assembled_scene.assembled_text.lower()
        matched = 0
        for detail in assembled_scene.used_world_details:
            if str(detail).lower() in text:
                matched += 1

        if assembled_scene.used_world_details:
            score += min(0.4, matched / len(assembled_scene.used_world_details) * 0.4)

        return self._bounded(score)

    def _character_presence_score(self, *, assembled_scene: AssembledScene) -> float:
        if not assembled_scene.used_character_ids:
            return 0.0

        text = assembled_scene.assembled_text.lower()
        visible = sum(1 for cid in assembled_scene.used_character_ids if cid.lower() in text)

        return self._bounded(0.4 + 0.6 * (visible / len(assembled_scene.used_character_ids)))

    def _relationship_pressure_score(self, *, assembled_scene: AssembledScene) -> float:
        score = 0.0

        if assembled_scene.used_relationship_ids:
            score += 0.45

        text = assembled_scene.assembled_text.lower()
        markers = ["relationship", "trust", "resentment", "betrayal", "repair", "affection", "silence"]
        score += min(0.55, sum(1 for marker in markers if marker in text) * 0.12)

        return self._bounded(score)

    def _secret_pressure_score(self, *, assembled_scene: AssembledScene) -> float:
        score = 0.0

        if assembled_scene.used_secret_ids:
            score += 0.50

        text = assembled_scene.assembled_text.lower()
        markers = ["secret", "hidden", "forbidden", "reveal", "does not know", "cannot name"]
        score += min(0.50, sum(1 for marker in markers if marker in text) * 0.12)

        return self._bounded(score)

    def _causal_trace_score(self, *, assembled_scene: AssembledScene) -> float:
        score = 0.0

        if assembled_scene.used_causal_ids:
            score += 0.45

        trace = assembled_scene.continuity_trace or {}
        if trace.get("scene_beat_ids"):
            score += 0.20
        if trace.get("ending_hook"):
            score += 0.15
        if trace.get("scene_objective"):
            score += 0.10
        if assembled_scene.used_causal_ids and any(cid in assembled_scene.assembled_text for cid in assembled_scene.used_causal_ids):
            score += 0.10

        return self._bounded(score)

    def _dialogue_presence_score(self, *, assembled_scene: AssembledScene) -> float:
        text = assembled_scene.assembled_text

        score = 0.0
        if assembled_scene.dialogue_block_id:
            score += 0.45
        if ":" in text or '"' in text:
            score += 0.30
        if "subtext" in text.lower() or "says" in text.lower():
            score += 0.15
        if any(section.get("beat_type") == "dialogue_block" for section in assembled_scene.sections):
            score += 0.10

        return self._bounded(score)

    def _generic_phrase_risk(self, *, text: str, prose_style_profile: Dict[str, Any]) -> float:
        lowered = text.lower()
        banned = list(self.GENERIC_PHRASES)

        for item in prose_style_profile.get("generic_phrase_bans", []):
            banned.append(str(item))

        matched = sum(1 for phrase in self._unique(banned) if phrase.lower() in lowered)

        if matched == 0:
            return 0.0

        return self._bounded(matched / 5)

    def _overall_score(
        self,
        *,
        length_score: float,
        world_specificity_score: float,
        character_presence_score: float,
        relationship_pressure_score: float,
        secret_pressure_score: float,
        causal_trace_score: float,
        dialogue_presence_score: float,
        generic_phrase_risk: float,
        commercial_score: float | None,
    ) -> float:
        score = (
            length_score * 0.10
            + world_specificity_score * 0.15
            + character_presence_score * 0.15
            + relationship_pressure_score * 0.12
            + secret_pressure_score * 0.12
            + causal_trace_score * 0.16
            + dialogue_presence_score * 0.10
            + (1.0 - generic_phrase_risk) * 0.05
        )

        if commercial_score is not None:
            score += commercial_score * 0.05
        else:
            score += 0.05

        return self._bounded(score)

    def _blockers(
        self,
        *,
        assembled_scene: AssembledScene,
        overall_score: float,
        length_score: float,
        character_presence_score: float,
        causal_trace_score: float,
    ) -> List[str]:
        blockers = []

        if not assembled_scene.assembled_text:
            blockers.append("assembled text missing")

        if length_score < 0.35:
            blockers.append("assembled scene is too short")

        if character_presence_score < 0.35:
            blockers.append("characters are not sufficiently present")

        if causal_trace_score < 0.35:
            blockers.append("causal trace is too weak")

        if overall_score < 0.45:
            blockers.append("overall quality score too low")

        return blockers

    def _warnings(
        self,
        *,
        assembled_scene: AssembledScene,
        world_specificity_score: float,
        relationship_pressure_score: float,
        secret_pressure_score: float,
        dialogue_presence_score: float,
        generic_phrase_risk: float,
        commercial_report: CommercialAppealReport | None,
    ) -> List[str]:
        warnings = list(assembled_scene.warnings)

        if world_specificity_score < 0.55:
            warnings.append("world specificity is weak")

        if relationship_pressure_score < 0.55:
            warnings.append("relationship pressure is weak")

        if secret_pressure_score < 0.55 and assembled_scene.used_secret_ids:
            warnings.append("secret pressure is weak")

        if dialogue_presence_score < 0.55:
            warnings.append("dialogue presence is weak")

        if generic_phrase_risk > 0.0:
            warnings.append("generic phrase risk detected")

        if commercial_report and commercial_report.overall_score < 0.55:
            warnings.append("commercial appeal report is weak")

        return self._unique(warnings)

    def _improvement_targets(
        self,
        *,
        length_score: float,
        world_specificity_score: float,
        character_presence_score: float,
        relationship_pressure_score: float,
        secret_pressure_score: float,
        causal_trace_score: float,
        dialogue_presence_score: float,
        generic_phrase_risk: float,
        commercial_report: CommercialAppealReport | None,
    ) -> List[str]:
        targets = []

        if length_score < 0.75:
            targets.append("length")
        if world_specificity_score < 0.65:
            targets.append("world_specificity")
        if character_presence_score < 0.65:
            targets.append("character_presence")
        if relationship_pressure_score < 0.65:
            targets.append("relationship_pressure")
        if secret_pressure_score < 0.65:
            targets.append("secret_pressure")
        if causal_trace_score < 0.65:
            targets.append("causal_trace")
        if dialogue_presence_score < 0.65:
            targets.append("dialogue_presence")
        if generic_phrase_risk > 0.0:
            targets.append("generic_phrase_risk")
        if commercial_report and commercial_report.overall_score < 0.65:
            targets.append("commercial_appeal")

        return targets

    def _weakest_dimension(self, *, report: SceneQualityReport) -> Dict[str, Any]:
        values = [
            {"dimension": "length", "score": report.length_score},
            {"dimension": "world_specificity", "score": report.world_specificity_score},
            {"dimension": "character_presence", "score": report.character_presence_score},
            {"dimension": "relationship_pressure", "score": report.relationship_pressure_score},
            {"dimension": "secret_pressure", "score": report.secret_pressure_score},
            {"dimension": "causal_trace", "score": report.causal_trace_score},
            {"dimension": "dialogue_presence", "score": report.dialogue_presence_score},
            {"dimension": "generic_phrase_safety", "score": 1.0 - report.generic_phrase_risk},
        ]
        return min(values, key=lambda item: item["score"])

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
