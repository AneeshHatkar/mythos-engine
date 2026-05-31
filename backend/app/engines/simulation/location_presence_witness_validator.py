from typing import Any, Dict, List, Optional, Set

from backend.app.schemas.simulation import (
    KnowledgeDelta,
    SimulationEventPayload,
    SimulationEventVisibility,
    SimulationState,
)


class LocationPresenceWitnessValidator:
    """Validates physical/social presence and witness paths.

    This prevents characters from reacting to events they could not witness,
    learning secrets without a path, appearing in impossible locations, or
    spreading rumors without a channel.
    """

    engine_name = "simulation.location_presence_witness_validator"

    REMOTE_ALLOWED_VISIBILITIES = {
        SimulationEventVisibility.PUBLIC,
        SimulationEventVisibility.FACTION_KNOWN,
    }

    def validate_event_presence(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        location_id = event_payload.location_id
        if not location_id:
            warnings.append("event has no location_id; presence validation is partial")
            return self._result(
                event_id=event_payload.event_id,
                valid=True,
                blockers=blockers,
                warnings=warnings,
                passed_checks=passed_checks,
                reports={},
            )

        location_report = self._validate_location_exists(state, location_id)
        participant_report = self._validate_participant_presence(state, event_payload)
        witness_report = self._validate_witnesses(state, event_payload)
        visibility_report = self._validate_visibility_support(state, event_payload)
        access_report = self._validate_access_rules(state, event_payload)

        reports = {
            "location": location_report,
            "participants": participant_report,
            "witnesses": witness_report,
            "visibility": visibility_report,
            "access": access_report,
        }

        for report in reports.values():
            blockers.extend(report.get("blockers", []))
            warnings.extend(report.get("warnings", []))
            passed_checks.extend(report.get("passed_checks", []))

        return self._result(
            event_id=event_payload.event_id,
            valid=len(blockers) == 0,
            blockers=blockers,
            warnings=warnings,
            passed_checks=passed_checks,
            reports=reports,
        )

    def validate_knowledge_witness_path(
        self,
        *,
        state: SimulationState,
        knowledge_delta: KnowledgeDelta,
        source_event: Optional[SimulationEventPayload] = None,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        holder_id = knowledge_delta.knowledge_holder_id
        holder = state.character_states.get(holder_id)

        if not holder and holder_id not in state.entity_states:
            blockers.append(f"knowledge holder {holder_id} does not exist in simulation state")
        else:
            passed_checks.append("knowledge_holder_exists")

        if not knowledge_delta.secret_ids_added:
            passed_checks.append("no_secret_added_no_witness_path_required")
            return {
                "success": True,
                "engine_name": self.engine_name,
                "valid": len(blockers) == 0,
                "validation_score": self._score(blockers, warnings),
                "passed_checks": passed_checks,
                "blockers": blockers,
                "warnings": warnings,
                "knowledge_path_type": "not_required",
                "recommendation": "allow_knowledge_delta" if not blockers else "fix_knowledge_holder",
            }

        if not knowledge_delta.no_magic_knowledge_checked:
            blockers.append("secret knowledge path was not marked as no_magic_knowledge_checked")

        evidence_path_exists = bool(knowledge_delta.evidence_ids_seen)
        explicit_path_exists = bool(knowledge_delta.knowledge_path)
        witness_path_exists = bool(knowledge_delta.witness_ids)

        if evidence_path_exists:
            passed_checks.append("knowledge_has_evidence_path")
        if explicit_path_exists:
            passed_checks.append("knowledge_has_explicit_path")
        if witness_path_exists:
            passed_checks.append("knowledge_has_witness_path")

        if not any([evidence_path_exists, explicit_path_exists, witness_path_exists]):
            blockers.append("secret knowledge has no evidence, witness, or explicit path")

        if source_event:
            event_report = self._validate_source_event_for_knowledge(
                state=state,
                source_event=source_event,
                knowledge_delta=knowledge_delta,
            )
            blockers.extend(event_report["blockers"])
            warnings.extend(event_report["warnings"])
            passed_checks.extend(event_report["passed_checks"])

        path_type = self._path_type(
            evidence_path_exists=evidence_path_exists,
            explicit_path_exists=explicit_path_exists,
            witness_path_exists=witness_path_exists,
        )

        valid = len(blockers) == 0

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": valid,
            "validation_score": self._score(blockers, warnings),
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "knowledge_path_type": path_type,
            "recommendation": "allow_knowledge_delta" if valid else "fix_witness_or_evidence_path",
        }

    def build_witness_path_report(
        self,
        *,
        state: SimulationState,
        event_payload: SimulationEventPayload,
    ) -> Dict[str, Any]:
        direct_witnesses = []
        possible_rumor_sources = []
        impossible_witnesses = []
        hidden_or_remote_witnesses = []

        location_id = event_payload.location_id

        for witness_id in event_payload.witness_ids:
            character = state.character_states.get(witness_id)
            if not character:
                impossible_witnesses.append(
                    {
                        "witness_id": witness_id,
                        "reason": "missing_character_state",
                    }
                )
                continue

            witness_location = character.current_location_id
            if witness_location == location_id:
                direct_witnesses.append(witness_id)
            elif self._can_receive_remote_public_info(event_payload):
                hidden_or_remote_witnesses.append(witness_id)
            elif self._rumor_channel_possible(state, location_id, witness_location):
                possible_rumor_sources.append(witness_id)
            else:
                impossible_witnesses.append(
                    {
                        "witness_id": witness_id,
                        "reason": f"witness at {witness_location} cannot witness event at {location_id}",
                    }
                )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_payload.event_id,
            "event_location_id": location_id,
            "direct_witnesses": direct_witnesses,
            "hidden_or_remote_witnesses": hidden_or_remote_witnesses,
            "possible_rumor_sources": possible_rumor_sources,
            "impossible_witnesses": impossible_witnesses,
            "witness_path_valid": len(impossible_witnesses) == 0,
        }

    def _validate_location_exists(self, state: SimulationState, location_id: str) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        active_location_ids = {
            item.get("location_id")
            for item in state.world_state.active_locations
            if isinstance(item, dict)
        }

        if active_location_ids and location_id not in active_location_ids:
            blockers.append(f"location {location_id} is not an active world location")
        else:
            passed.append("location_exists_or_location_list_unrestricted")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_participant_presence(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        location_id = event.location_id
        participant_ids = event.actor_ids + event.target_ids

        for character_id in participant_ids:
            character = state.character_states.get(character_id)
            if not character:
                blockers.append(f"participant {character_id} missing from character_states")
                continue

            if character.metadata.get("dead") is True:
                blockers.append(f"participant {character_id} is dead and cannot be present")
                continue

            current_location = character.current_location_id
            if current_location == location_id:
                passed.append(f"{character_id}_present_at_event_location")
                continue

            if self._travel_possible(state, current_location, location_id):
                warnings.append(f"{character_id} is not currently at event location but travel path exists")
                passed.append(f"{character_id}_travel_path_exists")
                continue

            if self._remote_participation_possible(event, character_id):
                warnings.append(f"{character_id} participates remotely/indirectly")
                passed.append(f"{character_id}_remote_participation_possible")
                continue

            blockers.append(f"{character_id} is at {current_location} and cannot be present at {location_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_witnesses(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        location_id = event.location_id

        for witness_id in event.witness_ids:
            character = state.character_states.get(witness_id)
            if not character:
                warnings.append(f"witness {witness_id} missing from character_states")
                continue

            current_location = character.current_location_id
            if current_location == location_id:
                passed.append(f"{witness_id}_direct_witness")
                continue

            if witness_id in event.actor_ids or witness_id in event.target_ids:
                if self._travel_possible(state, current_location, location_id):
                    warnings.append(
                        f"{witness_id} is an involved participant and can reach {location_id} through a travel path"
                    )
                    passed.append(f"{witness_id}_participant_witness_travel_path_exists")
                    continue

                if self._remote_participation_possible(event, witness_id):
                    warnings.append(f"{witness_id} is an involved participant through remote/proxy participation")
                    passed.append(f"{witness_id}_participant_remote_witness_possible")
                    continue

            if self._can_receive_remote_public_info(event):
                warnings.append(f"{witness_id} can know event through public/faction channel, not direct sight")
                passed.append(f"{witness_id}_remote_public_witness_channel")
                continue

            if self._rumor_channel_possible(state, location_id, current_location):
                warnings.append(f"{witness_id} can plausibly hear through rumor channel, not direct witness")
                passed.append(f"{witness_id}_rumor_channel_possible")
                continue

            blockers.append(f"witness {witness_id} cannot witness event at {location_id} from {current_location}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_visibility_support(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if event.visibility == SimulationEventVisibility.PUBLIC:
            if not event.witness_ids:
                warnings.append("public event has no witness_ids; reputation and rumor propagation may be weak")
            else:
                passed.append("public_event_has_witness_ids")

        if event.visibility == SimulationEventVisibility.PRIVATE:
            unexpected = set(event.witness_ids) - set(event.actor_ids) - set(event.target_ids)
            if unexpected:
                warnings.append(f"private event has outside witnesses: {sorted(unexpected)}")
            else:
                passed.append("private_event_has_no_outside_witnesses")

        if event.visibility == SimulationEventVisibility.READER_ONLY:
            if event.witness_ids:
                warnings.append("reader-only event includes witnesses; check whether this should be hidden from characters")
            else:
                passed.append("reader_only_event_has_no_character_witnesses")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_access_rules(
        self,
        state: SimulationState,
        event: SimulationEventPayload,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not event.location_id:
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        rule = self._find_access_rule(state.world_state.location_access_rules, event.location_id)
        if not rule:
            passed.append("no_specific_access_rule_for_event_location")
            return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

        if rule.get("requires_sponsor"):
            for actor_id in event.actor_ids:
                character = state.character_states.get(actor_id)
                if not character:
                    continue

                has_route = (
                    character.metadata.get("has_sponsor")
                    or character.metadata.get("access_route")
                    or "sponsor" in str(character.character_to_simulation_contract).lower()
                    or "sponsor" in str(character.metadata.get("backstory_policy", {})).lower()
                )

                if has_route:
                    passed.append(f"{actor_id}_has_required_sponsor_or_access_route")
                else:
                    warnings.append(f"{actor_id} lacks explicit sponsor/access route for {event.location_id}")

        restricted_classes = set(rule.get("restricted_classes", []))
        if restricted_classes:
            for actor_id in event.actor_ids + event.target_ids:
                character = state.character_states.get(actor_id)
                if not character:
                    continue
                backstory = str(character.metadata.get("backstory_policy", {})).lower()
                if any(cls.lower() in backstory for cls in restricted_classes):
                    warnings.append(f"{actor_id} may belong to restricted class for {event.location_id}")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _validate_source_event_for_knowledge(
        self,
        *,
        state: SimulationState,
        source_event: SimulationEventPayload,
        knowledge_delta: KnowledgeDelta,
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        holder_id = knowledge_delta.knowledge_holder_id

        if holder_id in source_event.actor_ids or holder_id in source_event.target_ids or holder_id in source_event.witness_ids:
            passed.append("knowledge_holder_present_or_witnessed_source_event")
        elif source_event.visibility in self.REMOTE_ALLOWED_VISIBILITIES:
            warnings.append("knowledge holder may know through public/faction visibility, not direct witness")
            passed.append("knowledge_holder_remote_visibility_path")
        else:
            blockers.append("knowledge holder was not actor, target, witness, or public receiver of source event")

        if knowledge_delta.evidence_ids_seen:
            evidence_locations = state.world_state.metadata.get("evidence_locations", {})
            for evidence_id in knowledge_delta.evidence_ids_seen:
                evidence_location = evidence_locations.get(evidence_id)
                holder = state.character_states.get(holder_id)
                if evidence_location and holder and holder.current_location_id != evidence_location:
                    if not self._travel_possible(state, holder.current_location_id, evidence_location):
                        warnings.append(f"{holder_id} saw {evidence_id}, but no travel path to evidence location is known")
                else:
                    passed.append(f"{evidence_id}_evidence_location_accessible_or_unrestricted")

        return {"blockers": blockers, "warnings": warnings, "passed_checks": passed}

    def _travel_possible(self, state: SimulationState, from_location: Optional[str], to_location: Optional[str]) -> bool:
        if not from_location or not to_location:
            return False
        if from_location == to_location:
            return True

        travel_edges = state.world_state.metadata.get("travel_edges", [])
        for edge in travel_edges:
            source = edge.get("from_location_id")
            target = edge.get("to_location_id")
            if source == from_location and target == to_location:
                return True
            if edge.get("bidirectional", True) and source == to_location and target == from_location:
                return True

        return False

    def _rumor_channel_possible(
        self,
        state: SimulationState,
        event_location: Optional[str],
        witness_location: Optional[str],
    ) -> bool:
        if not event_location or not witness_location:
            return False
        if event_location == witness_location:
            return True

        rumor_edges = state.world_state.metadata.get("rumor_edges", [])
        for edge in rumor_edges:
            source = edge.get("from_location_id")
            target = edge.get("to_location_id")
            if source == event_location and target == witness_location:
                return True
            if edge.get("bidirectional", True) and source == witness_location and target == event_location:
                return True

        return False

    def _remote_participation_possible(self, event: SimulationEventPayload, character_id: str) -> bool:
        remote_ids = set(event.metadata.get("remote_participant_ids", []))
        proxy_ids = set(event.metadata.get("proxy_participant_ids", []))
        return character_id in remote_ids or character_id in proxy_ids

    def _can_receive_remote_public_info(self, event: SimulationEventPayload) -> bool:
        return event.visibility in self.REMOTE_ALLOWED_VISIBILITIES

    def _find_access_rule(self, access_rules: List[Dict[str, Any]], location_id: str) -> Optional[Dict[str, Any]]:
        for rule in access_rules:
            if rule.get("location_id") == location_id:
                return rule
        return None

    def _path_type(
        self,
        *,
        evidence_path_exists: bool,
        explicit_path_exists: bool,
        witness_path_exists: bool,
    ) -> str:
        parts = []
        if evidence_path_exists:
            parts.append("evidence")
        if explicit_path_exists:
            parts.append("explicit")
        if witness_path_exists:
            parts.append("witness")
        return "+".join(parts) if parts else "missing"

    def _result(
        self,
        *,
        event_id: str,
        valid: bool,
        blockers: List[str],
        warnings: List[str],
        passed_checks: List[str],
        reports: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "event_id": event_id,
            "valid": valid,
            "validation_score": self._score(blockers, warnings),
            "passed_checks": passed_checks,
            "blockers": blockers,
            "warnings": warnings,
            "reports": reports,
            "recommendation": "allow_event" if valid else "fix_presence_or_witness_path",
        }

    def _score(self, blockers: List[str], warnings: List[str]) -> float:
        return round(max(0.0, 1.0 - 0.22 * len(blockers) - 0.05 * len(warnings)), 3)
