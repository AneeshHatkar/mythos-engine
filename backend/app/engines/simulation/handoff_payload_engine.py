from typing import Any, Dict, List, Optional


class HandoffPayloadEngine:
    """Builds structured payloads for dialogue, scene, and plot generation.

    Chunk 4 simulates state, relationships, choices, consequences, stakes,
    emotions, conflicts, and cast selection. Chunk 5 will generate scenes,
    dialogue, plot outlines, chapters, scripts, episodes, and novels.

    This engine is the bridge between them.
    """

    engine_name = "simulation.handoff_payload_engine"

    PAYLOAD_TYPES = {
        "dialogue",
        "scene",
        "plot",
        "choice",
        "conflict",
        "relationship",
        "emotional",
        "cast",
        "causal",
        "arc",
    }

    OUTPUT_FORMATS = {
        "novel",
        "chapter",
        "scene",
        "movie",
        "screenplay",
        "series_episode",
        "season_outline",
        "short_story",
        "game_scene",
        "comic_scene",
        "treatment",
    }

    def create_base_payload(
        self,
        *,
        payload_id: str,
        payload_type: str,
        output_format: str = "scene",
        story_request: Dict[str, Any] | None = None,
        selected_character_ids: List[str] | None = None,
        scene_id: Optional[str] = None,
        plot_arc_id: Optional[str] = None,
        summary: str = "",
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if payload_type not in self.PAYLOAD_TYPES:
            payload_type = "scene"
        if output_format not in self.OUTPUT_FORMATS:
            output_format = "scene"

        return {
            "payload_id": payload_id,
            "payload_type": payload_type,
            "output_format": output_format,
            "story_request": story_request or {},
            "selected_character_ids": selected_character_ids or [],
            "scene_id": scene_id,
            "plot_arc_id": plot_arc_id,
            "summary": summary,
            "metadata": metadata or {},
        }

    def build_dialogue_payload(
        self,
        *,
        state: Any,
        payload_id: str,
        speaker_ids: List[str],
        scene_context: Dict[str, Any] | None = None,
        relationship_ids: List[str] | None = None,
        emotional_requirements: List[Dict[str, Any]] | None = None,
        conflict_ids: List[str] | None = None,
        secret_ids: List[str] | None = None,
        evidence_ids: List[str] | None = None,
        output_format: str = "scene",
        story_request: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        speaker_cards = [self._character_card(state, cid) for cid in speaker_ids]

        relationships = [
            self._relationship_card(state, rid)
            for rid in (relationship_ids or self._relationships_between_speakers(state, speaker_ids))
        ]

        emotional_context = emotional_requirements or [
            self._emotional_context_for_character(state, cid)
            for cid in speaker_ids
        ]

        conflicts = [
            self._conflict_card(state, cid)
            for cid in conflict_ids or []
        ]

        base = self.create_base_payload(
            payload_id=payload_id,
            payload_type="dialogue",
            output_format=output_format,
            story_request=story_request or {},
            selected_character_ids=speaker_ids,
            scene_id=(scene_context or {}).get("scene_id"),
            summary=(scene_context or {}).get("summary", "Dialogue payload."),
        )

        base.update(
            {
                "speaker_cards": speaker_cards,
                "relationship_context": relationships,
                "emotional_context": emotional_context,
                "conflict_context": conflicts,
                "knowledge_context": self._knowledge_context(state, speaker_ids, secret_ids or [], evidence_ids or []),
                "dialogue_constraints": self._dialogue_constraints(
                    speaker_cards=speaker_cards,
                    relationships=relationships,
                    emotional_context=emotional_context,
                    story_request=story_request or {},
                ),
                "subtext_requirements": self._subtext_requirements(conflicts, emotional_context, secret_ids or []),
                "scene_context": scene_context or {},
                "quality_targets": {
                    "must_sound_character_specific": True,
                    "must_reflect_relationship_state": True,
                    "must_reflect_emotional_carryover": True,
                    "must_avoid_exposition_dump": True,
                    "must_preserve_hidden_knowledge": True,
                },
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload": base,
            "warnings": self._dialogue_payload_warnings(base),
        }

    def build_scene_payload(
        self,
        *,
        state: Any,
        payload_id: str,
        scene_id: str,
        selected_character_ids: List[str],
        event_ids: List[str] | None = None,
        choice_set_ids: List[str] | None = None,
        consequence_ids: List[str] | None = None,
        conflict_ids: List[str] | None = None,
        stakes_ids: List[str] | None = None,
        tension_curve_ids: List[str] | None = None,
        cast_id: Optional[str] = None,
        output_format: str = "scene",
        story_request: Dict[str, Any] | None = None,
        scene_goal: str = "",
        location_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        base = self.create_base_payload(
            payload_id=payload_id,
            payload_type="scene",
            output_format=output_format,
            story_request=story_request or {},
            selected_character_ids=selected_character_ids,
            scene_id=scene_id,
            summary=scene_goal or f"Scene payload for {scene_id}.",
        )

        events = [self._event_card(state, eid) for eid in event_ids or []]
        consequences = [self._consequence_card(state, cid) for cid in consequence_ids or []]
        conflicts = [self._conflict_card(state, cid) for cid in conflict_ids or []]
        stakes = [self._stakes_card(state, sid) for sid in stakes_ids or []]
        tension_curves = [self._tension_curve_card(state, tid) for tid in tension_curve_ids or []]
        cast = self._cast_card(state, cast_id) if cast_id else None

        base.update(
            {
                "scene_goal": scene_goal,
                "location_id": location_id,
                "character_cards": [self._character_card(state, cid) for cid in selected_character_ids],
                "event_context": events,
                "choice_context": [self._choice_set_card(state, cid) for cid in choice_set_ids or []],
                "consequence_context": consequences,
                "conflict_context": conflicts,
                "stakes_context": stakes,
                "tension_context": tension_curves,
                "cast_context": cast,
                "relationship_context": [
                    self._relationship_card(state, rid)
                    for rid in self._relationships_between_speakers(state, selected_character_ids)
                ],
                "emotional_context": [
                    self._emotional_context_for_character(state, cid)
                    for cid in selected_character_ids
                ],
                "causal_context": self._latest_causal_context(state),
                "scene_requirements": self._scene_requirements(
                    events=events,
                    consequences=consequences,
                    conflicts=conflicts,
                    stakes=stakes,
                    tension_curves=tension_curves,
                ),
                "quality_targets": {
                    "must_have_clear_scene_goal": True,
                    "must_preserve_causal_continuity": True,
                    "must_show_consequence_of_prior_state": bool(consequences),
                    "must_reflect_stakes": bool(stakes),
                    "must_reflect_tension_curve": bool(tension_curves),
                    "must_use_selected_cast_only_unless_needed": True,
                },
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload": base,
            "warnings": self._scene_payload_warnings(base),
        }

    def build_plot_payload(
        self,
        *,
        state: Any,
        payload_id: str,
        plot_arc_id: str,
        selected_character_ids: List[str],
        scene_payloads: List[Dict[str, Any]] | None = None,
        conflict_ids: List[str] | None = None,
        stakes_ids: List[str] | None = None,
        tension_curve_ids: List[str] | None = None,
        cast_id: Optional[str] = None,
        output_format: str = "novel",
        story_request: Dict[str, Any] | None = None,
        plot_goal: str = "",
    ) -> Dict[str, Any]:
        base = self.create_base_payload(
            payload_id=payload_id,
            payload_type="plot",
            output_format=output_format,
            story_request=story_request or {},
            selected_character_ids=selected_character_ids,
            plot_arc_id=plot_arc_id,
            summary=plot_goal or f"Plot payload for {plot_arc_id}.",
        )

        conflicts = [self._conflict_card(state, cid) for cid in conflict_ids or []]
        stakes = [self._stakes_card(state, sid) for sid in stakes_ids or []]
        tension_curves = [self._tension_curve_card(state, tid) for tid in tension_curve_ids or []]
        cast = self._cast_card(state, cast_id) if cast_id else None

        base.update(
            {
                "plot_goal": plot_goal,
                "scene_payloads": scene_payloads or [],
                "character_cards": [self._character_card(state, cid) for cid in selected_character_ids],
                "cast_context": cast,
                "conflict_context": conflicts,
                "stakes_context": stakes,
                "tension_context": tension_curves,
                "causal_context": self._latest_causal_context(state),
                "relationship_context": [
                    self._relationship_card(state, rid)
                    for rid in self._relationships_between_speakers(state, selected_character_ids)
                ],
                "plot_structure_requirements": self._plot_structure_requirements(
                    output_format=output_format,
                    story_request=story_request or {},
                    conflicts=conflicts,
                    stakes=stakes,
                    tension_curves=tension_curves,
                ),
                "quality_targets": {
                    "must_have_causal_chain": True,
                    "must_have_escalation": True,
                    "must_have_payoff": True,
                    "must_use_cast_purposefully": True,
                    "must_respect_user_request": True,
                    "must_preserve_format": True,
                },
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload": base,
            "warnings": self._plot_payload_warnings(base),
        }

    def build_master_handoff_package(
        self,
        *,
        state: Any,
        package_id: str,
        story_request: Dict[str, Any],
        cast_id: Optional[str] = None,
        scene_payloads: List[Dict[str, Any]] | None = None,
        plot_payload: Dict[str, Any] | None = None,
        dialogue_payloads: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        package = {
            "package_id": package_id,
            "engine_name": self.engine_name,
            "story_request": story_request,
            "cast": self._cast_card(state, cast_id) if cast_id else None,
            "plot_payload": plot_payload,
            "scene_payloads": scene_payloads or [],
            "dialogue_payloads": dialogue_payloads or [],
            "global_context": {
                "simulation_id": getattr(state, "simulation_id", None),
                "world_id": getattr(state.world_state, "world_id", None),
                "event_count": len(state.metadata.get("event_registry", {})),
                "conflict_count": len(state.metadata.get("conflict_registry", {})),
                "consequence_count": len(state.metadata.get("consequence_queue", {})),
                "stakes_count": len(state.metadata.get("stakes_registry", {})),
                "tension_curve_count": len(state.metadata.get("tension_curves", {})),
                "causal_graph_count": len(state.metadata.get("causal_graphs", {})),
            },
            "generation_contract": {
                "respect_user_characters": True,
                "allow_project_created_characters": story_request.get("allow_project_created_characters", True),
                "allow_any_character_count": story_request.get("allow_any_character_count", True),
                "preserve_hidden_knowledge": True,
                "preserve_causal_continuity": True,
                "make_choices_have_consequences": True,
                "format": story_request.get("format", "scene"),
            },
            "quality_targets": {
                "character_specificity": "high",
                "causal_coherence": "high",
                "emotional_continuity": "high",
                "anti_genericity": "high",
                "stakes_clarity": "high",
                "format_adherence": "high",
            },
        }

        state.metadata.setdefault("handoff_packages", {})[package_id] = package

        return {
            "success": True,
            "engine_name": self.engine_name,
            "package": package,
            "warnings": self._master_package_warnings(package),
            "updated_state": state,
        }

    def _character_card(self, state: Any, character_id: str) -> Dict[str, Any]:
        character = state.character_states.get(character_id)
        if not character:
            return {
                "character_id": character_id,
                "exists": False,
                "warning": "character missing from state",
            }

        metadata = character.metadata or {}
        return {
            "character_id": character_id,
            "exists": True,
            "display_name": metadata.get("display_name") or metadata.get("name") or character_id,
            "role_tags": metadata.get("role_tags", metadata.get("archetype_tags", [])),
            "story_function_tags": metadata.get("story_function_tags", []),
            "current_location_id": character.current_location_id,
            "goals": metadata.get("goals", {}),
            "psychology": metadata.get("psychology", {}),
            "backstory": metadata.get("backstory", metadata.get("backstory_summary", "")),
            "voice_profile": metadata.get("voice_profile", {}),
            "known_constraints": metadata.get("constraints", {}),
        }

    def _relationship_card(self, state: Any, relationship_id: str) -> Dict[str, Any]:
        rel = state.relationship_states.get(relationship_id)
        if not rel:
            return {
                "relationship_id": relationship_id,
                "exists": False,
                "warning": "relationship missing from state",
            }

        return {
            "relationship_id": relationship_id,
            "exists": True,
            "character_a_id": rel.character_a_id,
            "character_b_id": rel.character_b_id,
            "trust": rel.trust,
            "respect": rel.respect,
            "affection": rel.affection,
            "resentment": rel.resentment,
            "rivalry": rel.rivalry,
            "betrayal_risk": rel.betrayal_risk,
            "repair_potential": rel.repair_potential,
            "romantic_tension": getattr(rel, "romantic_tension", 0.0),
            "power_imbalance": rel.power_imbalance,
            "knowledge_asymmetry": rel.knowledge_asymmetry,
        }

    def _relationships_between_speakers(self, state: Any, character_ids: List[str]) -> List[str]:
        ids = set(character_ids)
        result = []
        for relationship_id, rel in state.relationship_states.items():
            if rel.character_a_id in ids and rel.character_b_id in ids:
                result.append(relationship_id)
        return result

    def _emotional_context_for_character(self, state: Any, character_id: str) -> Dict[str, Any]:
        records = [
            record
            for record in state.metadata.get("emotional_carryover_registry", {}).values()
            if record.get("character_id") == character_id and record.get("status") != "resolved"
        ]

        emotion_scores: Dict[str, float] = {}
        for record in records:
            emotion = record.get("emotion_type", "confusion")
            emotion_scores[emotion] = round(
                min(1.0, emotion_scores.get(emotion, 0.0) + float(record.get("intensity", 0.0))),
                3,
            )

        dominant = max(emotion_scores.items(), key=lambda item: item[1])[0] if emotion_scores else None

        return {
            "character_id": character_id,
            "active_carryover_count": len(records),
            "emotion_scores": emotion_scores,
            "dominant_emotion": dominant,
            "must_show_emotional_continuity": bool(records),
        }

    def _knowledge_context(self, state: Any, speaker_ids: List[str], secret_ids: List[str], evidence_ids: List[str]) -> Dict[str, Any]:
        records = {}
        for speaker_id in speaker_ids:
            knowledge = state.knowledge_states.get(speaker_id)
            if not knowledge:
                records[speaker_id] = {
                    "has_knowledge_state": False,
                    "known_secret_ids": [],
                    "suspected_secret_ids": [],
                    "evidence_seen_ids": [],
                }
            else:
                records[speaker_id] = {
                    "has_knowledge_state": True,
                    "known_secret_ids": [sid for sid in secret_ids if sid in knowledge.known_secret_ids],
                    "suspected_secret_ids": [sid for sid in secret_ids if sid in knowledge.suspected_secret_ids],
                    "evidence_seen_ids": [eid for eid in evidence_ids if eid in knowledge.evidence_seen_ids],
                }

        return {
            "speaker_knowledge": records,
            "secret_ids_in_scene": secret_ids,
            "evidence_ids_in_scene": evidence_ids,
            "must_prevent_magic_knowledge": True,
        }

    def _event_card(self, state: Any, event_id: str) -> Dict[str, Any]:
        event = state.metadata.get("event_registry", {}).get(event_id)
        if not event:
            return {"event_id": event_id, "exists": False}
        return {
            "event_id": event_id,
            "exists": True,
            "event_type": event.get("event_type"),
            "event_family": event.get("event_family"),
            "event_name": event.get("event_name"),
            "actor_ids": event.get("actor_ids", []),
            "target_ids": event.get("target_ids", []),
            "witness_ids": event.get("witness_ids", []),
            "visibility": event.get("visibility"),
            "intensity": event.get("intensity"),
            "location_id": event.get("location_id"),
        }

    def _choice_set_card(self, state: Any, choice_set_id: str) -> Dict[str, Any]:
        choice_sets = state.metadata.get("choice_set_registry", {})
        record = choice_sets.get(choice_set_id)
        if not record:
            return {"choice_set_id": choice_set_id, "exists": False}
        return record

    def _consequence_card(self, state: Any, consequence_id: str) -> Dict[str, Any]:
        consequence = state.metadata.get("consequence_queue", {}).get(consequence_id)
        if not consequence:
            return {"consequence_id": consequence_id, "exists": False}
        return {
            "consequence_id": consequence_id,
            "exists": True,
            "consequence_type": consequence.get("consequence_type"),
            "summary": consequence.get("summary"),
            "affected_entity_ids": consequence.get("affected_entity_ids", []),
            "status": consequence.get("status"),
            "severity": consequence.get("severity"),
            "source_choice_id": consequence.get("source_choice_id"),
            "source_event_id": consequence.get("source_event_id"),
        }

    def _conflict_card(self, state: Any, conflict_id: str) -> Dict[str, Any]:
        conflict = state.metadata.get("conflict_registry", {}).get(conflict_id)
        if not conflict:
            return {"conflict_id": conflict_id, "exists": False}
        return {
            "conflict_id": conflict_id,
            "exists": True,
            "conflict_type": conflict.get("conflict_type"),
            "title": conflict.get("title"),
            "participant_ids": conflict.get("participant_ids", []),
            "core_issue": conflict.get("core_issue"),
            "opposing_goals": conflict.get("opposing_goals", {}),
            "status": conflict.get("status"),
            "conflict_pressure": conflict.get("conflict_pressure"),
            "unresolved_threads": conflict.get("unresolved_threads", []),
        }

    def _stakes_card(self, state: Any, stakes_id: str) -> Dict[str, Any]:
        record = state.metadata.get("stakes_registry", {}).get(stakes_id)
        if not record:
            return {"stakes_id": stakes_id, "exists": False}
        return {
            "stakes_id": stakes_id,
            "exists": True,
            "source_type": record.get("source_type"),
            "source_id": record.get("source_id"),
            "stake_values": record.get("stake_values", {}),
            "overall_stakes_score": record.get("overall_stakes_score"),
            "dominant_stake_type": record.get("dominant_stake_type"),
            "stakes_label": record.get("stakes_label"),
            "summary": record.get("summary"),
        }

    def _tension_curve_card(self, state: Any, curve_id: str) -> Dict[str, Any]:
        curve = state.metadata.get("tension_curves", {}).get(curve_id)
        if not curve:
            return {"curve_id": curve_id, "exists": False}
        return {
            "curve_id": curve_id,
            "exists": True,
            "source_type": curve.get("source_type"),
            "source_id": curve.get("source_id"),
            "average_tension": curve.get("average_tension"),
            "peak_tension": curve.get("peak_tension"),
            "curve_label": curve.get("curve_label"),
            "pacing_score": curve.get("pacing_score"),
            "recommended_scene_adjustment": curve.get("chunk5_handoff", {}).get("recommended_scene_adjustment"),
        }

    def _cast_card(self, state: Any, cast_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not cast_id:
            return None
        cast = state.metadata.get("cast_registry", {}).get(cast_id)
        if not cast:
            return {"cast_id": cast_id, "exists": False}
        return {
            "cast_id": cast_id,
            "exists": True,
            "selected_character_ids": cast.get("selected_character_ids", []),
            "selected_count": cast.get("selected_count"),
            "ensemble_score": cast.get("ensemble_report", {}).get("ensemble_score"),
            "role_counts": cast.get("ensemble_report", {}).get("role_counts", {}),
            "function_counts": cast.get("ensemble_report", {}).get("function_counts", {}),
        }

    def _latest_causal_context(self, state: Any) -> Dict[str, Any]:
        graphs = state.metadata.get("causal_graphs", {})
        if not graphs:
            return {
                "has_causal_graph": False,
                "must_preserve_causal_continuity": True,
            }

        latest_id = list(graphs.keys())[-1]
        graph = graphs[latest_id]
        return {
            "has_causal_graph": True,
            "latest_graph_id": latest_id,
            "node_count": len(graph.get("nodes", {})),
            "edge_count": len(graph.get("edges", {})),
            "must_preserve_causal_continuity": True,
        }

    def _dialogue_constraints(
        self,
        *,
        speaker_cards: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        emotional_context: List[Dict[str, Any]],
        story_request: Dict[str, Any],
    ) -> Dict[str, Any]:
        high_tension = any(rel.get("betrayal_risk", 0.0) >= 0.55 or rel.get("resentment", 0.0) >= 0.55 for rel in relationships)
        emotional = any(item.get("must_show_emotional_continuity") for item in emotional_context)

        return {
            "dialogue_style": story_request.get("dialogue_style", "character-specific and subtextual"),
            "must_include_subtext": high_tension or emotional,
            "must_avoid_same_voice": True,
            "must_reflect_power_imbalance": any(rel.get("power_imbalance", 0.0) >= 0.45 for rel in relationships),
            "must_reflect_hidden_knowledge": True,
            "speaker_count": len(speaker_cards),
        }

    def _subtext_requirements(
        self,
        conflicts: List[Dict[str, Any]],
        emotional_context: List[Dict[str, Any]],
        secret_ids: List[str],
    ) -> List[str]:
        requirements = []
        if conflicts:
            requirements.append("characters should talk around the core conflict, not state everything directly")
        if secret_ids:
            requirements.append("hidden information should create asymmetry and subtext")
        if any(item.get("dominant_emotion") for item in emotional_context):
            requirements.append("dialogue should carry emotional residue from prior scenes")
        return requirements

    def _scene_requirements(
        self,
        *,
        events: List[Dict[str, Any]],
        consequences: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        stakes: List[Dict[str, Any]],
        tension_curves: List[Dict[str, Any]],
    ) -> List[str]:
        requirements = []
        if events:
            requirements.append("show event causality clearly")
        if consequences:
            requirements.append("show fallout from prior choices/events")
        if conflicts:
            requirements.append("make opposing goals visible")
        if stakes:
            requirements.append("make cost and stakes legible")
        if tension_curves:
            requirements.append("follow pacing and tension guidance")
        return requirements or ["write a clear scene with purpose"]

    def _plot_structure_requirements(
        self,
        *,
        output_format: str,
        story_request: Dict[str, Any],
        conflicts: List[Dict[str, Any]],
        stakes: List[Dict[str, Any]],
        tension_curves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        format_defaults = {
            "movie": ["setup", "inciting incident", "midpoint", "crisis", "climax", "resolution"],
            "screenplay": ["slugline-aware scenes", "visual action", "dialogue beats", "climax"],
            "novel": ["chapter arc", "interiority", "reversals", "payoff"],
            "series_episode": ["cold open", "A plot", "B plot", "turning point", "hanger or resolution"],
            "season_outline": ["episode arcs", "character turns", "midseason escalation", "finale payoff"],
            "scene": ["goal", "conflict", "turn", "consequence"],
        }

        return {
            "format_beats": format_defaults.get(output_format, ["setup", "escalation", "payoff"]),
            "must_resolve_or_progress_conflicts": bool(conflicts),
            "must_pay_off_high_stakes": any(item.get("overall_stakes_score", 0.0) >= 0.65 for item in stakes),
            "must_follow_tension_guidance": bool(tension_curves),
            "user_requested_structure": story_request.get("structure_notes", ""),
        }

    def _dialogue_payload_warnings(self, payload: Dict[str, Any]) -> List[str]:
        warnings = []
        if len(payload.get("speaker_cards", [])) < 2:
            warnings.append("dialogue payload has fewer than two speakers")
        if not payload.get("relationship_context"):
            warnings.append("dialogue payload has no relationship context")
        return warnings

    def _scene_payload_warnings(self, payload: Dict[str, Any]) -> List[str]:
        warnings = []
        if not payload.get("selected_character_ids"):
            warnings.append("scene payload has no selected characters")
        if not payload.get("scene_goal"):
            warnings.append("scene payload has no explicit scene goal")
        return warnings

    def _plot_payload_warnings(self, payload: Dict[str, Any]) -> List[str]:
        warnings = []
        if not payload.get("selected_character_ids"):
            warnings.append("plot payload has no selected characters")
        if not payload.get("conflict_context"):
            warnings.append("plot payload has no conflicts")
        return warnings

    def _master_package_warnings(self, package: Dict[str, Any]) -> List[str]:
        warnings = []
        if not package.get("cast"):
            warnings.append("handoff package has no cast")
        if not package.get("plot_payload") and not package.get("scene_payloads"):
            warnings.append("handoff package has no plot or scene payloads")
        if package["global_context"]["causal_graph_count"] == 0:
            warnings.append("handoff package has no causal graph context")
        return warnings
