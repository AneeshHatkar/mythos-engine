from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import SceneBeat, SceneBlueprint


class SceneBeatPlanner:
    """Turns a scene blueprint into ordered story beats.

    The beat planner is where the blueprint becomes a sequence of actions,
    pressures, reveals, choices, and consequences. Later dialogue/prose engines
    will write from these beats instead of inventing random story flow.
    """

    engine_name = "story_generation.scene_beat_planner"

    DEFAULT_BEAT_ORDER = [
        "setup",
        "world_pressure",
        "relationship_pressure",
        "secret_pressure",
        "dialogue_pressure",
        "choice",
        "consequence",
        "ending_hook",
    ]

    def build_scene_beats(
        self,
        *,
        blueprint: SceneBlueprint,
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> Dict[str, Any]:
        beats: List[SceneBeat] = []

        beat_specs = self._build_beat_specs(
            blueprint=blueprint,
            story_context=story_context,
            world_detail_pack=world_detail_pack,
        )

        for index, spec in enumerate(beat_specs):
            beats.append(
                SceneBeat(
                    beat_id=f"beat_{blueprint.scene_id}_{index + 1:02d}_{spec['beat_type']}",
                    scene_id=blueprint.scene_id,
                    beat_index=index + 1,
                    beat_type=spec["beat_type"],
                    purpose=spec["purpose"],
                    character_ids=spec.get("character_ids", blueprint.active_character_ids),
                    emotional_state=spec.get("emotional_state", {}),
                    knowledge_constraints=spec.get("knowledge_constraints", []),
                    causal_links=spec.get("causal_links", []),
                    relationship_change_hint=spec.get("relationship_change_hint"),
                    tension_value=spec.get("tension_value", 0.0),
                )
            )

        warnings = self._warnings(beats=beats, blueprint=blueprint)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "scene_beats": beats,
            "scene_beats_dict": [beat.model_dump(mode="json") for beat in beats],
            "beat_count": len(beats),
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.dialogue_beat_engine",
                "payload_keys": [
                    "scene_blueprint",
                    "scene_beats",
                    "story_context",
                    "world_detail_pack",
                ],
            },
        }

    def validate_scene_beats(self, *, beats: List[SceneBeat], blueprint: SceneBlueprint) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not beats:
            blockers.append("no scene beats generated")
        else:
            passed.append("beats_present")

        beat_types = [beat.beat_type for beat in beats]

        if "setup" in beat_types:
            passed.append("setup_beat_present")
        else:
            warnings.append("setup beat missing")

        if "choice" in beat_types:
            passed.append("choice_beat_present")
        else:
            warnings.append("choice beat missing")

        if "consequence" in beat_types:
            passed.append("consequence_beat_present")
        else:
            warnings.append("consequence beat missing")

        if "ending_hook" in beat_types:
            passed.append("ending_hook_beat_present")
        else:
            warnings.append("ending hook beat missing")

        if blueprint.secret_pressure and "secret_pressure" not in beat_types:
            warnings.append("blueprint has secret pressure but no secret pressure beat")

        if blueprint.relationship_pressure and "relationship_pressure" not in beat_types:
            warnings.append("blueprint has relationship pressure but no relationship pressure beat")

        indexes = [beat.beat_index for beat in beats]
        if indexes == sorted(indexes) and len(indexes) == len(set(indexes)):
            passed.append("beat_indexes_ordered")
        else:
            blockers.append("beat indexes are not ordered and unique")

        if all(0.0 <= beat.tension_value <= 1.0 for beat in beats):
            passed.append("tension_values_bounded")
        else:
            blockers.append("one or more tension values are out of bounds")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_beats(self, *, beats: List[SceneBeat]) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "beat_count": len(beats),
                "beat_types": [beat.beat_type for beat in beats],
                "average_tension": self._average([beat.tension_value for beat in beats]),
                "max_tension": max([beat.tension_value for beat in beats], default=0.0),
                "knowledge_constraint_count": sum(len(beat.knowledge_constraints) for beat in beats),
                "causal_link_count": sum(len(beat.causal_links) for beat in beats),
                "relationship_change_hint_count": sum(1 for beat in beats if beat.relationship_change_hint),
            },
        }

    def _build_beat_specs(
        self,
        *,
        blueprint: SceneBlueprint,
        story_context: Dict[str, Any],
        world_detail_pack: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        curve = blueprint.tension_curve or [0.25, 0.45, 0.65, 0.85]
        specs: List[Dict[str, Any]] = []

        specs.append(
            {
                "beat_type": "setup",
                "purpose": self._setup_purpose(blueprint=blueprint),
                "character_ids": blueprint.active_character_ids,
                "emotional_state": self._emotional_state(story_context),
                "knowledge_constraints": [],
                "causal_links": [],
                "relationship_change_hint": None,
                "tension_value": curve[0],
            }
        )

        if blueprint.required_world_details:
            specs.append(
                {
                    "beat_type": "world_pressure",
                    "purpose": self._world_pressure_purpose(blueprint=blueprint, world_detail_pack=world_detail_pack),
                    "character_ids": blueprint.active_character_ids,
                    "emotional_state": self._emotional_state(story_context),
                    "knowledge_constraints": [],
                    "causal_links": self._causal_links(story_context),
                    "relationship_change_hint": None,
                    "tension_value": self._curve_value(curve, 1),
                }
            )

        if blueprint.relationship_pressure:
            specs.append(
                {
                    "beat_type": "relationship_pressure",
                    "purpose": blueprint.relationship_pressure[0],
                    "character_ids": blueprint.active_character_ids,
                    "emotional_state": self._emotional_state(story_context),
                    "knowledge_constraints": [],
                    "causal_links": [],
                    "relationship_change_hint": "Relationship pressure should visibly shift trust, resentment, longing, rivalry, or silence.",
                    "tension_value": self._curve_value(curve, 1),
                }
            )

        if blueprint.secret_pressure:
            specs.append(
                {
                    "beat_type": "secret_pressure",
                    "purpose": blueprint.secret_pressure[0],
                    "character_ids": blueprint.active_character_ids,
                    "emotional_state": self._emotional_state(story_context),
                    "knowledge_constraints": blueprint.secret_pressure,
                    "causal_links": self._causal_links(story_context),
                    "relationship_change_hint": "Secret pressure should affect what characters can safely say.",
                    "tension_value": self._curve_value(curve, 2),
                }
            )

        specs.append(
            {
                "beat_type": "dialogue_pressure",
                "purpose": "Characters speak under pressure while hiding, revealing, or redirecting what they know.",
                "character_ids": blueprint.active_character_ids,
                "emotional_state": self._emotional_state(story_context),
                "knowledge_constraints": blueprint.secret_pressure,
                "causal_links": self._causal_links(story_context),
                "relationship_change_hint": "Dialogue should show subtext and power movement.",
                "tension_value": self._curve_value(curve, 2),
            }
        )

        specs.append(
            {
                "beat_type": "choice",
                "purpose": self._choice_purpose(blueprint=blueprint),
                "character_ids": [blueprint.pov_character_id] if blueprint.pov_character_id else blueprint.active_character_ids,
                "emotional_state": self._emotional_state(story_context),
                "knowledge_constraints": blueprint.secret_pressure,
                "causal_links": self._causal_links(story_context),
                "relationship_change_hint": "The choice should imply a relationship or reputation change.",
                "tension_value": self._curve_value(curve, 3),
            }
        )

        specs.append(
            {
                "beat_type": "consequence",
                "purpose": self._consequence_purpose(blueprint=blueprint, story_context=story_context),
                "character_ids": blueprint.active_character_ids,
                "emotional_state": self._emotional_state(story_context),
                "knowledge_constraints": blueprint.secret_pressure,
                "causal_links": self._causal_links(story_context),
                "relationship_change_hint": "The consequence should make the next scene harder.",
                "tension_value": self._curve_value(curve, 3),
            }
        )

        specs.append(
            {
                "beat_type": "ending_hook",
                "purpose": blueprint.ending_hook or "End with a hook that creates a new consequence.",
                "character_ids": blueprint.active_character_ids,
                "emotional_state": self._emotional_state(story_context),
                "knowledge_constraints": blueprint.secret_pressure,
                "causal_links": self._causal_links(story_context),
                "relationship_change_hint": "The ending hook should leave a changed emotional or causal state.",
                "tension_value": self._curve_value(curve, 3),
            }
        )

        return specs

    def _setup_purpose(self, *, blueprint: SceneBlueprint) -> str:
        opening = blueprint.opening_image or "Open on a concrete world-specific image."
        return f"Establish the scene through {opening} and make the objective clear: {blueprint.scene_objective}"

    def _world_pressure_purpose(self, *, blueprint: SceneBlueprint, world_detail_pack: Dict[str, Any]) -> str:
        detail = blueprint.required_world_details[0] if blueprint.required_world_details else "a world-specific rule"
        requirements = world_detail_pack.get("format_specific_world_notes", [])
        note = requirements[0] if requirements else "Use world detail through action."
        return f"Make the world pressure concrete through {detail}. {note}"

    def _choice_purpose(self, *, blueprint: SceneBlueprint) -> str:
        return f"Force the POV or lead character to choose under pressure: {blueprint.scene_objective}"

    def _consequence_purpose(self, *, blueprint: SceneBlueprint, story_context: Dict[str, Any]) -> str:
        obligations = story_context.get("causal_obligations", [])
        consequences = [item for item in obligations if item.get("obligation_type") == "consequence"]
        if consequences:
            return f"Show or trigger consequence {consequences[0].get('id')}."
        return "Show the immediate result of the choice so the scene changes the story state."

    def _emotional_state(self, story_context: Dict[str, Any]) -> Dict[str, float]:
        state: Dict[str, float] = {}
        for item in story_context.get("emotional_pressure", []):
            character_id = item.get("character_id")
            emotion = item.get("dominant_emotion")
            intensity = item.get("dominant_intensity")
            if character_id and emotion:
                try:
                    state[f"{character_id}:{emotion}"] = max(0.0, min(1.0, float(intensity)))
                except (TypeError, ValueError):
                    state[f"{character_id}:{emotion}"] = 0.5
        return state

    def _causal_links(self, story_context: Dict[str, Any]) -> List[str]:
        return [
            item.get("id")
            for item in story_context.get("causal_obligations", [])
            if item.get("id")
        ]

    def _curve_value(self, curve: List[float], index: int) -> float:
        if not curve:
            return 0.5
        if index < len(curve):
            return curve[index]
        return curve[-1]

    def _warnings(self, *, beats: List[SceneBeat], blueprint: SceneBlueprint) -> List[str]:
        warnings = []

        if len(beats) < 5:
            warnings.append("Scene has fewer than five beats; it may feel underdeveloped.")

        beat_types = [beat.beat_type for beat in beats]

        if blueprint.secret_pressure and "secret_pressure" not in beat_types:
            warnings.append("Secret pressure exists but no secret pressure beat was created.")

        if blueprint.relationship_pressure and "relationship_pressure" not in beat_types:
            warnings.append("Relationship pressure exists but no relationship pressure beat was created.")

        if "choice" not in beat_types:
            warnings.append("No choice beat found; scene may lack agency.")

        if "consequence" not in beat_types:
            warnings.append("No consequence beat found; scene may not change state.")

        return warnings

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)
