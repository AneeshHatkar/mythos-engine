from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import EmotionalArcProfile
from backend.app.schemas.foundation import EngineRunResult


class EmotionalArcEngine(BaseEngine):
    """Builds long-range emotional movement for a character.

    The Emotion Engine creates the current/baseline emotional state.
    This engine turns that state into long-term emotional trajectory:
    hope, despair, romance, healing, rage, corruption, redemption,
    climax, and resolution.
    """

    engine_name = "character.emotional_arc_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        trauma_records = payload.get("trauma_records") or character_seed.get("trauma_records", [])
        healing_profile = payload.get("healing_profile") or character_seed.get("healing_profile", {})
        emotional_state_profile = payload.get("emotional_state_profile") or character_seed.get("emotional_state", {})
        emotion_update_rules = payload.get("emotion_update_rules") or character_seed.get("emotion_update_rules", [])

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; emotional arc engine used draft defaults.")

        if not emotional_state_profile:
            warnings.append("No emotional_state_profile provided; emotional arc engine estimated curves from psychology.")

        character_id = (
            character_seed.get("character_id")
            or emotional_state_profile.get("character_id")
            or psychology_profile.get("character_id")
            or self._first_character_id(trauma_records)
            or f"char_{uuid4().hex[:12]}"
        )

        arc_type = self._choose_arc_type(character_seed, psychology_profile, trauma_records)

        arc = EmotionalArcProfile(
            emotional_arc_id=f"earc_{uuid4().hex[:12]}",
            character_id=character_id,
            arc_type=arc_type,
            hope_curve=self._hope_curve(arc_type, emotional_state_profile, healing_profile),
            despair_cycle=self._despair_cycle(arc_type, trauma_records, emotional_state_profile),
            romantic_tension_curve=self._romantic_tension_curve(character_seed, psychology_profile),
            healing_milestones=self._healing_milestones(healing_profile, psychology_profile),
            rage_escalation=self._rage_escalation(character_seed, emotional_state_profile, psychology_profile),
            corruption_curve=self._corruption_curve(arc_type, psychology_profile, character_seed),
            redemption_curve=self._redemption_curve(arc_type, psychology_profile, healing_profile),
            emotional_climax=self._emotional_climax(character_seed, psychology_profile, arc_type),
            emotional_resolution=self._emotional_resolution(character_seed, psychology_profile, arc_type),
            open_wounds=self._open_wounds(psychology_profile, trauma_records),
        )

        arc_beats = self._build_arc_beats(arc, psychology_profile, character_seed)
        arc_diagnostics = self._build_diagnostics(arc, emotion_update_rules)
        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            emotional_state_profile=emotional_state_profile,
            emotional_arc_profile=arc,
            arc_beats=arc_beats,
        )

        return self.build_result(
            success=True,
            data={
                "emotional_arc_profile": arc.model_dump(),
                "arc_beats": arc_beats,
                "arc_diagnostics": arc_diagnostics,
                "next_engine_payload": next_engine_payload,
                "emotional_arc_summary": {
                    "character_id": character_id,
                    "arc_type": arc.arc_type,
                    "hope_start": arc.hope_curve[0] if arc.hope_curve else 0.0,
                    "hope_end": arc.hope_curve[-1] if arc.hope_curve else 0.0,
                    "despair_peak": max(arc.despair_cycle, default=0.0),
                    "corruption_peak": max(arc.corruption_curve, default=0.0),
                    "redemption_end": arc.redemption_curve[-1] if arc.redemption_curve else 0.0,
                    "has_emotional_climax": arc.emotional_climax is not None,
                    "ready_for_memory_engine": True,
                    "ready_for_goal_engine": True,
                    "ready_for_plot_engine_later": True,
                },
                "training_notes": [
                    "Emotional arcs prepare characters for long-form story, not isolated scene reactions.",
                    "Relationship and plot engines should use arc curves to time conflict, healing, betrayal, and payoff.",
                    "Arc curves are deterministic scaffolds now; later Chunk 8 can learn curve shapes from curated stories.",
                    "A strong franchise character needs emotional movement that can sustain multiple books, seasons, or routes.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[arc.emotional_arc_id],
        )

    def _first_character_id(self, trauma_records: List[Dict[str, Any]]) -> str | None:
        if trauma_records and isinstance(trauma_records[0], dict):
            return trauma_records[0].get("character_id")
        return None

    def _choose_arc_type(
        self,
        seed: Dict[str, Any],
        psychology: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
    ) -> str:
        if seed.get("arc_type"):
            return seed["arc_type"]

        role = seed.get("role", "")
        text = (str(seed) + " " + str(psychology)).lower()

        if role == "villain":
            return "corruption_or_accountability_arc"

        if seed.get("adaptability_type") or seed.get("breakthrough_condition"):
            return "adaptive_breakthrough_arc"

        if "love_interest" in role or "romance" in text or "intimacy" in text:
            return "slow_burn_trust_arc"

        if "corruption" in text:
            return "corruption_or_accountability_arc"

        if trauma_records:
            return "wound_to_agency_arc"

        return "identity_growth_arc"

    def _hope_curve(self, arc_type: str, emotional_state: Dict[str, Any], healing: Dict[str, Any]) -> List[float]:
        base_hope = self._emotion_value(emotional_state, "hope", default=0.38)

        if arc_type == "corruption_or_accountability_arc":
            return self._curve([base_hope, 0.42, 0.32, 0.22, 0.28, 0.45])

        if arc_type == "slow_burn_trust_arc":
            return self._curve([base_hope, 0.36, 0.44, 0.52, 0.48, 0.68])

        if arc_type == "adaptive_breakthrough_arc":
            return self._curve([base_hope, 0.34, 0.48, 0.42, 0.72, 0.64])

        if arc_type == "wound_to_agency_arc":
            return self._curve([base_hope, 0.3, 0.38, 0.5, 0.58, 0.72])

        return self._curve([base_hope, 0.42, 0.5, 0.56, 0.62, 0.7])

    def _despair_cycle(
        self,
        arc_type: str,
        trauma_records: List[Dict[str, Any]],
        emotional_state: Dict[str, Any],
    ) -> List[float]:
        max_trauma = max([record.get("trauma_intensity", 0.0) for record in trauma_records], default=0.35)
        base_despair = max(self._emotion_value(emotional_state, "despair", default=0.25), max_trauma * 0.5)

        if arc_type == "corruption_or_accountability_arc":
            return self._curve([base_despair, 0.42, 0.62, 0.78, 0.7, 0.45])

        if arc_type == "adaptive_breakthrough_arc":
            return self._curve([base_despair, 0.4, 0.58, 0.64, 0.35, 0.42])

        if arc_type == "slow_burn_trust_arc":
            return self._curve([base_despair, 0.38, 0.46, 0.52, 0.34, 0.22])

        return self._curve([base_despair, 0.44, 0.5, 0.38, 0.28, 0.2])

    def _romantic_tension_curve(self, seed: Dict[str, Any], psychology: Dict[str, Any]) -> List[float]:
        text = (str(seed) + " " + str(psychology)).lower()
        role = seed.get("role", "")

        if "love_interest" in role or "romance" in text or "intimacy" in text:
            return self._curve([0.18, 0.32, 0.55, 0.7, 0.62, 0.82])

        if role in {"protagonist", "rival", "deuteragonist"}:
            return self._curve([0.08, 0.16, 0.28, 0.36, 0.42, 0.52])

        return self._curve([0.02, 0.04, 0.06, 0.08, 0.1, 0.12])

    def _healing_milestones(self, healing: Dict[str, Any], psychology: Dict[str, Any]) -> List[str]:
        milestones = list(healing.get("recovery_milestones", []))

        if psychology.get("healing_condition"):
            milestones.append(f"healing condition becomes possible: {psychology['healing_condition']}")

        if not milestones:
            milestones = [
                "recognizes emotional pattern",
                "takes one choice outside defense mechanism",
                "accepts repair without over-explaining worth",
            ]

        return sorted(set(milestones))

    def _rage_escalation(self, seed: Dict[str, Any], emotional_state: Dict[str, Any], psychology: Dict[str, Any]) -> List[float]:
        base_anger = self._emotion_value(emotional_state, "anger", default=0.3)
        text = (str(seed) + " " + str(psychology)).lower()

        if "injustice" in text or "protects someone weaker" in text:
            return self._curve([base_anger, 0.36, 0.48, 0.6, 0.72, 0.5])

        if seed.get("role") == "villain":
            return self._curve([base_anger, 0.42, 0.58, 0.76, 0.84, 0.7])

        return self._curve([base_anger, 0.32, 0.38, 0.44, 0.4, 0.35])

    def _corruption_curve(self, arc_type: str, psychology: Dict[str, Any], seed: Dict[str, Any]) -> List[float]:
        has_corruption = bool(psychology.get("corruption_condition"))
        role = seed.get("role")

        if arc_type == "corruption_or_accountability_arc" or role == "villain":
            return self._curve([0.25, 0.4, 0.62, 0.78, 0.85, 0.68])

        if has_corruption:
            return self._curve([0.12, 0.2, 0.34, 0.48, 0.38, 0.22])

        return self._curve([0.05, 0.08, 0.12, 0.16, 0.12, 0.08])

    def _redemption_curve(self, arc_type: str, psychology: Dict[str, Any], healing: Dict[str, Any]) -> List[float]:
        has_healing = bool(psychology.get("healing_condition") or healing.get("primary_healing_condition"))

        if arc_type == "corruption_or_accountability_arc":
            return self._curve([0.08, 0.1, 0.16, 0.22, 0.38, 0.58])

        if has_healing:
            return self._curve([0.18, 0.24, 0.36, 0.48, 0.62, 0.78])

        return self._curve([0.12, 0.16, 0.2, 0.25, 0.32, 0.4])

    def _emotional_climax(self, seed: Dict[str, Any], psychology: Dict[str, Any], arc_type: str) -> str:
        if seed.get("breakthrough_condition") and arc_type == "adaptive_breakthrough_arc":
            return f"Limit-break emotional climax occurs when: {seed['breakthrough_condition']}"

        if arc_type == "corruption_or_accountability_arc":
            return psychology.get("corruption_condition") or "Character chooses whether order is worth sacrificing a person."

        if arc_type == "slow_burn_trust_arc":
            return "Character must choose honest vulnerability before certainty of being accepted."

        return psychology.get("healing_condition") or "Character acts from truth instead of wound."

    def _emotional_resolution(self, seed: Dict[str, Any], psychology: Dict[str, Any], arc_type: str) -> str:
        if arc_type == "corruption_or_accountability_arc":
            return "Resolution depends on whether accountability becomes more important than control."

        if arc_type == "adaptive_breakthrough_arc":
            return "Resolution requires accepting consequence after breakthrough instead of chasing power."

        if arc_type == "slow_burn_trust_arc":
            return "Resolution requires love that preserves selfhood and truth."

        return psychology.get("core_truth") or "Resolution comes when worth is separated from usefulness."

    def _open_wounds(self, psychology: Dict[str, Any], trauma_records: List[Dict[str, Any]]) -> List[str]:
        wounds = []

        if psychology.get("core_wound"):
            wounds.append(psychology["core_wound"])

        for record in trauma_records:
            source = record.get("trauma_source")
            if source:
                wounds.append(source)

        return sorted(set(wounds))

    def _build_arc_beats(
        self,
        arc: EmotionalArcProfile,
        psychology: Dict[str, Any],
        seed: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "beat": "initial_mask",
                "function": "show defense mechanism before full wound is named",
                "emotional_focus": arc.dominant_focus if hasattr(arc, "dominant_focus") else "suppressed need",
                "scene_use": psychology.get("defense_mechanism", "controlled distance"),
            },
            {
                "beat": "first_trigger",
                "function": "repeat shame/fear trigger in a controlled situation",
                "emotional_focus": psychology.get("shame_trigger", "public judgment"),
                "scene_use": "early conflict or academy/public pressure scene",
            },
            {
                "beat": "relationship_pressure",
                "function": "force trust, love, rivalry, or betrayal response",
                "emotional_focus": psychology.get("love_response", "guarded vulnerability"),
                "scene_use": "Chunk 4 relationship simulation hook",
            },
            {
                "beat": "midpoint_collapse_or_breakthrough",
                "function": "test whether wound controls choice",
                "emotional_focus": arc.emotional_climax,
                "scene_use": "major plot or limit-break event",
            },
            {
                "beat": "resolution_choice",
                "function": "character acts from truth or doubles down on lie",
                "emotional_focus": arc.emotional_resolution,
                "scene_use": "final emotional payoff",
            },
        ]

    def _build_diagnostics(
        self,
        arc: EmotionalArcProfile,
        emotion_update_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        curves = [
            arc.hope_curve,
            arc.despair_cycle,
            arc.romantic_tension_curve,
            arc.rage_escalation,
            arc.corruption_curve,
            arc.redemption_curve,
        ]

        curve_lengths = [len(curve) for curve in curves]
        has_consistent_curves = len(set(curve_lengths)) == 1 and curve_lengths[0] >= 6

        return {
            "curve_count": len(curves),
            "curve_lengths": curve_lengths,
            "has_consistent_curves": has_consistent_curves,
            "has_healing_milestones": len(arc.healing_milestones) > 0,
            "has_climax": arc.emotional_climax is not None,
            "has_resolution": arc.emotional_resolution is not None,
            "has_update_rules": len(emotion_update_rules) > 0,
            "plot_ready": has_consistent_curves and arc.emotional_climax is not None and arc.emotional_resolution is not None,
            "relationship_arc_ready": max(arc.romantic_tension_curve, default=0.0) > 0.3,
            "corruption_or_redemption_ready": max(arc.corruption_curve, default=0.0) > 0.3 or max(arc.redemption_curve, default=0.0) > 0.5,
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        healing_profile: Dict[str, Any],
        emotional_state_profile: Dict[str, Any],
        emotional_arc_profile: EmotionalArcProfile,
        arc_beats: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["emotional_arc"] = emotional_arc_profile.model_dump()
        merged_seed["arc_beats"] = arc_beats

        return {
            "character_seed": merged_seed,
            "memory_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "trauma_records": trauma_records,
                "healing_profile": healing_profile,
                "emotional_state_profile": emotional_state_profile,
                "emotional_arc_profile": emotional_arc_profile.model_dump(),
                "arc_beats": arc_beats,
            },
            "goal_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "emotional_arc_profile": emotional_arc_profile.model_dump(),
            },
            "plot_engine_payload_later": {
                "character_id": emotional_arc_profile.character_id,
                "arc_type": emotional_arc_profile.arc_type,
                "curves": {
                    "hope": emotional_arc_profile.hope_curve,
                    "despair": emotional_arc_profile.despair_cycle,
                    "romantic_tension": emotional_arc_profile.romantic_tension_curve,
                    "rage": emotional_arc_profile.rage_escalation,
                    "corruption": emotional_arc_profile.corruption_curve,
                    "redemption": emotional_arc_profile.redemption_curve,
                },
                "arc_beats": arc_beats,
            },
        }

    def _emotion_value(self, emotional_state: Dict[str, Any], emotion: str, default: float) -> float:
        if not emotional_state:
            return default

        current = emotional_state.get("current", {})
        baseline = emotional_state.get("baseline", {})

        if emotion in current:
            return float(current[emotion])

        if emotion in baseline:
            return float(baseline[emotion])

        return default

    def _curve(self, values: List[float]) -> List[float]:
        return [round(max(0.0, min(1.0, value)), 3) for value in values]
