from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CausalContinuityReport,
    DialogueBeat,
    KnowledgeBoundaryReport,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class CausalContinuityValidator:
    """Validates cause/effect continuity before story drafting.

    This prevents the story layer from ignoring the simulation layer.
    It checks whether causal nodes, consequences, choices, relationship shifts,
    and ending hooks are present and logically connected.
    """

    engine_name = "story_generation.causal_continuity_validator"

    def validate_causal_continuity(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        knowledge_report: KnowledgeBoundaryReport | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        dialogue_beats = dialogue_beats or []
        relationship_beats = relationship_beats or []
        story_context = story_context or {}

        causal_index = self._build_causal_index(story_context=story_context)
        checked_causal_node_ids = self._checked_causal_nodes(
            blueprint=blueprint,
            scene_beats=scene_beats,
            story_context=story_context,
        )
        checked_consequence_ids = self._checked_consequences(
            blueprint=blueprint,
            scene_beats=scene_beats,
            story_context=story_context,
        )

        missing_causes = self._missing_causes(
            checked_causal_node_ids=checked_causal_node_ids,
            causal_index=causal_index,
        )
        missing_consequences = self._missing_consequences(
            checked_consequence_ids=checked_consequence_ids,
            blueprint=blueprint,
            scene_beats=scene_beats,
            relationship_beats=relationship_beats,
        )
        orphan_events = self._orphan_events(
            scene_beats=scene_beats,
            dialogue_beats=dialogue_beats,
            checked_causal_node_ids=checked_causal_node_ids,
        )
        warnings = self._warnings(
            blueprint=blueprint,
            scene_beats=scene_beats,
            dialogue_beats=dialogue_beats,
            relationship_beats=relationship_beats,
            knowledge_report=knowledge_report,
            causal_index=causal_index,
        )

        report = CausalContinuityReport(
            report_id=f"causal_report_{blueprint.scene_id}",
            valid=not missing_causes and not missing_consequences and not orphan_events,
            checked_causal_node_ids=checked_causal_node_ids,
            missing_causes=missing_causes,
            missing_consequences=missing_consequences,
            orphan_events=orphan_events,
            warnings=warnings,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "causal_continuity_report": report,
            "causal_continuity_report_dict": report.model_dump(mode="json"),
            "causal_index": causal_index,
            "checked_consequence_ids": checked_consequence_ids,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.consequence_payoff_engine",
                "payload_keys": [
                    "causal_continuity_report",
                    "scene_blueprint",
                    "scene_beats",
                    "relationship_beats",
                    "story_context",
                ],
            },
        }

    def build_causal_repair_plan(
        self,
        *,
        report: CausalContinuityReport,
    ) -> Dict[str, Any]:
        required_fixes: List[str] = []

        for cause_id in report.missing_causes:
            required_fixes.append(f"Add setup or reference for causal node {cause_id}.")

        for consequence_id in report.missing_consequences:
            required_fixes.append(f"Add consequence payoff beat for {consequence_id}.")

        for event_id in report.orphan_events:
            required_fixes.append(f"Connect orphan event/beat {event_id} to a cause or consequence.")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_for_generation": report.valid,
            "required_fixes": required_fixes,
            "repair_priority": "high" if required_fixes else "none",
        }

    def validate_report(self, *, report: CausalContinuityReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.report_id:
            blockers.append("report_id missing")
        else:
            passed.append("report_id_present")

        if report.valid:
            passed.append("causal_continuity_valid")
        else:
            blockers.extend(report.missing_causes)
            blockers.extend(report.missing_consequences)
            blockers.extend(report.orphan_events)

        if report.checked_causal_node_ids:
            passed.append("causal_nodes_checked")
        else:
            warnings.append("no causal nodes checked")

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

    def summarize_report(self, *, report: CausalContinuityReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "report_id": report.report_id,
                "valid": report.valid,
                "checked_causal_node_count": len(report.checked_causal_node_ids),
                "missing_cause_count": len(report.missing_causes),
                "missing_consequence_count": len(report.missing_consequences),
                "orphan_event_count": len(report.orphan_events),
                "warning_count": len(report.warnings),
            },
        }

    def _build_causal_index(self, *, story_context: Dict[str, Any]) -> Dict[str, Any]:
        causal = story_context.get("causal_context", {}) if isinstance(story_context.get("causal_context", {}), dict) else {}
        obligations = story_context.get("causal_obligations", []) if isinstance(story_context.get("causal_obligations", []), list) else []

        required_nodes = []
        required_consequences = []

        for item in obligations:
            if item.get("obligation_type") in {"causal_node", "handoff_causal_node"} and item.get("id"):
                required_nodes.append(item["id"])
            if item.get("obligation_type") == "consequence" and item.get("id"):
                required_consequences.append(item["id"])

        required_nodes.extend(causal.get("required_causal_node_ids", []))
        required_nodes.extend(causal.get("handoff_causal_node_ids", []))
        required_consequences.extend(causal.get("required_consequence_ids", []))
        required_consequences.extend(causal.get("handoff_consequence_ids", []))

        return {
            "required_causal_node_ids": self._unique(required_nodes),
            "required_consequence_ids": self._unique(required_consequences),
            "causal_chains": causal.get("causal_chains", {}),
            "causal_graphs": causal.get("causal_graphs", {}),
            "consequence_queue": causal.get("consequence_queue", {}),
        }

    def _checked_causal_nodes(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        story_context: Dict[str, Any],
    ) -> List[str]:
        values = []

        # Only real structured links count as checked causal nodes.
        # Blueprint stake text may mention a cause, but that alone should not
        # make an unsupported choice causally valid.
        for beat in scene_beats:
            values.extend(beat.causal_links)

        for obligation in story_context.get("causal_obligations", []):
            if obligation.get("obligation_type") in {"causal_node", "handoff_causal_node"} and obligation.get("id"):
                values.append(obligation["id"])

        # Do not add causal_context.required_causal_node_ids here.
        # Those are requirements, not proof that the scene actually supports them.
        # A required cause is only "checked" when it appears in scene beat links
        # or in explicit causal obligations.

        return self._unique(values)

    def _checked_consequences(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        story_context: Dict[str, Any],
    ) -> List[str]:
        values = []

        for obligation in story_context.get("causal_obligations", []):
            if obligation.get("obligation_type") == "consequence" and obligation.get("id"):
                values.append(obligation["id"])

        for beat in scene_beats:
            if beat.beat_type == "consequence":
                values.extend(self._extract_ids(beat.purpose, prefixes=["cons_"]))
                values.extend([item for item in beat.causal_links if item.startswith("cons_")])

        for stake in blueprint.stakes:
            values.extend(self._extract_ids(stake, prefixes=["cons_"]))

        return self._unique(values)

    def _missing_causes(
        self,
        *,
        checked_causal_node_ids: List[str],
        causal_index: Dict[str, Any],
    ) -> List[str]:
        required = set(causal_index.get("required_causal_node_ids", []))
        checked = set(checked_causal_node_ids)
        return sorted(required - checked)

    def _missing_consequences(
        self,
        *,
        checked_consequence_ids: List[str],
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        relationship_beats: List[RelationshipBeat],
    ) -> List[str]:
        # A consequence is considered covered if it appears in checked IDs,
        # a consequence beat exists, or relationship beats include expected shifts.
        missing = []
        has_consequence_beat = any(beat.beat_type == "consequence" for beat in scene_beats)
        has_relationship_shift = any(bool(beat.expected_end_state_shift) for beat in relationship_beats)

        for consequence_id in checked_consequence_ids:
            if has_consequence_beat or has_relationship_shift or consequence_id in " ".join(blueprint.stakes):
                continue
            missing.append(consequence_id)

        return self._unique(missing)

    def _orphan_events(
        self,
        *,
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat],
        checked_causal_node_ids: List[str],
    ) -> List[str]:
        orphan = []

        causal_set = set(checked_causal_node_ids)

        for beat in scene_beats:
            if beat.beat_type in {"choice", "consequence", "ending_hook"}:
                # Choice/consequence/hook beats must carry their own causal link.
                # A cause existing elsewhere in the scene is not enough.
                if not beat.causal_links:
                    orphan.append(beat.beat_id)

        for beat in dialogue_beats:
            text = " ".join(
                [
                    beat.surface_meaning or "",
                    beat.hidden_meaning or "",
                    beat.relationship_effect or "",
                ]
            )
            has_event_word = any(word in text.lower() for word in ["reveals", "exposes", "betrays", "kills", "confesses"])
            if has_event_word and not causal_set:
                orphan.append(beat.dialogue_beat_id)

        return self._unique(orphan)

    def _warnings(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat],
        dialogue_beats: List[DialogueBeat],
        relationship_beats: List[RelationshipBeat],
        knowledge_report: KnowledgeBoundaryReport | None,
        causal_index: Dict[str, Any],
    ) -> List[str]:
        warnings = []

        if not causal_index.get("required_causal_node_ids") and not causal_index.get("required_consequence_ids"):
            warnings.append("No required causal nodes or consequences found; validator has limited signal.")

        if blueprint.ending_hook and not any(beat.beat_type == "ending_hook" for beat in scene_beats):
            warnings.append("Blueprint has ending hook but no ending hook beat.")

        if not any(beat.beat_type == "choice" for beat in scene_beats):
            warnings.append("No choice beat found; agency may be weak.")

        if relationship_beats and not any(beat.expected_end_state_shift for beat in relationship_beats):
            warnings.append("Relationship beats exist but no expected relationship state shift is present.")

        if knowledge_report and not knowledge_report.valid:
            warnings.append("Knowledge boundary report is invalid; causal validation may be affected by impossible knowledge.")

        if not dialogue_beats:
            warnings.append("No dialogue beats supplied; dialogue causality was not checked.")

        return warnings

    def _extract_ids(self, text: str, prefixes: List[str]) -> List[str]:
        values = []
        for raw in str(text).split():
            token = raw.strip(".,:;()[]{}")
            if any(token.startswith(prefix) for prefix in prefixes):
                values.append(token)
        return values

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
