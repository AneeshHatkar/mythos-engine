from typing import Any, Dict, List, Optional


class StakesEngine:
    """Scores what is at risk in choices, events, scenes, and arcs.

    Stakes are not just "danger." MythOS tracks many kinds of risk:
    life, love, reputation, truth, identity, resources, faction power, world order,
    morality, branch consequences, and emotional cost.
    """

    engine_name = "simulation.stakes_engine"

    STAKE_TYPES = {
        "life",
        "relationship",
        "reputation",
        "truth",
        "resource",
        "faction",
        "world",
        "identity",
        "romance",
        "moral",
        "branch",
        "emotional",
        "agency",
        "legal",
        "spiritual",
    }

    def create_stakes_record(
        self,
        *,
        stakes_id: str,
        source_type: str,
        source_id: str,
        affected_entity_ids: List[str] | None = None,
        stake_values: Dict[str, float] | None = None,
        summary: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        normalized_values = {}
        for key, value in (stake_values or {}).items():
            normalized_key = key if key in self.STAKE_TYPES else "emotional"
            normalized_values[normalized_key] = max(
                normalized_values.get(normalized_key, 0.0),
                self._bounded(value),
            )

        return {
            "stakes_id": stakes_id,
            "source_type": source_type,
            "source_id": source_id,
            "affected_entity_ids": affected_entity_ids or [],
            "stake_values": normalized_values,
            "summary": summary,
            "overall_stakes_score": self._overall_score(normalized_values),
            "dominant_stake_type": self._dominant_stake_type(normalized_values),
            "stakes_label": self._stakes_label(self._overall_score(normalized_values)),
            "metadata": metadata or {},
        }

    def register_stakes_on_state(
        self,
        *,
        state: Any,
        stakes_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        stakes_id = stakes_record["stakes_id"]
        state.metadata.setdefault("stakes_registry", {})[stakes_id] = dict(stakes_record)
        state.metadata.setdefault("stakes_history", []).append(
            {
                "action": "register_stakes",
                "stakes_id": stakes_id,
                "source_type": stakes_record.get("source_type"),
                "source_id": stakes_record.get("source_id"),
                "overall_stakes_score": stakes_record.get("overall_stakes_score"),
                "dominant_stake_type": stakes_record.get("dominant_stake_type"),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "stakes_id": stakes_id,
            "updated_state": state,
        }

    def evaluate_event_stakes(
        self,
        *,
        state: Any,
        event_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        event_type = event_record.get("event_type", "")
        family = event_record.get("event_family", "")
        intensity = float(event_record.get("intensity", 0.5))
        visibility = event_record.get("visibility", "private")

        values = {
            "emotional": intensity * 0.45,
            "branch": intensity * 0.25,
        }

        if family == "knowledge" or event_record.get("linked_secret_ids") or event_record.get("linked_evidence_ids"):
            values["truth"] = max(values.get("truth", 0), 0.45 + intensity * 0.35)
            values["reputation"] = max(values.get("reputation", 0), 0.20 + intensity * 0.25)

        if family == "relationship":
            values["relationship"] = max(values.get("relationship", 0), 0.45 + intensity * 0.35)
            if event_type in {"private_confession", "romantic_turn"}:
                values["romance"] = max(values.get("romance", 0), 0.35 + intensity * 0.35)

        if family == "obligation" or event_record.get("linked_obligation_ids"):
            values["moral"] = max(values.get("moral", 0), 0.40 + intensity * 0.30)
            values["relationship"] = max(values.get("relationship", 0), 0.35 + intensity * 0.25)

        if family == "leverage" or event_record.get("linked_leverage_ids"):
            values["agency"] = max(values.get("agency", 0), 0.55 + intensity * 0.30)
            values["reputation"] = max(values.get("reputation", 0), 0.45 + intensity * 0.25)

        if family == "bargain" or event_record.get("linked_bargain_ids"):
            values["resource"] = max(values.get("resource", 0), 0.25 + intensity * 0.20)
            values["moral"] = max(values.get("moral", 0), 0.25 + intensity * 0.20)

        if event_type in {"trial", "public_humiliation", "public_event"} or visibility == "public":
            values["reputation"] = max(values.get("reputation", 0), 0.45 + intensity * 0.35)
            values["faction"] = max(values.get("faction", 0), 0.25 + intensity * 0.25)

        if event_type in {"combat", "sacrifice", "death", "attack"}:
            values["life"] = max(values.get("life", 0), 0.60 + intensity * 0.35)

        affected = self._unique(
            event_record.get("actor_ids", [])
            + event_record.get("target_ids", [])
            + event_record.get("witness_ids", [])
            + event_record.get("involved_faction_ids", [])
        )

        record = self.create_stakes_record(
            stakes_id=f"stakes_event_{event_record.get('event_id')}",
            source_type="event",
            source_id=event_record.get("event_id"),
            affected_entity_ids=affected,
            stake_values=values,
            summary=f"Stakes for event {event_record.get('event_id')}.",
            metadata={"event_type": event_type, "event_family": family},
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "stakes_record": record,
            "warnings": self._stakes_warnings(record),
            "chunk5_handoff": self._chunk5_handoff(record),
        }

    def evaluate_choice_stakes(
        self,
        *,
        state: Any,
        choice_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        action_type = choice_report.get("action_type", "")
        risk = choice_report.get("risk_profile", {})
        preview = choice_report.get("consequence_preview", {})
        actor_id = choice_report.get("actor_id")
        target_id = choice_report.get("target_id")

        values = {
            "moral": float(risk.get("moral_cost", 0.4)),
            "emotional": float(risk.get("emotional_cost", 0.4)),
            "reputation": float(risk.get("social_risk", 0.4)),
            "agency": float(risk.get("coercion_pressure", 0.0)),
            "branch": float(risk.get("overall_risk", 0.4)),
        }

        if preview.get("relationship_consequence") or action_type in {"betray", "protect", "repair_relationship", "forgive"}:
            values["relationship"] = max(values.get("relationship", 0), 0.55)

        if preview.get("knowledge_consequence") or action_type in {"expose_secret", "hide_truth", "confess"}:
            values["truth"] = max(values.get("truth", 0), 0.60)

        if preview.get("reputation_consequence") or action_type in {"spread_rumor", "attempt_blackmail"}:
            values["reputation"] = max(values.get("reputation", 0), 0.65)

        if preview.get("branch_consequence") or action_type in {"sacrifice", "break_oath", "accept_bargain", "reject_bargain"}:
            values["branch"] = max(values.get("branch", 0), 0.65)

        if action_type in {"sacrifice", "attack", "retreat"}:
            values["life"] = max(values.get("life", 0), 0.55)

        if action_type in {"accept_bargain", "negotiate", "reject_bargain"}:
            values["resource"] = max(values.get("resource", 0), 0.35)

        record = self.create_stakes_record(
            stakes_id=f"stakes_choice_{choice_report.get('choice_id')}",
            source_type="choice",
            source_id=choice_report.get("choice_id"),
            affected_entity_ids=self._unique([actor_id, target_id]),
            stake_values=values,
            summary=f"Stakes for choice {choice_report.get('choice_id')}.",
            metadata={"action_type": action_type},
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "stakes_record": record,
            "warnings": self._stakes_warnings(record),
            "chunk5_handoff": self._chunk5_handoff(record),
        }

    def evaluate_scene_stakes(
        self,
        *,
        state: Any,
        scene_id: str,
        event_records: List[Dict[str, Any]] | None = None,
        choice_reports: List[Dict[str, Any]] | None = None,
        consequence_records: List[Dict[str, Any]] | None = None,
        summary: str = "",
    ) -> Dict[str, Any]:
        child_records = []

        for event in event_records or []:
            child_records.append(self.evaluate_event_stakes(state=state, event_record=event)["stakes_record"])

        for choice in choice_reports or []:
            child_records.append(self.evaluate_choice_stakes(state=state, choice_report=choice)["stakes_record"])

        for consequence in consequence_records or []:
            child_records.append(self.evaluate_consequence_stakes(state=state, consequence_record=consequence)["stakes_record"])

        combined = self.combine_stakes_records(
            stakes_id=f"stakes_scene_{scene_id}",
            source_type="scene",
            source_id=scene_id,
            records=child_records,
            summary=summary or f"Combined stakes for scene {scene_id}.",
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_id": scene_id,
            "stakes_record": combined,
            "child_stakes_count": len(child_records),
            "warnings": self._stakes_warnings(combined),
            "chunk5_handoff": self._chunk5_handoff(combined),
        }

    def evaluate_consequence_stakes(
        self,
        *,
        state: Any,
        consequence_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        ctype = consequence_record.get("consequence_type", "plot_hook")
        severity = float(consequence_record.get("severity", 0.5))
        values = {
            "branch": severity * 0.35,
            "emotional": severity * 0.35,
        }

        if ctype == "relationship":
            values["relationship"] = 0.50 + severity * 0.35
        elif ctype == "reputation":
            values["reputation"] = 0.50 + severity * 0.35
        elif ctype == "knowledge":
            values["truth"] = 0.45 + severity * 0.35
        elif ctype == "resource":
            values["resource"] = 0.45 + severity * 0.35
        elif ctype == "faction":
            values["faction"] = 0.45 + severity * 0.35
        elif ctype == "obligation":
            values["moral"] = 0.45 + severity * 0.35
            values["relationship"] = 0.35 + severity * 0.25
        elif ctype == "leverage":
            values["agency"] = 0.50 + severity * 0.35
            values["reputation"] = 0.35 + severity * 0.25
        elif ctype == "branch":
            values["branch"] = 0.60 + severity * 0.35

        record = self.create_stakes_record(
            stakes_id=f"stakes_consequence_{consequence_record.get('consequence_id')}",
            source_type="consequence",
            source_id=consequence_record.get("consequence_id"),
            affected_entity_ids=consequence_record.get("affected_entity_ids", []),
            stake_values=values,
            summary=f"Stakes for consequence {consequence_record.get('consequence_id')}.",
            metadata={"consequence_type": ctype},
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "stakes_record": record,
            "warnings": self._stakes_warnings(record),
            "chunk5_handoff": self._chunk5_handoff(record),
        }

    def combine_stakes_records(
        self,
        *,
        stakes_id: str,
        source_type: str,
        source_id: str,
        records: List[Dict[str, Any]],
        summary: str = "",
    ) -> Dict[str, Any]:
        combined_values: Dict[str, float] = {}
        affected = []

        for record in records:
            affected.extend(record.get("affected_entity_ids", []))
            for stake_type, value in record.get("stake_values", {}).items():
                existing = combined_values.get(stake_type, 0.0)
                # combine by max + small accumulation bonus
                combined_values[stake_type] = self._bounded(max(existing, value) + min(existing, value) * 0.18)

        return self.create_stakes_record(
            stakes_id=stakes_id,
            source_type=source_type,
            source_id=source_id,
            affected_entity_ids=self._unique(affected),
            stake_values=combined_values,
            summary=summary,
            metadata={"combined_record_count": len(records)},
        )

    def compare_stakes(
        self,
        *,
        records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        ranked = sorted(records, key=lambda item: item.get("overall_stakes_score", 0.0), reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "record_count": len(records),
            "ranked_stakes": ranked,
            "highest_stakes_record": ranked[0] if ranked else None,
            "average_stakes_score": self._average([record.get("overall_stakes_score", 0.0) for record in records]),
            "dominant_stake_distribution": self._dominant_distribution(records),
        }

    def build_stakes_map(self, *, state: Any) -> Dict[str, Any]:
        records = state.metadata.get("stakes_registry", {})
        ranked = sorted(
            records.values(),
            key=lambda item: item.get("overall_stakes_score", 0.0),
            reverse=True,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "stakes_count": len(records),
            "ranked_stakes": ranked,
            "highest_stakes_record": ranked[0] if ranked else None,
            "average_stakes_score": self._average([record.get("overall_stakes_score", 0.0) for record in records.values()]),
            "warnings": self._map_warnings(ranked),
        }

    def _overall_score(self, values: Dict[str, float]) -> float:
        if not values:
            return 0.0

        sorted_values = sorted([self._bounded(v) for v in values.values()], reverse=True)
        top = sorted_values[0]
        second = sorted_values[1] if len(sorted_values) > 1 else 0.0
        breadth_bonus = min(0.20, len([v for v in sorted_values if v >= 0.35]) * 0.04)

        return round(min(1.0, top * 0.62 + second * 0.20 + breadth_bonus), 3)

    def _dominant_stake_type(self, values: Dict[str, float]) -> Optional[str]:
        if not values:
            return None
        return max(values.items(), key=lambda item: item[1])[0]

    def _stakes_label(self, score: float) -> str:
        if score >= 0.82:
            return "catastrophic"
        if score >= 0.65:
            return "high"
        if score >= 0.40:
            return "medium"
        if score > 0.0:
            return "low"
        return "none"

    def _stakes_warnings(self, record: Dict[str, Any]) -> List[str]:
        warnings = []
        if record["overall_stakes_score"] < 0.25:
            warnings.append("stakes may be too low for a major scene")
        if record["overall_stakes_score"] >= 0.82:
            warnings.append("stakes are catastrophic; ensure payoff and aftermath")
        if len([v for v in record["stake_values"].values() if v >= 0.6]) >= 4:
            warnings.append("many high stakes at once; scene may feel overloaded")
        return warnings

    def _chunk5_handoff(self, record: Dict[str, Any]) -> Dict[str, Any]:
        dominant = record.get("dominant_stake_type")
        scene_type = {
            "life": "survival_stakes_scene",
            "relationship": "relationship_stakes_scene",
            "reputation": "public_reputation_stakes_scene",
            "truth": "truth_reveal_stakes_scene",
            "resource": "scarcity_or_tradeoff_scene",
            "faction": "political_stakes_scene",
            "world": "world_order_stakes_scene",
            "identity": "identity_stakes_scene",
            "romance": "romantic_stakes_scene",
            "moral": "moral_stakes_scene",
            "branch": "branch_stakes_scene",
            "agency": "coercion_agency_stakes_scene",
        }.get(dominant, "stakes_scene")

        return {
            "source_id": record.get("source_id"),
            "scene_type": scene_type,
            "stakes_label": record.get("stakes_label"),
            "dominant_stake_type": dominant,
            "overall_stakes_score": record.get("overall_stakes_score"),
            "must_make_cost_clear": record.get("overall_stakes_score", 0.0) >= 0.4,
            "must_show_aftermath": record.get("overall_stakes_score", 0.0) >= 0.65,
            "stake_values": record.get("stake_values", {}),
        }

    def _dominant_distribution(self, records: List[Dict[str, Any]]) -> Dict[str, int]:
        distribution: Dict[str, int] = {}
        for record in records:
            key = record.get("dominant_stake_type") or "none"
            distribution[key] = distribution.get(key, 0) + 1
        return distribution

    def _map_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not ranked:
            warnings.append("no stakes records registered")
        if ranked and ranked[0].get("overall_stakes_score", 0.0) < 0.35:
            warnings.append("all registered stakes are low")
        catastrophic = [record for record in ranked if record.get("stakes_label") == "catastrophic"]
        if len(catastrophic) > 3:
            warnings.append("many catastrophic stakes records; pacing may be too extreme")
        return warnings

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[Any]) -> List[Any]:
        seen = set()
        result = []
        for value in values:
            if value is None:
                continue
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result
