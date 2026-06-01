from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    DialogueBeat,
    KnowledgeBoundaryReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class KnowledgeBoundaryValidator:
    """Validates hidden-knowledge boundaries before story drafting.

    This prevents impossible scenes like:
    - a character reveals a secret they do not know
    - a character references evidence they never saw
    - a mystery answer is exposed before the reveal point
    - dialogue leaks hidden knowledge without a valid scene reason
    """

    engine_name = "story_generation.knowledge_boundary_validator"

    def validate_knowledge_boundaries(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        story_context = story_context or {}

        knowledge_index = self._build_knowledge_index(story_context=story_context)
        checked_secret_ids = self._all_secret_ids(blueprint=blueprint, story_context=story_context)
        checked_evidence_ids = self._all_evidence_ids(story_context=story_context)

        violations = []
        warnings = []

        violations.extend(
            self._validate_blueprint_secret_pressure(
                blueprint=blueprint,
                knowledge_index=knowledge_index,
            )
        )
        violations.extend(
            self._validate_scene_beats(
                scene_beats=scene_beats,
                knowledge_index=knowledge_index,
            )
        )
        violations.extend(
            self._validate_dialogue_beats(
                dialogue_beats=dialogue_beats,
                knowledge_index=knowledge_index,
            )
        )
        violations.extend(
            self._validate_relationship_knowledge_asymmetry(
                relationship_beats=relationship_beats,
                knowledge_index=knowledge_index,
            )
        )

        warnings.extend(self._warnings(blueprint=blueprint, knowledge_index=knowledge_index, story_context=story_context))

        report = KnowledgeBoundaryReport(
            report_id=f"knowledge_report_{blueprint.scene_id}",
            valid=not violations,
            checked_secret_ids=checked_secret_ids,
            checked_evidence_ids=checked_evidence_ids,
            impossible_knowledge_violations=violations,
            warnings=warnings,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "knowledge_boundary_report": report,
            "knowledge_boundary_report_dict": report.model_dump(mode="json"),
            "knowledge_index": knowledge_index,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.causal_continuity_validator",
                "payload_keys": [
                    "knowledge_boundary_report",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_beats",
                    "relationship_beats",
                    "story_context",
                ],
            },
        }

    def build_safe_reveal_plan(
        self,
        *,
        report: KnowledgeBoundaryReport,
        story_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        required_setup: List[str] = []
        reveal_blocks: List[str] = []
        safe_reveal_candidates: List[Dict[str, Any]] = []

        for violation in report.impossible_knowledge_violations:
            lower = violation.lower()
            if "does not know" in lower:
                required_setup.append("add prior knowledge/reveal scene")
            if "evidence" in lower:
                required_setup.append("add evidence discovery/access scene")
            if "forbidden" in lower or "must not reveal" in lower:
                reveal_blocks.append(violation)

        for holder_id, data in self._build_knowledge_index(story_context=story_context).items():
            for secret_id in data.get("known_secret_ids", []):
                safe_reveal_candidates.append(
                    {
                        "holder_id": holder_id,
                        "secret_id": secret_id,
                        "safe_if_contract_allows": True,
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "required_setup": self._unique(required_setup),
            "reveal_blocks": self._unique(reveal_blocks),
            "safe_reveal_candidates": safe_reveal_candidates,
            "ready_for_generation": report.valid,
        }

    def validate_report(self, *, report: KnowledgeBoundaryReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.report_id:
            blockers.append("report_id missing")
        else:
            passed.append("report_id_present")

        if report.valid:
            passed.append("knowledge_boundaries_valid")
        else:
            blockers.extend(report.impossible_knowledge_violations)

        if report.checked_secret_ids:
            passed.append("secrets_checked")
        else:
            warnings.append("no secrets checked")

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

    def summarize_report(self, *, report: KnowledgeBoundaryReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "report_id": report.report_id,
                "valid": report.valid,
                "checked_secret_count": len(report.checked_secret_ids),
                "checked_evidence_count": len(report.checked_evidence_ids),
                "violation_count": len(report.impossible_knowledge_violations),
                "warning_count": len(report.warnings),
            },
        }

    def _build_knowledge_index(self, *, story_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}

        for boundary in story_context.get("knowledge_boundaries", []):
            holder_id = boundary.get("holder_id")
            if not holder_id or holder_id.startswith("_"):
                continue

            index[holder_id] = {
                "known_secret_ids": list(boundary.get("known_secret_ids", [])),
                "evidence_seen_ids": list(boundary.get("evidence_seen_ids", [])),
                "required_secret_ids": list(boundary.get("required_secret_ids", [])),
                "missing_required_secret_ids": list(boundary.get("missing_required_secret_ids", [])),
                "forbidden_secret_reveals": list(boundary.get("forbidden_secret_reveals", [])),
            }

        knowledge_context = story_context.get("knowledge_context", {})
        if isinstance(knowledge_context, dict):
            for holder_id, data in knowledge_context.items():
                if not isinstance(data, dict) or str(holder_id).startswith("_"):
                    continue

                index.setdefault(holder_id, {})
                index[holder_id].setdefault("known_secret_ids", list(data.get("known_secret_ids", [])))
                index[holder_id].setdefault("evidence_seen_ids", list(data.get("evidence_seen_ids", [])))
                index[holder_id].setdefault("required_secret_ids", list(data.get("required_secret_ids", [])))
                index[holder_id].setdefault("missing_required_secret_ids", list(data.get("missing_required_secret_ids", [])))
                index[holder_id].setdefault("forbidden_secret_reveals", list(data.get("forbidden_secret_reveals", [])))

        return index

    def _all_secret_ids(self, *, blueprint: SceneBlueprint, story_context: Dict[str, Any]) -> List[str]:
        values: List[str] = []

        for pressure in blueprint.secret_pressure:
            values.extend(self._extract_secret_like_tokens(pressure))

        for boundary in story_context.get("knowledge_boundaries", []):
            values.extend(boundary.get("known_secret_ids", []))
            values.extend(boundary.get("required_secret_ids", []))
            values.extend(boundary.get("missing_required_secret_ids", []))
            values.extend(boundary.get("forbidden_secret_reveals", []))

        return self._unique(values)

    def _all_evidence_ids(self, *, story_context: Dict[str, Any]) -> List[str]:
        values: List[str] = []

        for boundary in story_context.get("knowledge_boundaries", []):
            values.extend(boundary.get("evidence_seen_ids", []))

        return self._unique(values)

    def _validate_blueprint_secret_pressure(
        self,
        *,
        blueprint: SceneBlueprint,
        knowledge_index: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        violations = []

        for pressure in blueprint.secret_pressure:
            lower = pressure.lower()
            for holder_id, data in knowledge_index.items():
                for missing_secret in data.get("missing_required_secret_ids", []):
                    if missing_secret.lower() in lower and "lacks" not in lower and "does not know" not in lower:
                        violations.append(
                            f"{holder_id} appears to use {missing_secret} despite missing required knowledge."
                        )

                for forbidden in data.get("forbidden_secret_reveals", []):
                    if forbidden.lower() in lower and "must not reveal" not in lower:
                        violations.append(
                            f"{holder_id} blueprint pressure may reveal forbidden secret: {forbidden}."
                        )

        return violations

    def _validate_scene_beats(
        self,
        *,
        scene_beats: List[SceneBeat],
        knowledge_index: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        violations = []

        for beat in scene_beats:
            text = " ".join([beat.purpose, *beat.knowledge_constraints]).lower()

            for character_id in beat.character_ids:
                data = knowledge_index.get(character_id, {})
                known = set(data.get("known_secret_ids", []))
                missing = set(data.get("missing_required_secret_ids", []))
                forbidden = set(data.get("forbidden_secret_reveals", []))

                for secret_id in missing:
                    if secret_id.lower() in text and secret_id not in known:
                        if not any(marker in text for marker in ["lacks", "does not know", "missing"]):
                            violations.append(
                                f"{character_id} scene beat {beat.beat_id} uses {secret_id} but does not know it."
                            )

                for secret_id in forbidden:
                    if secret_id.lower() in text and "must not reveal" not in text:
                        violations.append(
                            f"{character_id} scene beat {beat.beat_id} risks forbidden reveal {secret_id}."
                        )

        return violations

    def _validate_dialogue_beats(
        self,
        *,
        dialogue_beats: List[DialogueBeat],
        knowledge_index: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        violations = []

        for beat in dialogue_beats:
            data = knowledge_index.get(beat.speaker_id, {})
            known = set(data.get("known_secret_ids", []))
            missing = set(data.get("missing_required_secret_ids", []))
            forbidden = set(data.get("forbidden_secret_reveals", []))

            text = " ".join(
                [
                    beat.surface_meaning or "",
                    beat.hidden_meaning or "",
                    beat.subtext or "",
                    beat.relationship_effect or "",
                ]
            ).lower()

            for secret_id in missing:
                if secret_id.lower() in text and secret_id not in known:
                    if not any(marker in text for marker in ["does not know", "lacks", "missing"]):
                        violations.append(
                            f"{beat.speaker_id} dialogue beat {beat.dialogue_beat_id} mentions {secret_id} but does not know it."
                        )

            for secret_id in forbidden:
                if secret_id.lower() in text and beat.secret_risk >= 0.5:
                    violations.append(
                        f"{beat.speaker_id} dialogue beat {beat.dialogue_beat_id} risks forbidden reveal {secret_id}."
                    )

        return violations

    def _validate_relationship_knowledge_asymmetry(
        self,
        *,
        relationship_beats: List[RelationshipBeat],
        knowledge_index: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        violations = []

        for beat in relationship_beats:
            for asymmetry in beat.knowledge_asymmetry:
                lower = asymmetry.lower()
                if "does not know" in lower:
                    continue
                if "must not reveal" in lower:
                    continue

                # Unknown asymmetry format is warning-worthy but not a blocker.
                continue

        return violations

    def _warnings(
        self,
        *,
        blueprint: SceneBlueprint,
        knowledge_index: Dict[str, Dict[str, Any]],
        story_context: Dict[str, Any],
    ) -> List[str]:
        warnings = []

        if not knowledge_index:
            warnings.append("No knowledge index found; validator has limited ability to prevent knowledge leaks.")

        if blueprint.secret_pressure and not knowledge_index:
            warnings.append("Blueprint has secret pressure but no knowledge boundaries were supplied.")

        for character_id in blueprint.active_character_ids:
            if character_id not in knowledge_index:
                warnings.append(f"No knowledge boundary record for active character {character_id}.")

        return warnings

    def _extract_secret_like_tokens(self, text: str) -> List[str]:
        return [
            part.strip(".,:;()[]{}")
            for part in text.split()
            if part.startswith("secret_") or part.startswith("major_mystery")
        ]

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
