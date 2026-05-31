from typing import Any, Dict, List, Optional


class TensionCurveEngine:
    """Builds and audits tension curves across scenes, choices, events, and arcs.

    A god-tier story needs pressure rhythm: rise, spike, release, aftermath,
    re-escalation, and payoff. This engine prevents flat pacing and also prevents
    every scene from being catastrophic with no breathing room.
    """

    engine_name = "simulation.tension_curve_engine"

    TENSION_SOURCES = {
        "stakes",
        "event",
        "choice",
        "consequence",
        "relationship",
        "social",
        "knowledge",
        "leverage",
        "obligation",
        "faction",
        "emotional",
        "branch",
    }

    CURVE_LABELS = {
        "flat",
        "rising",
        "falling",
        "spiking",
        "release",
        "overloaded",
        "balanced",
        "volatile",
    }

    def create_tension_point(
        self,
        *,
        point_id: str,
        source_type: str,
        source_id: str,
        sequence_index: int,
        tension_value: float,
        emotional_pressure: float = 0.0,
        stakes_pressure: float = 0.0,
        social_pressure: float = 0.0,
        knowledge_pressure: float = 0.0,
        consequence_pressure: float = 0.0,
        release_value: float = 0.0,
        summary: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if source_type not in self.TENSION_SOURCES:
            source_type = "event"

        value = self._bounded(tension_value)
        return {
            "point_id": point_id,
            "source_type": source_type,
            "source_id": source_id,
            "sequence_index": int(sequence_index),
            "tension_value": value,
            "emotional_pressure": self._bounded(emotional_pressure),
            "stakes_pressure": self._bounded(stakes_pressure),
            "social_pressure": self._bounded(social_pressure),
            "knowledge_pressure": self._bounded(knowledge_pressure),
            "consequence_pressure": self._bounded(consequence_pressure),
            "release_value": self._bounded(release_value),
            "net_pressure": self._net_pressure(
                value,
                emotional_pressure,
                stakes_pressure,
                social_pressure,
                knowledge_pressure,
                consequence_pressure,
                release_value,
            ),
            "summary": summary,
            "metadata": metadata or {},
        }

    def build_tension_point_from_stakes(
        self,
        *,
        stakes_record: Dict[str, Any],
        sequence_index: int,
    ) -> Dict[str, Any]:
        values = stakes_record.get("stake_values", {})
        overall = float(stakes_record.get("overall_stakes_score", 0.0))

        return self.create_tension_point(
            point_id=f"tension_{stakes_record.get('stakes_id')}",
            source_type="stakes",
            source_id=stakes_record.get("stakes_id"),
            sequence_index=sequence_index,
            tension_value=overall,
            emotional_pressure=float(values.get("emotional", 0.0)),
            stakes_pressure=overall,
            social_pressure=max(float(values.get("reputation", 0.0)), float(values.get("faction", 0.0))),
            knowledge_pressure=float(values.get("truth", 0.0)),
            consequence_pressure=max(float(values.get("branch", 0.0)), float(values.get("world", 0.0))),
            release_value=0.0,
            summary=stakes_record.get("summary", "Stakes tension point."),
            metadata={
                "dominant_stake_type": stakes_record.get("dominant_stake_type"),
                "stakes_label": stakes_record.get("stakes_label"),
            },
        )

    def build_tension_point_from_event(
        self,
        *,
        event_record: Dict[str, Any],
        sequence_index: int,
    ) -> Dict[str, Any]:
        intensity = float(event_record.get("intensity", 0.5))
        visibility = event_record.get("visibility", "private")
        family = event_record.get("event_family", "world")
        event_type = event_record.get("event_type", "")

        social_pressure = 0.25 if visibility == "public" else 0.12 if visibility == "witnessed" else 0.0
        knowledge_pressure = 0.0
        if event_record.get("linked_secret_ids") or event_record.get("linked_evidence_ids") or family == "knowledge":
            knowledge_pressure = 0.55 + intensity * 0.25

        emotional_pressure = 0.35 + intensity * 0.25 if family in {"relationship", "obligation", "leverage"} else intensity * 0.25
        consequence_pressure = intensity * 0.35 if event_type in {"trial", "betrayal", "public_humiliation", "blackmail_attempt"} else intensity * 0.18

        return self.create_tension_point(
            point_id=f"tension_event_{event_record.get('event_id')}",
            source_type="event",
            source_id=event_record.get("event_id"),
            sequence_index=sequence_index,
            tension_value=min(1.0, intensity * 0.55 + social_pressure * 0.25 + knowledge_pressure * 0.20),
            emotional_pressure=emotional_pressure,
            stakes_pressure=intensity,
            social_pressure=social_pressure,
            knowledge_pressure=knowledge_pressure,
            consequence_pressure=consequence_pressure,
            release_value=float(event_record.get("metadata", {}).get("release_value", 0.0)),
            summary=event_record.get("event_name", "Event tension point."),
            metadata={"event_type": event_type, "event_family": family},
        )

    def build_tension_point_from_choice(
        self,
        *,
        choice_report: Dict[str, Any],
        sequence_index: int,
    ) -> Dict[str, Any]:
        risk = choice_report.get("risk_profile", {})
        agency_score = float(choice_report.get("agency_score", 0.5))
        feasibility_score = float(choice_report.get("feasibility_score", 0.5))

        overall_risk = float(risk.get("overall_risk", 0.4))
        coercion = float(risk.get("coercion_pressure", 0.0))
        moral = float(risk.get("moral_cost", 0.4))
        emotional = float(risk.get("emotional_cost", 0.4))
        social = float(risk.get("social_risk", 0.4))

        uncertainty = max(0.0, 1.0 - ((agency_score + feasibility_score) / 2.0))

        return self.create_tension_point(
            point_id=f"tension_choice_{choice_report.get('choice_id')}",
            source_type="choice",
            source_id=choice_report.get("choice_id"),
            sequence_index=sequence_index,
            tension_value=min(1.0, overall_risk * 0.50 + uncertainty * 0.25 + coercion * 0.25),
            emotional_pressure=emotional,
            stakes_pressure=overall_risk,
            social_pressure=social,
            knowledge_pressure=0.55 if choice_report.get("action_type") in {"expose_secret", "hide_truth", "confess"} else 0.0,
            consequence_pressure=0.65 if choice_report.get("consequence_preview", {}).get("branch_consequence") else overall_risk * 0.35,
            release_value=0.0,
            summary=choice_report.get("summary", "Choice tension point."),
            metadata={
                "action_type": choice_report.get("action_type"),
                "agency_score": agency_score,
                "feasibility_score": feasibility_score,
                "moral_cost": moral,
            },
        )

    def build_tension_point_from_consequence(
        self,
        *,
        consequence_record: Dict[str, Any],
        sequence_index: int,
    ) -> Dict[str, Any]:
        severity = float(consequence_record.get("severity", 0.5))
        ctype = consequence_record.get("consequence_type", "plot_hook")

        release = 0.25 if consequence_record.get("status") in {"resolved", "triggered"} else 0.0
        emotional = 0.65 if ctype in {"relationship", "emotional", "obligation"} else severity * 0.35
        social = 0.65 if ctype in {"reputation", "faction"} else severity * 0.25
        knowledge = 0.65 if ctype == "knowledge" else 0.0

        return self.create_tension_point(
            point_id=f"tension_consequence_{consequence_record.get('consequence_id')}",
            source_type="consequence",
            source_id=consequence_record.get("consequence_id"),
            sequence_index=sequence_index,
            tension_value=severity,
            emotional_pressure=emotional,
            stakes_pressure=severity,
            social_pressure=social,
            knowledge_pressure=knowledge,
            consequence_pressure=severity,
            release_value=release,
            summary=consequence_record.get("summary", "Consequence tension point."),
            metadata={"consequence_type": ctype, "status": consequence_record.get("status")},
        )

    def build_tension_curve(
        self,
        *,
        curve_id: str,
        points: List[Dict[str, Any]],
        source_type: str = "arc",
        source_id: Optional[str] = None,
        summary: str = "",
    ) -> Dict[str, Any]:
        sorted_points = sorted(points, key=lambda item: item.get("sequence_index", 0))
        values = [float(point.get("net_pressure", point.get("tension_value", 0.0))) for point in sorted_points]

        curve = {
            "curve_id": curve_id,
            "source_type": source_type,
            "source_id": source_id,
            "summary": summary,
            "points": sorted_points,
            "point_count": len(sorted_points),
            "values": values,
            "average_tension": self._average(values),
            "peak_tension": max(values) if values else 0.0,
            "lowest_tension": min(values) if values else 0.0,
            "tension_range": round((max(values) - min(values)), 3) if values else 0.0,
            "curve_label": self._curve_label(values),
            "spike_indices": self._spike_indices(values),
            "release_indices": self._release_indices(sorted_points, values),
            "flat_segments": self._flat_segments(values),
            "overload_score": self._overload_score(values),
            "pacing_score": self._pacing_score(values, sorted_points),
        }

        curve["warnings"] = self._curve_warnings(curve)
        curve["chunk5_handoff"] = self._chunk5_handoff(curve)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "tension_curve": curve,
        }

    def register_tension_curve_on_state(
        self,
        *,
        state: Any,
        curve: Dict[str, Any],
    ) -> Dict[str, Any]:
        curve_id = curve["curve_id"]
        state.metadata.setdefault("tension_curves", {})[curve_id] = dict(curve)
        state.metadata.setdefault("tension_history", []).append(
            {
                "action": "register_tension_curve",
                "curve_id": curve_id,
                "point_count": curve.get("point_count"),
                "average_tension": curve.get("average_tension"),
                "peak_tension": curve.get("peak_tension"),
                "curve_label": curve.get("curve_label"),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "curve_id": curve_id,
            "updated_state": state,
        }

    def evaluate_scene_tension(
        self,
        *,
        scene_id: str,
        event_records: List[Dict[str, Any]] | None = None,
        choice_reports: List[Dict[str, Any]] | None = None,
        consequence_records: List[Dict[str, Any]] | None = None,
        stakes_records: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        points = []
        index = 0

        for event in event_records or []:
            points.append(self.build_tension_point_from_event(event_record=event, sequence_index=index))
            index += 1

        for choice in choice_reports or []:
            points.append(self.build_tension_point_from_choice(choice_report=choice, sequence_index=index))
            index += 1

        for consequence in consequence_records or []:
            points.append(self.build_tension_point_from_consequence(consequence_record=consequence, sequence_index=index))
            index += 1

        for stakes in stakes_records or []:
            points.append(self.build_tension_point_from_stakes(stakes_record=stakes, sequence_index=index))
            index += 1

        curve_result = self.build_tension_curve(
            curve_id=f"tension_scene_{scene_id}",
            points=points,
            source_type="scene",
            source_id=scene_id,
            summary=f"Tension curve for scene {scene_id}.",
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_id": scene_id,
            "tension_curve": curve_result["tension_curve"],
        }

    def compare_tension_curves(
        self,
        *,
        curves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        ranked_by_peak = sorted(curves, key=lambda item: item.get("peak_tension", 0.0), reverse=True)
        ranked_by_pacing = sorted(curves, key=lambda item: item.get("pacing_score", 0.0), reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "curve_count": len(curves),
            "highest_peak_curve": ranked_by_peak[0] if ranked_by_peak else None,
            "best_paced_curve": ranked_by_pacing[0] if ranked_by_pacing else None,
            "average_peak_tension": self._average([curve.get("peak_tension", 0.0) for curve in curves]),
            "average_pacing_score": self._average([curve.get("pacing_score", 0.0) for curve in curves]),
            "warnings": self._compare_warnings(curves),
        }

    def build_tension_map(self, *, state: Any) -> Dict[str, Any]:
        curves = state.metadata.get("tension_curves", {})
        records = {
            curve_id: {
                "curve_id": curve_id,
                "source_type": curve.get("source_type"),
                "source_id": curve.get("source_id"),
                "point_count": curve.get("point_count"),
                "average_tension": curve.get("average_tension"),
                "peak_tension": curve.get("peak_tension"),
                "curve_label": curve.get("curve_label"),
                "pacing_score": curve.get("pacing_score"),
                "warning_count": len(curve.get("warnings", [])),
            }
            for curve_id, curve in curves.items()
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "curve_count": len(records),
            "tension_curve_records": records,
            "average_tension": self._average([record["average_tension"] for record in records.values()]),
            "average_pacing_score": self._average([record["pacing_score"] for record in records.values()]),
            "warnings": self._map_warnings(records),
        }

    def _net_pressure(
        self,
        tension_value: float,
        emotional_pressure: float,
        stakes_pressure: float,
        social_pressure: float,
        knowledge_pressure: float,
        consequence_pressure: float,
        release_value: float,
    ) -> float:
        return round(
            max(
                0.0,
                min(
                    1.0,
                    self._bounded(tension_value) * 0.35
                    + self._bounded(emotional_pressure) * 0.14
                    + self._bounded(stakes_pressure) * 0.18
                    + self._bounded(social_pressure) * 0.10
                    + self._bounded(knowledge_pressure) * 0.12
                    + self._bounded(consequence_pressure) * 0.16
                    - self._bounded(release_value) * 0.20,
                ),
            ),
            3,
        )

    def _curve_label(self, values: List[float]) -> str:
        if not values:
            return "flat"

        avg = self._average(values)
        peak = max(values)
        value_range = peak - min(values)

        if avg >= 0.78:
            return "overloaded"
        if peak >= 0.82 and value_range >= 0.30:
            return "spiking"
        if value_range <= 0.12:
            return "flat"
        if len(values) >= 2 and values[-1] > values[0] + 0.18:
            return "rising"
        if len(values) >= 2 and values[-1] < values[0] - 0.18:
            return "falling"
        if len(self._release_indices([], values)) >= 1:
            return "release"
        if value_range >= 0.35:
            return "volatile"
        return "balanced"

    def _spike_indices(self, values: List[float]) -> List[int]:
        spikes = []
        for idx, value in enumerate(values):
            prev_value = values[idx - 1] if idx > 0 else value
            next_value = values[idx + 1] if idx + 1 < len(values) else value
            if value >= 0.75 and value - prev_value >= 0.18:
                spikes.append(idx)
            elif value >= 0.78 and value - next_value >= 0.20:
                spikes.append(idx)
        return spikes

    def _release_indices(self, points: List[Dict[str, Any]], values: List[float]) -> List[int]:
        releases = []
        for idx, value in enumerate(values):
            point_release = points[idx].get("release_value", 0.0) if points and idx < len(points) else 0.0
            prev_value = values[idx - 1] if idx > 0 else value
            if point_release >= 0.25 or (idx > 0 and prev_value - value >= 0.20):
                releases.append(idx)
        return releases

    def _flat_segments(self, values: List[float]) -> List[Dict[str, int]]:
        segments = []
        start = None

        for idx in range(1, len(values)):
            if abs(values[idx] - values[idx - 1]) <= 0.05:
                if start is None:
                    start = idx - 1
            else:
                if start is not None and idx - start >= 3:
                    segments.append({"start_index": start, "end_index": idx - 1})
                start = None

        if start is not None and len(values) - start >= 3:
            segments.append({"start_index": start, "end_index": len(values) - 1})

        return segments

    def _overload_score(self, values: List[float]) -> float:
        if not values:
            return 0.0
        high_count = sum(1 for value in values if value >= 0.75)
        consecutive_high = 0
        max_consecutive = 0
        for value in values:
            if value >= 0.75:
                consecutive_high += 1
                max_consecutive = max(max_consecutive, consecutive_high)
            else:
                consecutive_high = 0
        return round(min(1.0, high_count / len(values) * 0.55 + max_consecutive * 0.12), 3)

    def _pacing_score(self, values: List[float], points: List[Dict[str, Any]]) -> float:
        if len(values) <= 1:
            return 0.35 if values else 0.0

        value_range = max(values) - min(values)
        spikes = len(self._spike_indices(values))
        releases = len(self._release_indices(points, values))
        flat_penalty = len(self._flat_segments(values)) * 0.12
        overload_penalty = self._overload_score(values) * 0.25

        rise_bonus = 0.18 if values[-1] > values[0] + 0.15 else 0.0
        release_bonus = min(0.18, releases * 0.08)
        spike_bonus = min(0.18, spikes * 0.08)

        return round(
            max(
                0.0,
                min(
                    1.0,
                    0.35
                    + value_range * 0.28
                    + rise_bonus
                    + release_bonus
                    + spike_bonus
                    - flat_penalty
                    - overload_penalty,
                ),
            ),
            3,
        )

    def _curve_warnings(self, curve: Dict[str, Any]) -> List[str]:
        warnings = []
        if curve["point_count"] == 0:
            warnings.append("tension curve has no points")
        if curve["curve_label"] == "flat":
            warnings.append("tension curve is flat; add escalation, release, or contrast")
        if curve["curve_label"] == "overloaded":
            warnings.append("tension curve is overloaded; add release or aftermath")
        if curve["overload_score"] >= 0.6:
            warnings.append("too many high-tension beats clustered together")
        if curve["pacing_score"] < 0.35:
            warnings.append("pacing score is weak")
        if not curve["release_indices"] and curve["peak_tension"] >= 0.75:
            warnings.append("high tension has no release beat")
        return warnings

    def _chunk5_handoff(self, curve: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "curve_id": curve["curve_id"],
            "scene_or_arc_id": curve.get("source_id"),
            "curve_label": curve.get("curve_label"),
            "average_tension": curve.get("average_tension"),
            "peak_tension": curve.get("peak_tension"),
            "pacing_score": curve.get("pacing_score"),
            "needs_release_scene": curve.get("overload_score", 0.0) >= 0.55 or (
                curve.get("peak_tension", 0.0) >= 0.75 and not curve.get("release_indices")
            ),
            "needs_escalation": curve.get("curve_label") == "flat" or curve.get("average_tension", 0.0) < 0.30,
            "recommended_scene_adjustment": self._recommended_adjustment(curve),
        }

    def _recommended_adjustment(self, curve: Dict[str, Any]) -> str:
        if curve.get("curve_label") == "overloaded":
            return "add aftermath, silence, tenderness, humor, or reflection before next spike"
        if curve.get("curve_label") == "flat":
            return "add conflict escalation, reveal, cost, or deadline pressure"
        if curve.get("peak_tension", 0.0) >= 0.75 and not curve.get("release_indices"):
            return "add release beat after peak tension"
        if curve.get("pacing_score", 0.0) < 0.35:
            return "increase contrast between beats"
        return "tension rhythm acceptable"

    def _compare_warnings(self, curves: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not curves:
            warnings.append("no tension curves to compare")
        overloaded = [curve for curve in curves if curve.get("curve_label") == "overloaded"]
        if len(overloaded) >= 2:
            warnings.append("multiple curves are overloaded")
        flat = [curve for curve in curves if curve.get("curve_label") == "flat"]
        if len(flat) >= 2:
            warnings.append("multiple curves are flat")
        return warnings

    def _map_warnings(self, records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        if not records:
            warnings.append("no tension curves registered")
        low_pacing = [record for record in records.values() if record.get("pacing_score", 0.0) < 0.35]
        if low_pacing:
            warnings.append(f"{len(low_pacing)} curve(s) have weak pacing")
        return warnings

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)
