from typing import Any, Dict, List

from backend.app.services.character_learning_adapter import CharacterLearningAdapter


class CharacterLearningMetadataVerifier:
    """Verifies that Chunk 3 character outputs are global-learning ready.

    This verifier checks character engine/full-profile/bible outputs for the
    metadata required by Upgrade Pass C and future Chunk 8 learning.

    If metadata is missing, it can synthesize adapter-normalized learning
    metadata through CharacterLearningAdapter.
    """

    REQUIRED_METADATA_KEYS = [
        "engine_name",
        "target_object_id",
        "target_object_type",
        "ontology_records",
        "learned_type_candidates",
        "provenance_records",
        "embedding_metadata",
        "training_eligibility",
        "generated_training_labels",
    ]

    REQUIRED_TRAINING_KEYS = [
        "training_eligible",
        "human_review_required",
        "do_not_train",
        "recommended_split",
        "quality_score",
        "consistency_score",
        "originality_score",
        "safety_score",
    ]

    REQUIRED_EMBEDDING_KEYS = [
        "embedding_model",
        "similarity_tags",
        "retrieval_queries",
        "novelty_score",
        "originality_score",
        "similarity_threshold_used",
    ]

    def __init__(self, adapter: CharacterLearningAdapter | None = None) -> None:
        self.adapter = adapter or CharacterLearningAdapter()

    def verify_character_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        world_contract: Dict[str, Any] | None = None,
        allow_synthesis: bool = True,
    ) -> Dict[str, Any]:
        data = result_payload.get("data", {}) if isinstance(result_payload, dict) else {}
        existing_metadata = data.get("learning_metadata")

        if existing_metadata:
            metadata = existing_metadata
            synthesized = False
            normalized = self.adapter.normalize_character_result(
                result_payload=result_payload,
                project_id=project_id,
                universe_id=universe_id,
                world_contract=world_contract or {},
            )
        elif allow_synthesis:
            normalized = self.adapter.normalize_character_result(
                result_payload=result_payload,
                project_id=project_id,
                universe_id=universe_id,
                world_contract=world_contract or {},
            )
            metadata = normalized["learning_metadata"]
            synthesized = True
        else:
            normalized = {
                "character_id": "unknown_character",
                "character_profile": {},
                "world_contract_validation": {
                    "world_contract_checked": False,
                    "world_contract_valid": True,
                    "compatibility_score": 0.0,
                },
                "chunk4_handoff_contract": {
                    "handoff_ready": False,
                    "missing_sections": [],
                },
            }
            metadata = {}
            synthesized = False

        metadata_report = self._metadata_completeness_report(metadata)
        ontology_report = self._ontology_report(metadata)
        provenance_report = self._provenance_report(metadata)
        embedding_report = self._embedding_report(metadata)
        training_report = self._training_report(metadata)
        character_depth_report = self._character_depth_report(normalized.get("character_profile", {}))
        world_contract_report = normalized.get("world_contract_validation", {})
        chunk4_report = self._chunk4_report(normalized.get("chunk4_handoff_contract", {}))

        readiness = self._readiness_report(
            metadata_report=metadata_report,
            ontology_report=ontology_report,
            provenance_report=provenance_report,
            embedding_report=embedding_report,
            training_report=training_report,
            character_depth_report=character_depth_report,
            world_contract_report=world_contract_report,
            chunk4_report=chunk4_report,
        )

        return {
            "success": True,
            "character_id": normalized.get("character_id"),
            "engine_name": result_payload.get("engine_name", metadata.get("engine_name", "unknown_engine")),
            "metadata_synthesized": synthesized,
            "metadata_present": bool(existing_metadata),
            "metadata_completeness_report": metadata_report,
            "ontology_report": ontology_report,
            "provenance_report": provenance_report,
            "embedding_report": embedding_report,
            "training_report": training_report,
            "character_depth_report": character_depth_report,
            "world_contract_report": world_contract_report,
            "chunk4_handoff_report": chunk4_report,
            "readiness_report": readiness,
            "normalized_result_payload": normalized.get("result_payload", result_payload),
        }

    def verify_character_profile(
        self,
        *,
        character_profile: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        world_contract: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        normalized = self.adapter.normalize_character_profile(
            character_profile=character_profile,
            project_id=project_id,
            universe_id=universe_id,
            world_contract=world_contract or {},
        )

        metadata_records = self.adapter.integration.extract_learning_metadata_from_profile(
            normalized.get("profile_wrapper") or character_profile
        )

        metadata_ready_reports = []
        for metadata in metadata_records:
            metadata_ready_reports.append(
                {
                    "learning_metadata_id": metadata.get("learning_metadata_id"),
                    "metadata_completeness_report": self._metadata_completeness_report(metadata),
                    "ontology_report": self._ontology_report(metadata),
                    "provenance_report": self._provenance_report(metadata),
                    "embedding_report": self._embedding_report(metadata),
                    "training_report": self._training_report(metadata),
                }
            )

        character_depth_report = self._character_depth_report(normalized.get("character_profile", {}))
        chunk4_report = self._chunk4_report(normalized.get("chunk4_handoff_contract", {}))
        world_contract_report = normalized.get("world_contract_validation", {})

        profile_ready = (
            character_depth_report["character_depth_ready"]
            and chunk4_report["chunk4_ready"]
            and world_contract_report.get("world_contract_valid", True)
        )

        return {
            "success": True,
            "character_id": normalized["character_id"],
            "metadata_found": len(metadata_records),
            "metadata_ready_reports": metadata_ready_reports,
            "character_depth_report": character_depth_report,
            "world_contract_report": world_contract_report,
            "chunk4_handoff_report": chunk4_report,
            "profile_learning_ready": profile_ready,
        }

    def verify_many_character_results(
        self,
        *,
        result_payloads: List[Dict[str, Any]],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        world_contract: Dict[str, Any] | None = None,
        allow_synthesis: bool = True,
    ) -> Dict[str, Any]:
        reports = [
            self.verify_character_result(
                result_payload=result,
                project_id=project_id,
                universe_id=universe_id,
                world_contract=world_contract or {},
                allow_synthesis=allow_synthesis,
            )
            for result in result_payloads
        ]

        return {
            "success": True,
            "checked_count": len(reports),
            "global_learning_ready_count": sum(1 for item in reports if item["readiness_report"]["global_learning_ready"]),
            "training_ready_count": sum(1 for item in reports if item["readiness_report"]["training_queue_ready"]),
            "chunk4_ready_count": sum(1 for item in reports if item["readiness_report"]["chunk4_ready"]),
            "synthesized_count": sum(1 for item in reports if item["metadata_synthesized"]),
            "reports": reports,
        }

    def _metadata_completeness_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        missing = [key for key in self.REQUIRED_METADATA_KEYS if key not in metadata or metadata.get(key) in [None, "", [], {}]]
        present = [key for key in self.REQUIRED_METADATA_KEYS if key not in missing]
        score = len(present) / len(self.REQUIRED_METADATA_KEYS)

        return {
            "complete": not missing,
            "completeness_score": round(score, 3),
            "present_keys": present,
            "missing_keys": missing,
        }

    def _ontology_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        ontology = metadata.get("ontology_records", []) or []
        type_candidates = metadata.get("learned_type_candidates", []) or []

        ontology_valid = all(
            isinstance(item, dict)
            and item.get("ontology_type")
            and item.get("family")
            and item.get("generated_by_engine")
            for item in ontology
        )

        type_valid = all(
            isinstance(item, dict)
            and item.get("type_name")
            and item.get("type_family")
            for item in type_candidates
        )

        return {
            "ontology_count": len(ontology),
            "type_candidate_count": len(type_candidates),
            "ontology_valid": ontology_valid and bool(ontology),
            "type_candidates_valid": type_valid and bool(type_candidates),
            "character_ontology_ready": bool(ontology) and bool(type_candidates) and ontology_valid and type_valid,
        }

    def _provenance_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        records = metadata.get("provenance_records", []) or []

        approved = [
            item for item in records
            if item.get("usage_allowed") is True and item.get("human_review_required") is not True
        ]

        blocked = [
            item for item in records
            if item.get("usage_allowed") is not True or item.get("do_not_train") is True
        ]

        return {
            "provenance_count": len(records),
            "approved_source_count": len(approved),
            "blocked_source_count": len(blocked),
            "provenance_ready": len(approved) > 0,
            "training_source_allowed": len(approved) > 0 and len(blocked) == 0,
        }

    def _embedding_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        embedding = metadata.get("embedding_metadata", {}) or {}
        missing = [key for key in self.REQUIRED_EMBEDDING_KEYS if key not in embedding or embedding.get(key) in [None, "", [], {}]]
        present = [key for key in self.REQUIRED_EMBEDDING_KEYS if key not in missing]

        return {
            "embedding_metadata_present": bool(embedding),
            "embedding_metadata_complete": bool(embedding) and not missing,
            "present_keys": present,
            "missing_keys": missing,
            "similarity_tags": embedding.get("similarity_tags", []),
            "retrieval_queries": embedding.get("retrieval_queries", []),
            "originality_score": float(embedding.get("originality_score", 0.0)),
            "future_vectorization_ready": bool(embedding) and bool(embedding.get("similarity_tags") or embedding.get("retrieval_queries")),
        }

    def _training_report(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        training = metadata.get("training_eligibility", {}) or {}
        missing = [key for key in self.REQUIRED_TRAINING_KEYS if key not in training]
        present = [key for key in self.REQUIRED_TRAINING_KEYS if key not in missing]

        return {
            "training_metadata_present": bool(training),
            "training_metadata_complete": bool(training) and not missing,
            "present_keys": present,
            "missing_keys": missing,
            "training_eligible": training.get("training_eligible") is True,
            "do_not_train": training.get("do_not_train") is True,
            "human_review_required": training.get("human_review_required") is True,
            "quality_score": float(training.get("quality_score", 0.0)),
            "consistency_score": float(training.get("consistency_score", 0.0)),
            "originality_score": float(training.get("originality_score", 0.0)),
            "recommended_split": training.get("recommended_split", "unknown"),
        }

    def _character_depth_report(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        flat = self._flatten(profile)

        axes = {
            "identity": bool(flat.get("character_id") or flat.get("name")),
            "world_grounding": bool(flat.get("social_class") or flat.get("origin_location") or flat.get("family_name_status")),
            "psychology": bool(flat.get("core_wound") or flat.get("psychology_profile")),
            "goals": bool(flat.get("surface_goal") or flat.get("hidden_goal") or flat.get("true_need")),
            "memory": bool(flat.get("memory_id") or flat.get("memory_records")),
            "skill_power": bool(flat.get("skill_family") or flat.get("primary_skill")),
            "relationship_readiness": bool(flat.get("relationship_readiness_family") or flat.get("relationship_readiness_profile")),
            "dialogue_voice": bool(flat.get("voice_family") or flat.get("dialogue_voice_profile")),
        }

        score = sum(1 for value in axes.values() if value) / len(axes)
        missing = [key for key, value in axes.items() if not value]

        return {
            "character_depth_ready": score >= 0.7,
            "depth_score": round(score, 3),
            "axes": axes,
            "missing_axes": missing,
        }

    def _chunk4_report(self, handoff: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "chunk4_ready": handoff.get("handoff_ready") is True,
            "missing_sections": handoff.get("missing_sections", []),
            "has_relationship_readiness": bool(handoff.get("relationship_readiness")),
            "has_dialogue_voice": bool(handoff.get("dialogue_voice")),
            "has_psychology": bool(handoff.get("psychology")),
            "has_memory_records": bool(handoff.get("memory_records")),
        }

    def _readiness_report(
        self,
        *,
        metadata_report: Dict[str, Any],
        ontology_report: Dict[str, Any],
        provenance_report: Dict[str, Any],
        embedding_report: Dict[str, Any],
        training_report: Dict[str, Any],
        character_depth_report: Dict[str, Any],
        world_contract_report: Dict[str, Any],
        chunk4_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        world_valid = world_contract_report.get("world_contract_valid", True)

        global_ready = (
            metadata_report["completeness_score"] >= 0.85
            and ontology_report["character_ontology_ready"]
            and provenance_report["provenance_ready"]
            and embedding_report["future_vectorization_ready"]
            and character_depth_report["character_depth_ready"]
            and world_valid
            and chunk4_report["chunk4_ready"]
        )

        training_ready = (
            global_ready
            and training_report["training_metadata_complete"]
            and training_report["training_eligible"]
            and not training_report["do_not_train"]
            and not training_report["human_review_required"]
            and training_report["quality_score"] >= 0.78
            and training_report["consistency_score"] >= 0.7
            and training_report["originality_score"] >= 0.65
        )

        blockers = []

        if not metadata_report["complete"]:
            blockers.append("metadata incomplete")
        if not ontology_report["character_ontology_ready"]:
            blockers.append("character ontology/type metadata not ready")
        if not provenance_report["provenance_ready"]:
            blockers.append("approved provenance missing")
        if not embedding_report["future_vectorization_ready"]:
            blockers.append("embedding metadata not vectorization-ready")
        if not character_depth_report["character_depth_ready"]:
            blockers.append("character depth axes incomplete")
        if not world_valid:
            blockers.append("character violates world contract")
        if not chunk4_report["chunk4_ready"]:
            blockers.append("Chunk 4 handoff incomplete")
        if training_report["do_not_train"]:
            blockers.append("training eligibility says do_not_train")
        if training_report["human_review_required"]:
            blockers.append("human review required before training")
        if training_report["quality_score"] < 0.78:
            blockers.append("quality below training threshold")
        if training_report["consistency_score"] < 0.7:
            blockers.append("consistency below training threshold")
        if training_report["originality_score"] < 0.65:
            blockers.append("originality below training threshold")

        return {
            "global_learning_ready": global_ready,
            "training_queue_ready": training_ready,
            "chunk4_ready": chunk4_report["chunk4_ready"],
            "world_contract_ready": world_valid,
            "future_chunk8_ready": global_ready,
            "blockers": sorted(set(blockers)),
        }

    def _flatten(self, data: Dict[str, Any]) -> Dict[str, Any]:
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

        walk(data)
        return flat
