from typing import Any, Dict, List, Optional

from backend.app.engines.simulation.cast_selection_engine import CastSelectionEngine
from backend.app.engines.simulation.causal_chain_explanation_engine import CausalChainExplanationEngine
from backend.app.engines.simulation.consequence_queue_engine import ConsequenceQueueEngine
from backend.app.engines.simulation.consequence_resolver import ConsequenceResolver
from backend.app.engines.simulation.conflict_resolution_engine import ConflictResolutionEngine
from backend.app.engines.simulation.emotional_carryover_engine import EmotionalCarryoverEngine
from backend.app.engines.simulation.event_engine import EventEngine
from backend.app.engines.simulation.genre_adaptation_ml_hook_engine import GenreAdaptationMLHookEngine
from backend.app.engines.simulation.handoff_payload_engine import HandoffPayloadEngine
from backend.app.engines.simulation.stakes_engine import StakesEngine
from backend.app.engines.simulation.tension_curve_engine import TensionCurveEngine


class InteractionSimulationOrchestrator:
    """Coordinates Chunk 4 simulation engines into one usable interaction pipeline.

    This orchestrator does not replace specialized engines. It sequences them:
    cast -> event -> stakes -> tension -> conflict -> consequence -> causal graph
    -> handoff payload -> generation control.
    """

    engine_name = "simulation.interaction_simulation_orchestrator"

    def __init__(self) -> None:
        self.cast_engine = CastSelectionEngine()
        self.event_engine = EventEngine()
        self.stakes_engine = StakesEngine()
        self.tension_engine = TensionCurveEngine()
        self.conflict_engine = ConflictResolutionEngine()
        self.consequence_queue_engine = ConsequenceQueueEngine()
        self.consequence_resolver = ConsequenceResolver()
        self.causal_engine = CausalChainExplanationEngine()
        self.emotional_engine = EmotionalCarryoverEngine()
        self.handoff_engine = HandoffPayloadEngine()
        self.genre_engine = GenreAdaptationMLHookEngine()

    def create_simulation_run_record(
        self,
        *,
        run_id: str,
        story_request: Dict[str, Any],
        selected_character_ids: List[str] | None = None,
        event_ids: List[str] | None = None,
        status: str = "created",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return {
            "run_id": run_id,
            "story_request": story_request,
            "selected_character_ids": selected_character_ids or [],
            "event_ids": event_ids or [],
            "status": status,
            "steps": [],
            "outputs": {},
            "warnings": [],
            "errors": [],
            "metadata": metadata or {},
        }

    def register_run_on_state(
        self,
        *,
        state: Any,
        run_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        run_id = run_record["run_id"]
        state.metadata.setdefault("simulation_runs", {})[run_id] = dict(run_record)
        state.metadata.setdefault("simulation_run_history", []).append(
            {
                "action": "register_run",
                "run_id": run_id,
                "status": run_record.get("status"),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "updated_state": state,
        }

    def run_interaction_simulation(
        self,
        *,
        state: Any,
        run_id: str,
        story_request: Dict[str, Any],
        event_specs: List[Dict[str, Any]] | None = None,
        candidate_ids: List[str] | None = None,
        target_cast_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        run_record = self.create_simulation_run_record(
            run_id=run_id,
            story_request=story_request,
            status="running",
        )
        self.register_run_on_state(state=state, run_record=run_record)

        outputs: Dict[str, Any] = {}
        warnings: List[str] = []
        errors: List[str] = []

        # 1. Cast selection
        cast_result = self.cast_engine.select_cast(
            state=state,
            story_request={
                **story_request,
                "cast_id": story_request.get("cast_id", f"cast_{run_id}"),
            },
            candidate_ids=candidate_ids,
            target_cast_size=target_cast_size,
            allow_any_size=story_request.get("allow_any_character_count", True),
        )
        outputs["cast_selection"] = cast_result
        warnings.extend(cast_result.get("warnings", []))

        cast_record = cast_result["cast_record"]
        self.cast_engine.register_cast_on_state(state=state, cast_record=cast_record)
        selected_character_ids = cast_record.get("selected_character_ids", [])
        run_record["selected_character_ids"] = selected_character_ids
        run_record["steps"].append("cast_selected")

        # 2. Event creation/registration
        registered_event_ids = []
        for idx, spec in enumerate(event_specs or []):
            event = self.event_engine.create_event_record(
                event_id=spec.get("event_id", f"evt_{run_id}_{idx}"),
                event_type=spec.get("event_type", "public_event"),
                event_name=spec.get("event_name", spec.get("summary", "Simulation event.")),
                actor_ids=spec.get("actor_ids", selected_character_ids[:1]),
                target_ids=spec.get("target_ids", selected_character_ids[1:2]),
                witness_ids=spec.get("witness_ids", []),
                involved_faction_ids=spec.get("involved_faction_ids", []),
                location_id=spec.get("location_id"),
                visibility=spec.get("visibility", "private"),
                intensity=spec.get("intensity", 0.5),
                branch_id=spec.get("branch_id"),
                timeline_id=spec.get("timeline_id"),
                source_choice_id=spec.get("source_choice_id"),
                linked_secret_ids=spec.get("linked_secret_ids", []),
                linked_evidence_ids=spec.get("linked_evidence_ids", []),
                linked_rumor_ids=spec.get("linked_rumor_ids", []),
                linked_obligation_ids=spec.get("linked_obligation_ids", []),
                linked_leverage_ids=spec.get("linked_leverage_ids", []),
                linked_bargain_ids=spec.get("linked_bargain_ids", []),
                metadata=spec.get("metadata", {}),
            )

            registered = self.event_engine.register_event_on_state(
                state=state,
                event_record=event,
                validate=spec.get("validate", True),
            )

            if registered.get("success"):
                registered_event_ids.append(event["event_id"])
            else:
                errors.extend(registered.get("validation", {}).get("blockers", []))

        run_record["event_ids"] = registered_event_ids
        outputs["registered_event_ids"] = registered_event_ids
        run_record["steps"].append("events_registered")

        # 3. Stakes evaluation for events
        stakes_ids = []
        for event_id in registered_event_ids:
            event = state.metadata.get("event_registry", {}).get(event_id)
            if not event:
                continue
            stakes_result = self.stakes_engine.evaluate_event_stakes(state=state, event_record=event)
            stakes_record = stakes_result["stakes_record"]
            self.stakes_engine.register_stakes_on_state(state=state, stakes_record=stakes_record)
            stakes_ids.append(stakes_record["stakes_id"])
            warnings.extend(stakes_result.get("warnings", []))

        outputs["stakes_ids"] = stakes_ids
        run_record["steps"].append("stakes_scored")

        # 4. Scene tension curve
        event_records = [state.metadata["event_registry"][eid] for eid in registered_event_ids]
        stakes_records = [state.metadata["stakes_registry"][sid] for sid in stakes_ids]
        tension_result = self.tension_engine.evaluate_scene_tension(
            scene_id=story_request.get("scene_id", f"scene_{run_id}"),
            event_records=event_records,
            stakes_records=stakes_records,
        )
        tension_curve = tension_result["tension_curve"]
        self.tension_engine.register_tension_curve_on_state(state=state, curve=tension_curve)
        outputs["tension_curve_id"] = tension_curve["curve_id"]
        warnings.extend(tension_curve.get("warnings", []))
        run_record["steps"].append("tension_curve_built")

        # 5. Optional conflict creation from request
        conflict_ids = []
        for idx, conflict_spec in enumerate(story_request.get("conflicts", [])):
            conflict = self.conflict_engine.create_conflict_record(
                conflict_id=conflict_spec.get("conflict_id", f"conflict_{run_id}_{idx}"),
                conflict_type=conflict_spec.get("conflict_type", "relationship"),
                title=conflict_spec.get("title", "Simulation conflict"),
                participant_ids=conflict_spec.get("participant_ids", selected_character_ids[:2]),
                source_event_id=conflict_spec.get("source_event_id", registered_event_ids[0] if registered_event_ids else None),
                source_choice_id=conflict_spec.get("source_choice_id"),
                core_issue=conflict_spec.get("core_issue", ""),
                opposing_goals=conflict_spec.get("opposing_goals", {}),
                linked_secret_ids=conflict_spec.get("linked_secret_ids", []),
                linked_evidence_ids=conflict_spec.get("linked_evidence_ids", []),
                linked_obligation_ids=conflict_spec.get("linked_obligation_ids", []),
                linked_leverage_ids=conflict_spec.get("linked_leverage_ids", []),
                linked_bargain_ids=conflict_spec.get("linked_bargain_ids", []),
                linked_faction_ids=conflict_spec.get("linked_faction_ids", []),
                intensity=conflict_spec.get("intensity", 0.6),
                stakes_score=conflict_spec.get("stakes_score", 0.6),
                tension_score=conflict_spec.get("tension_score", 0.6),
                moral_complexity=conflict_spec.get("moral_complexity", 0.5),
            )
            self.conflict_engine.register_conflict_on_state(state=state, conflict_record=conflict)
            conflict_ids.append(conflict["conflict_id"])

        outputs["conflict_ids"] = conflict_ids
        run_record["steps"].append("conflicts_registered")

        # 6. Emotional carryover from events
        carryover_ids = []
        for event_id in registered_event_ids:
            event = state.metadata.get("event_registry", {}).get(event_id)
            generated = self.emotional_engine.generate_carryover_from_event(state=state, event_record=event)
            for record in generated.get("carryover_records", []):
                self.emotional_engine.register_carryover_on_state(state=state, carryover_record=record)
                carryover_ids.append(record["carryover_id"])

        outputs["emotional_carryover_ids"] = carryover_ids
        run_record["steps"].append("emotional_carryover_generated")

        # 7. Consequence queue from registered events
        consequence_ids = []
        for event_id in registered_event_ids:
            event = state.metadata.get("event_registry", {}).get(event_id)
            consequence = self.consequence_queue_engine.create_consequence_record(
                consequence_id=f"cons_{event_id}_fallout",
                consequence_type=self._consequence_type_from_event(event),
                source_event_id=event_id,
                source_choice_id=event.get("source_choice_id"),
                summary=f"Fallout from {event.get('event_name', event_id)}.",
                affected_entity_ids=self._unique(event.get("actor_ids", []) + event.get("target_ids", [])),
                trigger_type="immediate",
                severity=event.get("intensity", 0.5),
                payload={
                    "action_type": event.get("event_type"),
                    "secret_ids": event.get("linked_secret_ids", []),
                    "evidence_ids": event.get("linked_evidence_ids", []),
                    "rumor_ids": event.get("linked_rumor_ids", []),
                },
            )
            self.consequence_queue_engine.register_consequence_on_state(
                state=state,
                consequence_record=consequence,
            )
            consequence_ids.append(consequence["consequence_id"])

        outputs["consequence_ids"] = consequence_ids
        run_record["steps"].append("consequences_queued")

        # 8. Resolve ready consequences and build causal graphs.
        resolved_consequence_ids = []
        causal_graph_ids = []
        for consequence_id in consequence_ids:
            resolved = self.consequence_resolver.resolve_ready_consequence(
                state=state,
                consequence_id=consequence_id,
            )
            if not resolved.get("success"):
                warnings.extend(resolved.get("errors", []))
                continue

            resolved_consequence_ids.append(consequence_id)
            graph_id = f"graph_{consequence_id}"
            graph_result = self.causal_engine.build_graph_from_consequence_batch(
                state=state,
                graph_id=graph_id,
                consequence_id=consequence_id,
                delta_batch=resolved["delta_batch"],
            )
            if graph_result.get("success"):
                causal_graph_ids.append(graph_id)

        outputs["resolved_consequence_ids"] = resolved_consequence_ids
        outputs["causal_graph_ids"] = causal_graph_ids
        run_record["steps"].append("consequences_resolved_and_causal_graphs_built")

        # 9. Handoff payloads
        scene_payload_result = self.handoff_engine.build_scene_payload(
            state=state,
            payload_id=f"scene_payload_{run_id}",
            scene_id=story_request.get("scene_id", f"scene_{run_id}"),
            selected_character_ids=selected_character_ids,
            event_ids=registered_event_ids,
            consequence_ids=consequence_ids,
            conflict_ids=conflict_ids,
            stakes_ids=stakes_ids,
            tension_curve_ids=[tension_curve["curve_id"]],
            cast_id=cast_record["cast_id"],
            output_format=story_request.get("format", "scene"),
            story_request=story_request,
            scene_goal=story_request.get("scene_goal", "Simulate a meaningful character interaction."),
            location_id=story_request.get("location_id"),
        )

        plot_payload_result = self.handoff_engine.build_plot_payload(
            state=state,
            payload_id=f"plot_payload_{run_id}",
            plot_arc_id=story_request.get("plot_arc_id", f"arc_{run_id}"),
            selected_character_ids=selected_character_ids,
            scene_payloads=[scene_payload_result["payload"]],
            conflict_ids=conflict_ids,
            stakes_ids=stakes_ids,
            tension_curve_ids=[tension_curve["curve_id"]],
            cast_id=cast_record["cast_id"],
            output_format=story_request.get("format", "novel"),
            story_request=story_request,
            plot_goal=story_request.get("plot_goal", "Generate a causally coherent story beat."),
        )

        handoff_package_result = self.handoff_engine.build_master_handoff_package(
            state=state,
            package_id=f"handoff_{run_id}",
            story_request=story_request,
            cast_id=cast_record["cast_id"],
            scene_payloads=[scene_payload_result["payload"]],
            plot_payload=plot_payload_result["payload"],
            dialogue_payloads=[],
        )

        outputs["scene_payload_id"] = scene_payload_result["payload"]["payload_id"]
        outputs["plot_payload_id"] = plot_payload_result["payload"]["payload_id"]
        outputs["handoff_package_id"] = handoff_package_result["package"]["package_id"]
        warnings.extend(scene_payload_result.get("warnings", []))
        warnings.extend(plot_payload_result.get("warnings", []))
        warnings.extend(handoff_package_result.get("warnings", []))
        run_record["steps"].append("handoff_payloads_built")

        # 10. Genre / adaptation control
        genre_profile = self.genre_engine.create_genre_profile(
            profile_id=f"genre_{run_id}",
            primary_genres=story_request.get("primary_genres", ["drama"]),
            secondary_genres=story_request.get("secondary_genres", []),
            tone_tags=story_request.get("tone_tags", []),
            taboo_or_avoid_tags=story_request.get("avoid_tags", []),
            intensity_targets=story_request.get("intensity_targets", {}),
            convention_targets=story_request.get("convention_targets", {}),
        )
        adaptation_profile = self.genre_engine.create_adaptation_profile(
            adaptation_id=f"adapt_{run_id}",
            output_format=story_request.get("format", "novel"),
            target_length=story_request.get("target_length"),
            pov_mode=story_request.get("pov_mode", "third_person_limited"),
            prose_density=story_request.get("prose_density", 0.6),
            dialogue_density=story_request.get("dialogue_density", 0.5),
            scene_count_target=story_request.get("scene_count_target"),
            episode_count_target=story_request.get("episode_count_target"),
            chapter_count_target=story_request.get("chapter_count_target"),
            visuality_target=story_request.get("visuality_target", 0.5),
            interiority_target=story_request.get("interiority_target", 0.5),
        )
        generation_control_result = self.genre_engine.build_generation_control_payload(
            payload_id=f"generation_control_{run_id}",
            story_request=story_request,
            genre_profile=genre_profile,
            adaptation_profile=adaptation_profile,
            handoff_package=handoff_package_result["package"],
            learning_hooks=[],
        )
        self.genre_engine.register_generation_control_on_state(
            state=state,
            payload=generation_control_result["payload"],
        )

        outputs["generation_control_payload_id"] = generation_control_result["payload"]["payload_id"]
        warnings.extend(generation_control_result.get("warnings", []))
        run_record["steps"].append("generation_control_built")

        # Finalize run
        run_record["status"] = "completed" if not errors else "completed_with_errors"
        run_record["outputs"] = outputs
        run_record["warnings"] = self._unique(warnings)
        run_record["errors"] = self._unique(errors)

        state.metadata["simulation_runs"][run_id] = run_record
        state.metadata.setdefault("simulation_run_history", []).append(
            {
                "action": "complete_run",
                "run_id": run_id,
                "status": run_record["status"],
                "step_count": len(run_record["steps"]),
                "warning_count": len(run_record["warnings"]),
                "error_count": len(run_record["errors"]),
            }
        )

        return {
            "success": len(errors) == 0,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "run_record": run_record,
            "updated_state": state,
        }

    def build_orchestrator_summary(self, *, state: Any, run_id: str) -> Dict[str, Any]:
        run = state.metadata.get("simulation_runs", {}).get(run_id)
        if not run:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": [f"simulation run {run_id} not found"],
            }

        outputs = run.get("outputs", {})
        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "status": run.get("status"),
            "step_count": len(run.get("steps", [])),
            "steps": run.get("steps", []),
            "selected_character_ids": run.get("selected_character_ids", []),
            "event_ids": run.get("event_ids", []),
            "consequence_ids": outputs.get("consequence_ids", []),
            "causal_graph_ids": outputs.get("causal_graph_ids", []),
            "handoff_package_id": outputs.get("handoff_package_id"),
            "generation_control_payload_id": outputs.get("generation_control_payload_id"),
            "warning_count": len(run.get("warnings", [])),
            "error_count": len(run.get("errors", [])),
            "ready_for_chunk5_generation": (
                bool(outputs.get("handoff_package_id"))
                and bool(outputs.get("generation_control_payload_id"))
                and run.get("status") in {"completed", "completed_with_errors"}
            ),
        }

    def build_orchestrator_map(self, *, state: Any) -> Dict[str, Any]:
        runs = state.metadata.get("simulation_runs", {})
        records = {}

        for run_id, run in runs.items():
            summary = self.build_orchestrator_summary(state=state, run_id=run_id)
            records[run_id] = {
                "run_id": run_id,
                "status": summary.get("status"),
                "step_count": summary.get("step_count", 0),
                "selected_character_count": len(summary.get("selected_character_ids", [])),
                "event_count": len(summary.get("event_ids", [])),
                "ready_for_chunk5_generation": summary.get("ready_for_chunk5_generation", False),
                "warning_count": summary.get("warning_count", 0),
                "error_count": summary.get("error_count", 0),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_count": len(records),
            "run_records": records,
            "ready_run_count": sum(1 for record in records.values() if record["ready_for_chunk5_generation"]),
            "warnings": [] if records else ["no simulation runs registered"],
        }

    def _consequence_type_from_event(self, event: Dict[str, Any]) -> str:
        family = event.get("event_family")
        event_type = event.get("event_type")

        if family == "relationship" or event_type in {"betrayal", "private_confession", "repair_attempt"}:
            return "relationship"
        if family == "knowledge" or event.get("linked_secret_ids") or event.get("linked_evidence_ids"):
            return "knowledge"
        if family == "obligation":
            return "obligation"
        if family == "leverage":
            return "leverage"
        if event.get("visibility") == "public":
            return "reputation"
        return "plot_hook"

    def _unique(self, values: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for value in values:
            if value is None:
                continue
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result
