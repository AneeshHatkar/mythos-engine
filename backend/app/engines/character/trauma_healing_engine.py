from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import TraumaRecord
from backend.app.schemas.foundation import EngineRunResult


class TraumaHealingEngine(BaseEngine):
    """Builds trauma and healing logic for a character.

    Trauma in MythOS must never be decorative. It must affect behavior,
    triggers, avoidance, coping, relapse risk, healing conditions, relationship
    patterns, and future emotional arcs.

    This engine keeps trauma structured and tied to recovery paths.
    """

    engine_name = "character.trauma_healing_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin", {})
        family_profile = payload.get("family_profile") or character_seed.get("family", {})
        origin_story_hooks = payload.get("origin_story_hooks") or character_seed.get("origin_story_hooks", [])
        family_story_hooks = payload.get("family_story_hooks") or character_seed.get("family_story_hooks", [])

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; trauma engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or origin_profile.get("character_id")
            or family_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        trauma_records = self._build_trauma_records(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            origin_profile=origin_profile,
            family_profile=family_profile,
            origin_story_hooks=origin_story_hooks,
            family_story_hooks=family_story_hooks,
        )

        healing_profile = self._build_healing_profile(
            character_id=character_id,
            trauma_records=trauma_records,
            psychology_profile=psychology_profile,
            character_seed=character_seed,
        )

        trauma_diagnostics = self._build_trauma_diagnostics(
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            psychology_profile=psychology_profile,
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            trauma_records=trauma_records,
            healing_profile=healing_profile,
            psychology_profile=psychology_profile,
        )

        return self.build_result(
            success=True,
            data={
                "trauma_records": [record.model_dump() for record in trauma_records],
                "healing_profile": healing_profile,
                "trauma_diagnostics": trauma_diagnostics,
                "next_engine_payload": next_engine_payload,
                "trauma_summary": {
                    "character_id": character_id,
                    "trauma_count": len(trauma_records),
                    "highest_intensity": max([record.trauma_intensity for record in trauma_records], default=0.0),
                    "average_intensity": self._average([record.trauma_intensity for record in trauma_records]),
                    "has_healing_condition": bool(healing_profile.get("primary_healing_condition")),
                    "has_relapse_conditions": bool(healing_profile.get("relapse_conditions")),
                    "ready_for_emotion_engine": True,
                    "ready_for_emotional_arc_engine": True,
                    "ready_for_memory_engine": True,
                },
                "training_notes": [
                    "Trauma records are behavioral inputs, not aesthetic labels.",
                    "Healing requires conditions, milestones, relapse risks, and relationship/event support.",
                    "Future Chunk 8 training should treat trauma data carefully with provenance and safety review.",
                    "Trauma output should support character depth while avoiding shock-value generation.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[record.trauma_id for record in trauma_records],
        )

    def _build_trauma_records(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        origin_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        origin_story_hooks: List[str],
        family_story_hooks: List[str],
    ) -> List[TraumaRecord]:
        records: List[TraumaRecord] = []

        core_wound = psychology_profile.get("core_wound") or character_seed.get("core_wound")
        class_wound = origin_profile.get("class_wound")
        family_secrets = family_profile.get("family_secrets", [])
        inherited_trauma = family_profile.get("inherited_trauma", [])
        family_pressure = character_seed.get("family_pressure", {})

        if core_wound:
            records.append(
                TraumaRecord(
                    trauma_id=f"trauma_{uuid4().hex[:12]}",
                    character_id=character_id,
                    trauma_source=f"core wound: {core_wound}",
                    trauma_intensity=self._intensity_from_text(core_wound, default=0.72),
                    trigger_events=self._core_wound_triggers(core_wound, psychology_profile),
                    avoidance_behavior=self._avoidance_behavior(psychology_profile, origin_profile),
                    coping_behavior=self._coping_behavior(psychology_profile, character_seed),
                    relapse_risk=self._relapse_risk(psychology_profile, family_pressure, base=0.58),
                    healing_condition=psychology_profile.get("healing_condition") or character_seed.get("healing_condition"),
                    healing_relationship=self._healing_relationship(character_seed, psychology_profile),
                    recovery_milestones=self._recovery_milestones(core_wound, psychology_profile),
                    setback_conditions=self._setback_conditions(psychology_profile, family_profile),
                    content_safety_notes=[
                        "Treat core wound as behavior logic, not spectacle.",
                        "Do not use pain as automatic depth without agency and recovery path.",
                    ],
                )
            )

        if class_wound and class_wound != core_wound:
            records.append(
                TraumaRecord(
                    trauma_id=f"trauma_{uuid4().hex[:12]}",
                    character_id=character_id,
                    trauma_source=f"class wound: {class_wound}",
                    trauma_intensity=0.66,
                    trigger_events=[
                        "public rank evaluation",
                        "institutional dismissal",
                        "being judged by family name or class",
                    ],
                    avoidance_behavior="avoids situations where class status becomes public proof of worth",
                    coping_behavior="over-prepares, observes hierarchy, and searches for indirect leverage",
                    relapse_risk=0.52,
                    healing_condition="acts from self-worth instead of class permission",
                    healing_relationship="someone with higher status risks comfort to protect truth",
                    recovery_milestones=[
                        "names the class wound directly",
                        "accepts help without treating it as debt",
                        "makes one public choice despite status risk",
                    ],
                    setback_conditions=[
                        "public humiliation by elite authority",
                        "proof dismissed because of social class",
                    ],
                    content_safety_notes=[
                        "Do not equate low class with weakness.",
                        "Show structural pressure and agency together.",
                    ],
                )
            )

        if family_secrets:
            records.append(
                TraumaRecord(
                    trauma_id=f"trauma_{uuid4().hex[:12]}",
                    character_id=character_id,
                    trauma_source=f"family secrecy: {family_secrets[0]}",
                    trauma_intensity=0.62,
                    trigger_events=[
                        "questions about family history",
                        "official records request",
                        "intimacy that requires disclosure",
                    ],
                    avoidance_behavior="redirects family questions and controls personal information",
                    coping_behavior="keeps parallel explanations ready",
                    relapse_risk=0.57,
                    healing_condition="family truth is known by someone who does not weaponize it",
                    healing_relationship="trusted confidant who protects the secret without owning it",
                    recovery_milestones=[
                        "admits one partial truth",
                        "lets someone see a family artifact",
                        "chooses disclosure before coercion",
                    ],
                    setback_conditions=[
                        "secret exposed publicly",
                        "trusted person uses family truth for leverage",
                    ],
                    content_safety_notes=[
                        "Family secret should produce consequence, not mystery decoration.",
                    ],
                )
            )

        if inherited_trauma:
            records.append(
                TraumaRecord(
                    trauma_id=f"trauma_{uuid4().hex[:12]}",
                    character_id=character_id,
                    trauma_source=f"inherited trauma: {inherited_trauma[0]}",
                    trauma_intensity=0.55,
                    trigger_events=[
                        "repeating family pattern",
                        "guardian pressure",
                        "family obligation competing with personal truth",
                    ],
                    avoidance_behavior="mistakes inherited survival habits for personality",
                    coping_behavior="turns family warnings into personal rules",
                    relapse_risk=0.48,
                    healing_condition="recognizes inherited fear as inherited, not inevitable",
                    healing_relationship="mentor or peer who names the pattern without shaming it",
                    recovery_milestones=[
                        "separates family fear from personal choice",
                        "breaks one inherited rule safely",
                        "sets a boundary without abandoning family",
                    ],
                    setback_conditions=[
                        "family member punished",
                        "old family debt returns",
                    ],
                    content_safety_notes=[
                        "Inherited trauma should not remove personal agency.",
                    ],
                )
            )

        if not records:
            records.append(
                TraumaRecord(
                    trauma_id=f"trauma_{uuid4().hex[:12]}",
                    character_id=character_id,
                    trauma_source="low-intensity identity pressure",
                    trauma_intensity=0.32,
                    trigger_events=["being misread", "being assigned a role too quickly"],
                    avoidance_behavior="keeps emotional distance until trust is earned",
                    coping_behavior="uses observation and humor to stay safe",
                    relapse_risk=0.25,
                    healing_condition="is seen accurately during failure",
                    healing_relationship="consistent friend or rival who remembers details",
                    recovery_milestones=[
                        "admits discomfort",
                        "asks for help once",
                        "acts without overexplaining worth",
                    ],
                    setback_conditions=["public misinterpretation", "dismissal by authority"],
                    content_safety_notes=[
                        "Low-intensity pressure is valid; not every character needs extreme trauma.",
                    ],
                )
            )

        return records

    def _intensity_from_text(self, text: str, default: float) -> float:
        lowered = text.lower()

        if any(term in lowered for term in ["erasure", "erased", "death", "abandonment", "betrayal"]):
            return 0.82

        if any(term in lowered for term in ["humiliation", "disposable", "revoked", "failure"]):
            return 0.72

        if any(term in lowered for term in ["shame", "class", "worth"]):
            return 0.66

        return default

    def _core_wound_triggers(self, core_wound: str, psychology: Dict[str, Any]) -> List[str]:
        triggers = []

        shame_trigger = psychology.get("shame_trigger")
        if shame_trigger:
            triggers.append(shame_trigger)

        lowered = core_wound.lower()

        if "failure" in lowered or "revoked" in lowered:
            triggers.extend(["public failure", "rank comparison"])

        if "family" in lowered or "name" in lowered:
            triggers.extend(["family-name challenge", "legal testimony"])

        if "truth" in lowered or "believed" in lowered:
            triggers.extend(["truth dismissed by authority", "records contradicted"])

        if not triggers:
            triggers.extend(["being misunderstood", "public judgment"])

        return sorted(set(triggers))

    def _avoidance_behavior(self, psychology: Dict[str, Any], origin: Dict[str, Any]) -> str:
        stress = psychology.get("stress_response")
        if stress:
            return stress

        social_class = origin.get("social_class")

        if social_class in {"erased", "underclass"}:
            return "avoids documentation, official spaces, and questions of identity"

        if social_class == "academy_sponsored":
            return "avoids visible failure and over-manages public performance"

        return "withdraws before emotional dependence becomes visible"

    def _coping_behavior(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        defense = psychology.get("defense_mechanism") or seed.get("defense_mechanism")

        if defense:
            return f"relies on {defense} as primary coping behavior"

        return "uses control, observation, and delayed reaction to stay safe"

    def _relapse_risk(self, psychology: Dict[str, Any], family_pressure: Dict[str, Any], base: float) -> float:
        risk = base

        if family_pressure.get("pressure_tier") in {"high_family_pressure", "extreme_family_pressure"}:
            risk += 0.12

        if psychology.get("corruption_condition"):
            risk += 0.05

        return round(min(1.0, risk), 3)

    def _healing_relationship(self, seed: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if seed.get("healing_relationship"):
            return seed["healing_relationship"]

        love_response = psychology.get("love_response", "").lower()

        if "intimacy" in love_response:
            return "trusted person who receives truth without turning it into ownership"

        return "relationship that offers consistent protection without demanding performance"

    def _recovery_milestones(self, core_wound: str, psychology: Dict[str, Any]) -> List[str]:
        milestones = [
            "recognizes the wound in real time",
            "chooses one action not controlled by the wound",
            "accepts repair without needing to earn it first",
        ]

        healing = psychology.get("healing_condition")
        if healing:
            milestones.append(f"meets healing condition: {healing}")

        return milestones

    def _setback_conditions(self, psychology: Dict[str, Any], family: Dict[str, Any]) -> List[str]:
        conditions = []

        shame_trigger = psychology.get("shame_trigger")
        if shame_trigger:
            conditions.append(f"shame trigger repeats: {shame_trigger}")

        if family.get("family_secrets"):
            conditions.append("family secret is used as leverage")

        if psychology.get("betrayal_response"):
            conditions.append("trusted person repeats betrayal pattern")

        if not conditions:
            conditions.append("old defense mechanism is rewarded by the world")

        return conditions

    def _build_healing_profile(
        self,
        *,
        character_id: str,
        trauma_records: List[TraumaRecord],
        psychology_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        highest = max(trauma_records, key=lambda record: record.trauma_intensity)

        relapse_conditions = []
        recovery_milestones = []
        safety_notes = []

        for record in trauma_records:
            relapse_conditions.extend(record.setback_conditions)
            recovery_milestones.extend(record.recovery_milestones)
            safety_notes.extend(record.content_safety_notes)

        return {
            "character_id": character_id,
            "primary_trauma_id": highest.trauma_id,
            "primary_healing_condition": highest.healing_condition,
            "primary_healing_relationship": highest.healing_relationship,
            "healing_style": self._healing_style(psychology_profile, character_seed),
            "healing_pace": self._healing_pace(highest.trauma_intensity),
            "relapse_conditions": sorted(set(relapse_conditions)),
            "recovery_milestones": sorted(set(recovery_milestones)),
            "support_needed": self._support_needed(highest, psychology_profile),
            "unsafe_shortcuts": [
                "instant forgiveness",
                "romance curing trauma without earned trust",
                "power-up replacing emotional recovery",
                "using trauma only to justify cruelty",
            ],
            "content_safety_notes": sorted(set(safety_notes)),
        }

    def _healing_style(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        attachment = psychology.get("attachment_tendency", "").lower()

        if "avoidant" in attachment or "slow trust" in attachment:
            return "slow relational trust with repeated proof"

        if seed.get("role") == "villain":
            return "accountability before redemption"

        return "earned safety through action and memory integration"

    def _healing_pace(self, intensity: float) -> str:
        if intensity >= 0.8:
            return "slow_multi_arc_recovery"

        if intensity >= 0.6:
            return "gradual_arc_recovery"

        return "low_intensity_growth_recovery"

    def _support_needed(self, trauma: TraumaRecord, psychology: Dict[str, Any]) -> List[str]:
        support = [
            "consistent behavior over speeches",
            "space to choose disclosure timing",
        ]

        if trauma.trauma_intensity >= 0.7:
            support.append("visible protection during trigger event")

        if psychology.get("healing_condition"):
            support.append(psychology["healing_condition"])

        return support

    def _build_trauma_diagnostics(
        self,
        *,
        trauma_records: List[TraumaRecord],
        healing_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        high_intensity_count = sum(1 for record in trauma_records if record.trauma_intensity >= 0.7)
        has_triggers = all(len(record.trigger_events) > 0 for record in trauma_records)
        has_coping = all(bool(record.coping_behavior) for record in trauma_records)
        has_healing = all(bool(record.healing_condition) for record in trauma_records)
        has_setbacks = all(len(record.setback_conditions) > 0 for record in trauma_records)

        behavioral_completeness = sum(
            [
                has_triggers,
                has_coping,
                has_healing,
                has_setbacks,
                bool(healing_profile.get("relapse_conditions")),
                bool(healing_profile.get("recovery_milestones")),
            ]
        ) / 6

        return {
            "trauma_record_count": len(trauma_records),
            "high_intensity_count": high_intensity_count,
            "behavioral_completeness_score": round(behavioral_completeness, 3),
            "has_trigger_logic": has_triggers,
            "has_coping_logic": has_coping,
            "has_healing_logic": has_healing,
            "has_setback_logic": has_setbacks,
            "trauma_not_decorative": behavioral_completeness >= 0.8,
            "needs_content_review": any(record.trauma_intensity >= 0.85 for record in trauma_records),
            "ready_for_emotion_engine": behavioral_completeness >= 0.8,
        }

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        trauma_records: List[TraumaRecord],
        healing_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["trauma_records"] = [record.model_dump() for record in trauma_records]
        merged_seed["healing_profile"] = healing_profile

        return {
            "character_seed": merged_seed,
            "emotion_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "trauma_records": [record.model_dump() for record in trauma_records],
                "healing_profile": healing_profile,
            },
            "emotional_arc_engine_payload": {
                "character_seed": merged_seed,
                "psychology_profile": psychology_profile,
                "trauma_records": [record.model_dump() for record in trauma_records],
                "healing_profile": healing_profile,
            },
            "memory_engine_payload": {
                "character_seed": merged_seed,
                "trauma_records": [record.model_dump() for record in trauma_records],
                "healing_profile": healing_profile,
            },
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0

        return round(sum(values) / len(values), 3)
