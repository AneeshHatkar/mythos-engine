from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import GenerationContract, StoryContextPackage


class StoryContextBuilder:
    """Builds a story-ready context from normalized handoff data.

    The handoff loader normalizes raw Chunk 4 data.
    This builder turns that normalized package into generation-ready sections:
    active cast, world rules, location anchors, relationship pressure,
    knowledge boundaries, emotional pressure, causal obligations, and format needs.
    """

    engine_name = "story_generation.story_context_builder"

    def build_story_context(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        active_cast = self._build_active_cast(
            context_package=context_package,
            contract=contract,
        )
        world_rules = self._build_world_rule_context(
            context_package=context_package,
            contract=contract,
        )
        location_anchor = self._select_location_anchor(context_package=context_package)
        relationship_pressure = self._build_relationship_pressure(
            context_package=context_package,
            contract=contract,
        )
        knowledge_boundaries = self._build_knowledge_boundaries(
            context_package=context_package,
            contract=contract,
        )
        emotional_pressure = self._build_emotional_pressure(context_package=context_package)
        causal_obligations = self._build_causal_obligations(
            context_package=context_package,
            contract=contract,
        )
        format_requirements = self._build_format_requirements(contract=contract)
        large_pool_summary = self._build_large_pool_summary(context_package=context_package)

        readiness = self._score_readiness(
            active_cast=active_cast,
            world_rules=world_rules,
            relationship_pressure=relationship_pressure,
            knowledge_boundaries=knowledge_boundaries,
            causal_obligations=causal_obligations,
            format_requirements=format_requirements,
        )

        story_context = {
            "story_context_id": f"storyctx_{context_package.context_package_id}",
            "source_context_package_id": context_package.context_package_id,
            "generation_contract_id": contract.generation_contract_id,
            "active_cast": active_cast,
            "world_rules": world_rules,
            "location_anchor": location_anchor,
            "relationship_pressure": relationship_pressure,
            "knowledge_boundaries": knowledge_boundaries,
            "emotional_pressure": emotional_pressure,
            "causal_obligations": causal_obligations,
            "format_requirements": format_requirements,
            "large_pool_summary": large_pool_summary,
            "readiness": readiness,
            "warnings": self._warnings(
                active_cast=active_cast,
                world_rules=world_rules,
                relationship_pressure=relationship_pressure,
                knowledge_boundaries=knowledge_boundaries,
                causal_obligations=causal_obligations,
            ),
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_context": story_context,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.world_detail_injection_engine",
                "payload_keys": [
                    "story_context",
                    "world_rules",
                    "location_anchor",
                    "active_cast",
                    "format_requirements",
                ],
            },
        }

    def validate_story_context(self, *, story_context: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not story_context.get("story_context_id"):
            blockers.append("story_context_id is missing")
        else:
            passed.append("story_context_id_present")

        if story_context.get("active_cast"):
            passed.append("active_cast_present")
        else:
            blockers.append("active_cast is empty")

        if story_context.get("format_requirements"):
            passed.append("format_requirements_present")
        else:
            blockers.append("format_requirements missing")

        if story_context.get("world_rules"):
            passed.append("world_rules_present")
        else:
            warnings.append("world_rules empty; output may become generic")

        if story_context.get("relationship_pressure"):
            passed.append("relationship_pressure_present")
        else:
            warnings.append("relationship_pressure empty; relationship beats may be weak")

        if story_context.get("causal_obligations"):
            passed.append("causal_obligations_present")
        else:
            warnings.append("causal_obligations empty; causality may be weak")

        readiness = story_context.get("readiness", {})
        if readiness.get("ready_for_blueprint") is True:
            passed.append("ready_for_blueprint")
        else:
            warnings.append("story context may not be ready for blueprinting")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_story_context(self, *, story_context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "story_context_id": story_context.get("story_context_id"),
                "cast_count": len(story_context.get("active_cast", [])),
                "world_rule_count": len(story_context.get("world_rules", [])),
                "relationship_pressure_count": len(story_context.get("relationship_pressure", [])),
                "knowledge_boundary_count": len(story_context.get("knowledge_boundaries", [])),
                "causal_obligation_count": len(story_context.get("causal_obligations", [])),
                "selected_format": story_context.get("format_requirements", {}).get("selected_format"),
                "readiness_score": story_context.get("readiness", {}).get("readiness_score", 0.0),
                "ready_for_blueprint": story_context.get("readiness", {}).get("ready_for_blueprint", False),
            },
        }

    def _build_active_cast(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> List[Dict[str, Any]]:
        cast: List[Dict[str, Any]] = []

        required = set(contract.required_character_ids)
        allowed = set(contract.allowed_character_ids)

        if not allowed:
            allowed = set(context_package.character_context.keys())

        ordered_ids = []
        for cid in contract.required_character_ids:
            if cid not in ordered_ids:
                ordered_ids.append(cid)

        for cid in allowed:
            if cid not in ordered_ids:
                ordered_ids.append(cid)

        for character_id in ordered_ids:
            data = context_package.character_context.get(character_id, {})
            metadata = data.get("metadata", {}) if isinstance(data.get("metadata", {}), dict) else {}

            cast.append(
                {
                    "character_id": character_id,
                    "required": character_id in required,
                    "display_name": metadata.get("display_name", data.get("display_name", character_id)),
                    "current_location_id": data.get("current_location_id"),
                    "voice_profile": metadata.get("voice_profile", data.get("voice_profile", {})),
                    "goals": metadata.get("goals", data.get("goals", {})),
                    "psychology": metadata.get("psychology", data.get("psychology", {})),
                    "emotional_state": (
                        context_package.emotional_context.get(character_id)
                        or metadata.get("emotional_state", {})
                        or data.get("emotional_state", {})
                    ),
                    "story_function_tags": metadata.get("story_function_tags", []),
                    "role_tags": metadata.get("role_tags", []),
                }
            )

        return cast

    def _build_world_rule_context(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> List[Dict[str, Any]]:
        world_context = context_package.world_context or {}
        metadata = world_context.get("metadata", {}) if isinstance(world_context.get("metadata", {}), dict) else {}
        rules = world_context.get("world_rules", metadata.get("world_rules", {}))

        result: List[Dict[str, Any]] = []

        if isinstance(rules, dict):
            for rule_id, rule in rules.items():
                if contract.required_world_rule_ids and rule_id not in contract.required_world_rule_ids:
                    continue
                result.append(
                    {
                        "rule_id": str(rule_id),
                        "description": rule if isinstance(rule, str) else rule.get("description", str(rule)),
                        "required": rule_id in contract.required_world_rule_ids,
                    }
                )
        elif isinstance(rules, list):
            for index, rule in enumerate(rules):
                result.append(
                    {
                        "rule_id": f"world_rule_{index}",
                        "description": str(rule),
                        "required": False,
                    }
                )

        for rule_id in contract.required_world_rule_ids:
            if not any(item["rule_id"] == rule_id for item in result):
                result.append(
                    {
                        "rule_id": rule_id,
                        "description": "Required by generation contract but not found in world context.",
                        "required": True,
                        "missing_from_world_context": True,
                    }
                )

        return result

    def _select_location_anchor(self, *, context_package: StoryContextPackage) -> Dict[str, Any]:
        locations = context_package.location_context or {}

        if not locations:
            return {
                "location_id": None,
                "name": "unspecified location",
                "missing": True,
            }

        first_id = sorted(locations.keys())[0]
        value = locations[first_id]

        if isinstance(value, dict):
            return {
                "location_id": first_id,
                "name": value.get("name", first_id),
                "details": value,
                "missing": False,
            }

        return {
            "location_id": first_id,
            "name": str(value),
            "details": {"value": value},
            "missing": False,
        }

    def _build_relationship_pressure(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> List[Dict[str, Any]]:
        pressure = []

        for relationship_id, data in context_package.relationship_context.items():
            if contract.required_relationship_ids and relationship_id not in contract.required_relationship_ids:
                continue

            trust = self._float(data.get("trust", 0.0))
            resentment = self._float(data.get("resentment", 0.0))
            romantic_tension = self._float(data.get("romantic_tension", data.get("affection", 0.0)))
            betrayal_risk = self._float(data.get("betrayal_risk", 0.0))
            rivalry = self._float(data.get("rivalry", 0.0))

            pressure_score = max(
                resentment,
                romantic_tension,
                betrayal_risk,
                rivalry,
                1.0 - trust if trust > 0 else 0.0,
            )

            pressure.append(
                {
                    "relationship_id": relationship_id,
                    "character_a_id": data.get("character_a_id"),
                    "character_b_id": data.get("character_b_id"),
                    "trust": trust,
                    "resentment": resentment,
                    "romantic_tension": romantic_tension,
                    "betrayal_risk": betrayal_risk,
                    "rivalry": rivalry,
                    "pressure_score": round(pressure_score, 3),
                    "required": relationship_id in contract.required_relationship_ids,
                }
            )

        pressure.sort(key=lambda item: item["pressure_score"], reverse=True)
        return pressure

    def _build_knowledge_boundaries(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> List[Dict[str, Any]]:
        boundaries = []

        for holder_id, data in context_package.knowledge_context.items():
            if holder_id.startswith("_"):
                continue

            known_secret_ids = data.get("known_secret_ids", [])
            evidence_seen_ids = data.get("evidence_seen_ids", [])

            boundaries.append(
                {
                    "holder_id": holder_id,
                    "known_secret_ids": known_secret_ids,
                    "evidence_seen_ids": evidence_seen_ids,
                    "required_secret_ids": contract.required_secret_ids,
                    "forbidden_secret_reveals": contract.forbidden_secret_reveals,
                    "missing_required_secret_ids": [
                        sid for sid in contract.required_secret_ids if sid not in known_secret_ids
                    ],
                }
            )

        if not boundaries and (contract.required_secret_ids or contract.forbidden_secret_reveals):
            boundaries.append(
                {
                    "holder_id": "_contract",
                    "known_secret_ids": [],
                    "evidence_seen_ids": [],
                    "required_secret_ids": contract.required_secret_ids,
                    "forbidden_secret_reveals": contract.forbidden_secret_reveals,
                    "missing_required_secret_ids": contract.required_secret_ids,
                    "contract_only": True,
                }
            )

        return boundaries

    def _build_emotional_pressure(self, *, context_package: StoryContextPackage) -> List[Dict[str, Any]]:
        pressure = []

        for character_id, emotions in context_package.emotional_context.items():
            if not isinstance(emotions, dict):
                continue

            if emotions:
                dominant = max(emotions.items(), key=lambda item: self._float(item[1]))
                pressure.append(
                    {
                        "character_id": character_id,
                        "dominant_emotion": dominant[0],
                        "dominant_intensity": self._float(dominant[1]),
                        "emotions": emotions,
                    }
                )

        pressure.sort(key=lambda item: item["dominant_intensity"], reverse=True)
        return pressure

    def _build_causal_obligations(
        self,
        *,
        context_package: StoryContextPackage,
        contract: GenerationContract,
    ) -> List[Dict[str, Any]]:
        obligations = []

        for node_id in contract.required_causal_node_ids:
            obligations.append(
                {
                    "obligation_type": "causal_node",
                    "id": node_id,
                    "required": True,
                    "reason": "Required by generation contract.",
                }
            )

        for consequence_id in contract.required_consequence_ids:
            obligations.append(
                {
                    "obligation_type": "consequence",
                    "id": consequence_id,
                    "required": True,
                    "reason": "Required consequence must be acknowledged or paid off.",
                }
            )

        causal_context = context_package.causal_context or {}
        for node_id in causal_context.get("handoff_causal_node_ids", []):
            if not any(item["id"] == node_id for item in obligations):
                obligations.append(
                    {
                        "obligation_type": "handoff_causal_node",
                        "id": node_id,
                        "required": False,
                        "reason": "Provided by Chunk 4 handoff payload.",
                    }
                )

        return obligations

    def _build_format_requirements(self, *, contract: GenerationContract) -> Dict[str, Any]:
        return {
            "selected_format": contract.selected_format.value,
            "format_contract": contract.format_contract,
            "tone_contract": contract.tone_contract,
            "quality_thresholds": contract.quality_thresholds,
            "originality_rules": contract.originality_rules,
            "validation_required": contract.validation_required,
            "provenance_required": contract.provenance_required,
        }

    def _build_large_pool_summary(self, *, context_package: StoryContextPackage) -> Dict[str, Any]:
        large = context_package.large_pool_context or {}
        return {
            "character_count": large.get("character_count", len(context_package.character_context)),
            "skill_count": large.get("skill_count", 0),
            "power_count": large.get("power_count", 0),
            "artifact_count": large.get("artifact_count", 0),
            "faction_count": large.get("faction_count", len(context_package.faction_context)),
            "needs_scaling_controller": any(
                [
                    large.get("large_character_pool", False),
                    large.get("large_skill_pool", False),
                    large.get("large_power_pool", False),
                    large.get("large_artifact_pool", False),
                ]
            ),
        }

    def _score_readiness(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        world_rules: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
        knowledge_boundaries: List[Dict[str, Any]],
        causal_obligations: List[Dict[str, Any]],
        format_requirements: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = 0.15

        if active_cast:
            score += 0.20
        if world_rules:
            score += 0.15
        if relationship_pressure:
            score += 0.15
        if knowledge_boundaries:
            score += 0.10
        if causal_obligations:
            score += 0.15
        if format_requirements:
            score += 0.10

        score = round(max(0.0, min(1.0, score)), 3)

        return {
            "readiness_score": score,
            "ready_for_blueprint": score >= 0.60 and bool(active_cast) and bool(format_requirements),
            "missing_core_sections": self._missing_core_sections(
                active_cast=active_cast,
                world_rules=world_rules,
                relationship_pressure=relationship_pressure,
                knowledge_boundaries=knowledge_boundaries,
                causal_obligations=causal_obligations,
                format_requirements=format_requirements,
            ),
        }

    def _missing_core_sections(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        world_rules: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
        knowledge_boundaries: List[Dict[str, Any]],
        causal_obligations: List[Dict[str, Any]],
        format_requirements: Dict[str, Any],
    ) -> List[str]:
        missing = []
        if not active_cast:
            missing.append("active_cast")
        if not world_rules:
            missing.append("world_rules")
        if not relationship_pressure:
            missing.append("relationship_pressure")
        if not knowledge_boundaries:
            missing.append("knowledge_boundaries")
        if not causal_obligations:
            missing.append("causal_obligations")
        if not format_requirements:
            missing.append("format_requirements")
        return missing

    def _warnings(
        self,
        *,
        active_cast: List[Dict[str, Any]],
        world_rules: List[Dict[str, Any]],
        relationship_pressure: List[Dict[str, Any]],
        knowledge_boundaries: List[Dict[str, Any]],
        causal_obligations: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []
        if not active_cast:
            warnings.append("No active cast found; cannot generate character-grounded output.")
        if not world_rules:
            warnings.append("No world rules found; output may become generic.")
        if not relationship_pressure:
            warnings.append("No relationship pressure found; scene may lack relational stakes.")
        if not knowledge_boundaries:
            warnings.append("No knowledge boundaries found; secret handling may be weak.")
        if not causal_obligations:
            warnings.append("No causal obligations found; consequence payoff may be weak.")
        return warnings

    def _float(self, value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
