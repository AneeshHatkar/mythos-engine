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


class CharacterTypeOntologyEngine(BaseEngine):
    """Classifies character/people types into scalable ontology dimensions.

    This prevents the project from relying on fixed labels like "rival",
    "chosen one", "hidden kingmaker", or "failed prodigy" as hardcoded types.

    Any character type is decomposed into reusable axes so future ML/RAG systems
    can learn, retrieve, combine, mutate, and invent new character types.
    """

    engine_name = "character.character_type_ontology_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        people_type = payload.get("people_type") or character_seed.get("people_type", {})
        if isinstance(people_type, str):
            people_type = {"name": people_type, "description": character_seed.get("type_description", people_type)}

        population_context = payload.get("population_context", {})
        world_state = payload.get("world_state", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        reputation_profile = payload.get("reputation_profile") or character_seed.get("reputation", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed and not people_type:
            warnings.append("No character_seed or people_type provided; character type ontology engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or people_type.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        type_name = self._type_name(character_seed, people_type)
        type_description = self._type_description(character_seed, people_type, goal_profile)

        inferred = self._infer_type_ontology(
            type_name=type_name,
            type_description=type_description,
            character_seed=character_seed,
            people_type=people_type,
            population_context=population_context,
            world_state=world_state,
            skill_ontology=skill_ontology,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            reputation_profile=reputation_profile,
        )

        ontology_record = self._build_ontology_record(
            type_name=type_name,
            type_description=type_description,
            inferred=inferred,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_type",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=inferred["similarity_tags"],
            novelty_score=inferred["novelty_score"],
            originality_score=inferred["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            inferred=inferred,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=type_name,
            type_family="character_type",
            type_subfamily=inferred["type_family"],
            type_scope="character",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=inferred["similarity_tags"],
            generation_constraints=inferred["generation_constraints"],
            counter_patterns=inferred["anti_cliche_patterns"],
            learned_axes=inferred,
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_type",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=inferred["retrieval_context_queries"],
            generated_training_labels={
                "type_name": type_name,
                "type_family": inferred["type_family"],
                "type_subtype": inferred["type_subtype"],
                "role_function": inferred["role_function"],
                "social_position": inferred["social_position"],
                "power_access": inferred["power_access"],
                "psychological_pattern": inferred["psychological_pattern"],
                "relationship_function": inferred["relationship_function"],
                "plot_function": inferred["plot_function"],
                "agency_level": inferred["agency_level"],
                "threat_level": inferred["threat_level"],
                "adaptability_potential": inferred["adaptability_potential"],
                "destiny_relevance": inferred["destiny_relevance"],
            },
            learning_notes=[
                "Character type labels are surface names; ontology axes are the scalable representation.",
                "Future retrieval should use role, social, psychological, relationship, and plot axes.",
                "Future training should learn type combinations from curated people/story datasets.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            people_type=people_type,
            inferred=inferred,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "character_type_ontology": inferred,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "character_type_ontology_summary": {
                    "character_id": character_id,
                    "type_name": type_name,
                    "type_family": inferred["type_family"],
                    "type_subtype": inferred["type_subtype"],
                    "role_function": inferred["role_function"],
                    "social_position": inferred["social_position"],
                    "power_access": inferred["power_access"],
                    "agency_level": inferred["agency_level"],
                    "threat_level": inferred["threat_level"],
                    "adaptability_potential": inferred["adaptability_potential"],
                    "destiny_relevance": inferred["destiny_relevance"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_adaptability_engine": True,
                    "ready_for_destiny_engine": True,
                    "ready_for_relationship_readiness_engine": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "People/character types should be learned as combinations of axes, not fixed archetype labels.",
                    "Future datasets can add new type families without rewriting engine logic.",
                    "This ontology supports new heroes, villains, rivals, lovers, mentors, societies, and hybrid character types.",
                    "Use these labels for retrieval, similarity search, originality scoring, and future model training.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _type_name(self, seed: Dict[str, Any], people_type: Dict[str, Any]) -> str:
        return (
            people_type.get("name")
            or people_type.get("people_type_name")
            or seed.get("people_type")
            or seed.get("character_type")
            or seed.get("role")
            or "Unresolved Character Type"
        )

    def _type_description(
        self,
        seed: Dict[str, Any],
        people_type: Dict[str, Any],
        goal: Dict[str, Any],
    ) -> str:
        if people_type.get("description"):
            return people_type["description"]

        if seed.get("type_description"):
            return seed["type_description"]

        pieces = [
            f"Role: {seed.get('role', 'unknown')}",
            f"Social class: {seed.get('social_class', 'unknown')}",
            f"Goal: {goal.get('surface_goal') or seed.get('surface_goal') or seed.get('hidden_goal') or 'unknown'}",
        ]

        return ". ".join(pieces)

    def _infer_type_ontology(
        self,
        *,
        type_name: str,
        type_description: str,
        character_seed: Dict[str, Any],
        people_type: Dict[str, Any],
        population_context: Dict[str, Any],
        world_state: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        reputation_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = " ".join(
            [
                type_name,
                type_description,
                str(character_seed),
                str(people_type),
                str(population_context),
                str(world_state),
                str(skill_ontology),
                str(moral_profile),
                str(goal_profile),
                str(reputation_profile),
            ]
        ).lower()

        type_family, type_subtype = self._family_and_subtype(text, character_seed)
        role_function = self._role_function(text, character_seed, people_type)
        social_position = self._social_position(text, character_seed, reputation_profile)
        power_access = self._power_access(text, character_seed, skill_ontology)
        psychological_pattern = self._psychological_pattern(text, character_seed)
        moral_tendency = self._moral_tendency(text, moral_profile, character_seed)
        relationship_function = self._relationship_function(text, character_seed)
        plot_function = self._plot_function(text, type_family, role_function, goal_profile)
        world_pressure = self._world_pressure(text, character_seed, world_state)
        agency_level = self._agency_level(text, character_seed, goal_profile)
        threat_level = self._threat_level(text, character_seed, skill_ontology, reputation_profile)

        adaptability_potential = self._adaptability_potential(
            text=text,
            type_family=type_family,
            skill_ontology=skill_ontology,
            character_seed=character_seed,
        )
        destiny_relevance = self._destiny_relevance(
            text=text,
            type_family=type_family,
            skill_ontology=skill_ontology,
            character_seed=character_seed,
        )

        similarity_tags = self._similarity_tags(
            type_family=type_family,
            type_subtype=type_subtype,
            role_function=role_function,
            social_position=social_position,
            psychological_pattern=psychological_pattern,
            relationship_function=relationship_function,
            plot_function=plot_function,
            text=text,
        )

        return {
            "character_type_ontology_id": f"ctypeonto_{uuid4().hex[:12]}",
            "type_name": type_name,
            "type_family": type_family,
            "type_subtype": type_subtype,
            "role_function": role_function,
            "social_position": social_position,
            "power_access": power_access,
            "psychological_pattern": psychological_pattern,
            "moral_tendency": moral_tendency,
            "relationship_function": relationship_function,
            "plot_function": plot_function,
            "world_pressure": world_pressure,
            "agency_level": agency_level,
            "threat_level": threat_level,
            "adaptability_potential": adaptability_potential,
            "destiny_relevance": destiny_relevance,
            "compatibility_axes": {
                "romance_compatibility": self._romance_compatibility(text, relationship_function),
                "rivalry_compatibility": self._rivalry_compatibility(text, role_function),
                "mentor_compatibility": self._mentor_compatibility(text, role_function),
                "villain_pressure_compatibility": self._villain_pressure_compatibility(text, threat_level),
                "ensemble_utility": self._ensemble_utility(role_function, plot_function),
            },
            "scaling_axes": {
                "role_axis": role_function,
                "status_axis": social_position,
                "power_axis": power_access,
                "psyche_axis": psychological_pattern,
                "ethics_axis": moral_tendency,
                "relationship_axis": relationship_function,
                "plot_axis": plot_function,
                "world_pressure_axis": world_pressure,
                "agency_axis": agency_level,
                "threat_axis": threat_level,
            },
            "anti_cliche_patterns": self._anti_cliche_patterns(type_family, relationship_function, plot_function),
            "generation_constraints": self._generation_constraints(type_family, role_function, social_position, power_access),
            "retrieval_context_queries": self._retrieval_queries(type_name, type_family, type_subtype, similarity_tags),
            "similarity_tags": similarity_tags,
            "novelty_score": self._novelty_score(text, type_family, type_subtype),
            "originality_score": self._originality_score(text, type_family, type_subtype),
            "confidence_score": self._confidence_score(text, type_family, type_subtype),
        }

    def _family_and_subtype(self, text: str, seed: Dict[str, Any]) -> tuple[str, str]:
        role = seed.get("role", "").lower()

        # Specific high-signal type families first.
        if any(term in text for term in ["kingmaker", "hidden influence", "redirects power", "power flow"]):
            return "power_redirector", "hidden_kingmaker"

        if any(term in text for term in ["failed prodigy", "former prodigy", "disgraced prodigy"]):
            return "status_fall_character", "failed_prodigy"

        if any(term in text for term in ["false saint", "holy fraud", "fake saint"]):
            return "sacred_status_contradiction", "false_saint"

        if any(term in text for term in ["banished heir", "exiled heir", "lost heir"]):
            return "displaced_legacy", "banished_heir"

        if any(term in text for term in ["monster prince", "beast heir", "inhuman royal"]):
            return "hybrid_identity_power", "monstrous_nobility"

        if any(term in text for term in ["memory-eating", "memory eating", "eats memory"]):
            return "identity_erasure_character", "memory_consuming_figure"

        if any(term in text for term in ["villain", "antagonist", "magister", "tyrant"]):
            return "oppositional_force", "ideological_antagonist"

        if any(term in text for term in ["love interest", "romance", "beloved"]):
            return "intimacy_axis_character", "independent_love_interest"

        if any(term in text for term in ["rival", "competitor", "mirror"]):
            return "mirror_pressure_character", "rival_mirror"

        if any(term in text for term in ["mentor", "teacher", "guardian"]):
            return "guidance_power_character", "mentor_or_guardian"

        if role == "protagonist":
            return "central_agency_character", "protagonist_driver"

        return "general_ensemble_character", "contextual_role"

    def _role_function(self, text: str, seed: Dict[str, Any], people_type: Dict[str, Any]) -> List[str]:
        functions = set()

        role = seed.get("role", "").lower()
        compatible = people_type.get("compatible_roles", [])

        for item in compatible:
            functions.add(str(item))

        if role:
            functions.add(role)

        if "kingmaker" in text or "redirects power" in text:
            functions.update(["catalyst", "strategist", "power_redirector"])

        if "rival" in text:
            functions.update(["mirror", "pressure_character", "competitive_force"])

        if "villain" in text or "antagonist" in text:
            functions.update(["opposer", "ideological_pressure", "system_embodiment"])

        if "love interest" in text or "romance" in text:
            functions.update(["intimacy_test", "independent_desire_holder"])

        if "mentor" in text:
            functions.update(["guide", "gatekeeper", "legacy_transmitter"])

        if "protagonist" in text:
            functions.update(["main_agent", "choice_driver"])

        if not functions:
            functions.update(["ensemble_pressure", "witness", "choice_consequence"])

        return sorted(functions)

    def _social_position(self, text: str, seed: Dict[str, Any], reputation: Dict[str, Any]) -> str:
        social_class = seed.get("social_class", "").lower()
        family_status = seed.get("family_name_status", "").lower()

        if "low visible" in text or "hidden influence" in text:
            return "low_visible_status_high_hidden_influence"

        if social_class in {"erased", "underclass"} or family_status == "erased":
            return "socially_erased_or_low_trust"

        if social_class in {"old_nobility", "imperial_elite"}:
            return "high_visible_status_high_constraint"

        if social_class == "academy_sponsored":
            return "conditional_access_merit_position"

        if reputation.get("exposure_risk", 0.0) >= 0.6:
            return "unstable_public_status"

        if "banished" in text or "exiled" in text:
            return "displaced_high_status"

        return "context_dependent_social_position"

    def _power_access(self, text: str, seed: Dict[str, Any], skill_ontology: Dict[str, Any]) -> str:
        family = skill_ontology.get("skill_family", "")
        scale = skill_ontology.get("power_scale", "")

        if "kingmaker" in text or "strategist" in text or "hidden influence" in text:
            return "indirect_systemic_influence"

        if family in {"adaptive_limit_system"}:
            return "conditional_breakthrough_power"

        if scale in {"mythic_or_anomalous", "reality_scale"}:
            return "rare_high_impact_power"

        if family in {"institutional_authority", "social_influence"}:
            return "social_or_institutional_power"

        if family in {"cognitive_inference", "psychic_cognitive_mapping"}:
            return "information_asymmetry_power"

        if seed.get("skill_rarity") in {"S", "SS", "SSS", "rare", "anomaly", "mythic"}:
            return "rare_individual_power"

        return "ordinary_or_contextual_power"

    def _psychological_pattern(self, text: str, seed: Dict[str, Any]) -> str:
        if "unseen" in text or "hidden" in text:
            return "unseen_worth_and_controlled_visibility"

        if "failed" in text or "prodigy" in text:
            return "worth_bound_to_performance"

        if "banished" in text or "exiled" in text:
            return "belonging_loss_and_legacy_hunger"

        if "false saint" in text:
            return "public_purity_private_contradiction"

        if "villain" in text or seed.get("role") == "villain":
            return "fear_of_chaos_transformed_into_control"

        if "rival" in text:
            return "comparison_wound_and_respect_hunger"

        if "love" in text or "romance" in text:
            return "intimacy_vs_independence_tension"

        return "identity_pressure_and_unresolved_need"

    def _moral_tendency(self, text: str, moral: Dict[str, Any], seed: Dict[str, Any]) -> str:
        dominant = moral.get("dominant_moral_value")
        corruption = moral.get("corruption_risk", 0.0)

        if seed.get("role") == "villain" or corruption >= 0.6:
            return "order_control_or_corruption_prone"

        if dominant:
            return f"{dominant}_centered"

        if "protect" in text or "weaker" in text:
            return "protective_justice"

        if "truth" in text or "proof" in text:
            return "truth_seeking"

        return "contextual_ethics_under_pressure"

    def _relationship_function(self, text: str, seed: Dict[str, Any]) -> str:
        role = seed.get("role", "").lower()

        if "love interest" in text or role == "love_interest":
            return "romantic_axis_with_independent_agency"

        if "rival" in text or role == "rival":
            return "rivalry_to_respect_or_obsession"

        if "mentor" in text or role == "mentor":
            return "guidance_control_or_liberation"

        if "villain" in text or role == "villain":
            return "moral_pressure_and_antagonistic_mirror"

        if "kingmaker" in text:
            return "slow_trust_high_loyalty_power_broker"

        if "friend" in text:
            return "loyalty_test_and_support_anchor"

        return "relationship_pressure_or_witness_function"

    def _plot_function(
        self,
        text: str,
        type_family: str,
        role_function: List[str],
        goal: Dict[str, Any],
    ) -> str:
        if type_family == "power_redirector":
            return "redirects_power_flow_and_changes_who_can_win"

        if type_family == "status_fall_character":
            return "shows_the_cost_of_rank_systems_and_recovery"

        if type_family == "oppositional_force":
            return "forces_story_to_define_its_moral_center"

        if type_family == "intimacy_axis_character":
            return "tests_whether_love_can_coexist_with_agency"

        if type_family == "mirror_pressure_character":
            return "externalizes_comparison_and_growth_pressure"

        if goal.get("surface_goal"):
            return f"drives_or_complicates_goal: {goal['surface_goal']}"

        return "adds_choice_pressure_consequence_and_social_texture"

    def _world_pressure(self, text: str, seed: Dict[str, Any], world_state: Dict[str, Any]) -> List[str]:
        pressures = set()

        if "academy" in text:
            pressures.add("academy_gatekeeping")

        if "class" in text or seed.get("social_class"):
            pressures.add("class_hierarchy")

        if "family" in text or seed.get("family_name_status"):
            pressures.add("family_name_legitimacy")

        if "destiny" in text or seed.get("destiny_type"):
            pressures.add("destiny_classification")

        if "law" in text or "oath" in text:
            pressures.add("legal_or_oath_system")

        if "empire" in str(world_state).lower():
            pressures.add("imperial_pressure")

        if not pressures:
            pressures.add("local_social_pressure")

        return sorted(pressures)

    def _agency_level(self, text: str, seed: Dict[str, Any], goal: Dict[str, Any]) -> str:
        score = 0.45

        if seed.get("role") in {"protagonist", "villain", "rival"}:
            score += 0.2

        if goal.get("agency_score", 0.0) >= 0.65:
            score += 0.2

        if "kingmaker" in text or "strategist" in text:
            score += 0.18

        if "erased" in text or "underclass" in text:
            score -= 0.08

        if score >= 0.78:
            return "high_agency"

        if score >= 0.5:
            return "medium_agency"

        return "low_to_emerging_agency"

    def _threat_level(
        self,
        text: str,
        seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        reputation: Dict[str, Any],
    ) -> str:
        score = 0.25

        if seed.get("role") in {"villain", "antagonist"}:
            score += 0.35

        if skill_ontology.get("power_scale") in {"mythic_or_anomalous", "reality_scale"}:
            score += 0.25

        if skill_ontology.get("skill_family") in {"cognitive_inference", "adaptive_limit_system", "institutional_authority"}:
            score += 0.12

        if reputation.get("enemy_threat_reputation", 0.0) >= 0.55:
            score += 0.14

        if "kingmaker" in text:
            score += 0.18

        if score >= 0.75:
            return "severe_threat"

        if score >= 0.5:
            return "meaningful_threat"

        return "low_or_latent_threat"

    def _adaptability_potential(
        self,
        *,
        text: str,
        type_family: str,
        skill_ontology: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> float:
        score = 0.35

        if character_seed.get("adaptability_type") or character_seed.get("breakthrough_condition"):
            score += 0.28

        if skill_ontology.get("adaptability_compatibility", 0.0):
            score += float(skill_ontology["adaptability_compatibility"]) * 0.25

        if type_family in {"power_redirector", "status_fall_character", "mirror_pressure_character"}:
            score += 0.12

        if "limit" in text or "breakthrough" in text or "pressure" in text:
            score += 0.14

        return self._clamp(score)

    def _destiny_relevance(
        self,
        *,
        text: str,
        type_family: str,
        skill_ontology: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> float:
        score = 0.3

        if character_seed.get("destiny_type") or "destiny" in text or "prophecy" in text:
            score += 0.32

        if skill_ontology.get("destiny_compatibility", 0.0):
            score += float(skill_ontology["destiny_compatibility"]) * 0.2

        if type_family in {"power_redirector", "displaced_legacy", "sacred_status_contradiction"}:
            score += 0.16

        return self._clamp(score)

    def _romance_compatibility(self, text: str, relationship_function: str) -> float:
        score = 0.35

        if "romantic" in relationship_function or "love" in text or "intimacy" in text:
            score += 0.35

        if "slow_trust" in relationship_function:
            score += 0.18

        if "villain" in text:
            score -= 0.08

        return self._clamp(score)

    def _rivalry_compatibility(self, text: str, role_function: List[str]) -> float:
        score = 0.32

        if "rival" in text or "mirror" in role_function or "pressure_character" in role_function:
            score += 0.38

        if "prodigy" in text or "academy" in text:
            score += 0.16

        return self._clamp(score)

    def _mentor_compatibility(self, text: str, role_function: List[str]) -> float:
        score = 0.28

        if "mentor" in text or "guide" in role_function or "legacy_transmitter" in role_function:
            score += 0.42

        if "kingmaker" in text or "strategist" in role_function:
            score += 0.12

        return self._clamp(score)

    def _villain_pressure_compatibility(self, text: str, threat_level: str) -> float:
        score = 0.3

        if "villain" in text or "antagonist" in text:
            score += 0.4

        if threat_level in {"meaningful_threat", "severe_threat"}:
            score += 0.2

        return self._clamp(score)

    def _ensemble_utility(self, role_function: List[str], plot_function: str) -> float:
        score = 0.35 + min(0.35, len(role_function) * 0.06)

        if "choice" in plot_function or "power" in plot_function or "moral" in plot_function:
            score += 0.16

        return self._clamp(score)

    def _similarity_tags(
        self,
        *,
        type_family: str,
        type_subtype: str,
        role_function: List[str],
        social_position: str,
        psychological_pattern: str,
        relationship_function: str,
        plot_function: str,
        text: str,
    ) -> List[str]:
        tags = {
            type_family,
            type_subtype,
            social_position,
            psychological_pattern,
            relationship_function,
            plot_function,
        }

        tags.update(role_function)

        for term in [
            "academy",
            "class",
            "destiny",
            "kingmaker",
            "rival",
            "villain",
            "romance",
            "mentor",
            "family",
            "hidden",
            "prodigy",
            "exile",
            "saint",
            "monster",
            "memory",
        ]:
            if term in text:
                tags.add(term)

        return sorted(tags)

    def _anti_cliche_patterns(self, type_family: str, relationship_function: str, plot_function: str) -> List[str]:
        rules = [
            "must include agency beyond trope label",
            "must include contradiction or pressure source",
            "must include cost for power or social position",
            "must avoid making role function the entire personality",
        ]

        if type_family == "intimacy_axis_character":
            rules.append("love interest must have independent goals and non-romance stakes")

        if type_family == "oppositional_force":
            rules.append("villain needs ideology, wound, pressure, and internally consistent ethics")

        if type_family == "power_redirector":
            rules.append("kingmaker influence must create consequence and vulnerability")

        if type_family == "status_fall_character":
            rules.append("failed prodigy cannot only be jealous; must have worldview shaped by failure")

        return rules

    def _generation_constraints(
        self,
        type_family: str,
        role_function: List[str],
        social_position: str,
        power_access: str,
    ) -> List[str]:
        constraints = [
            "must include world pressure",
            "must include agency level",
            "must include relationship function",
            "must include plot function",
            "must include internal contradiction",
            "must include anti-cliche rule",
        ]

        constraints.append(f"must respect type family: {type_family}")
        constraints.append(f"must respect social position: {social_position}")
        constraints.append(f"must respect power access: {power_access}")

        for function in role_function[:4]:
            constraints.append(f"must support role function: {function}")

        return constraints

    def _retrieval_queries(self, type_name: str, family: str, subtype: str, tags: List[str]) -> List[str]:
        return [
            f"character type ontology similar to {type_name}",
            f"{family} {subtype} character examples",
            f"role social psychology plot axes for {family}",
            " ".join(tags[:8]),
        ]

    def _novelty_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.45

        if family not in {"general_ensemble_character"}:
            score += 0.16

        if subtype not in {"contextual_role"}:
            score += 0.12

        if any(term in text for term in ["memory", "kingmaker", "false saint", "monster", "banished", "hidden"]):
            score += 0.12

        return self._clamp(score)

    def _originality_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.5

        if any(term in text for term in ["cost", "pressure", "contradiction", "agency", "world", "family"]):
            score += 0.12

        if family in {"power_redirector", "sacred_status_contradiction", "identity_erasure_character"}:
            score += 0.1

        if family == "general_ensemble_character":
            score -= 0.06

        return self._clamp(score)

    def _confidence_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.55

        if family != "general_ensemble_character":
            score += 0.18

        if subtype != "contextual_role":
            score += 0.12

        if len(text.split()) >= 20:
            score += 0.08

        return self._clamp(score)

    def _build_ontology_record(
        self,
        *,
        type_name: str,
        type_description: str,
        inferred: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="people_type",
            name=type_name,
            family=inferred["type_family"],
            subtype=inferred["type_subtype"],
            description=type_description,
            axes={
                "role_function": inferred["role_function"],
                "social_position": inferred["social_position"],
                "power_access": inferred["power_access"],
                "psychological_pattern": inferred["psychological_pattern"],
                "moral_tendency": inferred["moral_tendency"],
                "relationship_function": inferred["relationship_function"],
                "plot_function": inferred["plot_function"],
                "world_pressure": inferred["world_pressure"],
                "agency_level": inferred["agency_level"],
                "threat_level": inferred["threat_level"],
                "adaptability_potential": inferred["adaptability_potential"],
                "destiny_relevance": inferred["destiny_relevance"],
                "compatibility_axes": inferred["compatibility_axes"],
            },
            tags=inferred["similarity_tags"],
            examples=[type_name],
            counterexamples=inferred["anti_cliche_patterns"],
            confidence_score=inferred["confidence_score"],
            novelty_score=inferred["novelty_score"],
            quality_score=inferred["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        inferred: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(inferred["confidence_score"], inferred["originality_score"], 0.95)
        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8

        eligible = approved_source and provenance.usage_allowed and quality >= 0.7 and high_rating

        rejection_reasons = []

        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")

        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")

        if quality < 0.7:
            rejection_reasons.append("quality score below threshold")

        if not high_rating:
            rejection_reasons.append("human rating below training threshold")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=round(quality, 3),
            consistency_score=inferred["confidence_score"],
            originality_score=inferred["originality_score"],
            safety_score=0.86,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Character type ontology labels generated for future retrieval/training.",
                "Training eligibility remains conservative until source provenance is approved.",
            ],
        )

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        people_type: Dict[str, Any],
        inferred: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["character_type_ontology"] = inferred
        merged_seed["character_type_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "people_type": people_type,
                "character_type_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "destiny_engine_payload": {
                "character_seed": merged_seed,
                "character_type_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "relationship_readiness_payload": {
                "character_seed": merged_seed,
                "character_type_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "chunk8_training_payload_later": {
                "target_type": "character_type",
                "character_type_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
