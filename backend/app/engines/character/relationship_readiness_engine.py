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


class RelationshipReadinessEngine(BaseEngine):
    """Prepares a character for future relationship simulation.

    This engine does not simulate relationships yet. It builds the structured
    readiness hooks Chunk 4 will need for friendship, rivalry, romance, family,
    mentorship, enemy dynamics, betrayal, reconciliation, and ensemble conflict.
    """

    engine_name = "character.relationship_readiness_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        memory_network = payload.get("memory_network") or character_seed.get("memory_network", {})
        reputation_profile = payload.get("reputation_profile") or character_seed.get("reputation", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        skill_profile = payload.get("skill_profile") or character_seed.get("skill_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        adaptability_profile = payload.get("adaptability_profile") or character_seed.get("adaptability_profile", {})
        destiny_profile = payload.get("destiny_profile") or character_seed.get("destiny_profile", {})
        legacy_model = payload.get("legacy_model") or character_seed.get("legacy_model", {})
        agency_conflict_model = payload.get("agency_conflict_model") or character_seed.get("destiny_agency_conflict_model", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; relationship readiness engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or destiny_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        readiness_profile = self._build_readiness_profile(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            memory_records=memory_records,
            reputation_profile=reputation_profile,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
            destiny_profile=destiny_profile,
        )

        relationship_hooks = self._build_relationship_hooks(
            readiness_profile=readiness_profile,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            memory_records=memory_records,
            reputation_profile=reputation_profile,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            destiny_profile=destiny_profile,
            legacy_model=legacy_model,
        )

        compatibility_vectors = self._build_compatibility_vectors(
            readiness_profile=readiness_profile,
            character_type_ontology=character_type_ontology,
            skill_ontology=skill_ontology,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
        )

        attachment_and_conflict_model = self._build_attachment_and_conflict_model(
            readiness_profile=readiness_profile,
            psychology_profile=psychology_profile,
            memory_records=memory_records,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            agency_conflict_model=agency_conflict_model,
        )

        boundary_model = self._build_boundary_model(
            readiness_profile=readiness_profile,
            psychology_profile=psychology_profile,
            moral_profile=moral_profile,
            skill_ontology=skill_ontology,
            adaptability_profile=adaptability_profile,
            destiny_profile=destiny_profile,
        )

        diagnostics = self._build_diagnostics(
            readiness_profile=readiness_profile,
            relationship_hooks=relationship_hooks,
            compatibility_vectors=compatibility_vectors,
            attachment_and_conflict_model=attachment_and_conflict_model,
            boundary_model=boundary_model,
        )

        ontology_record = self._build_ontology_record(
            readiness_profile=readiness_profile,
            relationship_hooks=relationship_hooks,
            compatibility_vectors=compatibility_vectors,
            attachment_and_conflict_model=attachment_and_conflict_model,
            boundary_model=boundary_model,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_relationship_readiness",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=readiness_profile["similarity_tags"],
            novelty_score=readiness_profile["novelty_score"],
            originality_score=readiness_profile["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            readiness_profile=readiness_profile,
            diagnostics=diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=readiness_profile["readiness_name"],
            type_family="relationship_readiness",
            type_subfamily=readiness_profile["relationship_readiness_family"],
            type_scope="character_relationship",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=readiness_profile["similarity_tags"],
            generation_constraints=boundary_model["relationship_generation_constraints"],
            counter_patterns=attachment_and_conflict_model["conflict_escalation_patterns"],
            learned_axes={
                "relationship_readiness_profile": readiness_profile,
                "relationship_hooks": relationship_hooks,
                "compatibility_vectors": compatibility_vectors,
                "attachment_and_conflict_model": attachment_and_conflict_model,
                "boundary_model": boundary_model,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_relationship_readiness",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=readiness_profile["retrieval_context_queries"],
            generated_training_labels={
                "relationship_readiness_family": readiness_profile["relationship_readiness_family"],
                "attachment_pattern": readiness_profile["attachment_pattern"],
                "trust_model": readiness_profile["trust_model"],
                "romance_readiness": compatibility_vectors["romance_vector"]["readiness_score"],
                "rivalry_readiness": compatibility_vectors["rivalry_vector"]["readiness_score"],
                "friendship_readiness": compatibility_vectors["friendship_vector"]["readiness_score"],
                "betrayal_sensitivity": attachment_and_conflict_model["betrayal_sensitivity"],
                "boundary_strength": boundary_model["boundary_strength"],
                "chunk4_ready": diagnostics["chunk4_relationship_ready"],
            },
            learning_notes=[
                "This engine prepares relationship simulation hooks without simulating full relationships yet.",
                "Future Chunk 4 should use compatibility vectors, boundaries, memories, and conflict triggers.",
                "Future training should learn relationship dynamics from curated dialogue/story/emotion datasets.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            readiness_profile=readiness_profile,
            relationship_hooks=relationship_hooks,
            compatibility_vectors=compatibility_vectors,
            attachment_and_conflict_model=attachment_and_conflict_model,
            boundary_model=boundary_model,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "relationship_readiness_profile": readiness_profile,
                "relationship_hooks": relationship_hooks,
                "compatibility_vectors": compatibility_vectors,
                "attachment_and_conflict_model": attachment_and_conflict_model,
                "boundary_model": boundary_model,
                "relationship_readiness_diagnostics": diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "relationship_readiness_summary": {
                    "character_id": character_id,
                    "relationship_readiness_family": readiness_profile["relationship_readiness_family"],
                    "attachment_pattern": readiness_profile["attachment_pattern"],
                    "trust_model": readiness_profile["trust_model"],
                    "romance_readiness": compatibility_vectors["romance_vector"]["readiness_score"],
                    "rivalry_readiness": compatibility_vectors["rivalry_vector"]["readiness_score"],
                    "friendship_readiness": compatibility_vectors["friendship_vector"]["readiness_score"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_dialogue_voice_engine": True,
                    "ready_for_chunk4_relationship_simulation": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "Relationship readiness should preserve agency and independent goals.",
                    "Romance, rivalry, friendship, betrayal, and mentorship must use different compatibility vectors.",
                    "Chunk 4 will simulate relationships using this structured readiness output.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                readiness_profile["relationship_readiness_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_readiness_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        reputation_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
        destiny_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        family = self._readiness_family(character_seed, psychology_profile, character_type_ontology)
        attachment_pattern = self._attachment_pattern(psychology_profile, memory_records, character_seed)
        trust_model = self._trust_model(psychology_profile, memory_records, reputation_profile)
        vulnerability_model = self._vulnerability_model(psychology_profile, goal_profile, destiny_profile)
        intimacy_risk = self._intimacy_risk(psychology_profile, skill_ontology, reputation_profile, destiny_profile)

        similarity_tags = self._similarity_tags(
            family=family,
            attachment_pattern=attachment_pattern,
            trust_model=trust_model,
            vulnerability_model=vulnerability_model,
            character_seed=character_seed,
            character_type_ontology=character_type_ontology,
            skill_ontology=skill_ontology,
            destiny_profile=destiny_profile,
        )

        return {
            "relationship_readiness_id": f"relready_{uuid4().hex[:12]}",
            "character_id": character_id,
            "readiness_name": self._readiness_name(family, attachment_pattern),
            "relationship_readiness_family": family,
            "attachment_pattern": attachment_pattern,
            "trust_model": trust_model,
            "vulnerability_model": vulnerability_model,
            "intimacy_risk": intimacy_risk,
            "relationship_agency_level": self._relationship_agency_level(character_seed, goal_profile, character_type_ontology),
            "social_visibility_risk": self._social_visibility_risk(reputation_profile, skill_ontology, adaptability_profile),
            "independent_goal_requirement": self._independent_goal_requirement(character_seed, goal_profile, character_type_ontology),
            "relationship_growth_need": self._relationship_growth_need(psychology_profile, goal_profile),
            "relationship_failure_mode": self._relationship_failure_mode(psychology_profile, character_seed),
            "relationship_success_cost": self._relationship_success_cost(psychology_profile, destiny_profile, reputation_profile),
            "similarity_tags": similarity_tags,
            "retrieval_context_queries": self._retrieval_queries(family, attachment_pattern, trust_model, similarity_tags),
            "novelty_score": self._novelty_score(family, character_type_ontology, destiny_profile),
            "originality_score": self._originality_score(family, attachment_pattern, vulnerability_model),
            "confidence_score": self._confidence_score(family, psychology_profile, character_type_ontology),
        }

    def _readiness_family(self, seed: Dict[str, Any], psychology: Dict[str, Any], type_ontology: Dict[str, Any]) -> str:
        text = " ".join([str(seed), str(psychology), str(type_ontology)]).lower()

        # Specific character ontology families should win before broad relationship labels.
        if "kingmaker" in text or "power_redirector" in text or "power_broker" in text:
            return "high_loyalty_power_broker_readiness"

        if "love_interest" in text or "romantic" in text or "romance" in text:
            return "romantic_agency_readiness"

        if "rival" in text or "mirror" in text:
            return "rivalry_pressure_readiness"

        if "villain" in text or "antagonistic" in text:
            return "antagonistic_mirror_readiness"

        if "mentor" in text or "guardian" in text:
            return "mentor_guidance_readiness"

        if "family" in text:
            return "family_burden_readiness"

        return "general_relationship_readiness"

    def _attachment_pattern(self, psychology: Dict[str, Any], memories: List[Dict[str, Any]], seed: Dict[str, Any]) -> str:
        text = " ".join([str(psychology), str(memories), str(seed)]).lower()

        if "family secret" in text or "secret" in text:
            return "guarded_attachment_with_secret_testing"

        if "betrayal" in text:
            return "betrayal_sensitive_attachment"

        if "intimacy" in text and "independence" in text:
            return "intimacy_independence_tension"

        if "controlled" in text or "self-erasure" in text:
            return "controlled_slow_trust_attachment"

        if "abandon" in text or "revoked" in text:
            return "fearful_belonging_attachment"

        return "contextual_attachment"

    def _trust_model(self, psychology: Dict[str, Any], memories: List[Dict[str, Any]], reputation: Dict[str, Any]) -> str:
        text = " ".join([str(psychology), str(memories), str(reputation)]).lower()

        if "protects family secrets" in text or "family secret" in text:
            return "trust_requires_truth_protection_without_weaponization"

        if "public failure" in text or "humiliation" in text:
            return "trust_requires_private_respect_after_public_pressure"

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "trust_requires_exposure_safety"

        if "betrayal" in text:
            return "trust_requires_repeated_consistency_after_betrayal"

        return "trust_requires_observed_consistency"

    def _vulnerability_model(self, psychology: Dict[str, Any], goal: Dict[str, Any], destiny: Dict[str, Any]) -> str:
        if psychology.get("healing_condition"):
            return psychology["healing_condition"]

        if goal.get("true_need"):
            return f"vulnerability requires living by true need: {goal['true_need']}"

        if destiny.get("destiny_burdens"):
            return f"vulnerability requires admitting destiny burden: {destiny['destiny_burdens'][0]}"

        return "vulnerability requires being seen accurately without performance"

    def _intimacy_risk(self, psychology: Dict[str, Any], skill_ontology: Dict[str, Any], reputation: Dict[str, Any], destiny: Dict[str, Any]) -> float:
        score = 0.3

        text = " ".join([str(psychology), str(skill_ontology), str(reputation), str(destiny)]).lower()

        if "secret" in text:
            score += 0.22

        if skill_ontology.get("skill_family") in {"cognitive_inference", "psychic_cognitive_mapping"}:
            score += 0.14

        if reputation.get("exposure_risk", 0.0) >= 0.55:
            score += 0.14

        if destiny.get("destiny_family") in {"power_flow_destiny", "prophetic_selection_destiny"}:
            score += 0.08

        return self._clamp(score)

    def _relationship_agency_level(self, seed: Dict[str, Any], goal: Dict[str, Any], type_ontology: Dict[str, Any]) -> str:
        score = 0.45

        if seed.get("role") in {"protagonist", "rival", "love_interest", "villain"}:
            score += 0.16

        if goal.get("agency_score", 0.0) >= 0.65:
            score += 0.18

        if type_ontology.get("compatibility_axes", {}).get("ensemble_utility", 0.0) >= 0.65:
            score += 0.12

        if score >= 0.72:
            return "high_relationship_agency"

        if score >= 0.5:
            return "medium_relationship_agency"

        return "emerging_relationship_agency"

    def _social_visibility_risk(self, reputation: Dict[str, Any], skill_ontology: Dict[str, Any], adaptability: Dict[str, Any]) -> float:
        score = 0.25

        score += float(reputation.get("exposure_risk", 0.0)) * 0.25

        if skill_ontology.get("visibility_model") in {"impossible_to_hide_after_major_use", "visible_when_demonstrated"}:
            score += 0.12

        if adaptability.get("relationship_risk", 0.0):
            score += float(adaptability["relationship_risk"]) * 0.2

        return self._clamp(score)

    def _independent_goal_requirement(self, seed: Dict[str, Any], goal: Dict[str, Any], type_ontology: Dict[str, Any]) -> str:
        if seed.get("role") == "love_interest" or "romantic" in str(type_ontology).lower():
            return "must have goal independent of romance and protagonist validation"

        if goal.get("hidden_goal"):
            return f"must preserve hidden goal: {goal['hidden_goal']}"

        if type_ontology.get("plot_function"):
            return f"must preserve plot function: {type_ontology['plot_function']}"

        return "must remain agentic beyond relationship label"

    def _relationship_growth_need(self, psychology: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if psychology.get("healing_condition"):
            return psychology["healing_condition"]

        if goal.get("true_need"):
            return goal["true_need"]

        return "learn to receive connection without surrendering agency"

    def _relationship_failure_mode(self, psychology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        if psychology.get("betrayal_response"):
            return psychology["betrayal_response"]

        if seed.get("role") == "villain":
            return "turns intimacy into control or leverage"

        if "secret" in str(psychology).lower():
            return "withholds truth until others lose choice"

        return "protects self so completely that connection cannot reach them"

    def _relationship_success_cost(self, psychology: Dict[str, Any], destiny: Dict[str, Any], reputation: Dict[str, Any]) -> str:
        if reputation.get("exposure_risk", 0.0) >= 0.55:
            return "must risk exposure or controlled disclosure"

        if destiny.get("destiny_burdens"):
            return "must let someone see destiny burden without turning them into a tool"

        if psychology.get("healing_condition"):
            return "must accept healing condition with vulnerability"

        return "must change behavior, not only feelings"

    def _build_relationship_hooks(
        self,
        *,
        readiness_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        reputation_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        destiny_profile: Dict[str, Any],
        legacy_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "hook_id": f"relhook_{uuid4().hex[:12]}",
            "friendship_hooks": self._friendship_hooks(readiness_profile, psychology_profile, memory_records),
            "romance_hooks": self._romance_hooks(readiness_profile, psychology_profile, goal_profile),
            "rivalry_hooks": self._rivalry_hooks(readiness_profile, character_seed, goal_profile),
            "family_hooks": self._family_hooks(readiness_profile, legacy_model, character_seed),
            "mentor_hooks": self._mentor_hooks(readiness_profile, character_seed),
            "enemy_hooks": self._enemy_hooks(readiness_profile, moral_profile, reputation_profile, destiny_profile),
            "betrayal_hooks": self._betrayal_hooks(readiness_profile, psychology_profile, memory_records),
            "reconciliation_hooks": self._reconciliation_hooks(readiness_profile, psychology_profile, moral_profile),
            "relationship_plot_hooks": [
                "relationship forces truth before character feels ready",
                "relationship changes reputation or exposure risk",
                "relationship reveals a hidden contradiction in goal, morality, or destiny",
            ],
        }

    def _friendship_hooks(self, readiness: Dict[str, Any], psychology: Dict[str, Any], memories: List[Dict[str, Any]]) -> List[str]:
        return [
            "friend notices pattern of controlled distance",
            "friend protects dignity without demanding disclosure",
            "friendship tests whether support feels like debt",
        ]

    def _romance_hooks(self, readiness: Dict[str, Any], psychology: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        hooks = [
            "romance requires consent, boundaries, and independent goals",
            f"intimacy risk: {readiness['intimacy_risk']}",
            f"vulnerability model: {readiness['vulnerability_model']}",
        ]

        if goal.get("true_need"):
            hooks.append(f"romance should pressure true need: {goal['true_need']}")

        return hooks

    def _rivalry_hooks(self, readiness: Dict[str, Any], seed: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        return [
            "rival sees the wound before the character names it",
            "rivalry forces competence without letting comparison define worth",
            "rival can become respect, obsession, or betrayal depending on public pressure",
        ]

    def _family_hooks(self, readiness: Dict[str, Any], legacy: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        hooks = [
            "family pressure affects disclosure and trust",
            "family name can become relationship liability",
        ]

        if legacy.get("legacy_pressure_type"):
            hooks.append(f"legacy pressure affects family dynamic: {legacy['legacy_pressure_type']}")

        if seed.get("family_name_status"):
            hooks.append(f"family name status must affect trust: {seed['family_name_status']}")

        return hooks

    def _mentor_hooks(self, readiness: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        return [
            "mentor must teach limits, not only power",
            "mentor relationship can become guidance, control, or betrayal",
            "student must eventually make an independent ethical choice",
        ]

    def _enemy_hooks(self, readiness: Dict[str, Any], moral: Dict[str, Any], reputation: Dict[str, Any], destiny: Dict[str, Any]) -> List[str]:
        hooks = [
            "enemy targets relationship vulnerabilities, not only physical weakness",
            "enemy may weaponize reputation, destiny, or secrets",
        ]

        if reputation.get("enemy_threat_reputation", 0.0) >= 0.55:
            hooks.append("enemy already treats character as strategic threat")

        if destiny.get("destiny_family"):
            hooks.append(f"enemy can exploit destiny interpretation: {destiny['destiny_family']}")

        return hooks

    def _betrayal_hooks(self, readiness: Dict[str, Any], psychology: Dict[str, Any], memories: List[Dict[str, Any]]) -> List[str]:
        hooks = [
            f"betrayal triggers attachment pattern: {readiness['attachment_pattern']}",
            f"betrayal failure mode: {readiness['relationship_failure_mode']}",
        ]

        if psychology.get("betrayal_response"):
            hooks.append(psychology["betrayal_response"])

        return hooks

    def _reconciliation_hooks(self, readiness: Dict[str, Any], psychology: Dict[str, Any], moral: Dict[str, Any]) -> List[str]:
        return [
            "reconciliation requires changed behavior, not apology alone",
            "reconciliation requires truth repair where secrecy caused harm",
            "forgiveness cannot erase boundary violation",
            f"growth need: {readiness['relationship_growth_need']}",
        ]

    def _build_compatibility_vectors(
        self,
        *,
        readiness_profile: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        compatibility_axes = character_type_ontology.get("compatibility_axes", {})

        return {
            "friendship_vector": self._compatibility_vector(
                relationship_type="friendship",
                base=0.62,
                readiness_profile=readiness_profile,
                boosts=["trust_model", "growth_need"],
            ),
            "romance_vector": self._compatibility_vector(
                relationship_type="romance",
                base=compatibility_axes.get("romance_compatibility", 0.46),
                readiness_profile=readiness_profile,
                boosts=["vulnerability_model", "independent_goal"],
            ),
            "rivalry_vector": self._compatibility_vector(
                relationship_type="rivalry",
                base=compatibility_axes.get("rivalry_compatibility", 0.42),
                readiness_profile=readiness_profile,
                boosts=["agency", "comparison_pressure"],
            ),
            "mentor_vector": self._compatibility_vector(
                relationship_type="mentor",
                base=compatibility_axes.get("mentor_compatibility", 0.38),
                readiness_profile=readiness_profile,
                boosts=["training", "boundary"],
            ),
            "enemy_vector": self._compatibility_vector(
                relationship_type="enemy",
                base=compatibility_axes.get("villain_pressure_compatibility", 0.5),
                readiness_profile=readiness_profile,
                boosts=["reputation", "destiny", "skill_counterplay"],
            ),
            "family_vector": self._compatibility_vector(
                relationship_type="family",
                base=0.52,
                readiness_profile=readiness_profile,
                boosts=["legacy", "name_status", "secret"],
            ),
            "ensemble_vector": {
                "readiness_score": self._clamp(compatibility_axes.get("ensemble_utility", 0.58)),
                "role": "adds social consequence, contrast, pressure, or support",
                "risk": "overlapping hooks must not collapse character into one relationship function",
            },
        }

    def _compatibility_vector(
        self,
        *,
        relationship_type: str,
        base: float,
        readiness_profile: Dict[str, Any],
        boosts: List[str],
    ) -> Dict[str, Any]:
        score = base

        if readiness_profile["relationship_agency_level"] == "high_relationship_agency":
            score += 0.08

        if relationship_type == "romance" and readiness_profile["intimacy_risk"] >= 0.7:
            score -= 0.08

        if relationship_type == "friendship" and "trust" in readiness_profile["trust_model"]:
            score += 0.08

        if relationship_type == "rivalry" and "rivalry" in readiness_profile["relationship_readiness_family"]:
            score += 0.12

        return {
            "relationship_type": relationship_type,
            "readiness_score": self._clamp(score),
            "required_conditions": boosts,
            "conflict_sources": [
                readiness_profile["relationship_failure_mode"],
                readiness_profile["social_visibility_risk"],
            ],
            "growth_opportunity": readiness_profile["relationship_growth_need"],
        }

    def _build_attachment_and_conflict_model(
        self,
        *,
        readiness_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        agency_conflict_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        betrayal_sensitivity = self._betrayal_sensitivity(psychology_profile, memory_records, readiness_profile)

        return {
            "attachment_model_id": f"attach_{uuid4().hex[:12]}",
            "attachment_pattern": readiness_profile["attachment_pattern"],
            "betrayal_sensitivity": betrayal_sensitivity,
            "conflict_triggers": self._conflict_triggers(readiness_profile, psychology_profile, goal_profile, agency_conflict_model),
            "conflict_escalation_patterns": self._conflict_escalation_patterns(readiness_profile, betrayal_sensitivity),
            "deescalation_conditions": self._deescalation_conditions(readiness_profile, psychology_profile, moral_profile),
            "repair_requirements": [
                "specific truth repair",
                "observable behavior change",
                "respect for boundary",
                "cost accepted without demanding forgiveness",
            ],
            "relationship_memory_hooks": self._relationship_memory_hooks(memory_records),
        }

    def _betrayal_sensitivity(self, psychology: Dict[str, Any], memories: List[Dict[str, Any]], readiness: Dict[str, Any]) -> float:
        score = 0.35

        text = " ".join([str(psychology), str(memories), readiness["attachment_pattern"]]).lower()

        if "betrayal" in text:
            score += 0.24

        if "secret" in text:
            score += 0.16

        if "public failure" in text or "humiliation" in text:
            score += 0.1

        if readiness["intimacy_risk"] >= 0.65:
            score += 0.08

        return self._clamp(score)

    def _conflict_triggers(
        self,
        readiness: Dict[str, Any],
        psychology: Dict[str, Any],
        goal: Dict[str, Any],
        agency_conflict: Dict[str, Any],
    ) -> List[str]:
        triggers = [
            readiness["trust_model"],
            readiness["relationship_failure_mode"],
        ]

        if psychology.get("shame_trigger"):
            triggers.append(psychology["shame_trigger"])

        if goal.get("false_need"):
            triggers.append(f"false need activated: {goal['false_need']}")

        if agency_conflict.get("agency_conflict_type"):
            triggers.append(f"destiny/agency conflict: {agency_conflict['agency_conflict_type']}")

        return triggers

    def _conflict_escalation_patterns(self, readiness: Dict[str, Any], betrayal_sensitivity: float) -> List[str]:
        patterns = [
            "withholds truth after feeling misread",
            "tests loyalty indirectly",
            "uses competence to avoid vulnerability",
        ]

        if betrayal_sensitivity >= 0.6:
            patterns.append("turns small inconsistency into evidence of betrayal")

        if readiness["social_visibility_risk"] >= 0.55:
            patterns.append("treats public attention as relationship danger")

        return patterns

    def _deescalation_conditions(self, readiness: Dict[str, Any], psychology: Dict[str, Any], moral: Dict[str, Any]) -> List[str]:
        conditions = [
            "private respect before public repair",
            "truth offered without coercion",
            "the other person protects agency instead of demanding access",
        ]

        if psychology.get("healing_condition"):
            conditions.append(psychology["healing_condition"])

        if moral.get("forgiveness_condition"):
            conditions.append(moral["forgiveness_condition"])

        return conditions

    def _relationship_memory_hooks(self, memories: List[Dict[str, Any]]) -> List[str]:
        hooks = []

        for memory in memories[:4]:
            memory_id = memory.get("memory_id", "unknown_memory")
            content = memory.get("content", "")
            hooks.append(f"{memory_id}: {content}")

        if not hooks:
            hooks.append("relationship memory must be created through first meaningful trust test")

        return hooks

    def _build_boundary_model(
        self,
        *,
        readiness_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
        destiny_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        boundaries = [
            "relationship cannot erase independent agency",
            "trust must be earned through behavior, not declared by trope",
            "romance cannot replace personal goal",
            "betrayal must have consequence",
            "repair must require changed action",
        ]

        if skill_ontology.get("skill_family") in {"cognitive_inference", "psychic_cognitive_mapping"}:
            boundaries.append("mind/insight-based ability requires consent and boundary awareness")

        if adaptability_profile.get("relationship_risk", 0.0) >= 0.5:
            boundaries.append("limit-break fallout must affect relationship trust")

        if destiny_profile.get("destiny_family"):
            boundaries.append("destiny cannot force love, loyalty, or forgiveness")

        boundary_strength = self._boundary_strength(boundaries, moral_profile, readiness_profile)

        return {
            "boundary_model_id": f"bound_{uuid4().hex[:12]}",
            "relationship_boundaries": boundaries,
            "boundary_strength": boundary_strength,
            "boundary_violation_consequences": [
                "trust score decreases",
                "attachment defense activates",
                "future repair requires specific behavior",
                "relationship route may permanently change type",
            ],
            "relationship_generation_constraints": [
                "preserve independent goals",
                "respect consent and emotional boundaries",
                "do not make relationship solve all wounds",
                "do not flatten character into romance/rival/friend label",
                "make conflict specific to memory, reputation, goal, morality, or destiny",
            ],
        }

    def _boundary_strength(self, boundaries: List[str], moral: Dict[str, Any], readiness: Dict[str, Any]) -> float:
        score = 0.48 + min(0.24, len(boundaries) * 0.03)

        if moral.get("moral_flexibility", 0.0) >= 0.55:
            score += 0.06

        if readiness["relationship_agency_level"] == "high_relationship_agency":
            score += 0.08

        return self._clamp(score)

    def _build_diagnostics(
        self,
        *,
        readiness_profile: Dict[str, Any],
        relationship_hooks: Dict[str, Any],
        compatibility_vectors: Dict[str, Any],
        attachment_and_conflict_model: Dict[str, Any],
        boundary_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(readiness_profile["relationship_readiness_family"]),
                bool(readiness_profile["attachment_pattern"]),
                bool(readiness_profile["trust_model"]),
                bool(readiness_profile["vulnerability_model"]),
                bool(relationship_hooks["friendship_hooks"]),
                bool(relationship_hooks["romance_hooks"]),
                bool(relationship_hooks["rivalry_hooks"]),
                bool(compatibility_vectors["friendship_vector"]),
                bool(compatibility_vectors["romance_vector"]),
                bool(attachment_and_conflict_model["conflict_triggers"]),
                bool(attachment_and_conflict_model["repair_requirements"]),
                bool(boundary_model["relationship_boundaries"]),
            ]
        ) / 12

        return {
            "relationship_readiness_completeness_score": round(completeness, 3),
            "has_attachment_model": bool(readiness_profile["attachment_pattern"]),
            "has_trust_model": bool(readiness_profile["trust_model"]),
            "has_compatibility_vectors": len(compatibility_vectors) >= 5,
            "has_conflict_triggers": bool(attachment_and_conflict_model["conflict_triggers"]),
            "has_repair_requirements": bool(attachment_and_conflict_model["repair_requirements"]),
            "has_boundaries": bool(boundary_model["relationship_boundaries"]),
            "chunk4_relationship_ready": completeness >= 0.9,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        readiness_profile: Dict[str, Any],
        relationship_hooks: Dict[str, Any],
        compatibility_vectors: Dict[str, Any],
        attachment_and_conflict_model: Dict[str, Any],
        boundary_model: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="relationship_readiness",
            name=readiness_profile["readiness_name"],
            family=readiness_profile["relationship_readiness_family"],
            subtype=readiness_profile["attachment_pattern"],
            description=readiness_profile["vulnerability_model"],
            axes={
                "readiness_profile": readiness_profile,
                "relationship_hooks": relationship_hooks,
                "compatibility_vectors": compatibility_vectors,
                "attachment_and_conflict_model": attachment_and_conflict_model,
                "boundary_model": boundary_model,
            },
            tags=readiness_profile["similarity_tags"],
            examples=[readiness_profile["readiness_name"]],
            counterexamples=boundary_model["relationship_generation_constraints"],
            confidence_score=readiness_profile["confidence_score"],
            novelty_score=readiness_profile["novelty_score"],
            quality_score=readiness_profile["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        readiness_profile: Dict[str, Any],
        diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(
            readiness_profile["confidence_score"],
            readiness_profile["originality_score"],
            diagnostics["relationship_readiness_completeness_score"],
            0.95,
        )

        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8
        eligible = approved_source and provenance.usage_allowed and quality >= 0.75 and high_rating

        rejection_reasons = []

        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if quality < 0.75:
            rejection_reasons.append("quality score below threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=round(quality, 3),
            consistency_score=readiness_profile["confidence_score"],
            originality_score=readiness_profile["originality_score"],
            safety_score=0.88,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Relationship readiness schema includes compatibility, boundaries, repair, and conflict labels.",
                "Training eligibility requires approved source and sufficient quality.",
            ],
        )

    def _similarity_tags(
        self,
        *,
        family: str,
        attachment_pattern: str,
        trust_model: str,
        vulnerability_model: str,
        character_seed: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        destiny_profile: Dict[str, Any],
    ) -> List[str]:
        tags = {
            family,
            attachment_pattern,
            trust_model,
            skill_ontology.get("skill_family", "unknown_skill_family"),
            character_type_ontology.get("type_family", "unknown_type_family"),
            destiny_profile.get("destiny_family", "unknown_destiny_family"),
        }

        role = character_seed.get("role")
        if role:
            tags.add(str(role))

        for term in ["trust", "secret", "rivalry", "romance", "family", "destiny", "memory"]:
            if term in " ".join([family, attachment_pattern, trust_model, vulnerability_model]).lower():
                tags.add(term)

        return sorted(tags)

    def _retrieval_queries(self, family: str, attachment: str, trust: str, tags: List[str]) -> List[str]:
        return [
            f"relationship readiness ontology {family} {attachment}",
            f"trust repair boundary model {trust}",
            "friendship rivalry romance betrayal compatibility vectors",
            " ".join(tags[:8]),
        ]

    def _novelty_score(self, family: str, type_ontology: Dict[str, Any], destiny: Dict[str, Any]) -> float:
        score = 0.48

        if family not in {"general_relationship_readiness"}:
            score += 0.12

        if type_ontology.get("type_family") in {"power_redirector", "sacred_status_contradiction", "identity_erasure_character"}:
            score += 0.1

        if destiny.get("destiny_family"):
            score += 0.06

        return self._clamp(score)

    def _originality_score(self, family: str, attachment: str, vulnerability: str) -> float:
        score = 0.52

        if "secret" in attachment or "truth" in vulnerability:
            score += 0.1

        if family not in {"general_relationship_readiness"}:
            score += 0.08

        # Ontology-backed readiness families with specific attachment/vulnerability
        # models are stronger training candidates than generic relationship labels.
        if family in {
            "high_loyalty_power_broker_readiness",
            "romantic_agency_readiness",
            "rivalry_pressure_readiness",
            "antagonistic_mirror_readiness",
            "mentor_guidance_readiness",
        }:
            score += 0.08

        if attachment not in {"contextual_attachment"}:
            score += 0.04

        return self._clamp(score)

    def _confidence_score(self, family: str, psychology: Dict[str, Any], type_ontology: Dict[str, Any]) -> float:
        score = 0.56

        if psychology:
            score += 0.12

        if type_ontology:
            score += 0.1

        if family != "general_relationship_readiness":
            score += 0.08

        return self._clamp(score)

    def _readiness_name(self, family: str, attachment: str) -> str:
        return f"{family}:{attachment}"

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        readiness_profile: Dict[str, Any],
        relationship_hooks: Dict[str, Any],
        compatibility_vectors: Dict[str, Any],
        attachment_and_conflict_model: Dict[str, Any],
        boundary_model: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["relationship_readiness_profile"] = readiness_profile
        merged_seed["relationship_hooks"] = relationship_hooks
        merged_seed["compatibility_vectors"] = compatibility_vectors
        merged_seed["attachment_and_conflict_model"] = attachment_and_conflict_model
        merged_seed["relationship_boundary_model"] = boundary_model
        merged_seed["relationship_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "dialogue_voice_payload": {
                "character_seed": merged_seed,
                "relationship_readiness_profile": readiness_profile,
                "attachment_and_conflict_model": attachment_and_conflict_model,
                "boundary_model": boundary_model,
            },
            "chunk4_relationship_simulation_payload_later": {
                "character_id": readiness_profile["character_id"],
                "relationship_readiness_profile": readiness_profile,
                "relationship_hooks": relationship_hooks,
                "compatibility_vectors": compatibility_vectors,
                "attachment_and_conflict_model": attachment_and_conflict_model,
                "boundary_model": boundary_model,
            },
            "character_validator_payload": {
                "character_seed": merged_seed,
                "relationship_readiness_profile": readiness_profile,
                "boundary_model": boundary_model,
            },
            "chunk8_training_payload_later": {
                "target_type": "relationship_readiness",
                "relationship_readiness_profile": readiness_profile,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
