from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import EmotionalStateProfile, EmotionVector
from backend.app.schemas.foundation import EngineRunResult


class EmotionEngine(BaseEngine):
    """Builds persistent emotional state for a character.

    This engine prevents characters from emotionally resetting between scenes.
    It converts psychology, trauma, healing, goals, and social pressure into
    baseline and current emotion vectors.
    """

    engine_name = "character.emotion_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        trauma_records = payload.get("trauma_records") or character_seed.get("trauma_records", [])
        healing_profile = payload.get("healing_profile") or character_seed.get("healing_profile", {})
        family_pressure = character_seed.get("family_pressure", {})

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; emotion engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or self._first_character_id(trauma_records)
            or f"char_{uuid4().hex[:12]}"
        )

        emotion_drivers = self._build_emotion_drivers(
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            family_pressure=family_pressure,
        )

        baseline = self._build_baseline_vector(emotion_drivers)
        current = self._build_current_vector(baseline, emotion_drivers)

        profile = EmotionalStateProfile(
            emotional_state_id=f"emo_{uuid4().hex[:12]}",
            character_id=character_id,
            baseline=baseline,
            current=current,
            volatility=self._volatility(emotion_drivers, trauma_records),
            recovery_rate=self._recovery_rate(healing_profile, trauma_records),
            dominant_state=self._dominant_state(current),
            suppressed_emotions=self._suppressed_emotions(psychology_profile, character_seed),
            recent_emotion_deltas=self._recent_emotion_deltas(emotion_drivers),
        )

        emotion_update_rules = self._build_update_rules(profile, psychology_profile, trauma_records, healing_profile)
        emotion_diagnostics = self._build_diagnostics(profile, emotion_drivers, trauma_records)
        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            emotional_state_profile=profile,
            emotion_update_rules=emotion_update_rules,
        )

        return self.build_result(
            success=True,
            data={
                "emotional_state_profile": profile.model_dump(),
                "emotion_drivers": emotion_drivers,
                "emotion_update_rules": emotion_update_rules,
                "emotion_diagnostics": emotion_diagnostics,
                "next_engine_payload": next_engine_payload,
                "emotion_summary": {
                    "character_id": character_id,
                    "dominant_state": profile.dominant_state,
                    "volatility": profile.volatility,
                    "recovery_rate": profile.recovery_rate,
                    "suppressed_emotion_count": len(profile.suppressed_emotions),
                    "ready_for_emotional_arc_engine": True,
                    "ready_for_memory_engine": True,
                    "ready_for_relationship_simulation_later": True,
                },
                "training_notes": [
                    "Emotion vectors allow stateful scene-to-scene continuity.",
                    "Future relationship simulation should update current emotions without overwriting baseline emotions.",
                    "Emotion deltas should be caused by events, memories, relationships, goals, and world pressure.",
                    "Future Chunk 8 can learn emotion-transition models from curated character-event data.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[profile.emotional_state_id],
        )

    def _first_character_id(self, trauma_records: List[Dict[str, Any]]) -> str | None:
        if trauma_records and isinstance(trauma_records[0], dict):
            return trauma_records[0].get("character_id")
        return None

    def _build_emotion_drivers(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        healing_profile: Dict[str, Any],
        family_pressure: Dict[str, Any],
    ) -> Dict[str, Any]:
        trauma_intensities = [
            float(record.get("trauma_intensity", 0.0))
            for record in trauma_records
            if isinstance(record, dict)
        ]

        avg_trauma = self._average(trauma_intensities)
        max_trauma = max(trauma_intensities, default=0.0)

        core_wound = psychology_profile.get("core_wound") or character_seed.get("core_wound", "")
        core_fear = psychology_profile.get("core_fear") or character_seed.get("core_fear", "")
        core_desire = psychology_profile.get("core_desire") or character_seed.get("core_desire", "")
        healing_condition = psychology_profile.get("healing_condition") or healing_profile.get("primary_healing_condition")
        corruption_condition = psychology_profile.get("corruption_condition")

        return {
            "core_wound": core_wound,
            "core_fear": core_fear,
            "core_desire": core_desire,
            "healing_condition": healing_condition,
            "corruption_condition": corruption_condition,
            "average_trauma_intensity": avg_trauma,
            "max_trauma_intensity": max_trauma,
            "family_pressure_tier": family_pressure.get("pressure_tier"),
            "has_family_secrecy": "family secrets" in str(psychology_profile).lower() or "secret" in str(character_seed).lower(),
            "has_destiny_pressure": bool(character_seed.get("destiny_type")),
            "has_limit_break_pressure": bool(character_seed.get("adaptability_type") or character_seed.get("breakthrough_condition")),
            "has_healing_path": bool(healing_condition),
            "relationship_vulnerability": self._relationship_vulnerability(psychology_profile),
            "public_shame_pressure": self._public_shame_pressure(psychology_profile, character_seed),
        }

    def _relationship_vulnerability(self, psychology: Dict[str, Any]) -> float:
        text = str(psychology).lower()

        score = 0.3

        if "intimacy" in text:
            score += 0.25

        if "slow trust" in text:
            score += 0.2

        if "betrayal" in text or "family secrets" in text:
            score += 0.15

        return round(min(1.0, score), 3)

    def _public_shame_pressure(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> float:
        text = (str(psychology) + " " + str(seed)).lower()

        score = 0.2

        if "shame" in text:
            score += 0.25

        if "public" in text:
            score += 0.2

        if "rank" in text or "failure" in text or "humiliation" in text:
            score += 0.2

        return round(min(1.0, score), 3)

    def _build_baseline_vector(self, drivers: Dict[str, Any]) -> EmotionVector:
        trauma = drivers["average_trauma_intensity"]
        max_trauma = drivers["max_trauma_intensity"]
        shame_pressure = drivers["public_shame_pressure"]
        vulnerability = drivers["relationship_vulnerability"]

        anger = 0.25 + trauma * 0.22
        fear = 0.25 + max_trauma * 0.35
        hope = 0.32 + (0.18 if drivers["has_healing_path"] else 0.0)
        love = 0.22 + vulnerability * 0.18
        shame = 0.22 + shame_pressure * 0.45
        grief = 0.18 + trauma * 0.25
        envy = 0.12 + (0.18 if "academy" in str(drivers).lower() else 0.0)
        pride = 0.22 + (0.15 if drivers["has_destiny_pressure"] else 0.0)
        trust = 0.18 + vulnerability * 0.08
        loneliness = 0.28 + trauma * 0.25
        guilt = 0.16 + (0.16 if drivers["family_pressure_tier"] in {"high_family_pressure", "extreme_family_pressure"} else 0.0)
        revenge = 0.1 + (0.18 if drivers["corruption_condition"] else 0.0)
        despair = 0.12 + max_trauma * 0.25
        purpose = 0.42 + (0.18 if drivers["has_destiny_pressure"] else 0.0)
        obsession = 0.18 + (0.18 if drivers["has_limit_break_pressure"] else 0.0)
        peace = 0.18 + (0.12 if drivers["has_healing_path"] else 0.0) - trauma * 0.1

        return EmotionVector(
            anger=self._clamp(anger),
            fear=self._clamp(fear),
            hope=self._clamp(hope),
            love=self._clamp(love),
            shame=self._clamp(shame),
            grief=self._clamp(grief),
            envy=self._clamp(envy),
            pride=self._clamp(pride),
            trust=self._clamp(trust),
            loneliness=self._clamp(loneliness),
            guilt=self._clamp(guilt),
            revenge=self._clamp(revenge),
            despair=self._clamp(despair),
            purpose=self._clamp(purpose),
            obsession=self._clamp(obsession),
            peace=self._clamp(peace),
        )

    def _build_current_vector(self, baseline: EmotionVector, drivers: Dict[str, Any]) -> EmotionVector:
        current = baseline.model_dump()

        if drivers["has_family_secrecy"]:
            current["fear"] += 0.08
            current["trust"] -= 0.04
            current["shame"] += 0.04

        if drivers["has_limit_break_pressure"]:
            current["obsession"] += 0.08
            current["purpose"] += 0.06
            current["peace"] -= 0.04

        if drivers["public_shame_pressure"] >= 0.6:
            current["shame"] += 0.08
            current["anger"] += 0.04

        return EmotionVector(**{key: self._clamp(value) for key, value in current.items()})

    def _volatility(self, drivers: Dict[str, Any], trauma_records: List[Dict[str, Any]]) -> float:
        score = 0.25
        score += drivers["max_trauma_intensity"] * 0.35

        if drivers["has_limit_break_pressure"]:
            score += 0.18

        if drivers["has_family_secrecy"]:
            score += 0.08

        return self._clamp(score)

    def _recovery_rate(self, healing_profile: Dict[str, Any], trauma_records: List[Dict[str, Any]]) -> float:
        score = 0.35

        if healing_profile.get("primary_healing_condition"):
            score += 0.18

        if healing_profile.get("recovery_milestones"):
            score += 0.12

        avg_trauma = self._average([
            float(record.get("trauma_intensity", 0.0))
            for record in trauma_records
            if isinstance(record, dict)
        ])

        score -= avg_trauma * 0.18

        return self._clamp(score)

    def _dominant_state(self, vector: EmotionVector) -> str:
        values = vector.model_dump()
        top = max(values, key=values.get)

        mapping = {
            "anger": "controlled anger",
            "fear": "guarded fear",
            "hope": "fragile hope",
            "love": "guarded tenderness",
            "shame": "restrained shame",
            "grief": "quiet grief",
            "envy": "competitive envy",
            "pride": "defensive pride",
            "trust": "cautious trust",
            "loneliness": "isolated longing",
            "guilt": "moral guilt",
            "revenge": "revenge pressure",
            "despair": "suppressed despair",
            "purpose": "focused purpose",
            "obsession": "unstable obsession",
            "peace": "rare calm",
        }

        return mapping[top]

    def _suppressed_emotions(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        text = (str(psychology) + " " + str(seed)).lower()
        suppressed = []

        if "controlled" in text or "restraint" in text or "silence" in text:
            suppressed.extend(["fear", "need", "grief"])

        if "family secrets" in text or "secret" in text:
            suppressed.append("trust")

        if "public" in text or "shame" in text:
            suppressed.append("humiliation")

        if not suppressed:
            suppressed.extend(["need", "uncertainty"])

        return sorted(set(suppressed))

    def _recent_emotion_deltas(self, drivers: Dict[str, Any]) -> List[Dict[str, Any]]:
        deltas = []

        if drivers["has_family_secrecy"]:
            deltas.append(
                {
                    "source": "family secrecy pressure",
                    "emotion": "fear",
                    "delta": 0.08,
                    "reason": "intimacy or record scrutiny threatens exposure",
                }
            )

        if drivers["has_limit_break_pressure"]:
            deltas.append(
                {
                    "source": "limit-break pressure",
                    "emotion": "obsession",
                    "delta": 0.08,
                    "reason": "breakthrough condition creates unstable focus",
                }
            )

        if drivers["public_shame_pressure"] >= 0.6:
            deltas.append(
                {
                    "source": "public shame pressure",
                    "emotion": "shame",
                    "delta": 0.08,
                    "reason": "public evaluation threatens core wound",
                }
            )

        return deltas

    def _build_update_rules(
        self,
        profile: EmotionalStateProfile,
        psychology: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        healing_profile: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        rules = [
            {
                "trigger": "shame_trigger_repeated",
                "updates": {"shame": 0.12, "anger": 0.06, "trust": -0.05},
                "notes": "Use when the character is publicly judged through the old wound.",
            },
            {
                "trigger": "trusted_person_protects_secret",
                "updates": {"trust": 0.12, "fear": -0.06, "hope": 0.08},
                "notes": "Use when someone protects truth without weaponizing it.",
            },
            {
                "trigger": "betrayal_pattern_repeats",
                "updates": {"trust": -0.15, "fear": 0.08, "anger": 0.1},
                "notes": "Use when a trusted character repeats the betrayal pattern.",
            },
            {
                "trigger": "limit_break_condition_approaches",
                "updates": {"obsession": 0.12, "purpose": 0.08, "peace": -0.08},
                "notes": "Use before adaptability or limit-break activation.",
            },
        ]

        if healing_profile.get("primary_healing_condition"):
            rules.append(
                {
                    "trigger": "healing_condition_met",
                    "updates": {"hope": 0.15, "peace": 0.1, "shame": -0.08},
                    "notes": healing_profile["primary_healing_condition"],
                }
            )

        return rules

    def _build_diagnostics(
        self,
        profile: EmotionalStateProfile,
        drivers: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        baseline = profile.baseline.model_dump()
        current = profile.current.model_dump()

        emotional_range = max(current.values()) - min(current.values())
        high_emotions = [key for key, value in current.items() if value >= 0.6]

        return {
            "emotion_vector_complete": len(baseline) == 16 and len(current) == 16,
            "dominant_state": profile.dominant_state,
            "high_emotions": high_emotions,
            "emotional_range": round(emotional_range, 3),
            "has_recent_deltas": len(profile.recent_emotion_deltas) > 0,
            "has_suppressed_emotions": len(profile.suppressed_emotions) > 0,
            "volatility_tier": self._volatility_tier(profile.volatility),
            "recovery_tier": self._recovery_tier(profile.recovery_rate),
            "stateful_scene_ready": len(profile.recent_emotion_deltas) > 0 or bool(trauma_records),
            "relationship_simulation_ready": profile.current.trust > 0.0 and profile.current.fear > 0.0,
        }

    def _volatility_tier(self, value: float) -> str:
        if value >= 0.7:
            return "high_volatility"
        if value >= 0.45:
            return "moderate_volatility"
        return "low_volatility"

    def _recovery_tier(self, value: float) -> str:
        if value >= 0.55:
            return "strong_recovery_capacity"
        if value >= 0.35:
            return "fragile_recovery_capacity"
        return "slow_recovery_capacity"

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        trauma_records: List[Dict[str, Any]],
        healing_profile: Dict[str, Any],
        emotional_state_profile: EmotionalStateProfile,
        emotion_update_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["emotional_state"] = emotional_state_profile.model_dump()
        merged_seed["emotion_update_rules"] = emotion_update_rules

        return {
            "character_seed": merged_seed,
            "emotional_arc_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "trauma_records": trauma_records,
                "healing_profile": healing_profile,
                "emotional_state_profile": emotional_state_profile.model_dump(),
                "emotion_update_rules": emotion_update_rules,
            },
            "memory_engine_payload": {
                "character_seed": merged_seed,
                "emotional_state_profile": emotional_state_profile.model_dump(),
                "trauma_records": trauma_records,
            },
            "relationship_simulation_payload_later": {
                "character_id": emotional_state_profile.character_id,
                "baseline_emotions": emotional_state_profile.baseline.model_dump(),
                "current_emotions": emotional_state_profile.current.model_dump(),
                "emotion_update_rules": emotion_update_rules,
            },
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
