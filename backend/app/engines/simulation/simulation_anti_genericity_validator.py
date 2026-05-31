from typing import Any, Dict, List, Optional


class SimulationAntiGenericityValidator:
    """Detects generic simulation setups before they become generic stories.

    A story can be technically coherent but still boring. This validator checks
    whether the simulation has enough specificity: character wounds, unique
    world rules, non-interchangeable relationships, distinctive user wants,
    concrete stakes, causal consequences, and non-template conflicts.
    """

    engine_name = "simulation.simulation_anti_genericity_validator"

    GENERIC_PHRASES = {
        "save the world",
        "chosen one",
        "dark secret",
        "must choose",
        "ancient evil",
        "forbidden love",
        "powerful artifact",
        "hidden past",
        "ultimate battle",
        "good versus evil",
        "mysterious stranger",
        "destiny awaits",
        "only hope",
        "fight for survival",
        "uncover the truth",
    }

    def validate_simulation_run(
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

        story_request = run.get("story_request", {})
        selected_character_ids = run.get("selected_character_ids", [])
        outputs = run.get("outputs", {})

        checks = {
            "user_specificity": self.check_user_specificity(story_request=story_request),
            "character_specificity": self.check_character_specificity(state=state, character_ids=selected_character_ids),
            "relationship_specificity": self.check_relationship_specificity(state=state, character_ids=selected_character_ids),
            "world_specificity": self.check_world_specificity(state=state, story_request=story_request),
            "conflict_specificity": self.check_conflict_specificity(state=state, conflict_ids=outputs.get("conflict_ids", [])),
            "stakes_specificity": self.check_stakes_specificity(state=state, stakes_ids=outputs.get("stakes_ids", [])),
            "causal_specificity": self.check_causal_specificity(state=state, graph_ids=outputs.get("causal_graph_ids", [])),
            "handoff_specificity": self.check_handoff_specificity(
                state=state,
                handoff_package_id=outputs.get("handoff_package_id"),
            ),
        }

        anti_genericity_score = self._weighted_score(checks)
        blockers = self._blockers(checks)
        warnings = self._warnings(checks)

        report = {
            "anti_genericity_report_id": f"anti_genericity_{run_id}",
            "run_id": run_id,
            "checks": checks,
            "anti_genericity_score": anti_genericity_score,
            "genericity_risk": round(1.0 - anti_genericity_score, 3),
            "label": self._label(anti_genericity_score, blockers),
            "passes": anti_genericity_score >= 0.60 and not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "recommendations": self._recommendations(checks, blockers, warnings),
        }

        state.metadata.setdefault("simulation_anti_genericity_reports", {})[report["anti_genericity_report_id"]] = report
        state.metadata.setdefault("simulation_anti_genericity_history", []).append(
            {
                "action": "validate_simulation_run",
                "report_id": report["anti_genericity_report_id"],
                "run_id": run_id,
                "anti_genericity_score": anti_genericity_score,
                "label": report["label"],
                "passes": report["passes"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "anti_genericity_report": report,
            "updated_state": state,
        }

    def check_user_specificity(self, *, story_request: Dict[str, Any]) -> Dict[str, Any]:
        distinctive = story_request.get("distinctive_elements", [])
        constraints = story_request.get("constraints", {})
        tone_tags = story_request.get("tone_tags", [])
        primary_genres = story_request.get("primary_genres", [])
        scene_goal = story_request.get("scene_goal", "")
        plot_goal = story_request.get("plot_goal", "")

        text = " ".join(
            [scene_goal, plot_goal]
            + list(map(str, distinctive))
            + list(map(str, tone_tags))
            + list(map(str, primary_genres))
            + list(map(str, constraints.values() if isinstance(constraints, dict) else []))
        ).lower()

        generic_hits = self._generic_hits(text)

        score = 0.20
        score += min(0.25, len(distinctive) * 0.07)
        score += min(0.15, len(tone_tags) * 0.04)
        score += 0.12 if constraints else 0.0
        score += 0.12 if len(scene_goal) > 40 or len(plot_goal) > 40 else 0.0
        score += 0.10 if story_request.get("allow_any_character_count", False) else 0.0
        score += 0.08 if story_request.get("allow_project_created_characters", False) else 0.0
        score -= min(0.25, len(generic_hits) * 0.05)

        return {
            "score": self._bounded(score),
            "generic_phrase_hits": generic_hits,
            "distinctive_element_count": len(distinctive),
            "has_constraints": bool(constraints),
            "warnings": self._check_warnings("user_specificity", score, generic_hits),
        }

    def check_character_specificity(self, *, state: Any, character_ids: List[str]) -> Dict[str, Any]:
        if not character_ids:
            return {
                "score": 0.0,
                "character_reports": {},
                "warnings": ["no selected characters"],
            }

        reports = {}
        scores = []

        for cid in character_ids:
            character = state.character_states.get(cid)
            if not character:
                reports[cid] = {"score": 0.0, "missing": True}
                scores.append(0.0)
                continue

            metadata = character.metadata or {}
            text = " ".join(
                str(metadata.get(key, ""))
                for key in ["display_name", "name", "backstory", "backstory_summary"]
            ).lower()

            score = 0.20
            score += 0.12 if metadata.get("display_name") or metadata.get("name") else 0.0
            score += 0.15 if metadata.get("role_tags") or metadata.get("archetype_tags") else 0.0
            score += 0.15 if metadata.get("story_function_tags") else 0.0
            score += 0.18 if metadata.get("backstory") or metadata.get("backstory_summary") or metadata.get("backstory_depth", 0) >= 0.6 else 0.0
            score += 0.12 if metadata.get("goals") else 0.0
            score += 0.10 if metadata.get("psychology") else 0.0
            score += 0.08 if metadata.get("voice_profile") else 0.0
            score += 0.06 if metadata.get("uniqueness_score", 0.0) >= 0.6 else 0.0
            score -= min(0.20, len(self._generic_hits(text)) * 0.04)

            score = self._bounded(score)
            scores.append(score)
            reports[cid] = {
                "score": score,
                "has_role": bool(metadata.get("role_tags") or metadata.get("archetype_tags")),
                "has_story_function": bool(metadata.get("story_function_tags")),
                "has_backstory": bool(metadata.get("backstory") or metadata.get("backstory_summary") or metadata.get("backstory_depth", 0) >= 0.6),
                "has_goals": bool(metadata.get("goals")),
                "has_psychology": bool(metadata.get("psychology")),
                "has_voice": bool(metadata.get("voice_profile")),
                "generic_phrase_hits": self._generic_hits(text),
            }

        average = self._average(scores)
        return {
            "score": average,
            "character_reports": reports,
            "warnings": self._character_warnings(reports, average),
        }

    def check_relationship_specificity(self, *, state: Any, character_ids: List[str]) -> Dict[str, Any]:
        if len(character_ids) < 2:
            return {
                "score": 0.55,
                "relationship_count": 0,
                "warnings": ["single-character selection has limited relationship specificity"],
            }

        selected = set(character_ids)
        relationship_reports = {}
        scores = []

        for rid, rel in state.relationship_states.items():
            if rel.character_a_id not in selected or rel.character_b_id not in selected:
                continue

            non_default_fields = 0
            for value in [
                rel.trust,
                rel.respect,
                rel.affection,
                rel.resentment,
                rel.rivalry,
                rel.betrayal_risk,
                rel.repair_potential,
                rel.romantic_tension,
                rel.power_imbalance,
                rel.knowledge_asymmetry,
            ]:
                if abs(float(value) - 0.0) > 0.05 and abs(float(value) - 0.5) > 0.05:
                    non_default_fields += 1

            score = min(1.0, 0.25 + non_default_fields * 0.075)
            if rel.betrayal_risk > 0.4 or rel.repair_potential > 0.4:
                score += 0.08
            if rel.knowledge_asymmetry > 0.3 or rel.power_imbalance > 0.3:
                score += 0.07
            score = self._bounded(score)

            relationship_reports[rid] = {
                "score": score,
                "character_a_id": rel.character_a_id,
                "character_b_id": rel.character_b_id,
                "non_default_field_count": non_default_fields,
            }
            scores.append(score)

        if not scores:
            return {
                "score": 0.20,
                "relationship_count": 0,
                "relationship_reports": {},
                "warnings": ["selected cast has no relationship records"],
            }

        return {
            "score": self._average(scores),
            "relationship_count": len(scores),
            "relationship_reports": relationship_reports,
            "warnings": [] if self._average(scores) >= 0.55 else ["relationships may be too interchangeable"],
        }

    def check_world_specificity(self, *, state: Any, story_request: Dict[str, Any]) -> Dict[str, Any]:
        world_metadata = state.world_state.metadata or {}
        request_specifics = story_request.get("distinctive_elements", [])

        score = 0.25
        score += 0.15 if state.world_state.world_id else 0.0
        score += 0.15 if world_metadata.get("rules") or world_metadata.get("world_rules") else 0.0
        score += 0.12 if world_metadata.get("factions") or story_request.get("preferred_faction_ids") else 0.0
        score += 0.12 if world_metadata.get("locations") else 0.0
        score += 0.10 if world_metadata.get("culture") or world_metadata.get("beliefs") else 0.0
        score += min(0.16, len(request_specifics) * 0.04)

        return {
            "score": self._bounded(score),
            "world_id": state.world_state.world_id,
            "has_world_rules": bool(world_metadata.get("rules") or world_metadata.get("world_rules")),
            "has_factions": bool(world_metadata.get("factions") or story_request.get("preferred_faction_ids")),
            "has_locations": bool(world_metadata.get("locations")),
            "warnings": [] if score >= 0.55 else ["world may need more specific rules, factions, locations, or culture"],
        }

    def check_conflict_specificity(self, *, state: Any, conflict_ids: List[str]) -> Dict[str, Any]:
        if not conflict_ids:
            return {
                "score": 0.35,
                "conflict_reports": {},
                "warnings": ["no conflict records attached to run"],
            }

        reports = {}
        scores = []

        for cid in conflict_ids:
            conflict = state.metadata.get("conflict_registry", {}).get(cid, {})
            if not conflict:
                reports[cid] = {"score": 0.0, "missing": True}
                scores.append(0.0)
                continue

            text = " ".join([str(conflict.get("title", "")), str(conflict.get("core_issue", ""))]).lower()
            generic_hits = self._generic_hits(text)

            score = 0.20
            score += 0.18 if conflict.get("core_issue") else 0.0
            score += 0.18 if conflict.get("opposing_goals") else 0.0
            score += 0.12 if conflict.get("participant_ids") and len(conflict.get("participant_ids", [])) >= 2 else 0.0
            score += 0.12 if conflict.get("linked_secret_ids") or conflict.get("linked_evidence_ids") else 0.0
            score += 0.10 if conflict.get("conflict_pressure", 0.0) >= 0.45 else 0.0
            score += 0.10 if conflict.get("unresolved_threads") else 0.0
            score -= min(0.20, len(generic_hits) * 0.04)

            score = self._bounded(score)
            scores.append(score)
            reports[cid] = {
                "score": score,
                "generic_phrase_hits": generic_hits,
                "has_core_issue": bool(conflict.get("core_issue")),
                "has_opposing_goals": bool(conflict.get("opposing_goals")),
                "has_specific_links": bool(conflict.get("linked_secret_ids") or conflict.get("linked_evidence_ids")),
            }

        return {
            "score": self._average(scores),
            "conflict_reports": reports,
            "warnings": [] if self._average(scores) >= 0.55 else ["conflicts may need sharper, more specific opposing goals"],
        }

    def check_stakes_specificity(self, *, state: Any, stakes_ids: List[str]) -> Dict[str, Any]:
        if not stakes_ids:
            return {
                "score": 0.25,
                "warnings": ["no stakes records attached to run"],
            }

        scores = []
        reports = {}

        for sid in stakes_ids:
            stakes = state.metadata.get("stakes_registry", {}).get(sid, {})
            if not stakes:
                scores.append(0.0)
                reports[sid] = {"score": 0.0, "missing": True}
                continue

            values = stakes.get("stake_values", {})
            high_specific = [key for key, value in values.items() if value >= 0.55]
            score = 0.25
            score += min(0.25, len(values) * 0.05)
            score += min(0.20, len(high_specific) * 0.06)
            score += 0.14 if stakes.get("dominant_stake_type") else 0.0
            score += 0.10 if stakes.get("summary") else 0.0
            score += 0.06 if stakes.get("overall_stakes_score", 0.0) >= 0.55 else 0.0

            score = self._bounded(score)
            scores.append(score)
            reports[sid] = {
                "score": score,
                "stake_type_count": len(values),
                "high_specific_stakes": high_specific,
                "dominant_stake_type": stakes.get("dominant_stake_type"),
            }

        return {
            "score": self._average(scores),
            "stakes_reports": reports,
            "warnings": [] if self._average(scores) >= 0.55 else ["stakes may be too vague or too narrow"],
        }

    def check_causal_specificity(self, *, state: Any, graph_ids: List[str]) -> Dict[str, Any]:
        if not graph_ids:
            return {
                "score": 0.25,
                "warnings": ["no causal graph IDs attached to run"],
            }

        scores = []
        reports = {}

        for gid in graph_ids:
            graph = state.metadata.get("causal_graphs", {}).get(gid, {})
            nodes = graph.get("nodes", {})
            edges = graph.get("edges", {})
            node_types = {node.get("node_type") for node in nodes.values()}

            score = 0.25
            score += min(0.20, len(nodes) * 0.03)
            score += min(0.20, len(edges) * 0.04)
            score += 0.10 if "choice" in node_types or "event" in node_types else 0.0
            score += 0.10 if "consequence" in node_types else 0.0
            score += 0.10 if "delta" in node_types else 0.0
            score += 0.05 if len(node_types) >= 3 else 0.0

            score = self._bounded(score)
            scores.append(score)
            reports[gid] = {
                "score": score,
                "node_count": len(nodes),
                "edge_count": len(edges),
                "node_types": sorted([str(t) for t in node_types if t]),
            }

        return {
            "score": self._average(scores),
            "causal_graph_reports": reports,
            "warnings": [] if self._average(scores) >= 0.55 else ["causal graphs may be too thin"],
        }

    def check_handoff_specificity(self, *, state: Any, handoff_package_id: Optional[str]) -> Dict[str, Any]:
        if not handoff_package_id:
            return {
                "score": 0.0,
                "warnings": ["no handoff package attached to run"],
            }

        package = state.metadata.get("handoff_packages", {}).get(handoff_package_id)
        if not package:
            return {
                "score": 0.0,
                "warnings": ["handoff package missing from state"],
            }

        score = 0.20
        score += 0.12 if package.get("cast") else 0.0
        score += 0.15 if package.get("plot_payload") else 0.0
        score += 0.15 if package.get("scene_payloads") else 0.0
        score += 0.12 if package.get("generation_contract", {}).get("respect_user_characters") else 0.0
        score += 0.12 if package.get("generation_contract", {}).get("allow_any_character_count") else 0.0
        score += 0.12 if package.get("quality_targets", {}).get("anti_genericity") == "high" else 0.0
        score += 0.08 if package.get("global_context", {}).get("causal_graph_count", 0) > 0 else 0.0

        return {
            "score": self._bounded(score),
            "has_cast": bool(package.get("cast")),
            "has_plot_payload": bool(package.get("plot_payload")),
            "has_scene_payloads": bool(package.get("scene_payloads")),
            "warnings": [] if score >= 0.6 else ["handoff package may not carry enough specificity"],
        }

    def build_anti_genericity_map(self, *, state: Any) -> Dict[str, Any]:
        reports = state.metadata.get("simulation_anti_genericity_reports", {})
        compact = {}

        for report_id, report in reports.items():
            compact[report_id] = {
                "report_id": report_id,
                "run_id": report.get("run_id"),
                "anti_genericity_score": report.get("anti_genericity_score"),
                "genericity_risk": report.get("genericity_risk"),
                "label": report.get("label"),
                "passes": report.get("passes"),
                "blocker_count": len(report.get("blockers", [])),
                "warning_count": len(report.get("warnings", [])),
            }

        ranked = sorted(compact.values(), key=lambda item: item.get("anti_genericity_score", 0.0), reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "report_count": len(compact),
            "anti_genericity_reports": compact,
            "best_report": ranked[0] if ranked else None,
            "passing_report_count": sum(1 for item in compact.values() if item.get("passes")),
            "warnings": [] if compact else ["no anti-genericity reports registered"],
        }

    def _generic_hits(self, text: str) -> List[str]:
        lower = text.lower()
        return sorted([phrase for phrase in self.GENERIC_PHRASES if phrase in lower])

    def _weighted_score(self, checks: Dict[str, Dict[str, Any]]) -> float:
        weights = {
            "user_specificity": 0.13,
            "character_specificity": 0.15,
            "relationship_specificity": 0.13,
            "world_specificity": 0.10,
            "conflict_specificity": 0.13,
            "stakes_specificity": 0.11,
            "causal_specificity": 0.12,
            "handoff_specificity": 0.13,
        }
        return round(
            max(
                0.0,
                min(1.0, sum(checks.get(key, {}).get("score", 0.0) * weight for key, weight in weights.items())),
            ),
            3,
        )

    def _blockers(self, checks: Dict[str, Dict[str, Any]]) -> List[str]:
        blockers = []
        if checks["character_specificity"]["score"] < 0.30:
            blockers.append("characters are too generic or underdeveloped")
        if checks["handoff_specificity"]["score"] < 0.35:
            blockers.append("handoff payload lacks specificity")
        if checks["user_specificity"]["score"] < 0.25:
            blockers.append("story request lacks distinctive user-specific direction")
        return blockers

    def _warnings(self, checks: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        for check_name, check in checks.items():
            warnings.extend(check.get("warnings", []))
            if check.get("score", 0.0) < 0.50:
                warnings.append(f"{check_name} is below specificity target")
        return self._unique(warnings)

    def _recommendations(self, checks: Dict[str, Dict[str, Any]], blockers: List[str], warnings: List[str]) -> List[str]:
        recs = []
        if checks["user_specificity"]["score"] < 0.6:
            recs.append("add distinctive user wants: exact themes, format, tone, story constraints, and unusual elements")
        if checks["character_specificity"]["score"] < 0.6:
            recs.append("add unique backstory, wound, goal, voice, and story function for each selected character")
        if checks["relationship_specificity"]["score"] < 0.6:
            recs.append("make relationships non-interchangeable using trust, resentment, secrets, power imbalance, and repair potential")
        if checks["world_specificity"]["score"] < 0.6:
            recs.append("add world rules, factions, locations, culture, and consequences specific to this world")
        if checks["conflict_specificity"]["score"] < 0.6:
            recs.append("sharpen conflict with specific core issue, opposing goals, and linked secrets/evidence")
        if checks["stakes_specificity"]["score"] < 0.6:
            recs.append("make stakes concrete: what is lost, who pays, and what changes afterward")
        if checks["causal_specificity"]["score"] < 0.6:
            recs.append("add stronger causal graph nodes and edges from choice to event to consequence to state delta")
        if checks["handoff_specificity"]["score"] < 0.6:
            recs.append("rebuild handoff package with cast, plot, scene, causal, and quality contracts")
        return self._unique(recs)

    def _label(self, score: float, blockers: List[str]) -> str:
        if blockers:
            return "blocked_generic"
        if score >= 0.85:
            return "highly_specific"
        if score >= 0.70:
            return "specific"
        if score >= 0.60:
            return "acceptable"
        if score >= 0.45:
            return "generic_risk"
        return "too_generic"

    def _check_warnings(self, check_name: str, score: float, generic_hits: List[str]) -> List[str]:
        warnings = []
        if score < 0.5:
            warnings.append(f"{check_name} specificity is weak")
        if generic_hits:
            warnings.append(f"generic phrase hits found: {generic_hits}")
        return warnings

    def _character_warnings(self, reports: Dict[str, Dict[str, Any]], average: float) -> List[str]:
        warnings = []
        if average < 0.55:
            warnings.append("selected characters need more specificity")
        for cid, report in reports.items():
            if report.get("score", 0.0) < 0.45:
                warnings.append(f"{cid} is underdeveloped")
            if not report.get("has_story_function", False):
                warnings.append(f"{cid} lacks story function tags")
        return self._unique(warnings)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

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
