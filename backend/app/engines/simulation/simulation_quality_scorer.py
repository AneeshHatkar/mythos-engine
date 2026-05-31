from typing import Any, Dict, List, Optional


class SimulationQualityScorer:
    """Scores simulation quality before story generation.

    This checks whether a Chunk 4 run is ready for Chunk 5:
    causality, cast, relationships, emotional carryover, stakes, tension,
    conflicts, consequences, handoff payloads, and generation controls.
    """

    engine_name = "simulation.simulation_quality_scorer"

    QUALITY_DIMENSIONS = {
        "causal_coherence",
        "character_readiness",
        "relationship_continuity",
        "emotional_continuity",
        "stakes_clarity",
        "tension_pacing",
        "conflict_usefulness",
        "consequence_traceability",
        "cast_balance",
        "handoff_readiness",
        "generation_control_readiness",
        "overall",
    }

    def score_simulation_run(
        self,
        *,
        state: Any,
        run_id: str,
    ) -> Dict[str, Any]:
        run = state.metadata.get("simulation_runs", {}).get(run_id)
        if not run:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": [f"simulation run {run_id} not found"],
            }

        outputs = run.get("outputs", {})
        selected_character_ids = run.get("selected_character_ids", [])
        event_ids = run.get("event_ids", [])

        dimension_scores = {
            "causal_coherence": self.score_causal_coherence(state=state, run=run),
            "character_readiness": self.score_character_readiness(state=state, selected_character_ids=selected_character_ids),
            "relationship_continuity": self.score_relationship_continuity(state=state, selected_character_ids=selected_character_ids),
            "emotional_continuity": self.score_emotional_continuity(state=state, selected_character_ids=selected_character_ids),
            "stakes_clarity": self.score_stakes_clarity(state=state, stakes_ids=outputs.get("stakes_ids", [])),
            "tension_pacing": self.score_tension_pacing(state=state, tension_curve_id=outputs.get("tension_curve_id")),
            "conflict_usefulness": self.score_conflict_usefulness(state=state, conflict_ids=outputs.get("conflict_ids", [])),
            "consequence_traceability": self.score_consequence_traceability(state=state, consequence_ids=outputs.get("consequence_ids", [])),
            "cast_balance": self.score_cast_balance(state=state, cast_id=run.get("story_request", {}).get("cast_id")),
            "handoff_readiness": self.score_handoff_readiness(state=state, handoff_package_id=outputs.get("handoff_package_id")),
            "generation_control_readiness": self.score_generation_control_readiness(
                state=state,
                generation_control_payload_id=outputs.get("generation_control_payload_id"),
            ),
        }

        overall = self._weighted_overall(dimension_scores)
        blockers = self._quality_blockers(dimension_scores, run)
        warnings = self._quality_warnings(dimension_scores, run)

        report = {
            "quality_report_id": f"quality_{run_id}",
            "run_id": run_id,
            "dimension_scores": dimension_scores,
            "overall_quality_score": overall,
            "quality_label": self._quality_label(overall, blockers),
            "ready_for_generation": overall >= 0.60 and not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "recommendations": self._recommendations(dimension_scores, blockers, warnings),
        }

        state.metadata.setdefault("simulation_quality_reports", {})[report["quality_report_id"]] = report
        state.metadata.setdefault("simulation_quality_history", []).append(
            {
                "action": "score_simulation_run",
                "quality_report_id": report["quality_report_id"],
                "run_id": run_id,
                "overall_quality_score": overall,
                "quality_label": report["quality_label"],
                "ready_for_generation": report["ready_for_generation"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "quality_report": report,
            "updated_state": state,
        }

    def score_causal_coherence(self, *, state: Any, run: Dict[str, Any]) -> float:
        outputs = run.get("outputs", {})
        graph_ids = outputs.get("causal_graph_ids", [])
        if not graph_ids:
            return 0.25

        scores = []
        for graph_id in graph_ids:
            graph = state.metadata.get("causal_graphs", {}).get(graph_id, {})
            nodes = graph.get("nodes", {})
            edges = graph.get("edges", {})
            if not nodes:
                scores.append(0.2)
                continue
            density = min(1.0, len(edges) / max(1, len(nodes)))
            has_consequence = any(node.get("node_type") == "consequence" for node in nodes.values())
            has_delta = any(node.get("node_type") == "delta" for node in nodes.values())
            score = 0.35 + density * 0.35 + (0.15 if has_consequence else 0.0) + (0.15 if has_delta else 0.0)
            scores.append(min(1.0, score))

        return self._average(scores)

    def score_character_readiness(self, *, state: Any, selected_character_ids: List[str]) -> float:
        if not selected_character_ids:
            return 0.0

        scores = []
        for cid in selected_character_ids:
            character = state.character_states.get(cid)
            if not character:
                scores.append(0.0)
                continue

            metadata = character.metadata or {}
            score = 0.30
            if metadata.get("display_name") or metadata.get("name"):
                score += 0.10
            if metadata.get("role_tags") or metadata.get("archetype_tags"):
                score += 0.12
            if metadata.get("story_function_tags"):
                score += 0.12
            if metadata.get("backstory") or metadata.get("backstory_summary") or metadata.get("backstory_depth", 0) >= 0.5:
                score += 0.16
            if metadata.get("goals") or metadata.get("psychology"):
                score += 0.12
            if metadata.get("voice_profile"):
                score += 0.08

            scores.append(min(1.0, score))

        return self._average(scores)

    def score_relationship_continuity(self, *, state: Any, selected_character_ids: List[str]) -> float:
        if len(selected_character_ids) < 2:
            return 0.55

        selected = set(selected_character_ids)
        possible_pairs = len(selected) * (len(selected) - 1) / 2
        relationship_count = 0
        detailed_count = 0

        for rel in state.relationship_states.values():
            if rel.character_a_id in selected and rel.character_b_id in selected:
                relationship_count += 1
                if (
                    rel.trust != 0.5
                    or rel.affection > 0
                    or rel.resentment > 0
                    or rel.rivalry > 0
                    or rel.betrayal_risk > 0
                    or rel.repair_potential > 0
                ):
                    detailed_count += 1

        coverage = min(1.0, relationship_count / max(1, possible_pairs))
        detail = min(1.0, detailed_count / max(1, relationship_count)) if relationship_count else 0.0

        return round(coverage * 0.55 + detail * 0.45, 3)

    def score_emotional_continuity(self, *, state: Any, selected_character_ids: List[str]) -> float:
        if not selected_character_ids:
            return 0.0

        registry = state.metadata.get("emotional_carryover_registry", {})
        if not registry:
            return 0.45

        active_by_character = {
            cid: [
                record for record in registry.values()
                if record.get("character_id") == cid and record.get("status") != "resolved"
            ]
            for cid in selected_character_ids
        }

        coverage = sum(1 for records in active_by_character.values() if records) / max(1, len(selected_character_ids))
        intensity_quality = self._average([
            min(1.0, self._average([float(r.get("intensity", 0.0)) for r in records]))
            for records in active_by_character.values()
            if records
        ])

        return round(0.45 + coverage * 0.30 + intensity_quality * 0.25, 3)

    def score_stakes_clarity(self, *, state: Any, stakes_ids: List[str]) -> float:
        if not stakes_ids:
            return 0.30

        scores = []
        for sid in stakes_ids:
            record = state.metadata.get("stakes_registry", {}).get(sid, {})
            if not record:
                scores.append(0.0)
                continue
            values = record.get("stake_values", {})
            score = 0.25
            if values:
                score += 0.25
            if record.get("dominant_stake_type"):
                score += 0.18
            if record.get("overall_stakes_score", 0.0) >= 0.4:
                score += 0.18
            if record.get("summary"):
                score += 0.14
            scores.append(min(1.0, score))

        return self._average(scores)

    def score_tension_pacing(self, *, state: Any, tension_curve_id: Optional[str]) -> float:
        if not tension_curve_id:
            return 0.30

        curve = state.metadata.get("tension_curves", {}).get(tension_curve_id)
        if not curve:
            return 0.20

        pacing = float(curve.get("pacing_score", 0.0))
        average = float(curve.get("average_tension", 0.0))
        peak = float(curve.get("peak_tension", 0.0))
        label = curve.get("curve_label")

        score = pacing * 0.55 + min(1.0, average + 0.15) * 0.20 + min(1.0, peak) * 0.15
        if label in {"balanced", "rising", "spiking", "volatile"}:
            score += 0.10
        if label in {"flat", "overloaded"}:
            score -= 0.12

        return round(max(0.0, min(1.0, score)), 3)

    def score_conflict_usefulness(self, *, state: Any, conflict_ids: List[str]) -> float:
        if not conflict_ids:
            return 0.45

        scores = []
        for cid in conflict_ids:
            conflict = state.metadata.get("conflict_registry", {}).get(cid, {})
            if not conflict:
                scores.append(0.0)
                continue
            score = 0.25
            if conflict.get("participant_ids"):
                score += 0.12
            if conflict.get("core_issue"):
                score += 0.16
            if conflict.get("opposing_goals"):
                score += 0.16
            if conflict.get("conflict_pressure", 0.0) >= 0.45:
                score += 0.16
            if conflict.get("status") in {"active", "escalated", "compromised", "unresolved", "transformed"}:
                score += 0.10
            if conflict.get("linked_secret_ids") or conflict.get("linked_evidence_ids") or conflict.get("linked_obligation_ids"):
                score += 0.05
            scores.append(min(1.0, score))

        return self._average(scores)

    def score_consequence_traceability(self, *, state: Any, consequence_ids: List[str]) -> float:
        if not consequence_ids:
            return 0.35

        scores = []
        for cid in consequence_ids:
            consequence = state.metadata.get("consequence_queue", {}).get(cid, {})
            if not consequence:
                scores.append(0.0)
                continue

            score = 0.25
            if consequence.get("source_event_id") or consequence.get("source_choice_id"):
                score += 0.20
            if consequence.get("affected_entity_ids"):
                score += 0.12
            if consequence.get("summary"):
                score += 0.12
            if consequence.get("severity", 0.0) > 0:
                score += 0.10
            if consequence.get("status") in {"ready", "triggered", "resolved"}:
                score += 0.10
            if consequence.get("metadata", {}).get("generated_delta_count", 0) > 0:
                score += 0.11
            scores.append(min(1.0, score))

        return self._average(scores)

    def score_cast_balance(self, *, state: Any, cast_id: Optional[str]) -> float:
        if not cast_id:
            return 0.35

        cast = state.metadata.get("cast_registry", {}).get(cast_id)
        if not cast:
            return 0.20

        ensemble = cast.get("ensemble_report", {})
        score = (
            float(ensemble.get("ensemble_score", 0.0)) * 0.50
            + float(ensemble.get("diversity_score", 0.0)) * 0.20
            + float(ensemble.get("role_coverage", 0.0)) * 0.15
            + float(ensemble.get("function_coverage", 0.0)) * 0.15
        )
        return round(max(0.0, min(1.0, score)), 3)

    def score_handoff_readiness(self, *, state: Any, handoff_package_id: Optional[str]) -> float:
        if not handoff_package_id:
            return 0.0

        package = state.metadata.get("handoff_packages", {}).get(handoff_package_id)
        if not package:
            return 0.0

        score = 0.25
        if package.get("cast"):
            score += 0.15
        if package.get("plot_payload"):
            score += 0.18
        if package.get("scene_payloads"):
            score += 0.18
        if package.get("generation_contract", {}).get("preserve_causal_continuity"):
            score += 0.12
        if package.get("quality_targets"):
            score += 0.12

        return round(min(1.0, score), 3)

    def score_generation_control_readiness(self, *, state: Any, generation_control_payload_id: Optional[str]) -> float:
        if not generation_control_payload_id:
            return 0.0

        payload = state.metadata.get("generation_control_payloads", {}).get(generation_control_payload_id)
        if not payload:
            return 0.0

        score = 0.25
        if payload.get("genre_profile", {}).get("primary_genres"):
            score += 0.16
        if payload.get("adaptation_profile", {}).get("output_format"):
            score += 0.16
        if payload.get("format_contract"):
            score += 0.12
        if payload.get("quality_contract"):
            score += 0.14
        if payload.get("anti_genericity_contract", {}).get("must_avoid_generic_plot"):
            score += 0.12
        if payload.get("continuity_contract", {}).get("allow_any_character_count"):
            score += 0.05

        return round(min(1.0, score), 3)

    def build_quality_map(self, *, state: Any) -> Dict[str, Any]:
        reports = state.metadata.get("simulation_quality_reports", {})
        compact = {}

        for report_id, report in reports.items():
            compact[report_id] = {
                "quality_report_id": report_id,
                "run_id": report.get("run_id"),
                "overall_quality_score": report.get("overall_quality_score"),
                "quality_label": report.get("quality_label"),
                "ready_for_generation": report.get("ready_for_generation"),
                "blocker_count": len(report.get("blockers", [])),
                "warning_count": len(report.get("warnings", [])),
            }

        ranked = sorted(compact.values(), key=lambda item: item.get("overall_quality_score", 0.0), reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "quality_report_count": len(compact),
            "quality_reports": compact,
            "best_quality_report": ranked[0] if ranked else None,
            "ready_report_count": sum(1 for item in compact.values() if item.get("ready_for_generation")),
            "warnings": [] if compact else ["no simulation quality reports registered"],
        }

    def _weighted_overall(self, scores: Dict[str, float]) -> float:
        weights = {
            "causal_coherence": 0.13,
            "character_readiness": 0.10,
            "relationship_continuity": 0.09,
            "emotional_continuity": 0.09,
            "stakes_clarity": 0.09,
            "tension_pacing": 0.09,
            "conflict_usefulness": 0.08,
            "consequence_traceability": 0.09,
            "cast_balance": 0.08,
            "handoff_readiness": 0.08,
            "generation_control_readiness": 0.08,
        }
        total = sum(scores.get(key, 0.0) * weight for key, weight in weights.items())
        return round(max(0.0, min(1.0, total)), 3)

    def _quality_blockers(self, scores: Dict[str, float], run: Dict[str, Any]) -> List[str]:
        blockers = []
        if run.get("errors"):
            blockers.append("simulation run has errors")
        if scores.get("handoff_readiness", 0.0) < 0.45:
            blockers.append("handoff package is not ready")
        if scores.get("generation_control_readiness", 0.0) < 0.45:
            blockers.append("generation control payload is not ready")
        if scores.get("character_readiness", 0.0) < 0.30:
            blockers.append("selected characters are underdeveloped")
        return blockers

    def _quality_warnings(self, scores: Dict[str, float], run: Dict[str, Any]) -> List[str]:
        warnings = list(run.get("warnings", []))
        for key, value in scores.items():
            if value < 0.45:
                warnings.append(f"{key} score is weak")
        return self._unique(warnings)

    def _recommendations(self, scores: Dict[str, float], blockers: List[str], warnings: List[str]) -> List[str]:
        recs = []
        if "selected characters are underdeveloped" in blockers or scores.get("character_readiness", 0) < 0.6:
            recs.append("add stronger character metadata: role, backstory, goals, psychology, and voice")
        if scores.get("causal_coherence", 0) < 0.6:
            recs.append("add clearer causal graph links between choices, events, consequences, and deltas")
        if scores.get("relationship_continuity", 0) < 0.6:
            recs.append("add or enrich relationship states between selected cast members")
        if scores.get("emotional_continuity", 0) < 0.6:
            recs.append("add emotional carryover records or activate existing emotional residue")
        if scores.get("stakes_clarity", 0) < 0.6:
            recs.append("increase explicit stakes records for truth, reputation, relationship, or branch costs")
        if scores.get("tension_pacing", 0) < 0.6:
            recs.append("adjust tension curve with escalation, release, or contrast beats")
        if scores.get("conflict_usefulness", 0) < 0.6:
            recs.append("add clearer conflict core issue and opposing goals")
        if scores.get("handoff_readiness", 0) < 0.6:
            recs.append("rebuild handoff payload package")
        if scores.get("generation_control_readiness", 0) < 0.6:
            recs.append("add genre/adaptation/generation-control payload")
        return self._unique(recs)

    def _quality_label(self, score: float, blockers: List[str]) -> str:
        if blockers:
            return "blocked"
        if score >= 0.85:
            return "excellent"
        if score >= 0.70:
            return "strong"
        if score >= 0.60:
            return "usable"
        if score >= 0.45:
            return "needs_revision"
        return "weak"

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

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
