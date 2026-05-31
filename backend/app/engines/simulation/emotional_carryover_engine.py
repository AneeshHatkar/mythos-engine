from typing import Any, Dict, List, Optional


class EmotionalCarryoverEngine:
    """Tracks emotional residue across simulation beats.

    Characters should not emotionally reset after every scene. This engine stores
    carryover states like guilt, fear, anger, hope, grief, shame, romantic tension,
    trust aftertaste, wound activation, and unresolved emotional pressure.
    """

    engine_name = "simulation.emotional_carryover_engine"

    EMOTION_TYPES = {
        "anger",
        "fear",
        "guilt",
        "shame",
        "grief",
        "hope",
        "trust",
        "distrust",
        "romantic_tension",
        "longing",
        "relief",
        "resentment",
        "loyalty",
        "betrayal_pain",
        "awe",
        "isolation",
        "determination",
        "confusion",
    }

    CARRYOVER_STATUS_VALUES = {
        "active",
        "intensified",
        "softened",
        "resolved",
        "suppressed",
        "transformed",
    }

    def create_emotional_carryover_record(
        self,
        *,
        carryover_id: str,
        character_id: str,
        emotion_type: str,
        source_event_id: Optional[str] = None,
        source_choice_id: Optional[str] = None,
        source_conflict_id: Optional[str] = None,
        source_relationship_id: Optional[str] = None,
        intensity: float = 0.5,
        decay_rate: float = 0.12,
        persistence: float = 0.5,
        trigger_tags: List[str] | None = None,
        linked_character_ids: List[str] | None = None,
        linked_secret_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
        summary: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if emotion_type not in self.EMOTION_TYPES:
            emotion_type = "confusion"

        return {
            "carryover_id": carryover_id,
            "character_id": character_id,
            "emotion_type": emotion_type,
            "source_event_id": source_event_id,
            "source_choice_id": source_choice_id,
            "source_conflict_id": source_conflict_id,
            "source_relationship_id": source_relationship_id,
            "intensity": self._bounded(intensity),
            "decay_rate": self._bounded(decay_rate),
            "persistence": self._bounded(persistence),
            "trigger_tags": trigger_tags or [],
            "linked_character_ids": linked_character_ids or [],
            "linked_secret_ids": linked_secret_ids or [],
            "linked_obligation_ids": linked_obligation_ids or [],
            "summary": summary,
            "status": "active",
            "activation_count": 0,
            "last_activated_by": None,
            "history": [],
            "metadata": metadata or {},
        }

    def register_carryover_on_state(
        self,
        *,
        state: Any,
        carryover_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        carryover_id = carryover_record["carryover_id"]
        state.metadata.setdefault("emotional_carryover_registry", {})[carryover_id] = dict(carryover_record)

        character_id = carryover_record["character_id"]
        if character_id in state.character_states:
            state.character_states[character_id].metadata.setdefault("emotional_carryover_ids", [])
            state.character_states[character_id].metadata["emotional_carryover_ids"] = self._unique(
                state.character_states[character_id].metadata["emotional_carryover_ids"] + [carryover_id]
            )

        state.metadata.setdefault("emotional_carryover_history", []).append(
            {
                "action": "register_carryover",
                "carryover_id": carryover_id,
                "character_id": character_id,
                "emotion_type": carryover_record["emotion_type"],
                "intensity": carryover_record["intensity"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "carryover_id": carryover_id,
            "updated_state": state,
        }

    def generate_carryover_from_event(
        self,
        *,
        state: Any,
        event_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        created = []
        event_type = event_record.get("event_type", "")
        family = event_record.get("event_family", "")
        intensity = float(event_record.get("intensity", 0.5))
        actors = event_record.get("actor_ids", [])
        targets = event_record.get("target_ids", [])

        for character_id in self._unique(actors + targets):
            emotion = self._emotion_from_event(event_type, family, character_id in actors)
            linked_characters = [cid for cid in self._unique(actors + targets) if cid != character_id]

            record = self.create_emotional_carryover_record(
                carryover_id=f"emo_{event_record.get('event_id')}_{character_id}_{emotion}",
                character_id=character_id,
                emotion_type=emotion,
                source_event_id=event_record.get("event_id"),
                intensity=self._bounded(0.35 + intensity * 0.55),
                decay_rate=0.10 if intensity >= 0.7 else 0.16,
                persistence=0.70 if intensity >= 0.7 else 0.45,
                trigger_tags=[event_type, family, event_record.get("visibility", "private")],
                linked_character_ids=linked_characters,
                linked_secret_ids=event_record.get("linked_secret_ids", []),
                linked_obligation_ids=event_record.get("linked_obligation_ids", []),
                summary=f"{character_id} carries {emotion} from {event_record.get('event_id')}.",
                metadata={"source": "event"},
            )
            created.append(record)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "source_event_id": event_record.get("event_id"),
            "carryover_records": created,
            "carryover_count": len(created),
        }

    def generate_carryover_from_conflict_resolution(
        self,
        *,
        state: Any,
        conflict_record: Dict[str, Any],
        outcome_type: str,
    ) -> Dict[str, Any]:
        created = []
        pressure = float(conflict_record.get("conflict_pressure", 0.5))
        participants = conflict_record.get("participant_ids", [])

        for participant_id in participants:
            emotion = self._emotion_from_conflict_outcome(outcome_type)
            record = self.create_emotional_carryover_record(
                carryover_id=f"emo_{conflict_record.get('conflict_id')}_{participant_id}_{emotion}",
                character_id=participant_id,
                emotion_type=emotion,
                source_conflict_id=conflict_record.get("conflict_id"),
                intensity=self._bounded(0.30 + pressure * 0.55),
                decay_rate=0.08 if outcome_type in {"open_wound", "relationship_break", "mutual_loss"} else 0.16,
                persistence=0.75 if outcome_type in {"open_wound", "relationship_break"} else 0.45,
                trigger_tags=[conflict_record.get("conflict_type", "conflict"), outcome_type],
                linked_character_ids=[cid for cid in participants if cid != participant_id],
                linked_secret_ids=conflict_record.get("linked_secret_ids", []),
                linked_obligation_ids=conflict_record.get("linked_obligation_ids", []),
                summary=f"{participant_id} carries {emotion} after conflict {conflict_record.get('conflict_id')}.",
                metadata={"source": "conflict_resolution", "outcome_type": outcome_type},
            )
            created.append(record)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "source_conflict_id": conflict_record.get("conflict_id"),
            "carryover_records": created,
            "carryover_count": len(created),
        }

    def activate_carryovers_for_scene(
        self,
        *,
        state: Any,
        character_id: str,
        scene_tags: List[str],
        present_character_ids: List[str] | None = None,
        linked_secret_ids: List[str] | None = None,
        linked_obligation_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        registry = state.metadata.get("emotional_carryover_registry", {})
        activated = []

        present = set(present_character_ids or [])
        secrets = set(linked_secret_ids or [])
        obligations = set(linked_obligation_ids or [])
        tags = set(scene_tags)

        for carryover_id, record in registry.items():
            if record.get("character_id") != character_id:
                continue
            if record.get("status") not in {"active", "intensified", "softened", "suppressed"}:
                continue

            score = self._activation_score(
                record=record,
                tags=tags,
                present=present,
                secrets=secrets,
                obligations=obligations,
            )

            if score >= 0.20:
                record["activation_count"] = int(record.get("activation_count", 0)) + 1
                record["last_activated_by"] = {
                    "scene_tags": scene_tags,
                    "present_character_ids": present_character_ids or [],
                    "linked_secret_ids": linked_secret_ids or [],
                    "linked_obligation_ids": linked_obligation_ids or [],
                    "activation_score": score,
                }
                record.setdefault("history", []).append(
                    {
                        "action": "activated",
                        "activation_score": score,
                        "scene_tags": scene_tags,
                    }
                )

                if score >= 0.60:
                    record["status"] = "intensified"
                    record["intensity"] = self._bounded(float(record.get("intensity", 0.5)) + 0.10)
                elif record.get("status") == "suppressed":
                    record["status"] = "active"

                activated.append(
                    {
                        "carryover_id": carryover_id,
                        "emotion_type": record.get("emotion_type"),
                        "intensity": record.get("intensity"),
                        "activation_score": score,
                        "summary": record.get("summary"),
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "activated_count": len(activated),
            "activated_carryovers": sorted(activated, key=lambda item: item["activation_score"], reverse=True),
            "scene_emotional_pressure": self._average([item["intensity"] * item["activation_score"] for item in activated]),
            "warnings": self._activation_warnings(activated),
        }

    def decay_carryovers(
        self,
        *,
        state: Any,
        character_id: Optional[str] = None,
        ticks: int = 1,
    ) -> Dict[str, Any]:
        registry = state.metadata.get("emotional_carryover_registry", {})
        updated = []

        for carryover_id, record in registry.items():
            if character_id and record.get("character_id") != character_id:
                continue
            if record.get("status") in {"resolved", "transformed"}:
                continue

            old_intensity = float(record.get("intensity", 0.0))
            decay_rate = float(record.get("decay_rate", 0.12))
            persistence = float(record.get("persistence", 0.5))
            effective_decay = decay_rate * max(0.20, 1.0 - persistence)

            new_intensity = self._bounded(old_intensity - effective_decay * max(1, ticks))

            record["intensity"] = new_intensity
            record.setdefault("history", []).append(
                {
                    "action": "decayed",
                    "old_intensity": old_intensity,
                    "new_intensity": new_intensity,
                    "ticks": ticks,
                }
            )

            if new_intensity <= 0.08:
                record["status"] = "resolved"
            elif new_intensity < old_intensity:
                record["status"] = "softened"

            updated.append(
                {
                    "carryover_id": carryover_id,
                    "old_intensity": old_intensity,
                    "new_intensity": new_intensity,
                    "status": record["status"],
                }
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "updated_count": len(updated),
            "updated_carryovers": updated,
            "updated_state": state,
        }

    def resolve_carryover(
        self,
        *,
        state: Any,
        carryover_id: str,
        resolution_reason: str,
        transformed_emotion_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        record = state.metadata.get("emotional_carryover_registry", {}).get(carryover_id)
        if not record:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "carryover_id": carryover_id,
                "errors": [f"carryover {carryover_id} not found"],
                "updated_state": state,
            }

        if transformed_emotion_type:
            if transformed_emotion_type not in self.EMOTION_TYPES:
                transformed_emotion_type = "hope"
            old_emotion = record["emotion_type"]
            record["emotion_type"] = transformed_emotion_type
            record["status"] = "transformed"
            record["intensity"] = self._bounded(float(record.get("intensity", 0.5)) * 0.65)
            record.setdefault("history", []).append(
                {
                    "action": "transformed",
                    "from": old_emotion,
                    "to": transformed_emotion_type,
                    "reason": resolution_reason,
                }
            )
        else:
            record["status"] = "resolved"
            record["intensity"] = 0.0
            record.setdefault("history", []).append(
                {
                    "action": "resolved",
                    "reason": resolution_reason,
                }
            )

        state.metadata.setdefault("emotional_carryover_history", []).append(
            {
                "action": "resolve_carryover",
                "carryover_id": carryover_id,
                "status": record["status"],
                "reason": resolution_reason,
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "carryover_id": carryover_id,
            "updated_carryover": record,
            "updated_state": state,
        }

    def build_character_emotional_state(
        self,
        *,
        state: Any,
        character_id: str,
    ) -> Dict[str, Any]:
        records = [
            record
            for record in state.metadata.get("emotional_carryover_registry", {}).values()
            if record.get("character_id") == character_id and record.get("status") != "resolved"
        ]

        emotion_scores: Dict[str, float] = {}
        for record in records:
            emotion = record.get("emotion_type")
            score = float(record.get("intensity", 0.0)) * (0.75 + float(record.get("persistence", 0.5)) * 0.25)
            emotion_scores[emotion] = self._bounded(emotion_scores.get(emotion, 0.0) + score)

        dominant = max(emotion_scores.items(), key=lambda item: item[1])[0] if emotion_scores else None
        pressure = self._average(list(emotion_scores.values()))

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": character_id,
            "active_carryover_count": len(records),
            "emotion_scores": emotion_scores,
            "dominant_emotion": dominant,
            "emotional_pressure": pressure,
            "scene_guidance": self._scene_guidance(dominant, pressure),
            "warnings": self._state_warnings(character_id, records, pressure),
        }

    def build_emotional_carryover_map(self, *, state: Any) -> Dict[str, Any]:
        registry = state.metadata.get("emotional_carryover_registry", {})
        character_ids = sorted({record.get("character_id") for record in registry.values() if record.get("character_id")})

        character_states = {
            character_id: self.build_character_emotional_state(state=state, character_id=character_id)
            for character_id in character_ids
        }

        active_records = {
            cid: record
            for cid, record in registry.items()
            if record.get("status") != "resolved"
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "carryover_count": len(registry),
            "active_carryover_count": len(active_records),
            "character_emotional_states": character_states,
            "highest_pressure_character": self._highest_pressure_character(character_states),
            "warnings": self._map_warnings(character_states, active_records),
            "chunk5_handoff": self._chunk5_handoff(character_states),
        }

    def _emotion_from_event(self, event_type: str, family: str, is_actor: bool) -> str:
        if event_type in {"betrayal", "promise_broken", "blackmail_refused"}:
            return "guilt" if is_actor else "betrayal_pain"
        if event_type in {"public_humiliation", "falsehood_exposed"}:
            return "shame"
        if event_type in {"private_confession", "truth_confession"}:
            return "hope" if is_actor else "trust"
        if event_type in {"blackmail_attempt", "threat_made"}:
            return "fear" if not is_actor else "determination"
        if event_type in {"romantic_turn"}:
            return "romantic_tension"
        if event_type in {"death", "sacrifice"}:
            return "grief"
        if family == "knowledge":
            return "confusion"
        if family == "relationship":
            return "resentment"
        if family == "obligation":
            return "loyalty"
        return "determination"

    def _emotion_from_conflict_outcome(self, outcome_type: str) -> str:
        return {
            "compromise": "relief",
            "mutual_gain": "hope",
            "relationship_repair": "trust",
            "truth_reveal": "determination",
            "open_wound": "resentment",
            "avoidance": "confusion",
            "relationship_break": "grief",
            "mutual_loss": "grief",
            "win_loss": "distrust",
            "power_shift": "fear",
            "sacrifice": "guilt",
        }.get(outcome_type, "confusion")

    def _activation_score(
        self,
        *,
        record: Dict[str, Any],
        tags: set,
        present: set,
        secrets: set,
        obligations: set,
    ) -> float:
        score = 0.0

        trigger_overlap = tags.intersection(set(record.get("trigger_tags", [])))
        score += len(trigger_overlap) * 0.18

        character_overlap = present.intersection(set(record.get("linked_character_ids", [])))
        score += len(character_overlap) * 0.22

        secret_overlap = secrets.intersection(set(record.get("linked_secret_ids", [])))
        score += len(secret_overlap) * 0.20

        obligation_overlap = obligations.intersection(set(record.get("linked_obligation_ids", [])))
        score += len(obligation_overlap) * 0.18

        score += float(record.get("persistence", 0.5)) * 0.10
        score += float(record.get("intensity", 0.5)) * 0.12

        return round(min(1.0, score), 3)

    def _activation_warnings(self, activated: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if len(activated) >= 4:
            warnings.append("many emotional carryovers activated; scene may be emotionally dense")
        if any(item["intensity"] >= 0.8 for item in activated):
            warnings.append("high-intensity emotional residue is active")
        return warnings

    def _scene_guidance(self, dominant: Optional[str], pressure: float) -> Dict[str, Any]:
        if not dominant:
            return {
                "tone": "neutral",
                "must_acknowledge_emotion": False,
                "suggested_expression": "no major carryover",
            }

        expression = {
            "anger": "sharpness, interruption, physical tension",
            "fear": "hesitation, scanning for threat, guarded wording",
            "guilt": "avoidance, overcompensation, self-protection",
            "shame": "withdrawal, defensive humor, lowered status behavior",
            "grief": "quiet heaviness, memory intrusion, reduced appetite for conflict",
            "hope": "softening, risk-taking, future-oriented language",
            "trust": "openness, vulnerability, slower defensive reactions",
            "distrust": "testing, guarded questions, refusal to fully commit",
            "romantic_tension": "charged silence, misread closeness, restrained longing",
            "resentment": "barbed honesty, old wound references, scorekeeping",
            "betrayal_pain": "coldness, disbelief, emotional recoil",
            "determination": "clearer choices, narrowed focus, action bias",
            "confusion": "contradictory reactions, searching questions",
        }.get(dominant, "subtle emotional coloring")

        return {
            "tone": dominant,
            "must_acknowledge_emotion": pressure >= 0.35,
            "suggested_expression": expression,
        }

    def _state_warnings(self, character_id: str, records: List[Dict[str, Any]], pressure: float) -> List[str]:
        warnings = []
        if pressure >= 0.75:
            warnings.append(f"{character_id} has very high emotional pressure")
        if len(records) >= 5:
            warnings.append(f"{character_id} has many active emotional carryovers")
        return warnings

    def _highest_pressure_character(self, character_states: Dict[str, Dict[str, Any]]) -> Optional[str]:
        if not character_states:
            return None
        return max(character_states.values(), key=lambda item: item.get("emotional_pressure", 0.0)).get("character_id")

    def _map_warnings(self, character_states: Dict[str, Dict[str, Any]], active_records: Dict[str, Dict[str, Any]]) -> List[str]:
        warnings = []
        if len(active_records) > 30:
            warnings.append("many unresolved emotional carryovers; consider resolving or transforming some")
        for report in character_states.values():
            warnings.extend(report.get("warnings", []))
        return self._unique(warnings)

    def _chunk5_handoff(self, character_states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "highest_pressure_character": self._highest_pressure_character(character_states),
            "emotional_scene_requirements": [
                {
                    "character_id": character_id,
                    "dominant_emotion": report.get("dominant_emotion"),
                    "emotional_pressure": report.get("emotional_pressure"),
                    "scene_guidance": report.get("scene_guidance"),
                }
                for character_id, report in character_states.items()
                if report.get("emotional_pressure", 0.0) >= 0.30
            ],
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

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
