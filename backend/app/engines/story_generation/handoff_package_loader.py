from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import (
    GenerationContract,
    HandoffReference,
    StoryContextPackage,
)


class HandoffPackageLoader:
    """Loads and normalizes Chunk 4 handoff data for Chunk 5 generation.

    Chunk 4 may store data in different metadata groups depending on which
    engine created it. This loader creates a stable StoryContextPackage so
    downstream Chunk 5 engines do not need to know every raw Chunk 4 shape.
    """

    engine_name = "story_generation.handoff_package_loader"

    def load_from_state(
        self,
        *,
        state: Any,
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        metadata = getattr(state, "metadata", {}) or {}
        reference = contract.handoff_reference

        raw_handoff = self._find_handoff(metadata=metadata, reference=reference)
        raw_generation_control = self._find_generation_control(metadata=metadata, reference=reference)
        raw_quality_report = self._find_by_id_candidates(
            metadata=metadata,
            wanted_id=reference.quality_report_id,
            buckets=[
                "simulation_quality_reports",
                "quality_reports",
            ],
        )
        raw_anti_genericity_report = self._find_by_id_candidates(
            metadata=metadata,
            wanted_id=reference.anti_genericity_report_id,
            buckets=[
                "simulation_anti_genericity_reports",
                "anti_genericity_reports",
            ],
        )

        context = self.build_context_package(
            state=state,
            contract=contract,
            handoff_payload=raw_handoff,
            generation_control_payload=raw_generation_control,
            quality_report=raw_quality_report,
            anti_genericity_report=raw_anti_genericity_report,
        )

        warnings = []
        if not raw_handoff:
            warnings.append("No explicit Chunk 4 handoff package found; context was built from state fallback.")
        if not context.character_context:
            warnings.append("No character context found.")
        if not context.world_context:
            warnings.append("No world context found.")
        if not context.causal_context:
            warnings.append("No causal context found; causal validation may be limited.")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "simulation_id": getattr(state, "simulation_id", reference.simulation_id),
            "handoff_reference": reference.model_dump(mode="json"),
            "raw_handoff_found": bool(raw_handoff),
            "raw_generation_control_found": bool(raw_generation_control),
            "context_package": context,
            "context_package_dict": context.model_dump(mode="json"),
            "warnings": warnings,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_context_builder",
                "payload_keys": [
                    "context_package",
                    "generation_contract",
                    "world_context",
                    "character_context",
                    "relationship_context",
                    "knowledge_context",
                    "causal_context",
                ],
            },
        }

    def load_from_payloads(
        self,
        *,
        contract: GenerationContract,
        handoff_payload: Optional[Dict[str, Any]] = None,
        generation_control_payload: Optional[Dict[str, Any]] = None,
        state_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        handoff_payload = handoff_payload or {}
        generation_control_payload = generation_control_payload or {}
        state_payload = state_payload or {}

        context = self.build_context_package_from_dicts(
            contract=contract,
            handoff_payload=handoff_payload,
            generation_control_payload=generation_control_payload,
            state_payload=state_payload,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "context_package": context,
            "context_package_dict": context.model_dump(mode="json"),
            "warnings": [] if handoff_payload else ["No handoff payload supplied; used dict fallback only."],
        }

    def build_context_package(
        self,
        *,
        state: Any,
        contract: GenerationContract,
        handoff_payload: Optional[Dict[str, Any]] = None,
        generation_control_payload: Optional[Dict[str, Any]] = None,
        quality_report: Optional[Dict[str, Any]] = None,
        anti_genericity_report: Optional[Dict[str, Any]] = None,
    ) -> StoryContextPackage:
        handoff_payload = handoff_payload or {}
        generation_control_payload = generation_control_payload or {}
        metadata = getattr(state, "metadata", {}) or {}

        world_state = getattr(state, "world_state", None)
        character_states = getattr(state, "character_states", {}) or {}
        relationship_states = getattr(state, "relationship_states", {}) or {}
        knowledge_states = getattr(state, "knowledge_states", {}) or {}

        world_context = self._merge_dicts(
            self._model_to_dict(world_state),
            handoff_payload.get("world_context", {}),
            generation_control_payload.get("world_context", {}),
        )

        character_context = self._build_character_context(
            character_states=character_states,
            handoff_payload=handoff_payload,
            contract=contract,
        )

        relationship_context = self._build_relationship_context(
            relationship_states=relationship_states,
            handoff_payload=handoff_payload,
            contract=contract,
        )

        knowledge_context = self._build_knowledge_context(
            knowledge_states=knowledge_states,
            handoff_payload=handoff_payload,
            contract=contract,
        )

        causal_context = self._build_causal_context(
            metadata=metadata,
            handoff_payload=handoff_payload,
            contract=contract,
        )

        emotional_context = self._build_emotional_context(character_context=character_context)
        location_context = self._extract_context_bucket(world_context, "locations")
        faction_context = self._extract_context_bucket(world_context, "factions")
        culture_context = self._extract_context_bucket(world_context, "cultures")

        format_context = {
            "selected_format": contract.selected_format.value,
            "format_contract": contract.format_contract,
            "tone_contract": contract.tone_contract,
            "quality_thresholds": contract.quality_thresholds,
            "originality_rules": contract.originality_rules,
        }

        user_intent_context = {
            "story_intent_id": contract.story_intent_id,
            "required_character_ids": contract.required_character_ids,
            "required_secret_ids": contract.required_secret_ids,
            "required_causal_node_ids": contract.required_causal_node_ids,
            "required_consequence_ids": contract.required_consequence_ids,
            "required_relationship_ids": contract.required_relationship_ids,
        }

        large_pool_context = self._build_large_pool_context(
            character_context=character_context,
            world_context=world_context,
            metadata=metadata,
        )

        if quality_report:
            format_context["quality_report"] = quality_report
        if anti_genericity_report:
            format_context["anti_genericity_report"] = anti_genericity_report

        return StoryContextPackage(
            context_package_id=f"context_{contract.generation_contract_id}",
            project_id=metadata.get("project_id"),
            universe_id=metadata.get("universe_id"),
            world_context=world_context,
            location_context=location_context,
            faction_context=faction_context,
            culture_context=culture_context,
            character_context=character_context,
            relationship_context=relationship_context,
            knowledge_context=knowledge_context,
            emotional_context=emotional_context,
            causal_context=causal_context,
            format_context=format_context,
            user_intent_context=user_intent_context,
            large_pool_context=large_pool_context,
        )

    def build_context_package_from_dicts(
        self,
        *,
        contract: GenerationContract,
        handoff_payload: Dict[str, Any],
        generation_control_payload: Dict[str, Any],
        state_payload: Dict[str, Any],
    ) -> StoryContextPackage:
        world_context = self._merge_dicts(
            state_payload.get("world_context", {}),
            handoff_payload.get("world_context", {}),
            generation_control_payload.get("world_context", {}),
        )

        character_context = self._merge_dicts(
            state_payload.get("character_context", {}),
            handoff_payload.get("character_context", {}),
        )

        relationship_context = self._merge_dicts(
            state_payload.get("relationship_context", {}),
            handoff_payload.get("relationship_context", {}),
        )

        knowledge_context = self._merge_dicts(
            state_payload.get("knowledge_context", {}),
            handoff_payload.get("knowledge_context", {}),
        )

        causal_context = self._merge_dicts(
            state_payload.get("causal_context", {}),
            {
                "causal_node_ids": handoff_payload.get("causal_node_ids", []),
                "consequence_ids": handoff_payload.get("consequence_ids", []),
            },
        )

        return StoryContextPackage(
            context_package_id=f"context_{contract.generation_contract_id}",
            project_id=state_payload.get("project_id"),
            universe_id=state_payload.get("universe_id"),
            world_context=world_context,
            location_context=self._extract_context_bucket(world_context, "locations"),
            faction_context=self._extract_context_bucket(world_context, "factions"),
            culture_context=self._extract_context_bucket(world_context, "cultures"),
            character_context=character_context,
            relationship_context=relationship_context,
            knowledge_context=knowledge_context,
            emotional_context=self._build_emotional_context(character_context=character_context),
            causal_context=causal_context,
            format_context={
                "selected_format": contract.selected_format.value,
                "format_contract": contract.format_contract,
                "tone_contract": contract.tone_contract,
                "quality_thresholds": contract.quality_thresholds,
                "originality_rules": contract.originality_rules,
            },
            user_intent_context={
                "story_intent_id": contract.story_intent_id,
                "required_character_ids": contract.required_character_ids,
                "required_secret_ids": contract.required_secret_ids,
                "required_causal_node_ids": contract.required_causal_node_ids,
                "required_consequence_ids": contract.required_consequence_ids,
                "required_relationship_ids": contract.required_relationship_ids,
            },
            large_pool_context=self._build_large_pool_context(
                character_context=character_context,
                world_context=world_context,
                metadata=state_payload,
            ),
        )

    def validate_context_package(self, *, context: StoryContextPackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not context.context_package_id:
            blockers.append("context_package_id is missing")
        else:
            passed.append("context_package_id_present")

        if context.character_context:
            passed.append("character_context_present")
        else:
            warnings.append("character_context is empty")

        if context.world_context:
            passed.append("world_context_present")
        else:
            warnings.append("world_context is empty")

        if context.format_context:
            passed.append("format_context_present")
        else:
            blockers.append("format_context is missing")

        if context.user_intent_context:
            passed.append("user_intent_context_present")
        else:
            warnings.append("user_intent_context is empty")

        if not context.relationship_context:
            warnings.append("relationship_context is empty; relationship beat engines may have limited signal")

        if not context.knowledge_context:
            warnings.append("knowledge_context is empty; knowledge boundary validation may be limited")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def summarize_context(self, *, context: StoryContextPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "context_package_id": context.context_package_id,
            "summary": {
                "world_context_keys": sorted(context.world_context.keys()),
                "character_count": len(context.character_context),
                "relationship_count": len(context.relationship_context),
                "knowledge_holder_count": len(context.knowledge_context),
                "causal_key_count": len(context.causal_context),
                "selected_format": context.format_context.get("selected_format"),
                "large_pool_context": context.large_pool_context,
            },
        }

    def _find_handoff(
        self,
        *,
        metadata: Dict[str, Any],
        reference: HandoffReference,
    ) -> Dict[str, Any]:
        return self._find_by_id_candidates(
            metadata=metadata,
            wanted_id=reference.handoff_package_id,
            buckets=[
                "handoff_packages",
                "simulation_handoff_packages",
                "chunk4_handoff_packages",
                "generation_handoff_packages",
            ],
        )

    def _find_generation_control(
        self,
        *,
        metadata: Dict[str, Any],
        reference: HandoffReference,
    ) -> Dict[str, Any]:
        return self._find_by_id_candidates(
            metadata=metadata,
            wanted_id=reference.generation_control_payload_id,
            buckets=[
                "generation_control_payloads",
                "simulation_generation_control_payloads",
                "story_generation_control_payloads",
            ],
        )

    def _find_by_id_candidates(
        self,
        *,
        metadata: Dict[str, Any],
        wanted_id: Optional[str],
        buckets: List[str],
    ) -> Dict[str, Any]:
        if not wanted_id:
            return {}

        for bucket in buckets:
            values = metadata.get(bucket, {})
            if isinstance(values, dict) and wanted_id in values:
                item = values[wanted_id]
                return item if isinstance(item, dict) else {"value": item}

        return {}

    def _build_character_context(
        self,
        *,
        character_states: Dict[str, Any],
        handoff_payload: Dict[str, Any],
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {}

        for character_id, state in character_states.items():
            data = self._model_to_dict(state)
            if data:
                context[character_id] = data

        for character_id, data in handoff_payload.get("character_context", {}).items():
            if isinstance(data, dict):
                context.setdefault(character_id, {}).update(data)

        allowed = set(contract.allowed_character_ids or [])
        required = set(contract.required_character_ids or [])

        if allowed or required:
            keep = allowed | required
            if keep:
                filtered = {cid: data for cid, data in context.items() if cid in keep}
                if filtered:
                    context = filtered

        for cid in contract.required_character_ids:
            context.setdefault(cid, {"character_id": cid, "required_by_contract": True})

        return context

    def _build_relationship_context(
        self,
        *,
        relationship_states: Dict[str, Any],
        handoff_payload: Dict[str, Any],
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {}

        for relationship_id, state in relationship_states.items():
            data = self._model_to_dict(state)
            if data:
                context[relationship_id] = data

        for relationship_id, data in handoff_payload.get("relationship_context", {}).items():
            if isinstance(data, dict):
                context.setdefault(relationship_id, {}).update(data)

        if contract.required_relationship_ids:
            for rid in contract.required_relationship_ids:
                context.setdefault(rid, {"relationship_id": rid, "required_by_contract": True})

        return context

    def _build_knowledge_context(
        self,
        *,
        knowledge_states: Dict[str, Any],
        handoff_payload: Dict[str, Any],
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {}

        for holder_id, state in knowledge_states.items():
            data = self._model_to_dict(state)
            if data:
                context[holder_id] = data

        for holder_id, data in handoff_payload.get("knowledge_context", {}).items():
            if isinstance(data, dict):
                context.setdefault(holder_id, {}).update(data)

        context.setdefault("_contract_required_secret_ids", contract.required_secret_ids)
        context.setdefault("_contract_forbidden_secret_reveals", contract.forbidden_secret_reveals)

        return context

    def _build_causal_context(
        self,
        *,
        metadata: Dict[str, Any],
        handoff_payload: Dict[str, Any],
        contract: GenerationContract,
    ) -> Dict[str, Any]:
        return {
            "required_causal_node_ids": contract.required_causal_node_ids,
            "required_consequence_ids": contract.required_consequence_ids,
            "handoff_causal_node_ids": handoff_payload.get("causal_node_ids", []),
            "handoff_consequence_ids": handoff_payload.get("consequence_ids", []),
            "causal_chains": metadata.get("causal_chains", {}),
            "causal_graphs": metadata.get("causal_graphs", {}),
            "consequence_queue": metadata.get("consequence_queue", {}),
        }

    def _build_emotional_context(self, *, character_context: Dict[str, Any]) -> Dict[str, Any]:
        emotional: Dict[str, Any] = {}

        for character_id, data in character_context.items():
            if not isinstance(data, dict):
                continue

            metadata = data.get("metadata", {}) if isinstance(data.get("metadata", {}), dict) else {}
            emotional_state = data.get("emotional_state", metadata.get("emotional_state", {}))
            if emotional_state:
                emotional[character_id] = emotional_state

        return emotional

    def _extract_context_bucket(self, world_context: Dict[str, Any], key: str) -> Dict[str, Any]:
        value = world_context.get(key, {})
        if isinstance(value, dict):
            return value
        if isinstance(value, list):
            return {str(item): {"name": str(item)} for item in value}
        return {}

    def _build_large_pool_context(
        self,
        *,
        character_context: Dict[str, Any],
        world_context: Dict[str, Any],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        skill_count = len(metadata.get("skill_registry", {})) if isinstance(metadata.get("skill_registry", {}), dict) else 0
        power_count = len(metadata.get("power_registry", {})) if isinstance(metadata.get("power_registry", {}), dict) else 0
        artifact_count = len(metadata.get("artifact_registry", {})) if isinstance(metadata.get("artifact_registry", {}), dict) else 0
        faction_count = len(self._extract_context_bucket(world_context, "factions"))

        return {
            "character_count": len(character_context),
            "skill_count": skill_count,
            "power_count": power_count,
            "artifact_count": artifact_count,
            "faction_count": faction_count,
            "large_character_pool": len(character_context) >= 100,
            "large_skill_pool": skill_count >= 100,
            "large_power_pool": power_count >= 100,
            "large_artifact_pool": artifact_count >= 100,
        }

    def _model_to_dict(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")
        if hasattr(value, "dict"):
            return value.dict()
        return {}

    def _merge_dicts(self, *items: Dict[str, Any]) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        for item in items:
            if isinstance(item, dict):
                merged.update(item)
        return merged
