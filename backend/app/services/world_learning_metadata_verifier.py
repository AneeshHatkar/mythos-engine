from typing import Any, Dict, List

from backend.app.services.world_learning_adapter import WorldLearningAdapter


class WorldLearningMetadataVerifier:
    """Verifies that Chunk 2 world outputs are global-learning ready.

    This does not replace the world engines. It checks whether their outputs
    expose the metadata needed for Upgrade Pass B and future Chunk 8 learning.

    If metadata is missing, it can produce adapter-normalized/synthesized metadata
    through WorldLearningAdapter.
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

    def __init__(self, adapter: WorldLearningAdapter | None = None) -> None:
        self.adapter = adapter or WorldLearningAdapter()

    def verify_world_result(
        self,
        *,
        result_payload: Dict[str, Any],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        allow_synthesis: bool = True,
    ) -> Dict[str, Any]:
        data = result_payload.get("data", {}) if isinstance(result_payload, dict) else {}
        existing_metadata = data.get("learning_metadata")

        if existing_metadata:
            metadata = existing_metadata
            synthesized = False
            normalized = self.adapter.normalize_world_result(
                result_payload=result_payload,
                project_id=project_id,
                universe_id=universe_id,
            )
        elif allow_synthesis:
            normalized = self.adapter.normalize_world_result(
                result_payload=result_payload,
                project_id=project_id,
                universe_id=universe_id,
            )
            metadata = normalized["learning_metadata"]
            synthesized = True
        else:
            normalized = {
                "world_id": "unknown_world",
                "world_to_character_contract": {},
                "world_profile": {},
            }
            metadata = {}
            synthesized = False

        metadata_report = self._metadata_completeness_report(metadata)
        ontology_report = self._ontology_report(metadata)
        provenance_report = self._provenance_report(metadata)
        embedding_report = self._embedding_report(metadata)
        training_report = self._training_report(metadata)
        contract_report = self.adapter.evaluate_world_learning_quality_gates(normalized)["contract_quality_report"]

        readiness = self._readiness_report(
            metadata_report=metadata_report,
            ontology_report=ontology_report,
            provenance_report=provenance_report,
            embedding_report=embedding_report,
            training_report=training_report,
            contract_report=contract_report,
        )

        return {
            "success": True,
            "world_id": normalized.get("world_id"),
            "engine_name": result_payload.get("engine_name", metadata.get("engine_name", "unknown_engine")),
            "metadata_synthesized": synthesized,
            "metadata_present": bool(existing_metadata),
            "metadata_completeness_report": metadata_report,
            "ontology_report": ontology_report,
            "provenance_report": provenance_report,
            "embedding_report": embedding_report,
            "training_report": training_report,
            "world_to_character_contract_report": contract_report,
            "readiness_report": readiness,
            "normalized_result_payload": normalized.get("result_payload", result_payload),
        }

    def verify_many_world_results(
        self,
        *,
        result_payloads: List[Dict[str, Any]],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        allow_synthesis: bool = True,
    ) -> Dict[str, Any]:
        reports = [
            self.verify_world_result(
                result_payload=result,
                project_id=project_id,
                universe_id=universe_id,
                allow_synthesis=allow_synthesis,
            )
            for result in result_payloads
        ]

        return {
            "success": True,
            "checked_count": len(reports),
            "global_learning_ready_count": sum(1 for item in reports if item["readiness_report"]["global_learning_ready"]),
            "training_ready_count": sum(1 for item in reports if item["readiness_report"]["training_queue_ready"]),
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
            "world_ontology_ready": bool(ontology) and bool(type_candidates) and ontology_valid and type_valid,
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

    def _readiness_report(
        self,
        *,
        metadata_report: Dict[str, Any],
        ontology_report: Dict[str, Any],
        provenance_report: Dict[str, Any],
        embedding_report: Dict[str, Any],
        training_report: Dict[str, Any],
        contract_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        global_ready = (
            metadata_report["completeness_score"] >= 0.85
            and ontology_report["world_ontology_ready"]
            and provenance_report["provenance_ready"]
            and embedding_report["future_vectorization_ready"]
            and contract_report["contract_usable"]
        )

        training_ready = (
            global_ready
            and training_report["training_metadata_complete"]
            and training_report["training_eligible"]
            and not training_report["do_not_train"]
            and not training_report["human_review_required"]
            and training_report["quality_score"] >= 0.75
            and training_report["consistency_score"] >= 0.7
            and training_report["originality_score"] >= 0.65
        )

        blockers = []

        if not metadata_report["complete"]:
            blockers.append("metadata incomplete")

        if not ontology_report["world_ontology_ready"]:
            blockers.append("world ontology/type metadata not ready")

        if not provenance_report["provenance_ready"]:
            blockers.append("approved provenance missing")

        if not embedding_report["future_vectorization_ready"]:
            blockers.append("embedding metadata not vectorization-ready")

        if not contract_report["contract_usable"]:
            blockers.append("world-to-character contract incomplete")

        if not training_ready:
            if training_report["do_not_train"]:
                blockers.append("training eligibility says do_not_train")
            if training_report["human_review_required"]:
                blockers.append("human review required before training")
            if training_report["quality_score"] < 0.75:
                blockers.append("quality below training threshold")
            if training_report["consistency_score"] < 0.7:
                blockers.append("consistency below training threshold")
            if training_report["originality_score"] < 0.65:
                blockers.append("originality below training threshold")

        return {
            "global_learning_ready": global_ready,
            "training_queue_ready": training_ready,
            "chunk3_contract_ready": contract_report["contract_usable"],
            "chunk4_relationship_context_ready": contract_report["contract_usable"],
            "future_chunk8_ready": global_ready,
            "blockers": sorted(set(blockers)),
        }
