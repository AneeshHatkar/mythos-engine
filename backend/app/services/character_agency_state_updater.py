from typing import Any, Dict, List


class CharacterAgencyStateUpdater:
    """Updates what a character can, will, refuses, or cannot do under pressure."""

    def update_agency_state(
        self,
        *,
        character_id: str,
        current_agency_state: Dict[str, Any] | None = None,
        event_payload: Dict[str, Any] | None = None,
        emotion_state: Dict[str, Any] | None = None,
        knowledge_state: Dict[str, Any] | None = None,
        relationship_state: Dict[str, Any] | None = None,
        world_constraints: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        current = current_agency_state or {}
        event = event_payload or {}
        emotion = emotion_state or {}
        knowledge = knowledge_state or {}
        relationship = relationship_state or {}
        world = world_constraints or {}

        fear_pressure = self._score_fear_pressure(emotion, event)
        knowledge_completeness = self._score_knowledge_completeness(knowledge)
        resource_access = current.get("resource_access", "limited")
        legal_pressure = self._score_legal_pressure(world, event)
        relationship_pressure = self._score_relationship_pressure(relationship)
        agency_capacity = round(max(0.0, min(1.0, 0.75 - fear_pressure * 0.25 - legal_pressure * 0.15 + knowledge_completeness * 0.2)), 3)

        available_actions = self._available_actions(event, knowledge_completeness, agency_capacity)
        blocked_actions = self._blocked_actions(world, legal_pressure, knowledge_completeness)
        unthinkable_actions = self._unthinkable_actions(emotion, relationship)
        surprising_but_valid = self._surprising_but_valid_actions(agency_capacity, emotion)

        state = {
            "character_id": character_id,
            "agency_capacity": agency_capacity,
            "fear_pressure": round(fear_pressure, 3),
            "knowledge_completeness": round(knowledge_completeness, 3),
            "resource_access": resource_access,
            "relationship_constraints": relationship.get("constraints", []),
            "legal_constraints_active": world.get("legal_constraints", []),
            "social_constraints_active": world.get("social_constraints", []),
            "available_actions": available_actions,
            "blocked_actions": blocked_actions,
            "unthinkable_actions": unthinkable_actions,
            "surprising_but_valid_actions": surprising_but_valid,
            "agency_constraints": {
                "fear_pressure": fear_pressure,
                "legal_pressure": legal_pressure,
                "relationship_pressure": relationship_pressure,
                "knowledge_gap": round(1.0 - knowledge_completeness, 3),
            },
        }

        return {
            "success": True,
            "character_id": character_id,
            "agency_state": state,
        }

    def _score_fear_pressure(self, emotion: Dict[str, Any], event: Dict[str, Any]) -> float:
        vector = emotion.get("emotion_vector", {})
        base = float(vector.get("fear", 0.0)) + float(vector.get("dread", 0.0)) * 0.8
        if event.get("event_type") in ["blackmail_attempt", "trial", "public_humiliation"]:
            base += 0.2
        return min(1.0, base)

    def _score_knowledge_completeness(self, knowledge: Dict[str, Any]) -> float:
        known = len(knowledge.get("known_secret_ids", [])) + len(knowledge.get("evidence_seen_ids", []))
        suspected = len(knowledge.get("suspected_secret_ids", [])) + len(knowledge.get("rumors_heard_ids", []))
        return min(1.0, known * 0.25 + suspected * 0.12)

    def _score_legal_pressure(self, world: Dict[str, Any], event: Dict[str, Any]) -> float:
        pressure = 0.0
        if world.get("legal_constraints"):
            pressure += 0.25
        if event.get("event_type") in ["trial", "public_humiliation", "blackmail_attempt"]:
            pressure += 0.25
        return min(1.0, pressure)

    def _score_relationship_pressure(self, relationship: Dict[str, Any]) -> float:
        return min(1.0, float(relationship.get("betrayal_risk", 0.0)) + float(relationship.get("debt_pressure", 0.0)))

    def _available_actions(self, event: Dict[str, Any], knowledge_score: float, agency_capacity: float) -> List[str]:
        actions = ["stay_silent", "ask_for_time"]
        if knowledge_score >= 0.35:
            actions.append("confront_with_partial_truth")
        if agency_capacity >= 0.65:
            actions.append("publicly_resist")
        if event.get("event_type") == "blackmail_attempt":
            actions.extend(["negotiate_terms", "search_for_counter_leverage"])
        return actions

    def _blocked_actions(self, world: Dict[str, Any], legal_pressure: float, knowledge_score: float) -> List[str]:
        blocked = []
        if legal_pressure >= 0.4:
            blocked.append("public_accusation_without_witness")
        if knowledge_score < 0.3:
            blocked.append("prove_secret_without_evidence")
        if world.get("restricted_locations"):
            blocked.append("enter_restricted_location_without_route")
        return blocked

    def _unthinkable_actions(self, emotion: Dict[str, Any], relationship: Dict[str, Any]) -> List[str]:
        items = []
        if emotion.get("dominant_emotion") == "grief":
            items.append("casual_forgiveness_without_repair")
        if relationship.get("loyalty", 0.0) >= 0.8:
            items.append("betray_without_extreme_pressure")
        return items

    def _surprising_but_valid_actions(self, agency_capacity: float, emotion: Dict[str, Any]) -> List[str]:
        actions = []
        if agency_capacity >= 0.7 and emotion.get("dominant_emotion") in ["anger", "shame"]:
            actions.append("tell_truth_in_controlled_public_way")
        if agency_capacity < 0.45:
            actions.append("choose_strategic_silence_to_survive")
        return actions
