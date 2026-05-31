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


class CharacterOriginalityEngine(BaseEngine):
    """Scores character originality and similarity risk.

    This is the deterministic scaffold for a future embedding/RAG originality
    system. Later, Chunk 8 should replace/augment lexical similarity with real
    vector retrieval against licensed datasets and the learned type registry.
    """

    engine_name = "character.originality_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        world_state = payload.get("world_state", {})
        consistency_report = payload.get("consistency_report") or character_seed.get("consistency_report", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        adaptability_profile = payload.get("adaptability_profile") or character_seed.get("adaptability_profile", {})
        destiny_profile = payload.get("destiny_profile") or character_seed.get("destiny_profile", {})
        relationship_readiness_profile = payload.get("relationship_readiness_profile") or character_seed.get("relationship_readiness_profile", {})
        dialogue_voice_profile = payload.get("dialogue_voice_profile") or character_seed.get("dialogue_voice_profile", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; originality engine used partial defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or dialogue_voice_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        feature_vector = self._build_feature_vector(
            character_seed=character_seed,
            world_state=world_state,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            moral_profile=moral_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
            destiny_profile=destiny_profile,
            relationship_readiness_profile=relationship_readiness_profile,
            dialogue_voice_profile=dialogue_voice_profile,
        )

        similarity_report = self._build_similarity_report(feature_vector)
        originality_report = self._build_originality_report(
            character_id=character_id,
            feature_vector=feature_vector,
            similarity_report=similarity_report,
            consistency_report=consistency_report,
        )
        anti_genericity_report = self._build_anti_genericity_report(
            feature_vector=feature_vector,
            similarity_report=similarity_report,
            originality_report=originality_report,
        )
        improvement_plan = self._build_improvement_plan(
            originality_report=originality_report,
            anti_genericity_report=anti_genericity_report,
            similarity_report=similarity_report,
        )
        diagnostics = self._build_diagnostics(
            originality_report=originality_report,
            anti_genericity_report=anti_genericity_report,
            improvement_plan=improvement_plan,
        )

        ontology_record = self._build_ontology_record(
            originality_report=originality_report,
            feature_vector=feature_vector,
            similarity_report=similarity_report,
            anti_genericity_report=anti_genericity_report,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_originality",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=originality_report["similarity_tags"],
            novelty_score=originality_report["novelty_score"],
            originality_score=originality_report["overall_originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            originality_report=originality_report,
            diagnostics=diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=originality_report["originality_name"],
            type_family="character_originality",
            type_subfamily=originality_report["originality_tier"],
            type_scope="character_quality_control",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=originality_report["similarity_tags"],
            generation_constraints=improvement_plan["originality_constraints"],
            counter_patterns=anti_genericity_report["genericity_risks"],
            learned_axes={
                "feature_vector": feature_vector,
                "similarity_report": similarity_report,
                "originality_report": originality_report,
                "anti_genericity_report": anti_genericity_report,
                "improvement_plan": improvement_plan,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_originality",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=similarity_report["future_retrieval_queries"],
            generated_training_labels={
                "originality_tier": originality_report["originality_tier"],
                "overall_originality_score": originality_report["overall_originality_score"],
                "trope_risk_score": anti_genericity_report["trope_risk_score"],
                "similarity_risk_score": similarity_report["similarity_risk_score"],
                "genericity_risk_score": anti_genericity_report["genericity_risk_score"],
                "originality_ready_for_quality_scorer": diagnostics["ready_for_quality_scorer"],
                "ready_for_quality_scorer": diagnostics["ready_for_quality_scorer"],
            },
            learning_notes=[
                "This deterministic originality engine is a scaffold for future embedding-based similarity search.",
                "Chunk 8 should compare characters against licensed novel/story/people/character datasets.",
                "High originality requires unusual combinations plus coherent cost, agency, contradiction, and voice.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            originality_report=originality_report,
            similarity_report=similarity_report,
            anti_genericity_report=anti_genericity_report,
            improvement_plan=improvement_plan,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "character_originality_feature_vector": feature_vector,
                "similarity_report": similarity_report,
                "originality_report": originality_report,
                "anti_genericity_report": anti_genericity_report,
                "originality_improvement_plan": improvement_plan,
                "originality_diagnostics": diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "originality_summary": {
                    "character_id": character_id,
                    "overall_originality_score": originality_report["overall_originality_score"],
                    "originality_tier": originality_report["originality_tier"],
                    "similarity_risk_score": similarity_report["similarity_risk_score"],
                    "genericity_risk_score": anti_genericity_report["genericity_risk_score"],
                    "trope_risk_score": anti_genericity_report["trope_risk_score"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_quality_scorer": diagnostics["ready_for_quality_scorer"],
                    "ready_for_character_bible_export": diagnostics["ready_for_character_bible_export"],
                    "ready_for_chunk8_embedding_upgrade": True,
                },
                "training_notes": [
                    "Originality is not random weirdness; it requires coherent uncommon combinations.",
                    "Generic tropes are allowed only when inverted, constrained, or causally grounded.",
                    "Future versions should use embeddings and learned registry comparisons.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                originality_report["originality_report_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_feature_vector(self, **kwargs: Any) -> Dict[str, Any]:
        seed = kwargs["character_seed"]
        psychology = kwargs["psychology_profile"]
        goal = kwargs["goal_profile"]
        moral = kwargs["moral_profile"]
        skill = kwargs["skill_ontology"]
        ctype = kwargs["character_type_ontology"]
        adapt = kwargs["adaptability_profile"]
        destiny = kwargs["destiny_profile"]
        rel = kwargs["relationship_readiness_profile"]
        voice = kwargs["dialogue_voice_profile"]

        tags = set()

        for source in [seed, psychology, goal, moral, skill, ctype, adapt, destiny, rel, voice]:
            tags.update(self._extract_tags(source))

        return {
            "feature_vector_id": f"origvec_{uuid4().hex[:12]}",
            "surface_role": seed.get("role", "unknown"),
            "social_class": seed.get("social_class", "unknown"),
            "family_name_status": seed.get("family_name_status", "unknown"),
            "people_type_family": ctype.get("type_family", "unknown_type_family"),
            "people_type_subtype": ctype.get("type_subtype", "unknown_type_subtype"),
            "skill_family": skill.get("skill_family", "unknown_skill_family"),
            "skill_subtype": skill.get("skill_subtype", "unknown_skill_subtype"),
            "adaptability_family": adapt.get("adaptability_family", "unknown_adaptability_family"),
            "destiny_family": destiny.get("destiny_family", "unknown_destiny_family"),
            "relationship_readiness_family": rel.get("relationship_readiness_family", "unknown_relationship_family"),
            "voice_family": voice.get("voice_family", "unknown_voice_family"),
            "core_wound": psychology.get("core_wound", ""),
            "true_need": goal.get("true_need", ""),
            "false_need": goal.get("false_need", ""),
            "moral_value": moral.get("dominant_moral_value", ""),
            "contradiction_markers": self._contradiction_markers(psychology, goal, moral, destiny, rel),
            "complexity_tags": sorted(tags),
            "unusual_combination_count": self._unusual_combination_count(skill, ctype, adapt, destiny, rel, voice),
            "grounding_count": self._grounding_count(seed, psychology, goal, skill, ctype, adapt, destiny, rel, voice),
        }

    def _extract_tags(self, obj: Any) -> List[str]:
        text = str(obj).lower()
        tags = []
        for term in [
            "kingmaker", "academy", "family", "secret", "destiny", "rival", "villain",
            "love", "memory", "oath", "law", "class", "adapt", "threshold", "voice",
            "betrayal", "prophecy", "legacy", "pattern", "curse", "saint", "monster",
        ]:
            if term in text:
                tags.append(term)
        return tags

    def _contradiction_markers(self, psychology: Dict[str, Any], goal: Dict[str, Any], moral: Dict[str, Any], destiny: Dict[str, Any], rel: Dict[str, Any]) -> List[str]:
        markers = []

        if psychology.get("core_wound") and goal.get("true_need"):
            markers.append("wound_vs_true_need")

        if goal.get("false_need") and goal.get("true_need"):
            markers.append("false_need_vs_true_need")

        if moral.get("corruption_risk", 0.0) >= 0.5:
            markers.append("ethics_vs_corruption_risk")

        if destiny.get("destiny_burdens"):
            markers.append("agency_vs_destiny_burden")

        if rel.get("intimacy_risk", 0.0) >= 0.6:
            markers.append("connection_vs_exposure_risk")

        return markers

    def _unusual_combination_count(self, skill: Dict[str, Any], ctype: Dict[str, Any], adapt: Dict[str, Any], destiny: Dict[str, Any], rel: Dict[str, Any], voice: Dict[str, Any]) -> int:
        count = 0

        if ctype.get("type_family") == "power_redirector" and skill.get("skill_family") == "cognitive_inference":
            count += 1
        if destiny.get("destiny_family") == "power_flow_destiny" and rel.get("relationship_readiness_family") == "high_loyalty_power_broker_readiness":
            count += 1
        if adapt.get("adaptability_family") in {"earned_moral_breakthrough", "limit_break_anomaly"}:
            count += 1
        if voice.get("voice_family") in {"controlled_subtext_voice", "institutional_authority_voice", "sacred_contradiction_voice"}:
            count += 1
        if skill.get("skill_family") in {"psychic_cognitive_mapping", "adaptive_limit_system", "institutional_authority"}:
            count += 1

        return count

    def _grounding_count(self, *objs: Dict[str, Any]) -> int:
        count = 0
        keys = [
            "core_wound", "true_need", "false_need", "cost_family", "counter_family",
            "destiny_burdens", "relationship_readiness_family", "voice_family",
            "adaptability_family", "type_family",
        ]

        for obj in objs:
            for key in keys:
                if obj.get(key):
                    count += 1

        return count

    def _build_similarity_report(self, feature_vector: Dict[str, Any]) -> Dict[str, Any]:
        trope_matches = self._trope_matches(feature_vector)
        internal_similarity_patterns = self._internal_similarity_patterns(feature_vector)

        risk = 0.2
        risk += len(trope_matches) * 0.08
        risk += max(0, 3 - feature_vector["unusual_combination_count"]) * 0.05
        risk -= min(0.22, feature_vector["grounding_count"] * 0.015)

        risk = self._clamp(risk)

        return {
            "similarity_report_id": f"simchar_{uuid4().hex[:12]}",
            "similarity_risk_score": risk,
            "trope_matches": trope_matches,
            "internal_similarity_patterns": internal_similarity_patterns,
            "future_embedding_search_required": True,
            "future_retrieval_queries": [
                f"character similar to {feature_vector['people_type_family']} {feature_vector['skill_family']}",
                f"{feature_vector['destiny_family']} {feature_vector['relationship_readiness_family']} character",
                f"{feature_vector['voice_family']} {feature_vector['core_wound']}",
                "licensed character dataset similarity search later",
            ],
            "nearest_neighbor_placeholder": [
                "future_vector_neighbor_1",
                "future_vector_neighbor_2",
                "future_vector_neighbor_3",
            ],
            "similarity_warning": "Current similarity is lexical/rule-based; Chunk 8 should add embedding retrieval.",
        }

    def _trope_matches(self, vec: Dict[str, Any]) -> List[str]:
        matches = []

        role = vec["surface_role"]
        destiny = vec["destiny_family"]
        skill = vec["skill_family"]
        ctype = vec["people_type_family"]

        if role == "protagonist" and destiny in {"prophetic_selection_destiny", "unknown_destiny_family"}:
            matches.append("generic_chosen_protagonist_risk")

        if skill == "elemental_authority":
            matches.append("generic_elemental_power_risk")

        if ctype in {"general_ensemble_character", "unknown_type_family"}:
            matches.append("generic_character_type_risk")

        if not vec["core_wound"]:
            matches.append("missing_wound_genericity_risk")

        if not vec["true_need"]:
            matches.append("missing_true_need_genericity_risk")

        return matches

    def _internal_similarity_patterns(self, vec: Dict[str, Any]) -> List[str]:
        patterns = []

        if vec["people_type_family"] == "power_redirector":
            patterns.append("similar_to_hidden_power_broker_family")

        if vec["skill_family"] == "cognitive_inference":
            patterns.append("similar_to_pattern_reader_family")

        if vec["destiny_family"] == "power_flow_destiny":
            patterns.append("similar_to_power_flow_destiny_family")

        if vec["voice_family"] == "controlled_subtext_voice":
            patterns.append("similar_to_controlled_subtext_voice_family")

        return patterns

    def _build_originality_report(self, *, character_id: str, feature_vector: Dict[str, Any], similarity_report: Dict[str, Any], consistency_report: Dict[str, Any]) -> Dict[str, Any]:
        base = 0.45
        base += min(0.22, feature_vector["unusual_combination_count"] * 0.055)
        base += min(0.18, len(feature_vector["contradiction_markers"]) * 0.045)
        base += min(0.18, feature_vector["grounding_count"] * 0.012)
        base -= similarity_report["similarity_risk_score"] * 0.25

        if consistency_report.get("overall_consistency_score", 0.0) >= 0.85:
            base += 0.08

        score = self._clamp(base)

        if score >= 0.82:
            tier = "high_originality"
        elif score >= 0.68:
            tier = "strong_originality"
        elif score >= 0.52:
            tier = "moderate_originality"
        else:
            tier = "generic_or_underdeveloped"

        return {
            "originality_report_id": f"origrep_{uuid4().hex[:12]}",
            "character_id": character_id,
            "originality_name": f"character_originality:{tier}",
            "overall_originality_score": score,
            "originality_tier": tier,
            "novelty_score": self._clamp(score + 0.04),
            "coherence_adjusted_originality": self._clamp(score + (consistency_report.get("overall_consistency_score", 0.8) - 0.8) * 0.15),
            "unusual_combination_count": feature_vector["unusual_combination_count"],
            "grounding_count": feature_vector["grounding_count"],
            "contradiction_markers": feature_vector["contradiction_markers"],
            "strong_originality_sources": self._strong_sources(feature_vector),
            "weak_originality_sources": similarity_report["trope_matches"],
            "similarity_tags": [
                "character_originality",
                tier,
                feature_vector["people_type_family"],
                feature_vector["skill_family"],
                feature_vector["destiny_family"],
                feature_vector["voice_family"],
            ],
        }

    def _strong_sources(self, vec: Dict[str, Any]) -> List[str]:
        sources = []

        if vec["people_type_family"] == "power_redirector" and vec["skill_family"] == "cognitive_inference":
            sources.append("power_redirector_plus_cognitive_inference")

        if vec["destiny_family"] == "power_flow_destiny":
            sources.append("destiny_as_power_flow_not_chosen_one")

        if vec["relationship_readiness_family"] == "high_loyalty_power_broker_readiness":
            sources.append("relationship_readiness_as_power_broker_trust_logic")

        if vec["voice_family"] == "controlled_subtext_voice":
            sources.append("dialogue_voice_matches_strategy_and_wound")

        if vec["contradiction_markers"]:
            sources.append("internal_contradictions_create_depth")

        return sources

    def _build_anti_genericity_report(self, *, feature_vector: Dict[str, Any], similarity_report: Dict[str, Any], originality_report: Dict[str, Any]) -> Dict[str, Any]:
        trope_risk = self._clamp(len(similarity_report["trope_matches"]) * 0.18)
        genericity = self._clamp(1.0 - originality_report["overall_originality_score"] + trope_risk * 0.25)

        risks = list(similarity_report["trope_matches"])

        if feature_vector["grounding_count"] < 6:
            risks.append("insufficient_cross_engine_grounding")

        if feature_vector["unusual_combination_count"] < 2:
            risks.append("low_unusual_combination_count")

        return {
            "anti_genericity_report_id": f"antigen_{uuid4().hex[:12]}",
            "genericity_risk_score": genericity,
            "trope_risk_score": trope_risk,
            "genericity_risks": risks,
            "anti_genericity_strengths": originality_report["strong_originality_sources"],
            "required_inversions": self._required_inversions(risks),
            "minimum_originality_repairs": self._minimum_repairs(risks),
        }

    def _required_inversions(self, risks: List[str]) -> List[str]:
        inversions = []

        for risk in risks:
            if risk == "generic_chosen_protagonist_risk":
                inversions.append("make destiny pressure-based, misinterpreted, or socially weaponized")
            elif risk == "generic_elemental_power_risk":
                inversions.append("add cost, counterplay, legality, and emotional/social consequence")
            elif risk == "generic_character_type_risk":
                inversions.append("add people-type ontology with role, social, psychological, and plot axes")
            elif risk == "missing_wound_genericity_risk":
                inversions.append("add core wound linked to memory and goal")
            elif risk == "missing_true_need_genericity_risk":
                inversions.append("add true_need distinct from false_need")
            else:
                inversions.append(f"repair originality risk: {risk}")

        return inversions

    def _minimum_repairs(self, risks: List[str]) -> List[str]:
        if not risks:
            return ["preserve current originality sources in orchestrator and export"]

        return [
            "increase cross-engine grounding",
            "add specific cost/counterplay/consequence",
            "add relationship-specific conflict hook",
            "add voice-specific forbidden generic patterns",
        ]

    def _build_improvement_plan(self, *, originality_report: Dict[str, Any], anti_genericity_report: Dict[str, Any], similarity_report: Dict[str, Any]) -> Dict[str, Any]:
        needs_improvement = originality_report["overall_originality_score"] < 0.75 or anti_genericity_report["genericity_risks"]

        return {
            "originality_improvement_plan_id": f"origplan_{uuid4().hex[:12]}",
            "requires_originality_improvement": needs_improvement,
            "priority_repairs": anti_genericity_report["minimum_originality_repairs"],
            "required_inversions": anti_genericity_report["required_inversions"],
            "originality_constraints": [
                "do not add random uniqueness without causal grounding",
                "increase originality through unusual coherent combinations",
                "preserve world constraints and consistency report",
                "make trope use intentional, costly, and inverted",
                "add relationship and dialogue specificity before export",
                "future embedding search must be run before training on public-scale datasets",
            ],
            "future_embedding_upgrade_tasks": [
                "embed full character bible",
                "retrieve nearest internal learned type records",
                "retrieve nearest licensed dataset archetype/character records",
                "compute semantic originality delta",
                "store originality result in learned registry",
            ],
        }

    def _build_diagnostics(self, *, originality_report: Dict[str, Any], anti_genericity_report: Dict[str, Any], improvement_plan: Dict[str, Any]) -> Dict[str, Any]:
        score = originality_report["overall_originality_score"]

        return {
            "originality_completeness_score": 1.0,
            "has_similarity_report": True,
            "has_trope_risk_report": True,
            "has_improvement_plan": True,
            "embedding_upgrade_required_later": True,
            "ready_for_quality_scorer": score >= 0.55,
            "ready_for_character_bible_export": score >= 0.6,
            "training_ready_schema": True,
        }

    def _build_ontology_record(self, *, originality_report: Dict[str, Any], feature_vector: Dict[str, Any], similarity_report: Dict[str, Any], anti_genericity_report: Dict[str, Any]) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="character_originality",
            name=originality_report["originality_name"],
            family="character_originality",
            subtype=originality_report["originality_tier"],
            description=f"Originality score {originality_report['overall_originality_score']}",
            axes={
                "feature_vector": feature_vector,
                "similarity_report": similarity_report,
                "originality_report": originality_report,
                "anti_genericity_report": anti_genericity_report,
            },
            tags=originality_report["similarity_tags"],
            examples=[originality_report["originality_name"]],
            counterexamples=anti_genericity_report["genericity_risks"],
            confidence_score=0.82,
            novelty_score=originality_report["novelty_score"],
            quality_score=originality_report["overall_originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(self, *, originality_report: Dict[str, Any], diagnostics: Dict[str, Any], source_mode: str, user_rating: Any, provenance: DatasetProvenanceRecord) -> TrainingEligibility:
        quality = min(
            originality_report["overall_originality_score"],
            originality_report["coherence_adjusted_originality"],
            0.95,
        )

        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8
        eligible = approved_source and provenance.usage_allowed and quality >= 0.7 and high_rating and diagnostics["ready_for_quality_scorer"]

        rejection_reasons = []
        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if quality < 0.7:
            rejection_reasons.append("originality quality below threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")
        if not diagnostics["ready_for_quality_scorer"]:
            rejection_reasons.append("not ready for quality scorer")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=round(quality, 3),
            consistency_score=0.82,
            originality_score=originality_report["overall_originality_score"],
            safety_score=0.86,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Originality report is deterministic until Chunk 8 embedding search is added.",
                "Training eligibility is allowed only for sufficiently original approved-source records.",
            ],
        )

    def _build_next_engine_payload(self, *, character_seed: Dict[str, Any], originality_report: Dict[str, Any], similarity_report: Dict[str, Any], anti_genericity_report: Dict[str, Any], improvement_plan: Dict[str, Any], learning_metadata: EngineLearningMetadata) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["originality_report"] = originality_report
        merged_seed["similarity_report"] = similarity_report
        merged_seed["anti_genericity_report"] = anti_genericity_report
        merged_seed["originality_improvement_plan"] = improvement_plan
        merged_seed["originality_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "quality_scorer_payload": {
                "character_seed": merged_seed,
                "originality_report": originality_report,
                "similarity_report": similarity_report,
                "anti_genericity_report": anti_genericity_report,
            },
            "character_bible_export_payload": {
                "character_seed": merged_seed,
                "originality_report": originality_report,
                "anti_genericity_report": anti_genericity_report,
            },
            "chunk8_embedding_payload_later": {
                "target_type": "character_originality",
                "originality_report": originality_report,
                "similarity_report": similarity_report,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
