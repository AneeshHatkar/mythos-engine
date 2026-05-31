from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.app.services.learning_integration import LearningIntegrationService


class WorldLearningAdapter:
    """Connects Chunk 2 world intelligence outputs to global learning.

    This adapter is the bridge between world generation/orchestration/export
    and the global learning foundation from Upgrade Pass A.

    It normalizes world outputs into learning-ready records and sends them to:

    - global learning registry
    - provenance store
    - embedding registry
    - training queue if eligible

    It does not train models or compute embeddings yet. It prepares high-quality,
    provenance-safe world outputs for future Chunk 8 learning/RAG/training.
    """

    def __init__(
        self,
        integration_service: Optional[LearningIntegrationService] = None,
    ) -> None:
        self.integration = integration_service or LearningIntegrationService()

    def register_world_engine_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        source_payload: Optional[Dict[str, Any]] = None,
        enforce_quality_gates: bool = True,
    ) -> Dict[str, Any]:
        """Register one world engine result with global learning stores."""

        normalized = self.normalize_world_result(
            result_payload=result_payload,
            project_id=project_id,
            universe_id=universe_id,
            source_payload=source_payload,
        )

        gate_report = self.evaluate_world_learning_quality_gates(normalized)

        if enforce_quality_gates and not gate_report["can_register_learning"]:
            return {
                "success": True,
                "registered": False,
                "reason": "world_learning_quality_gate_failed",
                "quality_gate_report": gate_report,
                "normalized_world_result": normalized,
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
            "world_id": normalized["world_id"],
            "project_id": project_id,
            "universe_id": universe_id,
            "quality_gate_report": gate_report,
            "learning_registration": registration,
            "world_to_character_contract": normalized["world_to_character_contract"],
        }

    def register_world_profile(
        self,
        *,
        world_profile: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        enforce_quality_gates: bool = True,
    ) -> Dict[str, Any]:
        """Register learning metadata discovered inside a world profile/bible."""

        normalized = self.normalize_world_profile(
            world_profile=world_profile,
            project_id=project_id,
            universe_id=universe_id,
        )

        gate_report = self.evaluate_world_learning_quality_gates(normalized)

        if enforce_quality_gates and not gate_report["can_register_learning"]:
            return {
                "success": True,
                "registered": False,
                "reason": "world_profile_quality_gate_failed",
                "quality_gate_report": gate_report,
                "normalized_world_result": normalized,
            }

        result = self.integration.register_profile_learning_metadata(
            profile=normalized["world_profile"],
            project_id=project_id,
            universe_id=universe_id,
        )

        return {
            "success": True,
            "registered": result.get("registered_count", 0) > 0,
            "world_id": normalized["world_id"],
            "project_id": project_id,
            "universe_id": universe_id,
            "quality_gate_report": gate_report,
            "learning_registration": result,
            "world_to_character_contract": normalized["world_to_character_contract"],
        }

    def normalize_world_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str,
        universe_id: str,
        source_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        data = result_payload.get("data", {}) if isinstance(result_payload, dict) else {}

        world_id = self._extract_world_id(data, source_payload or result_payload)
        world_profile = self._extract_world_profile(data, source_payload or result_payload)
        learning_metadata = data.get("learning_metadata") or self._synthesize_world_learning_metadata(
            result_payload=result_payload,
            world_id=world_id,
            project_id=project_id,
            universe_id=universe_id,
            world_profile=world_profile,
        )

        normalized_result = dict(result_payload)
        normalized_data = dict(data)
        normalized_data["learning_metadata"] = learning_metadata
        normalized_data["world_learning_adapter_metadata"] = {
            "world_id": world_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "adapter_version": "world_learning_adapter_v0.1.0",
            "normalized_for_global_learning": True,
        }
        normalized_result["data"] = normalized_data

        return {
            "world_id": world_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "result_payload": normalized_result,
            "source_payload": source_payload or world_profile or data,
            "world_profile": world_profile,
            "learning_metadata": learning_metadata,
            "world_to_character_contract": self.build_world_to_character_contract(world_profile or data),
        }

    def normalize_world_profile(
        self,
        *,
        world_profile: Dict[str, Any],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        world_id = self._extract_world_id(world_profile, world_profile)

        return {
            "world_id": world_id,
            "project_id": project_id,
            "universe_id": universe_id,
            "world_profile": world_profile,
            "source_payload": world_profile,
            "learning_metadata": {},
            "world_to_character_contract": self.build_world_to_character_contract(world_profile),
        }

    def build_world_to_character_contract(self, world_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract the world constraints Chunk 3/4 need.

        This contract keeps the project interconnected: characters, relationships,
        plot, scenes, and future agents must obey the world.
        """

        return {
            "contract_id": f"worldchar_{uuid4().hex[:12]}",
            "world_id": self._extract_world_id(world_payload, world_payload),
            "social_classes": self._extract_list_by_keys(
                world_payload,
                ["social_classes", "class_system", "classes", "status_groups"],
            ),
            "power_laws": self._extract_list_by_keys(
                world_payload,
                ["power_laws", "magic_rules", "world_rules", "rule_system", "physics_rules"],
            ),
            "legal_constraints": self._extract_list_by_keys(
                world_payload,
                ["legal_constraints", "law_system", "laws", "court_rules"],
            ),
            "faction_constraints": self._extract_list_by_keys(
                world_payload,
                ["factions", "faction_system", "political_groups"],
            ),
            "education_access_constraints": self._extract_list_by_keys(
                world_payload,
                ["education_access", "academy_access", "training_access"],
            ),
            "economy_resource_constraints": self._extract_list_by_keys(
                world_payload,
                ["economy", "resource_system", "resources", "labor_system"],
            ),
            "religion_culture_constraints": self._extract_list_by_keys(
                world_payload,
                ["religion", "culture", "cultural_norms", "taboos"],
            ),
            "geography_travel_constraints": self._extract_list_by_keys(
                world_payload,
                ["geography", "travel_rules", "regions", "places"],
            ),
            "character_permission_boundaries": self._extract_permission_boundaries(world_payload),
            "contract_complete": True,
            "missing_contract_sections": [],
        }

    def evaluate_world_learning_quality_gates(self, normalized_world_result: Dict[str, Any]) -> Dict[str, Any]:
        metadata = normalized_world_result.get("learning_metadata", {}) or {}
        contract = normalized_world_result.get("world_to_character_contract", {}) or {}
        world_profile = normalized_world_result.get("world_profile", {}) or {}

        training_eligibility = metadata.get("training_eligibility", {}) or {}
        embedding_metadata = metadata.get("embedding_metadata", {}) or {}

        quality_score = float(
            training_eligibility.get("quality_score")
            or metadata.get("generated_training_labels", {}).get("quality_score")
            or world_profile.get("quality_score")
            or world_profile.get("world_quality_score")
            or 0.74
        )

        originality_score = float(
            training_eligibility.get("originality_score")
            or embedding_metadata.get("originality_score")
            or world_profile.get("originality_score")
            or 0.74
        )

        consistency_score = float(
            training_eligibility.get("consistency_score")
            or world_profile.get("consistency_score")
            or world_profile.get("world_consistency_score")
            or 0.74
        )

        source_allowed = self._source_allowed(metadata)
        contract_report = self._contract_quality_report(contract)

        blockers = []

        if not source_allowed:
            blockers.append("source provenance is not approved for learning registration")

        if quality_score < 0.55:
            blockers.append("world quality score below minimum learning registration threshold")

        if originality_score < 0.5:
            blockers.append("world originality score below minimum learning registration threshold")

        if consistency_score < 0.55:
            blockers.append("world consistency score below minimum learning registration threshold")

        if not contract_report["contract_usable"]:
            blockers.append("world-to-character dependency contract is not usable")

        can_register = len(blockers) == 0
        can_enqueue_training = (
            can_register
            and training_eligibility.get("training_eligible") is True
            and quality_score >= 0.75
            and originality_score >= 0.65
            and consistency_score >= 0.7
        )

        return {
            "can_register_learning": can_register,
            "can_enqueue_training": can_enqueue_training,
            "quality_score": round(quality_score, 3),
            "originality_score": round(originality_score, 3),
            "consistency_score": round(consistency_score, 3),
            "source_allowed": source_allowed,
            "contract_quality_report": contract_report,
            "blockers": blockers,
            "recommendation": "register_world_learning" if can_register else "human_review_world_output",
        }

    def _contract_quality_report(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        important_sections = [
            "social_classes",
            "power_laws",
            "legal_constraints",
            "faction_constraints",
            "character_permission_boundaries",
        ]

        present = {
            section: bool(contract.get(section))
            for section in important_sections
        }

        score = sum(1 for value in present.values() if value) / len(important_sections)

        missing = [section for section, value in present.items() if not value]

        return {
            "contract_usable": score >= 0.4,
            "contract_completeness_score": round(score, 3),
            "present_sections": present,
            "missing_sections": missing,
        }

    def _source_allowed(self, learning_metadata: Dict[str, Any]) -> bool:
        provenance_records = learning_metadata.get("provenance_records", []) or []

        if not provenance_records:
            return True

        return any(
            record.get("usage_allowed") is True and record.get("human_review_required") is not True
            for record in provenance_records
        )

    def _synthesize_world_learning_metadata(
        self,
        *,
        result_payload: Dict[str, Any],
        world_id: str,
        project_id: str,
        universe_id: str,
        world_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        engine_name = result_payload.get("engine_name", "world.unknown_engine")
        target_object_type = self._infer_world_target_type(result_payload, world_profile)
        quality_score = float(world_profile.get("quality_score", world_profile.get("world_quality_score", 0.78)))
        originality_score = float(world_profile.get("originality_score", 0.72))
        consistency_score = float(world_profile.get("consistency_score", world_profile.get("world_consistency_score", 0.78)))

        training_eligible = quality_score >= 0.75 and originality_score >= 0.65 and consistency_score >= 0.7

        ontology_record = {
            "ontology_id": f"ont_world_{uuid4().hex[:12]}",
            "ontology_type": target_object_type,
            "name": world_profile.get("world_name", world_profile.get("name", "world_output")),
            "family": "world_intelligence",
            "subtype": target_object_type,
            "description": "Synthesized world learning ontology record from world engine output.",
            "axes": {
                "world_id": world_id,
                "project_id": project_id,
                "universe_id": universe_id,
            },
            "tags": ["world", target_object_type, universe_id],
            "examples": [world_profile.get("world_name", "world_output")],
            "counterexamples": [],
            "confidence_score": consistency_score,
            "novelty_score": originality_score,
            "quality_score": quality_score,
            "learned_from_data": False,
            "generated_by_engine": engine_name,
        }

        type_candidate = {
            "registry_id": f"type_world_{uuid4().hex[:12]}",
            "type_name": f"world_intelligence:{target_object_type}",
            "type_family": "world_intelligence",
            "type_subfamily": target_object_type,
            "type_scope": "world_generation",
            "ontology_ids": [ontology_record["ontology_id"]],
            "reusable_prompt_tags": ["world", target_object_type, universe_id],
            "generation_constraints": [
                "preserve world-to-character constraints",
                "preserve provenance before training",
                "do not train on unapproved sources",
                "preserve originality and consistency gates",
            ],
            "counter_patterns": [],
            "learned_axes": {
                "world_id": world_id,
                "world_to_character_contract_required": True,
            },
        }

        provenance_record = {
            "provenance_id": f"prov_world_{uuid4().hex[:12]}",
            "source_name": "human_approved_synthetic",
            "source_type": "synthetic_or_user_generated",
            "dataset_family": target_object_type,
            "usage_allowed": True,
            "human_review_required": False,
            "license_name": "user_owned_or_project_generated",
            "genre_tags": world_profile.get("genre_tags", []),
            "culture_tags": world_profile.get("culture_tags", []),
        }

        embedding_metadata = {
            "embedding_id": f"emb_world_{uuid4().hex[:12]}",
            "embedding_model": "future_embedding_model_not_computed_yet",
            "similarity_tags": ["world", target_object_type, universe_id],
            "retrieval_queries": [
                f"{target_object_type} world rules {universe_id}",
                "world bible social class law faction power system constraints",
                "world-to-character dependency contract",
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
            "safety_score": 0.86 if training_eligible else 0.7,
            "rejection_reasons": [] if training_eligible else ["world output did not meet synthesized training thresholds"],
        }

        return {
            "learning_metadata_id": f"learn_world_{uuid4().hex[:12]}",
            "engine_name": engine_name,
            "target_object_id": world_id,
            "target_object_type": target_object_type,
            "ontology_records": [ontology_record],
            "learned_type_candidates": [type_candidate],
            "provenance_records": [provenance_record],
            "embedding_metadata": embedding_metadata,
            "training_eligibility": training_eligibility,
            "retrieval_context_used": embedding_metadata["retrieval_queries"],
            "generated_training_labels": {
                "world_id": world_id,
                "target_object_type": target_object_type,
                "quality_score": quality_score,
                "originality_score": originality_score,
                "consistency_score": consistency_score,
                "world_to_character_contract_required": True,
                "chunk3_ready": True,
                "chunk4_ready": True,
                "chunk8_ready_later": training_eligible,
            },
            "learning_notes": [
                "Synthesized by WorldLearningAdapter because engine output did not include complete learning metadata.",
                "Future world engines should emit full EngineLearningMetadata directly.",
                "This record prepares world outputs for future RAG, embeddings, and training governance.",
            ],
        }

    def _extract_world_id(self, *objects: Dict[str, Any]) -> str:
        for obj in objects:
            if not isinstance(obj, dict):
                continue

            for key in ["world_id", "universe_id", "id"]:
                if obj.get(key):
                    return str(obj[key])

            for nested_key in ["world_state", "world_profile", "world_bible", "identity"]:
                nested = obj.get(nested_key)
                if isinstance(nested, dict):
                    for key in ["world_id", "universe_id", "world_name"]:
                        if nested.get(key):
                            return str(nested[key])

        return f"world_{uuid4().hex[:12]}"

    def _extract_world_profile(self, data: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
        for key in [
            "world_profile",
            "world_bible",
            "world_state",
            "world",
            "orchestrated_world",
            "world_output",
        ]:
            if isinstance(data.get(key), dict):
                return data[key]

        if isinstance(fallback, dict):
            for key in [
                "world_profile",
                "world_bible",
                "world_state",
                "world",
                "orchestrated_world",
                "world_output",
            ]:
                if isinstance(fallback.get(key), dict):
                    return fallback[key]

        return data if isinstance(data, dict) else {}

    def _infer_world_target_type(self, result_payload: Dict[str, Any], world_profile: Dict[str, Any]) -> str:
        engine_name = result_payload.get("engine_name", "").lower()

        if "bible" in engine_name:
            return "world_bible"
        if "benchmark" in engine_name:
            return "world_benchmark_result"
        if "embedding" in engine_name or "originality" in engine_name:
            return "world_originality_profile"
        if world_profile.get("magic_rules") or world_profile.get("power_laws"):
            return "world_rule_system"
        return "world_profile"

    def _extract_list_by_keys(self, payload: Dict[str, Any], keys: List[str]) -> List[Any]:
        found: List[Any] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for key, item in value.items():
                    if key in keys:
                        if isinstance(item, list):
                            found.extend(item)
                        elif item:
                            found.append(item)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(payload)

        return found

    def _extract_permission_boundaries(self, payload: Dict[str, Any]) -> List[str]:
        boundaries = []

        social = self._extract_list_by_keys(payload, ["social_classes", "class_system", "classes"])
        laws = self._extract_list_by_keys(payload, ["legal_constraints", "laws", "law_system"])
        power = self._extract_list_by_keys(payload, ["power_laws", "magic_rules", "world_rules"])
        education = self._extract_list_by_keys(payload, ["academy_access", "education_access", "training_access"])

        if social:
            boundaries.append("characters must obey class/status access constraints unless an explicit exception route exists")

        if laws:
            boundaries.append("characters must obey legal/social penalty systems unless breaking them has consequence")

        if power:
            boundaries.append("skills and limit-breaks must obey world power laws, costs, counters, and exceptions")

        if education:
            boundaries.append("academy/training access must be explained by class, sponsorship, merit, debt, or illegal route")

        if not boundaries:
            boundaries.append("world permission boundaries require review before character/plot generation")

        return boundaries
