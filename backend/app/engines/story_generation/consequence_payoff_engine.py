from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CausalContinuityReport,
    ConsequencePayoffPlan,
    RelationshipBeat,
    SceneBeat,
    SceneBlueprint,
)


class ConsequencePayoffEngine:
    """Plans how consequences should be paid off in generated story.

    This keeps long-form stories from forgetting what happened earlier.
    It turns causal/consequence obligations into scene-level payoff plans:
    immediate payoffs, delayed payoffs, relationship payoffs, knowledge payoffs,
    world payoffs, and continuation hooks.
    """

    engine_name = "story_generation.consequence_payoff_engine"

    def build_payoff_plan(
        self,
        *,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        relationship_beats: List[RelationshipBeat] | None = None,
        causal_report: CausalContinuityReport | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        relationship_beats = relationship_beats or []
        story_context = story_context or {}

        source_consequence_ids = self._source_consequence_ids(
            causal_report=causal_report,
            story_context=story_context,
            scene_beats=scene_beats,
            blueprint=blueprint,
        )

        payoff_obligations = self._payoff_obligations(
            source_consequence_ids=source_consequence_ids,
            relationship_beats=relationship_beats,
            story_context=story_context,
        )

        required_scene_beats = self._required_scene_beats(
            source_consequence_ids=source_consequence_ids,
            scene_beats=scene_beats,
            relationship_beats=relationship_beats,
        )

        delayed_payoff_candidates = self._delayed_payoff_candidates(
            source_consequence_ids=source_consequence_ids,
            blueprint=blueprint,
            causal_report=causal_report,
            story_context=story_context,
        )

        plan = ConsequencePayoffPlan(
            payoff_plan_id=f"payoff_plan_{blueprint.scene_id}",
            source_consequence_ids=source_consequence_ids,
            payoff_obligations=payoff_obligations,
            required_scene_beats=required_scene_beats,
            delayed_payoff_candidates=delayed_payoff_candidates,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "consequence_payoff_plan": plan,
            "consequence_payoff_plan_dict": plan.model_dump(mode="json"),
            "warnings": self._warnings(plan=plan, causal_report=causal_report),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.constraint_satisfaction_engine",
                "payload_keys": [
                    "consequence_payoff_plan",
                    "scene_blueprint",
                    "scene_beats",
                    "relationship_beats",
                    "causal_continuity_report",
                    "story_context",
                ],
            },
        }

    def validate_payoff_plan(self, *, plan: ConsequencePayoffPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not plan.payoff_plan_id:
            blockers.append("payoff_plan_id missing")
        else:
            passed.append("payoff_plan_id_present")

        if plan.source_consequence_ids:
            passed.append("source_consequences_present")
        else:
            warnings.append("no source consequences found")

        if plan.payoff_obligations:
            passed.append("payoff_obligations_present")
        elif plan.source_consequence_ids:
            warnings.append("source consequences exist but no payoff obligations were built")

        if plan.required_scene_beats:
            passed.append("required_scene_beats_present")
        elif plan.source_consequence_ids:
            warnings.append("source consequences exist but no required scene beats were built")

        if plan.delayed_payoff_candidates:
            passed.append("delayed_payoff_candidates_present")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def build_open_loop_registry_update(
        self,
        *,
        plan: ConsequencePayoffPlan,
        existing_open_loops: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        existing_open_loops = existing_open_loops or []
        updates = list(existing_open_loops)

        for consequence_id in plan.delayed_payoff_candidates:
            loop_id = f"open_loop_{consequence_id}"
            if not any(item.get("loop_id") == loop_id for item in updates):
                updates.append(
                    {
                        "loop_id": loop_id,
                        "source_consequence_id": consequence_id,
                        "status": "open",
                        "loop_type": "delayed_consequence_payoff",
                        "required_future_payoff": True,
                    }
                )

        for consequence_id in plan.source_consequence_ids:
            if consequence_id not in plan.delayed_payoff_candidates:
                updates.append(
                    {
                        "loop_id": f"paid_or_acknowledged_{consequence_id}",
                        "source_consequence_id": consequence_id,
                        "status": "acknowledged",
                        "loop_type": "scene_payoff",
                        "required_future_payoff": False,
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "open_loop_registry": updates,
            "open_loop_count": len(updates),
        }

    def summarize_payoff_plan(self, *, plan: ConsequencePayoffPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "payoff_plan_id": plan.payoff_plan_id,
                "source_consequence_count": len(plan.source_consequence_ids),
                "payoff_obligation_count": len(plan.payoff_obligations),
                "required_scene_beat_count": len(plan.required_scene_beats),
                "delayed_payoff_count": len(plan.delayed_payoff_candidates),
            },
        }

    def _source_consequence_ids(
        self,
        *,
        causal_report: CausalContinuityReport | None,
        story_context: Dict[str, Any],
        scene_beats: List[SceneBeat],
        blueprint: SceneBlueprint,
    ) -> List[str]:
        values: List[str] = []

        causal_context = story_context.get("causal_context", {})
        if isinstance(causal_context, dict):
            values.extend(causal_context.get("required_consequence_ids", []))
            values.extend(causal_context.get("handoff_consequence_ids", []))

        for obligation in story_context.get("causal_obligations", []):
            if obligation.get("obligation_type") == "consequence" and obligation.get("id"):
                values.append(obligation["id"])

        for beat in scene_beats:
            if beat.beat_type == "consequence":
                values.extend(self._extract_ids(beat.purpose, prefixes=["cons_"]))
                values.extend([item for item in beat.causal_links if item.startswith("cons_")])

        for stake in blueprint.stakes:
            values.extend(self._extract_ids(stake, prefixes=["cons_"]))

        if causal_report:
            values.extend(causal_report.missing_consequences)

        return self._unique(values)

    def _payoff_obligations(
        self,
        *,
        source_consequence_ids: List[str],
        relationship_beats: List[RelationshipBeat],
        story_context: Dict[str, Any],
    ) -> List[str]:
        obligations: List[str] = []

        for consequence_id in source_consequence_ids:
            obligations.append(f"Acknowledge consequence {consequence_id} in action, dialogue, or state change.")

        for relationship in relationship_beats:
            if relationship.expected_end_state_shift:
                obligations.append(
                    f"Reflect relationship shift for {relationship.relationship_id}: {relationship.expected_end_state_shift}."
                )

        knowledge_boundaries = story_context.get("knowledge_boundaries", [])
        for boundary in knowledge_boundaries:
            missing = boundary.get("missing_required_secret_ids", [])
            if missing:
                obligations.append(
                    f"Maintain knowledge consequence for {boundary.get('holder_id')}: missing {', '.join(missing)}."
                )

        return self._unique(obligations)

    def _required_scene_beats(
        self,
        *,
        source_consequence_ids: List[str],
        scene_beats: List[SceneBeat],
        relationship_beats: List[RelationshipBeat],
    ) -> List[str]:
        required: List[str] = []

        consequence_beats = [beat for beat in scene_beats if beat.beat_type == "consequence"]
        if source_consequence_ids and not consequence_beats:
            required.append("add consequence beat")

        for consequence_id in source_consequence_ids:
            matched = any(
                consequence_id in beat.purpose or consequence_id in beat.causal_links
                for beat in scene_beats
            )
            if not matched:
                required.append(f"add beat referencing {consequence_id}")

        if relationship_beats and not any(beat.beat_type == "relationship_pressure" for beat in scene_beats):
            required.append("add relationship pressure payoff beat")

        if relationship_beats and not any(beat.beat_type == "consequence" for beat in scene_beats):
            required.append("add relationship consequence beat")

        return self._unique(required)

    def _delayed_payoff_candidates(
        self,
        *,
        source_consequence_ids: List[str],
        blueprint: SceneBlueprint,
        causal_report: CausalContinuityReport | None,
        story_context: Dict[str, Any],
    ) -> List[str]:
        delayed: List[str] = []

        if causal_report:
            delayed.extend(causal_report.missing_consequences)

        ending_hook_text = blueprint.ending_hook or ""
        for consequence_id in source_consequence_ids:
            if consequence_id not in ending_hook_text and "delayed" in ending_hook_text.lower():
                delayed.append(consequence_id)

        open_loop_context = story_context.get("open_loops", [])
        if isinstance(open_loop_context, list):
            for item in open_loop_context:
                if isinstance(item, dict) and item.get("source_consequence_id"):
                    delayed.append(item["source_consequence_id"])

        return self._unique(delayed)

    def _warnings(
        self,
        *,
        plan: ConsequencePayoffPlan,
        causal_report: CausalContinuityReport | None,
    ) -> List[str]:
        warnings: List[str] = []

        if not plan.source_consequence_ids:
            warnings.append("No source consequences were found for payoff planning.")

        if plan.source_consequence_ids and not plan.payoff_obligations:
            warnings.append("Consequences exist but no payoff obligations were created.")

        if causal_report and not causal_report.valid:
            warnings.append("Causal continuity is invalid; payoff plan may require repair first.")

        if plan.delayed_payoff_candidates:
            warnings.append("Some consequences are delayed and must be tracked in open loops.")

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
