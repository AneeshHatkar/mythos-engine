from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.app.services.learning_integration import LearningIntegrationService


class CharacterLearningAdapter:
    """Connects Chunk 3 character intelligence outputs to global learning.

    This adapter normalizes character engine outputs, full character profiles,
    and character bible exports into learning-ready records and registers them
    into the global learning foundation from Upgrade Pass A.

    It does not train models or compute embeddings yet. It prepares high-quality,
    provenance-safe character outputs for future Chunk 8 learning/RAG/training.
    """

    def __init__(
        self,
        integration_service: Optional[LearningIntegrationService] = None,
    ) -> None:
        self.integration = integration_service or LearningIntegrationService()

    def register_character_engine_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
        world_contract: Optional[Dict[str, Any]] = None,
        enforce_quality_gates: bool = True,
    ) -> Dict[str, Any]:
        """Register one character engine result into global learning stores."""

        normalized = self.normalize_character_result(
            result_payload=result_payload,
            project_id=project_id,
            universe_id=universe_id,
            source_payload=source_payload,
            world_contract=world_contract,
        )

        gate_report = self.evaluate_character_learning_quality_gates(normalized)

        if enforce_quality_gates and not gate_report["can_register_learning"]:
            return {
                "success": True,
                "registered": False,
                "reason": "character_learning_quality_gate_failed",
                "quality_gate_report": gate_report,
                "normalized_character_result": normalized,
            }

        registration = self.integration.register_engine_result(
            result_payload=normalized["result_payload"],
            project_id=project_id,
            universe_id=universe_id,
            source_payload=normalized["source_payload"],
        )

        return {
            "success": True,
            "registered": registration.get("registered", False),
            "character_id": normalized["character_id"],
            "project_id": project_id,
            "universe_id": universe_id,
            "quality_gate_report": gate_report,
            "learning_registration": registration,
            "world_contract_validation": normalized["world_contract_validation"],
            "chunk4_handoff_contract": normalized["chunk4_handoff_contract"],
        }

    def register_character_profile(
        self,
        *,
        character_profile: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        world_contract: Optional[Dict[str, Any]] = None,
        enforce_quality_gates: bool = True,
    ) -> Dict[str, Any]:
        """Register learning metadata discovered inside a character profile."""

        normalized = self.normalize_character_profile(
            character_profile=character_profile,
            project_id=project_id,
            universe_id=universe_id,
            world_contract=world_contract,
        )

        gate_report = self.evaluate_character_learning_quality_gates(normalized)

        if enforce_quality_gates and not gate_report["can_register_learning"]:
            return {
                "success": True,
                "registered": False,
                "reason": "character_profile_quality_gate_failed",
                "quality_gate_report": gate_report,
                "normalized_character_result": normalized,
            }

        result = self.integration.register_profile_learning_metadata(
            profile=normalized.get("profile_wrapper") or normalized["character_profile"],
            project_id=project_id,
            universe_id=universe_id,
        )

        return {
            "success": True,
            "registered": result.get("registered_count", 0) > 0,
            "character_id": normalized["character_id"],
            "project_id": project_id,
            "universe_id": universe_id,
            "quality_gate_report": gate_report,
            "learning_registration": result,
            "world_contract_validation": normalized["world_contract_validation"],
            "chunk4_handoff_contract": normalized["chunk4_handoff_contract"],
        }

    def normalize_character_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str,
        universe_id: str,
        source_payload: Optional[Dict[str, Any]] = None,
        world_contract: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        data = result_payload.get("data", {}) if isinstance(result_payload, dict) else {}

        character_profile = self._extract_character_profile(data, source_payload or result_payload)
        character_id = self._extract_character_id(data, character_profile, source_payload or result_payload)

        learning_metadata = data.get("learning_metadata") or self._synthesize_character_learning_metadata(
            result_payload=result_payload,
            character_id=character_id,
            project_id=project_id,
            universe_id=universe_id,
            character_profile=character_profile,
        )

        world_validation = self.validate_character_against_world_contract(
            character_profile=character_profile or data,
            world_contract=world_contract or {},
        )

        chunk4_handoff = self.build_chunk4_handoff_contract(
            character_id=character_id,
            character_profile=character_profile or data,
        )

        normalized_result = dict(result_payload)
        normalized_data = dict(data)
        normalized_data["learning_metadata"] = learning_metadata
        normalized_data["character_learning_adapter_metadata"] = {
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "adapter_version": "character_learning_adapter_v0.1.0",
            "normalized_for_global_learning": True,
            "world_contract_validated": world_validation["world_contract_checked"],
            "chunk4_handoff_ready": chunk4_handoff["handoff_ready"],
        }
        normalized_result["data"] = normalized_data

        return {
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "result_payload": normalized_result,
            "source_payload": source_payload or character_profile or data,
            "character_profile": character_profile,
            "learning_metadata": learning_metadata,
            "world_contract_validation": world_validation,
            "chunk4_handoff_contract": chunk4_handoff,
        }

    def normalize_character_profile(
        self,
        *,
        character_profile: Dict[str, Any],
        project_id: str,
        universe_id: str,
        world_contract: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Keep the full wrapper for learning metadata extraction, but use the
        # inner full profile for quality gates, world-contract validation, and
        # Chunk 4 handoff checks.
        inner_profile = self._extract_character_profile(character_profile, character_profile) or character_profile
        character_id = self._extract_character_id(character_profile, inner_profile)

        world_validation = self.validate_character_against_world_contract(
            character_profile=inner_profile,
            world_contract=world_contract or {},
        )

        chunk4_handoff = self.build_chunk4_handoff_contract(
            character_id=character_id,
            character_profile=inner_profile,
        )

        return {
            "character_id": character_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "character_profile": inner_profile,
            "source_payload": character_profile,
            "profile_wrapper": character_profile,
            "learning_metadata": {},
            "world_contract_validation": world_validation,
            "chunk4_handoff_contract": chunk4_handoff,
        }

    def validate_character_against_world_contract(
        self,
        *,
        character_profile: Dict[str, Any],
        world_contract: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate that a character is not disconnected from the world.

        This does not need to be perfect yet. It gives Chunk 4+ a reliable
        contract check and prevents obvious world-breaking outputs from entering
        high-quality learning queues.
        """

        if not world_contract:
            return {
                "world_contract_checked": False,
                "world_contract_valid": True,
                "compatibility_score": 0.72,
                "violations": [],
                "warnings": ["No world contract provided; validation is partial."],
                "validated_axes": [],
            }

        profile = character_profile or {}
        flat = self._flatten_character(profile)

        social_class = flat.get("social_class")
        family_name_status = flat.get("family_name_status")
        education_access = flat.get("education_access") or flat.get("education_goal") or flat.get("scholarship")
        primary_skill = flat.get("primary_skill") or flat.get("skill_family")

        violations: List[str] = []
        warnings: List[str] = []
        validated_axes: List[str] = []

        social_classes = self._stringify_list(world_contract.get("social_classes", []))
        if social_class:
            validated_axes.append("social_class")
            if social_classes and social_class not in social_classes:
                warnings.append(f"social_class '{social_class}' is not explicitly listed in world contract")

        legal_constraints_text = " ".join(self._stringify_list(world_contract.get("legal_constraints", []))).lower()
        permission_boundaries = " ".join(self._stringify_list(world_contract.get("character_permission_boundaries", []))).lower()

        if family_name_status:
            validated_axes.append("family_name_status")
            if "erased" in str(family_name_status).lower() and "sponsor" in legal_constraints_text:
                has_route = any(
                    token in str(education_access).lower()
                    for token in ["sponsor", "debt", "illegal", "exam", "patron", "exception"]
                )
                if not has_route:
                    violations.append("erased/distrusted family status requires a concrete sponsor, debt, exam, illegal route, patron, or exception")

        power_text = " ".join(self._stringify_list(world_contract.get("power_laws", []))).lower()
        if primary_skill:
            validated_axes.append("skill_power")
            if power_text and "cost" in power_text:
                cost_model = str(flat.get("cost_model") or flat.get("skill_cost") or flat.get("adaptation_cost") or "").lower()
                if not cost_model:
                    warnings.append("world power laws mention cost, but character skill/power cost is not explicit")

        if education_access:
            validated_axes.append("education_access")

        score = 1.0
        score -= 0.22 * len(violations)
        score -= 0.08 * len(warnings)
        score = round(max(0.0, min(1.0, score)), 3)

        return {
            "world_contract_checked": True,
            "world_contract_valid": len(violations) == 0,
            "compatibility_score": score,
            "violations": violations,
            "warnings": warnings,
            "validated_axes": sorted(set(validated_axes)),
        }

    def build_chunk4_handoff_contract(
        self,
        *,
        character_id: str,
        character_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        profile = character_profile or {}
        flat = self._flatten_character(profile)

        relationship_readiness = self._extract_nested(profile, ["relationships", "relationship_readiness_profile"]) or flat.get("relationship_readiness_profile") or {}
        dialogue_voice = self._extract_nested(profile, ["dialogue", "dialogue_voice_profile"]) or flat.get("dialogue_voice_profile") or {}
        psychology = self._extract_nested(profile, ["psychology", "psychology_profile"]) or flat.get("psychology_profile") or {}
        goals = self._extract_nested(profile, ["psychology", "goal_profile"]) or flat.get("goal_profile") or {}
        memory_records = self._extract_nested(profile, ["psychology", "memory_records"]) or flat.get("memory_records") or []
        destiny = self._extract_nested(profile, ["destiny", "destiny_profile"]) or flat.get("destiny_profile") or {}

        missing = []
        if not relationship_readiness:
            missing.append("relationship_readiness")
        if not dialogue_voice:
            missing.append("dialogue_voice")
        if not psychology:
            missing.append("psychology")
        if not goals:
            missing.append("goals")
        if not memory_records:
            missing.append("memory_records")

        return {
            "handoff_id": f"charhandoff_{uuid4().hex[:12]}",
            "character_id": character_id,
            "relationship_readiness": relationship_readiness,
            "dialogue_voice": dialogue_voice,
            "psychology": psychology,
            "goals": goals,
            "memory_records": memory_records,
            "destiny": destiny,
            "handoff_ready": len(missing) <= 2,
            "missing_sections": missing,
            "chunk4_usage": [
                "friendship simulation",
                "rivalry simulation",
                "romance simulation",
                "family pressure simulation",
                "betrayal and repair simulation",
                "ensemble dialogue pressure",
            ],
        }

    def evaluate_character_learning_quality_gates(self, normalized_character_result: Dict[str, Any]) -> Dict[str, Any]:
        metadata = normalized_character_result.get("learning_metadata", {}) or {}
        profile = normalized_character_result.get("character_profile", {}) or {}
        world_validation = normalized_character_result.get("world_contract_validation", {}) or {}
        chunk4_handoff = normalized_character_result.get("chunk4_handoff_contract", {}) or {}

        training_eligibility = metadata.get("training_eligibility", {}) or {}
        embedding_metadata = metadata.get("embedding_metadata", {}) or {}
        labels = metadata.get("generated_training_labels", {}) or {}

        quality_score = float(
            training_eligibility.get("quality_score")
            or labels.get("quality_score")
            or self._extract_quality_score(profile)
            or 0.74
        )

        originality_score = float(
            training_eligibility.get("originality_score")
            or embedding_metadata.get("originality_score")
            or self._extract_originality_score(profile)
            or 0.72
        )

        consistency_score = float(
            training_eligibility.get("consistency_score")
            or self._extract_consistency_score(profile)
            or 0.74
        )

        genericity_risk = float(self._extract_genericity_risk(profile) or 0.25)
        source_allowed = self._source_allowed(metadata)

        blockers = []

        if not source_allowed:
            blockers.append("source provenance is not approved for learning registration")

        if quality_score < 0.55:
            blockers.append("character quality score below minimum learning registration threshold")

        if originality_score < 0.5:
            blockers.append("character originality score below minimum learning registration threshold")

        if consistency_score < 0.55:
            blockers.append("character consistency score below minimum learning registration threshold")

        if genericity_risk > 0.8:
            blockers.append("character genericity risk too high")

        if world_validation.get("world_contract_valid") is False:
            blockers.append("character violates world contract")

        if chunk4_handoff.get("handoff_ready") is False:
            blockers.append("character missing too many Chunk 4 handoff sections")

        can_register = len(blockers) == 0

        can_enqueue_training = (
            can_register
            and training_eligibility.get("training_eligible") is True
            and training_eligibility.get("do_not_train") is not True
            and training_eligibility.get("human_review_required") is not True
            and quality_score >= 0.78
            and originality_score >= 0.65
            and consistency_score >= 0.7
            and genericity_risk <= 0.5
        )

        return {
            "can_register_learning": can_register,
            "can_enqueue_training": can_enqueue_training,
            "quality_score": round(quality_score, 3),
            "originality_score": round(originality_score, 3),
            "consistency_score": round(consistency_score, 3),
            "genericity_risk": round(genericity_risk, 3),
            "source_allowed": source_allowed,
            "world_contract_valid": world_validation.get("world_contract_valid", True),
            "chunk4_handoff_ready": chunk4_handoff.get("handoff_ready", False),
            "blockers": blockers,
            "recommendation": "register_character_learning" if can_register else "human_review_character_output",
        }

    def _synthesize_character_learning_metadata(
        self,
        *,
        result_payload: Dict[str, Any],
        character_id: str,
        project_id: str,
        universe_id: str,
        character_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        engine_name = result_payload.get("engine_name", "character.unknown_engine")
        target_object_type = self._infer_character_target_type(result_payload, character_profile)

        quality_score = float(self._extract_quality_score(character_profile) or 0.78)
        originality_score = float(self._extract_originality_score(character_profile) or 0.72)
        consistency_score = float(self._extract_consistency_score(character_profile) or 0.78)
        genericity_risk = float(self._extract_genericity_risk(character_profile) or 0.25)

        training_eligible = (
            quality_score >= 0.78
            and originality_score >= 0.65
            and consistency_score >= 0.7
            and genericity_risk <= 0.5
        )

        ontology_record = {
            "ontology_id": f"ont_character_{uuid4().hex[:12]}",
            "ontology_type": target_object_type,
            "name": self._extract_character_name(character_profile),
            "family": "character_intelligence",
            "subtype": target_object_type,
            "description": "Synthesized character learning ontology record from character engine output.",
            "axes": {
                "character_id": character_id,
                "project_id": project_id,
                "universe_id": universe_id,
            },
            "tags": ["character", target_object_type, universe_id],
            "examples": [self._extract_character_name(character_profile)],
            "counterexamples": [],
            "confidence_score": consistency_score,
            "novelty_score": originality_score,
            "quality_score": quality_score,
            "learned_from_data": False,
            "generated_by_engine": engine_name,
        }

        type_candidate = {
            "registry_id": f"type_character_{uuid4().hex[:12]}",
            "type_name": f"character_intelligence:{target_object_type}",
            "type_family": "character_intelligence",
            "type_subfamily": target_object_type,
            "type_scope": "character_generation",
            "ontology_ids": [ontology_record["ontology_id"]],
            "reusable_prompt_tags": ["character", target_object_type, universe_id],
            "generation_constraints": [
                "preserve world grounding",
                "preserve character psychology and agency",
                "preserve dialogue voice and relationship readiness",
                "do not train on unapproved sources",
                "preserve originality and consistency gates",
            ],
            "counter_patterns": ["generic archetype without wound/goal/world grounding"],
            "learned_axes": {
                "character_id": character_id,
                "chunk4_handoff_required": True,
            },
        }

        provenance_record = {
            "provenance_id": f"prov_character_{uuid4().hex[:12]}",
            "source_name": "human_approved_synthetic",
            "source_type": "synthetic_or_user_generated",
            "dataset_family": target_object_type,
            "usage_allowed": True,
            "human_review_required": False,
            "license_name": "user_owned_or_project_generated",
            "genre_tags": character_profile.get("genre_tags", []),
            "culture_tags": character_profile.get("culture_tags", []),
        }

        embedding_metadata = {
            "embedding_id": f"emb_character_{uuid4().hex[:12]}",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["character", target_object_type, universe_id, self._extract_character_name(character_profile)],
            "retrieval_queries": [
                f"{target_object_type} character profile {universe_id}",
                "character psychology memory dialogue relationship readiness world grounding",
                "character originality quality consistency training candidate",
            ],
            "nearest_neighbor_placeholders": [],
            "novelty_score": originality_score,
            "originality_score": originality_score,
            "similarity_threshold_used": 0.82,
            "vector_computed": False,
        }

        training_eligibility = {
            "training_eligible": training_eligible,
            "human_review_required": not training_eligible,
            "do_not_train": not training_eligible,
            "recommended_split": "train" if training_eligible else "human_review_queue",
            "quality_score": quality_score,
            "consistency_score": consistency_score,
            "originality_score": originality_score,
            "safety_score": 0.88 if training_eligible else 0.72,
            "rejection_reasons": [] if training_eligible else ["character output did not meet synthesized training thresholds"],
        }

        return {
            "learning_metadata_id": f"learn_character_{uuid4().hex[:12]}",
            "engine_name": engine_name,
            "target_object_id": character_id,
            "target_object_type": target_object_type,
            "ontology_records": [ontology_record],
            "learned_type_candidates": [type_candidate],
            "provenance_records": [provenance_record],
            "embedding_metadata": embedding_metadata,
            "training_eligibility": training_eligibility,
            "retrieval_context_used": embedding_metadata["retrieval_queries"],
            "generated_training_labels": {
                "character_id": character_id,
                "target_object_type": target_object_type,
                "quality_score": quality_score,
                "originality_score": originality_score,
                "consistency_score": consistency_score,
                "genericity_risk": genericity_risk,
                "chunk4_ready": True,
                "chunk8_ready_later": training_eligible,
            },
            "learning_notes": [
                "Synthesized by CharacterLearningAdapter because engine output did not include complete learning metadata.",
                "Future character engines should emit full EngineLearningMetadata directly.",
                "This record prepares character outputs for future RAG, embeddings, and training governance.",
            ],
        }

    def _extract_character_profile(self, data: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        for key in [
            "character_full_profile",
            "character_bible",
            "character_profile",
            "profile",
            "character",
            "character_output",
        ]:
            if isinstance(data.get(key), dict):
                return data[key]

        if isinstance(fallback, dict):
            for key in [
                "character_full_profile",
                "character_bible",
                "character_profile",
                "profile",
                "character",
                "character_output",
            ]:
                if isinstance(fallback.get(key), dict):
                    return fallback[key]

        return data if isinstance(data, dict) else {}

    def _extract_character_id(self, *objects: Dict[str, Any]) -> str:
        for obj in objects:
            if not isinstance(obj, dict):
                continue

            for key in ["character_id", "id"]:
                if obj.get(key):
                    return str(obj[key])

            for nested_key in ["identity", "character_identity", "character_seed", "profile"]:
                nested = obj.get(nested_key)
                if isinstance(nested, dict):
                    for key in ["character_id", "id", "name"]:
                        if nested.get(key):
                            return str(nested[key])

        return f"char_{uuid4().hex[:12]}"

    def _extract_character_name(self, profile: Dict[str, Any]) -> str:
        flat = self._flatten_character(profile)
        return str(flat.get("name") or flat.get("character_name") or flat.get("character_id") or "Unnamed Character")

    def _infer_character_target_type(self, result_payload: Dict[str, Any], character_profile: Dict[str, Any]) -> str:
        engine_name = result_payload.get("engine_name", "").lower()

        if "bible" in engine_name:
            return "character_bible"
        if "orchestrator" in engine_name or "full_profile" in engine_name:
            return "character_full_profile"
        if "quality" in engine_name:
            return "character_quality"
        if "originality" in engine_name:
            return "character_originality_profile"
        if "dialogue" in engine_name:
            return "character_dialogue_voice"
        if "relationship" in engine_name:
            return "character_relationship_readiness"
        if character_profile.get("character_full_profile") or character_profile.get("identity"):
            return "character_full_profile"
        return "character_profile"

    def _source_allowed(self, learning_metadata: Dict[str, Any]) -> bool:
        provenance_records = learning_metadata.get("provenance_records", []) or []

        if not provenance_records:
            return True

        return any(
            record.get("usage_allowed") is True and record.get("human_review_required") is not True
            for record in provenance_records
        )

    def _extract_quality_score(self, profile: Dict[str, Any]) -> Optional[float]:
        quality = self._extract_nested(profile, ["validation", "quality_report"]) or profile.get("quality_report", {})
        if isinstance(quality, dict):
            return quality.get("overall_quality_score") or quality.get("quality_score")
        return profile.get("quality_score")

    def _extract_originality_score(self, profile: Dict[str, Any]) -> Optional[float]:
        originality = self._extract_nested(profile, ["validation", "originality_report"]) or profile.get("originality_report", {})
        if isinstance(originality, dict):
            return originality.get("overall_originality_score") or originality.get("originality_score") or originality.get("novelty_score")
        return profile.get("originality_score")

    def _extract_consistency_score(self, profile: Dict[str, Any]) -> Optional[float]:
        consistency = self._extract_nested(profile, ["validation", "consistency_report"]) or profile.get("consistency_report", {})
        if isinstance(consistency, dict):
            return consistency.get("overall_consistency_score") or consistency.get("consistency_score")
        return profile.get("consistency_score")

    def _extract_genericity_risk(self, profile: Dict[str, Any]) -> Optional[float]:
        anti_genericity = self._extract_nested(profile, ["validation", "anti_genericity_report"]) or profile.get("anti_genericity_report", {})
        if isinstance(anti_genericity, dict):
            return anti_genericity.get("genericity_risk_score")
        return profile.get("genericity_risk_score")

    def _extract_nested(self, data: Dict[str, Any], path: List[str]) -> Any:
        current: Any = data
        for key in path:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current

    def _flatten_character(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key not in flat and not isinstance(item, (dict, list)):
                        flat[key] = item
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(profile)
        return flat

    def _stringify_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, dict):
            return [str(item) for item in value.values()]
        return [str(value)]
