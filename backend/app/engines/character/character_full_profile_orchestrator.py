from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import (
    DatasetProvenanceRecord,
    EmbeddingMetadata,
    EngineLearningMetadata,
    LearnedOntologyRecord,
    LearnedTypeRegistryRecord,
    TrainingEligibility,
)


class CharacterFullProfileOrchestrator(BaseEngine):
    """Assembles a full character intelligence profile.

    This orchestrator does not replace the individual engines. It packages their
    outputs into one coherent character profile for persistence, API responses,
    benchmark evaluation, export, and future relationship/plot/training layers.
    """

    engine_name = "character.full_profile_orchestrator"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; orchestrator used partial defaults.")

        character_id = (
            character_seed.get("character_id")
            or payload.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        identity_block = self._identity_block(character_id, character_seed, payload)
        origin_block = self._origin_block(character_seed, payload)
        psychology_block = self._psychology_block(character_seed, payload)
        power_block = self._power_block(character_seed, payload)
        destiny_block = self._destiny_block(character_seed, payload)
        relationship_block = self._relationship_block(character_seed, payload)
        dialogue_block = self._dialogue_block(character_seed, payload)
        validation_block = self._validation_block(character_seed, payload)
        learning_block = self._learning_block(character_seed, payload)

        full_profile = self._build_full_profile(
            character_id=character_id,
            identity_block=identity_block,
            origin_block=origin_block,
            psychology_block=psychology_block,
            power_block=power_block,
            destiny_block=destiny_block,
            relationship_block=relationship_block,
            dialogue_block=dialogue_block,
            validation_block=validation_block,
            learning_block=learning_block,
        )

        orchestration_report = self._build_orchestration_report(full_profile)
        export_manifest = self._build_export_manifest(full_profile, orchestration_report)
        missing_component_report = self._build_missing_component_report(full_profile)
        diagnostics = self._build_diagnostics(
            full_profile=full_profile,
            orchestration_report=orchestration_report,
            missing_component_report=missing_component_report,
        )

        ontology_record = self._build_ontology_record(
            full_profile=full_profile,
            orchestration_report=orchestration_report,
            missing_component_report=missing_component_report,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_full_profile",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=orchestration_report["similarity_tags"],
            novelty_score=orchestration_report["novelty_score"],
            originality_score=orchestration_report["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            full_profile=full_profile,
            orchestration_report=orchestration_report,
            diagnostics=diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=orchestration_report["profile_name"],
            type_family="character_full_profile",
            type_subfamily=orchestration_report["profile_tier"],
            type_scope="character_orchestration",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=orchestration_report["similarity_tags"],
            generation_constraints=export_manifest["export_constraints"],
            counter_patterns=missing_component_report["missing_or_weak_components"],
            learned_axes={
                "full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "export_manifest": export_manifest,
                "missing_component_report": missing_component_report,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_full_profile",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=orchestration_report["retrieval_context_queries"],
            generated_training_labels={
                "profile_tier": orchestration_report["profile_tier"],
                "profile_completeness_score": orchestration_report["profile_completeness_score"],
                "overall_quality_score": validation_block.get("quality_report", {}).get("overall_quality_score", 0.0),
                "character_bible_ready": diagnostics["character_bible_ready"],
                "api_ready": diagnostics["api_ready"],
                "persistence_ready": diagnostics["persistence_ready"],
                "benchmark_ready": diagnostics["benchmark_ready"],
                "chunk4_ready": diagnostics["chunk4_ready"],
                "training_queue_ready": diagnostics["training_queue_ready"],
            },
            learning_notes=[
                "Full profile orchestration is the final packaging step before persistence/API/export.",
                "Future training should only use full profiles with strong provenance, quality, and consistency metadata.",
                "Chunk 4 relationship simulation should consume relationship/dialogue/destiny blocks from this profile.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            full_profile=full_profile,
            orchestration_report=orchestration_report,
            export_manifest=export_manifest,
            missing_component_report=missing_component_report,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "character_full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "export_manifest": export_manifest,
                "missing_component_report": missing_component_report,
                "orchestrator_diagnostics": diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "full_profile_summary": {
                    "character_id": character_id,
                    "character_name": identity_block["name"],
                    "profile_tier": orchestration_report["profile_tier"],
                    "profile_completeness_score": orchestration_report["profile_completeness_score"],
                    "character_bible_ready": diagnostics["character_bible_ready"],
                    "api_ready": diagnostics["api_ready"],
                    "persistence_ready": diagnostics["persistence_ready"],
                    "benchmark_ready": diagnostics["benchmark_ready"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_character_store": True,
                    "ready_for_character_api": diagnostics["api_ready"],
                    "ready_for_character_bible_export": diagnostics["character_bible_ready"],
                    "ready_for_chunk4_relationship_simulation": diagnostics["chunk4_ready"],
                },
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                full_profile["profile_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _identity_block(self, character_id: str, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "character_id": character_id,
            "name": seed.get("name") or seed.get("character_name") or payload.get("name") or "Unnamed Character",
            "role": seed.get("role", "unknown"),
            "archetype_label": seed.get("people_type") or seed.get("character_type") or "unresolved",
            "project_id": seed.get("project_id") or payload.get("project_id", "default_project"),
            "universe_id": seed.get("universe_id") or payload.get("universe_id", "default_universe"),
            "profile_version": seed.get("profile_version", "v0.3.0-character-layer"),
        }

    def _origin_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "origin_profile": payload.get("origin_profile") or seed.get("origin_profile", {}),
            "family_profile": payload.get("family_profile") or seed.get("family_profile", {}),
            "social_class": seed.get("social_class") or payload.get("origin_profile", {}).get("social_class"),
            "family_name_status": seed.get("family_name_status") or payload.get("origin_profile", {}).get("family_name_status"),
            "world_character_constraints": payload.get("world_character_constraints") or seed.get("world_character_constraints", {}),
        }

    def _psychology_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "psychology_profile": payload.get("psychology_profile") or seed.get("psychology", {}),
            "goal_profile": payload.get("goal_profile") or seed.get("goal_profile", {}),
            "moral_profile": payload.get("moral_profile") or seed.get("moral_profile", {}),
            "memory_records": payload.get("memory_records") or seed.get("memories", []),
            "emotional_state_profile": payload.get("emotional_state_profile") or seed.get("emotional_state_profile", {}),
            "emotional_arc_profile": payload.get("emotional_arc_profile") or seed.get("emotional_arc_profile", {}),
            "trauma_records": payload.get("trauma_records") or seed.get("trauma_records", []),
            "healing_profile": payload.get("healing_profile") or seed.get("healing_profile", {}),
        }

    def _power_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "skill_profile": payload.get("skill_profile") or seed.get("skill_profile", {}),
            "skill_ontology": payload.get("skill_ontology") or seed.get("skill_ontology", {}),
            "character_type_ontology": payload.get("character_type_ontology") or seed.get("character_type_ontology", {}),
            "adaptability_profile": payload.get("adaptability_profile") or seed.get("adaptability_profile", {}),
            "limit_break_rules": payload.get("limit_break_rules") or seed.get("limit_break_rules", {}),
            "adaptation_pathways": payload.get("adaptation_pathways") or seed.get("adaptation_pathways", {}),
            "failure_and_cost_model": payload.get("failure_and_cost_model") or seed.get("adaptability_failure_and_cost_model", {}),
        }

    def _destiny_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "destiny_profile": payload.get("destiny_profile") or seed.get("destiny_profile", {}),
            "prophecy_model": payload.get("prophecy_model") or seed.get("prophecy_model", {}),
            "legacy_model": payload.get("legacy_model") or seed.get("legacy_model", {}),
            "agency_conflict_model": payload.get("agency_conflict_model") or seed.get("destiny_agency_conflict_model", {}),
        }

    def _relationship_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_readiness_profile": payload.get("relationship_readiness_profile") or seed.get("relationship_readiness_profile", {}),
            "relationship_hooks": payload.get("relationship_hooks") or seed.get("relationship_hooks", {}),
            "compatibility_vectors": payload.get("compatibility_vectors") or seed.get("compatibility_vectors", {}),
            "attachment_and_conflict_model": payload.get("attachment_and_conflict_model") or seed.get("attachment_and_conflict_model", {}),
            "boundary_model": payload.get("boundary_model") or seed.get("relationship_boundary_model", {}),
        }

    def _dialogue_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dialogue_voice_profile": payload.get("dialogue_voice_profile") or seed.get("dialogue_voice_profile", {}),
            "speech_pattern_model": payload.get("speech_pattern_model") or seed.get("speech_pattern_model", {}),
            "emotional_dialogue_rules": payload.get("emotional_dialogue_rules") or seed.get("emotional_dialogue_rules", {}),
            "relationship_dialogue_variants": payload.get("relationship_dialogue_variants") or seed.get("relationship_dialogue_variants", {}),
            "destiny_dialogue_layer": payload.get("destiny_dialogue_layer") or seed.get("destiny_dialogue_layer", {}),
            "forbidden_dialogue_patterns": payload.get("forbidden_dialogue_patterns") or seed.get("forbidden_dialogue_patterns", {}),
        }

    def _validation_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "consistency_report": payload.get("consistency_report") or seed.get("consistency_report", {}),
            "validation_checks": payload.get("validation_checks") or seed.get("validation_checks", []),
            "repair_plan": payload.get("repair_plan") or seed.get("repair_plan", {}),
            "originality_report": payload.get("originality_report") or seed.get("originality_report", {}),
            "similarity_report": payload.get("similarity_report") or seed.get("similarity_report", {}),
            "anti_genericity_report": payload.get("anti_genericity_report") or seed.get("anti_genericity_report", {}),
            "quality_report": payload.get("quality_report") or seed.get("quality_report", {}),
            "readiness_report": payload.get("readiness_report") or seed.get("readiness_report", {}),
            "quality_recommendation_report": payload.get("quality_recommendation_report") or seed.get("quality_recommendation_report", {}),
        }

    def _learning_block(self, seed: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        keys = [
            "skill_learning_metadata",
            "character_type_learning_metadata",
            "adaptability_learning_metadata",
            "destiny_learning_metadata",
            "relationship_learning_metadata",
            "dialogue_learning_metadata",
            "consistency_learning_metadata",
            "originality_learning_metadata",
            "quality_learning_metadata",
        ]

        learning_records = {}

        for key in keys:
            if seed.get(key):
                learning_records[key] = seed[key]
            elif payload.get(key):
                learning_records[key] = payload[key]

        return {
            "learning_metadata_records": learning_records,
            "training_queue_payloads": {
                key: value for key, value in seed.items() if "chunk8" in key or "training_payload" in key
            },
            "provenance_ready": bool(learning_records),
            "future_chunk8_training_ready": bool(seed.get("quality_report") or payload.get("quality_report")),
        }

    def _build_full_profile(
        self,
        *,
        character_id: str,
        identity_block: Dict[str, Any],
        origin_block: Dict[str, Any],
        psychology_block: Dict[str, Any],
        power_block: Dict[str, Any],
        destiny_block: Dict[str, Any],
        relationship_block: Dict[str, Any],
        dialogue_block: Dict[str, Any],
        validation_block: Dict[str, Any],
        learning_block: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "profile_id": f"charprofile_{uuid4().hex[:12]}",
            "character_id": character_id,
            "identity": identity_block,
            "origin": origin_block,
            "psychology": psychology_block,
            "power": power_block,
            "destiny": destiny_block,
            "relationships": relationship_block,
            "dialogue": dialogue_block,
            "validation": validation_block,
            "learning": learning_block,
        }

    def _build_orchestration_report(self, full_profile: Dict[str, Any]) -> Dict[str, Any]:
        components = self._component_presence(full_profile)
        completeness = self._clamp(sum(1 for present in components.values() if present) / len(components))

        quality_report = full_profile["validation"].get("quality_report", {})
        quality_score = float(quality_report.get("overall_quality_score", 0.0))

        if completeness >= 0.9 and quality_score >= 0.82:
            tier = "complete_high_quality_profile"
        elif completeness >= 0.8 and quality_score >= 0.74:
            tier = "complete_profile_ready"
        elif completeness >= 0.65:
            tier = "partial_profile_needs_completion"
        else:
            tier = "incomplete_profile"

        return {
            "orchestration_report_id": f"orchrep_{uuid4().hex[:12]}",
            "profile_name": f"character_full_profile:{tier}",
            "profile_tier": tier,
            "profile_completeness_score": completeness,
            "component_presence": components,
            "quality_score_used": quality_score,
            "block_count": len(full_profile.keys()),
            "similarity_tags": [
                "character_full_profile",
                tier,
                full_profile["identity"].get("role", "unknown_role"),
                full_profile["power"].get("skill_ontology", {}).get("skill_family", "unknown_skill"),
                full_profile["destiny"].get("destiny_profile", {}).get("destiny_family", "unknown_destiny"),
                full_profile["dialogue"].get("dialogue_voice_profile", {}).get("voice_family", "unknown_voice"),
            ],
            "retrieval_context_queries": [
                f"full character profile {tier}",
                "complete character bible psychology skill destiny relationship dialogue",
                "character orchestrator profile quality consistency originality",
            ],
            "novelty_score": full_profile["validation"].get("originality_report", {}).get("novelty_score", 0.62),
            "originality_score": full_profile["validation"].get("originality_report", {}).get("overall_originality_score", 0.62),
        }

    def _component_presence(self, full_profile: Dict[str, Any]) -> Dict[str, bool]:
        return {
            "identity": bool(full_profile["identity"].get("character_id")),
            "origin": bool(full_profile["origin"].get("origin_profile") or full_profile["origin"].get("social_class")),
            "family": bool(full_profile["origin"].get("family_profile") or full_profile["origin"].get("family_name_status")),
            "psychology": bool(full_profile["psychology"].get("psychology_profile")),
            "goals": bool(full_profile["psychology"].get("goal_profile")),
            "morality": bool(full_profile["psychology"].get("moral_profile")),
            "memory": bool(full_profile["psychology"].get("memory_records")),
            "skill": bool(full_profile["power"].get("skill_ontology")),
            "character_type": bool(full_profile["power"].get("character_type_ontology")),
            "adaptability": bool(full_profile["power"].get("adaptability_profile")),
            "destiny": bool(full_profile["destiny"].get("destiny_profile")),
            "relationships": bool(full_profile["relationships"].get("relationship_readiness_profile")),
            "dialogue": bool(full_profile["dialogue"].get("dialogue_voice_profile")),
            "consistency": bool(full_profile["validation"].get("consistency_report")),
            "originality": bool(full_profile["validation"].get("originality_report")),
            "quality": bool(full_profile["validation"].get("quality_report")),
        }

    def _build_export_manifest(self, full_profile: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "export_manifest_id": f"exportmanifest_{uuid4().hex[:12]}",
            "recommended_exports": [
                "json_profile",
                "character_bible_markdown",
                "character_bible_docx_later",
                "api_response_payload",
                "benchmark_fixture",
            ],
            "export_constraints": [
                "do not export if profile completeness below 0.75",
                "do not export if quality report has export blockers",
                "include validation, originality, and quality metadata",
                "include relationship and dialogue hooks for Chunk 4",
                "include provenance/training metadata for Chunk 8",
            ],
            "profile_sections_for_bible": [
                "identity",
                "origin",
                "psychology",
                "power",
                "destiny",
                "relationships",
                "dialogue",
                "validation",
                "learning",
            ],
            "safe_to_export": report["profile_completeness_score"] >= 0.75,
        }

    def _build_missing_component_report(self, full_profile: Dict[str, Any]) -> Dict[str, Any]:
        presence = self._component_presence(full_profile)
        missing = [name for name, present in presence.items() if not present]
        weak = []

        quality = full_profile["validation"].get("quality_report", {})
        if quality.get("weak_axes"):
            weak.extend(quality["weak_axes"])

        return {
            "missing_component_report_id": f"missing_{uuid4().hex[:12]}",
            "missing_components": missing,
            "weak_components": weak,
            "missing_or_weak_components": missing + weak,
            "completion_recommendations": self._completion_recommendations(missing, weak),
        }

    def _completion_recommendations(self, missing: List[str], weak: List[str]) -> List[str]:
        recommendations = []

        for item in missing:
            recommendations.append(f"run or repair missing component: {item}")

        for item in weak:
            recommendations.append(f"strengthen weak quality axis: {item}")

        if not recommendations:
            recommendations.append("profile is complete enough for store/API/export pipeline")

        return recommendations

    def _build_diagnostics(
        self,
        *,
        full_profile: Dict[str, Any],
        orchestration_report: Dict[str, Any],
        missing_component_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        quality_report = full_profile["validation"].get("quality_report", {})
        readiness_report = full_profile["validation"].get("readiness_report", {})

        completeness = orchestration_report["profile_completeness_score"]
        quality = float(quality_report.get("overall_quality_score", 0.0))

        return {
            "orchestrator_completeness_score": completeness,
            "has_full_profile": True,
            "has_identity": bool(full_profile["identity"].get("character_id")),
            "has_validation": bool(full_profile["validation"].get("quality_report")),
            "missing_count": len(missing_component_report["missing_components"]),
            "weak_count": len(missing_component_report["weak_components"]),
            "character_bible_ready": completeness >= 0.75 and quality >= 0.74 and readiness_report.get("character_bible_ready", False),
            "api_ready": completeness >= 0.7,
            "persistence_ready": bool(full_profile["character_id"]),
            "benchmark_ready": completeness >= 0.72 and quality >= 0.68,
            "chunk4_ready": bool(full_profile["relationships"].get("relationship_readiness_profile")) and bool(full_profile["dialogue"].get("dialogue_voice_profile")),
            "training_queue_ready": readiness_report.get("training_queue_ready", False) and completeness >= 0.8,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        full_profile: Dict[str, Any],
        orchestration_report: Dict[str, Any],
        missing_component_report: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="character_full_profile",
            name=orchestration_report["profile_name"],
            family="character_full_profile",
            subtype=orchestration_report["profile_tier"],
            description=f"Full character profile completeness {orchestration_report['profile_completeness_score']}",
            axes={
                "full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "missing_component_report": missing_component_report,
            },
            tags=orchestration_report["similarity_tags"],
            examples=[orchestration_report["profile_name"]],
            counterexamples=missing_component_report["missing_or_weak_components"],
            confidence_score=orchestration_report["profile_completeness_score"],
            novelty_score=orchestration_report["novelty_score"],
            quality_score=orchestration_report["quality_score_used"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        full_profile: Dict[str, Any],
        orchestration_report: Dict[str, Any],
        diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality_score = float(full_profile["validation"].get("quality_report", {}).get("overall_quality_score", 0.0))

        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8

        eligible = (
            approved_source
            and provenance.usage_allowed
            and diagnostics["training_queue_ready"]
            and quality_score >= 0.78
            and orchestration_report["profile_completeness_score"] >= 0.8
            and high_rating
        )

        rejection_reasons = []
        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if not diagnostics["training_queue_ready"]:
            rejection_reasons.append("profile not training-queue ready")
        if quality_score < 0.78:
            rejection_reasons.append("quality score below training threshold")
        if orchestration_report["profile_completeness_score"] < 0.8:
            rejection_reasons.append("profile completeness below training threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=quality_score,
            consistency_score=orchestration_report["profile_completeness_score"],
            originality_score=orchestration_report["originality_score"],
            safety_score=0.88 if diagnostics["character_bible_ready"] else 0.72,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Full profile orchestration is the final character-layer training/export gate.",
                "Training eligibility requires quality, completeness, provenance, and readiness metadata.",
            ],
        )

    def _build_next_engine_payload(
        self,
        *,
        full_profile: Dict[str, Any],
        orchestration_report: Dict[str, Any],
        export_manifest: Dict[str, Any],
        missing_component_report: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        return {
            "character_store_payload": {
                "character_id": full_profile["character_id"],
                "profile": full_profile,
                "orchestration_report": orchestration_report,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "character_api_payload": {
                "character_full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "export_manifest": export_manifest,
            },
            "character_bible_export_payload": {
                "character_full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "export_manifest": export_manifest,
            },
            "benchmark_payload": {
                "character_id": full_profile["character_id"],
                "full_profile": full_profile,
                "orchestration_report": orchestration_report,
                "missing_component_report": missing_component_report,
            },
            "chunk4_relationship_payload_later": {
                "character_id": full_profile["character_id"],
                "relationship_block": full_profile["relationships"],
                "dialogue_block": full_profile["dialogue"],
                "destiny_block": full_profile["destiny"],
                "psychology_block": full_profile["psychology"],
            },
            "chunk8_training_payload_later": {
                "target_type": "character_full_profile",
                "full_profile": full_profile,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
