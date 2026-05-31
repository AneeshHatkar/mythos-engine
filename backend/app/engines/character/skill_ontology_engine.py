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


class SkillOntologyEngine(BaseEngine):
    """Classifies any skill/ability into scalable ontology dimensions.

    This engine is a bridge between deterministic generation and future ML/RAG
    learning. It should not treat "Pattern Reading" or "Flame Authority" as
    isolated hardcoded names. It decomposes any ability into reusable axes so
    future models can generalize to millions of unseen skills.
    """

    engine_name = "character.skill_ontology_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        skill_profile = payload.get("skill_profile") or character_seed.get("skill_profile", {})
        power_limits = payload.get("power_limits") or character_seed.get("power_limits", {})
        world_grounding = payload.get("world_grounding", {})
        world_constraints = payload.get("world_constraints", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed and not skill_profile:
            warnings.append("No character_seed or skill_profile provided; skill ontology engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or skill_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        skill_name = self._skill_name(character_seed, skill_profile)
        skill_description = self._skill_description(character_seed, skill_profile)
        inferred = self._infer_skill_ontology(
            skill_name=skill_name,
            skill_description=skill_description,
            character_seed=character_seed,
            skill_profile=skill_profile,
            power_limits=power_limits,
            world_constraints=world_constraints,
        )

        ontology_record = self._build_ontology_record(
            skill_name=skill_name,
            skill_description=skill_description,
            inferred=inferred,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_skill",
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
            type_name=skill_name,
            type_family="skill",
            type_subfamily=inferred["skill_family"],
            type_scope="character_skill",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=inferred["similarity_tags"],
            generation_constraints=inferred["generation_constraints"],
            counter_patterns=inferred["counter_family"],
            learned_axes=inferred,
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_skill",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=inferred["retrieval_context_queries"],
            generated_training_labels={
                "skill_name": skill_name,
                "skill_family": inferred["skill_family"],
                "skill_subtype": inferred["skill_subtype"],
                "activation_model": inferred["activation_model"],
                "cost_family": inferred["cost_family"],
                "counter_family": inferred["counter_family"],
                "growth_model": inferred["growth_model"],
                "power_scale": inferred["power_scale"],
                "world_legality_family": inferred["world_legality_family"],
                "adaptability_compatibility": inferred["adaptability_compatibility"],
                "destiny_compatibility": inferred["destiny_compatibility"],
            },
            learning_notes=[
                "This skill is represented as ontology axes, not as a fixed hardcoded ability.",
                "Future embeddings should retrieve neighboring skill families before generation.",
                "Future training should use these labels to generalize to unseen abilities.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            skill_profile=skill_profile,
            power_limits=power_limits,
            inferred=inferred,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "skill_ontology": inferred,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "skill_ontology_summary": {
                    "character_id": character_id,
                    "skill_name": skill_name,
                    "skill_family": inferred["skill_family"],
                    "skill_subtype": inferred["skill_subtype"],
                    "power_scale": inferred["power_scale"],
                    "activation_model": inferred["activation_model"],
                    "growth_model": inferred["growth_model"],
                    "adaptability_compatibility": inferred["adaptability_compatibility"],
                    "destiny_compatibility": inferred["destiny_compatibility"],
                    "training_eligible": training_eligibility.training_eligible,
                    "learned_from_data": ontology_record.learned_from_data,
                    "ready_for_adaptability_engine": True,
                    "ready_for_destiny_engine": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "The project should treat this ontology as the scalable skill representation.",
                    "Skill names are surface labels; ontology axes are the reusable learned structure.",
                    "Future data pipelines should update the registry with human-approved skill variants.",
                    "This engine prepares new skills for retrieval, similarity search, and training labels.",
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

    def _skill_name(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> str:
        return (
            skill_profile.get("primary_skill")
            or seed.get("primary_skill")
            or seed.get("skill_name")
            or "Adaptive Observation"
        )

    def _skill_description(self, seed: Dict[str, Any], skill_profile: Dict[str, Any]) -> str:
        return (
            seed.get("skill_description")
            or skill_profile.get("narrative_function")
            or f"{self._skill_name(seed, skill_profile)} used by a character under story pressure."
        )

    def _infer_skill_ontology(
        self,
        *,
        skill_name: str,
        skill_description: str,
        character_seed: Dict[str, Any],
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = " ".join(
            [
                skill_name,
                skill_description,
                str(character_seed),
                str(skill_profile),
                str(power_limits),
            ]
        ).lower()

        family, subtype = self._family_and_subtype(text, skill_profile)
        activation_model = self._activation_model(text, family, character_seed)
        cost_family = self._cost_family(text, family, power_limits)
        counter_family = self._counter_family(text, family, power_limits)
        growth_model = self._growth_model(text, family, skill_profile)
        power_scale = self._power_scale(text, skill_profile, character_seed)
        legality = self._world_legality_family(text, family, skill_profile, world_constraints)
        relationship_impact = self._relationship_impact(text, family)
        narrative_use = self._narrative_use(text, family, character_seed)
        similarity_tags = self._similarity_tags(family, subtype, activation_model, growth_model, text)

        adaptability = self._adaptability_compatibility(text, family, growth_model, character_seed)
        destiny = self._destiny_compatibility(text, family, character_seed)

        return {
            "skill_ontology_id": f"skonto_{uuid4().hex[:12]}",
            "skill_name": skill_name,
            "skill_family": family,
            "skill_subtype": subtype,
            "domain_cluster": self._domain_cluster(family),
            "activation_model": activation_model,
            "range_model": self._range_model(text, family),
            "resource_model": self._resource_model(cost_family),
            "cost_family": cost_family,
            "counter_family": counter_family,
            "growth_model": growth_model,
            "power_scale": power_scale,
            "world_legality_family": legality,
            "visibility_model": self._visibility_model(text, skill_profile, power_scale),
            "abuse_risk_model": self._abuse_risk_model(family, text),
            "relationship_impact_model": relationship_impact,
            "narrative_use_model": narrative_use,
            "training_data_axes": {
                "input_surface_name": skill_name,
                "family_label": family,
                "subtype_label": subtype,
                "activation_label": activation_model,
                "cost_labels": cost_family,
                "counter_labels": counter_family,
                "growth_label": growth_model,
                "scale_label": power_scale,
                "legality_label": legality,
            },
            "adaptability_compatibility": adaptability,
            "destiny_compatibility": destiny,
            "similarity_tags": similarity_tags,
            "generation_constraints": self._generation_constraints(cost_family, counter_family, power_scale),
            "retrieval_context_queries": self._retrieval_queries(skill_name, family, subtype, similarity_tags),
            "novelty_score": self._novelty_score(text, family, subtype),
            "originality_score": self._originality_score(text, family, subtype),
            "confidence_score": self._confidence_score(text, family, subtype),
        }

    def _family_and_subtype(self, text: str, skill_profile: Dict[str, Any]) -> tuple[str, str]:
        explicit_domain = skill_profile.get("skill_domain")

        # High-specificity / unusual ontology families must be checked before broad families.
        if any(term in text for term in ["dream", "memory map", "thread", "symbol", "vision", "sleeping minds"]):
            return "psychic_cognitive_mapping", "symbolic_navigation"

        if any(term in text for term in ["pattern", "inference", "read", "probability", "analysis", "detect"]):
            return "cognitive_inference", "pattern_detection"

        if any(term in text for term in ["fire", "flame", "water", "wind", "earth", "lightning", "ice", "element"]):
            return "elemental_authority", "element_control"

        if any(term in text for term in ["heal", "restore", "regenerate", "mend", "medicine"]):
            return "healing_restoration", "body_or_spirit_repair"

        if any(term in text for term in ["summon", "familiar", "spirit", "creature", "construct"]):
            return "summoning_binding", "external_entity_control"

        if any(term in text for term in ["curse", "hex", "decay", "rot", "blight"]):
            return "curse_affliction", "harmful_condition_imposition"

        if any(term in text for term in ["law", "oath", "court", "contract", "legal", "institution"]):
            return "institutional_authority", "rule_weaponization"

        if any(term in text for term in ["adapt", "limit", "breakthrough", "pressure", "threshold", "anomaly"]):
            return "adaptive_limit_system", "pressure_evolution"

        if any(term in text for term in ["sword", "combat", "martial", "weapon", "stance", "duel"]):
            return "martial_combat", "technique_execution"

        if any(term in text for term in ["social", "voice", "charm", "status", "persuasion", "influence"]):
            return "social_influence", "status_navigation"

        if any(term in text for term in ["machine", "technology", "device", "engineer", "code", "system"]):
            return "technological_craft", "system_manipulation"

        if explicit_domain:
            return f"{explicit_domain}_general", "generalized_skill"

        return "general_adaptive_skill", "contextual_problem_solving"

    def _activation_model(self, text: str, family: str, seed: Dict[str, Any]) -> str:
        if any(term in text for term in ["passive", "notice", "read", "sense", "detect"]):
            return "passive_focus"

        if any(term in text for term in ["ritual", "chant", "seal", "circle", "oath"]):
            return "ritual_conditioned"

        if seed.get("breakthrough_condition") or "threshold" in text or "pressure" in text:
            return "pressure_triggered"

        if any(term in text for term in ["touch", "contact", "blood"]):
            return "contact_triggered"

        if family in {"elemental_authority", "martial_combat", "curse_affliction"}:
            return "active_execution"

        return "contextual_activation"

    def _cost_family(self, text: str, family: str, power_limits: Dict[str, Any]) -> List[str]:
        costs = set()

        for cost in power_limits.get("costs", []):
            lowered = str(cost).lower()
            if "emotion" in lowered or "fear" in lowered or "shame" in lowered:
                costs.add("emotional_exposure")
            if "fatigue" in lowered or "mental" in lowered or "decision" in lowered:
                costs.add("mental_fatigue")
            if "body" in lowered or "injury" in lowered or "stamina" in lowered:
                costs.add("physical_strain")
            if "reputation" in lowered or "public" in lowered or "anonymity" in lowered:
                costs.add("social_visibility")
            if "memory" in lowered:
                costs.add("memory_distortion")

        if family == "cognitive_inference":
            costs.update(["mental_fatigue", "emotional_bias_risk"])

        elif family == "adaptive_limit_system":
            costs.update(["instability", "post_break_recovery", "identity_strain"])

        elif family == "elemental_authority":
            costs.update(["stamina_drain", "environmental_risk", "visibility"])

        elif family == "institutional_authority":
            costs.update(["legitimacy_risk", "public_accountability"])

        elif family == "healing_restoration":
            costs.update(["energy_transfer", "delayed_consequence"])

        elif family == "curse_affliction":
            costs.update(["moral_corrosion", "backlash_risk"])

        if not costs:
            costs.add("contextual_energy_cost")

        return sorted(costs)

    def _counter_family(self, text: str, family: str, power_limits: Dict[str, Any]) -> List[str]:
        counters = set()

        for counter in power_limits.get("limitations", []) + power_limits.get("cannot_do", []):
            lowered = str(counter).lower()
            if "evidence" in lowered or "false" in lowered or "misinform" in lowered:
                counters.add("false_signal")
            if "emotion" in lowered or "attached" in lowered:
                counters.add("emotional_bias")
            if "authority" in lowered or "legitimacy" in lowered:
                counters.add("legitimacy_break")
            if "recovery" in lowered or "repeat" in lowered:
                counters.add("recovery_window_attack")

        defaults = {
            "cognitive_inference": ["false_signal", "missing_evidence", "emotional_bias"],
            "psychic_cognitive_mapping": ["anchor_disruption", "symbol_corruption", "memory_noise"],
            "elemental_authority": ["opposing_element", "environment_denial", "resource_depletion"],
            "healing_restoration": ["wound_complexity", "energy_exhaustion", "delayed_backlash"],
            "summoning_binding": ["contract_break", "anchor_destroyed", "entity_rebellion"],
            "curse_affliction": ["purification", "backlash", "protective_oath"],
            "institutional_authority": ["jurisdiction_escape", "public_delegitimization", "counter_clause"],
            "adaptive_limit_system": ["pressure_denial", "recovery_window_attack", "instability_exploitation"],
            "martial_combat": ["terrain_shift", "rhythm_break", "fatigue"],
            "social_influence": ["isolation", "counter_rumor", "trust_anchor"],
            "technological_craft": ["system_patch", "power_loss", "hardware_constraint"],
            "general_adaptive_skill": ["context_denial", "resource_limit", "time_pressure"],
        }

        counters.update(defaults.get(family, defaults["general_adaptive_skill"]))
        return sorted(counters)

    def _growth_model(self, text: str, family: str, skill_profile: Dict[str, Any]) -> str:
        if family == "cognitive_inference":
            return "precision_refinement"

        if family == "adaptive_limit_system":
            return "threshold_expansion_with_recovery"

        if family in {"elemental_authority", "martial_combat"}:
            return "output_control_and_restraint"

        if family in {"institutional_authority", "social_influence"}:
            return "context_mastery_and_consequence_awareness"

        if family in {"psychic_cognitive_mapping", "curse_affliction"}:
            return "symbolic_accuracy_and_backlash_control"

        if family == "healing_restoration":
            return "cost_transfer_management"

        return "experience_based_generalization"

    def _power_scale(self, text: str, skill_profile: Dict[str, Any], seed: Dict[str, Any]) -> str:
        rarity = str(skill_profile.get("skill_rarity") or seed.get("skill_rarity", "")).lower()
        rank = str(skill_profile.get("skill_rank") or seed.get("skill_rank", "")).upper()

        if rarity in {"mythic", "legendary", "anomaly"} or rank in {"SS", "SSS"}:
            return "mythic_or_anomalous"

        if rarity in {"rare", "elite"} or rank == "S":
            return "rare_human_plus"

        if rank in {"A", "B"}:
            return "trained_elite"

        if any(term in text for term in ["god", "causality", "reality", "time", "fate"]):
            return "reality_scale"

        return "ordinary_to_trained"

    def _world_legality_family(
        self,
        text: str,
        family: str,
        skill_profile: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> str:
        existing = skill_profile.get("world_legality")
        if existing:
            return existing

        if "forbidden" in text or "illegal" in text:
            return "forbidden_or_illegal"

        if family in {"curse_affliction", "summoning_binding"}:
            return "restricted_or_taboo"

        if family == "institutional_authority":
            return "regulated_by_institution"

        if family == "adaptive_limit_system":
            return "unclassified_by_current_law"

        if world_constraints.get("commoner_royal_magic_restricted") and family in {"elemental_authority", "healing_restoration"}:
            return "class_restricted"

        return "legal_but_context_dependent"

    def _relationship_impact(self, text: str, family: str) -> Dict[str, str]:
        return {
            "friendship": "creates reliance but may create fear if cost is visible",
            "romance": "requires consent and boundaries when ability reads, changes, heals, or exposes truth",
            "rivalry": "creates counter-training and comparison pressure",
            "enemy": "makes the character a tactical or symbolic target",
            "mentor": "requires teaching limits, not only increasing output",
            "family": "may become family asset, burden, secret, or bargaining chip",
        }

    def _narrative_use(self, text: str, family: str, seed: Dict[str, Any]) -> str:
        if family == "cognitive_inference":
            return "reveals hidden systems, lies, patterns, and future risks before proof is socially accepted"

        if family == "adaptive_limit_system":
            return "creates earned breakthrough under pressure with aftermath and cost"

        if family == "institutional_authority":
            return "turns rules, law, or procedure into power and moral pressure"

        if family == "elemental_authority":
            return "externalizes emotion, status, and destructive/creative force"

        if family == "healing_restoration":
            return "forces choices about who deserves repair and what healing costs"

        return "creates agency while requiring cost, limitation, and consequence"

    def _domain_cluster(self, family: str) -> str:
        if family in {"cognitive_inference", "psychic_cognitive_mapping"}:
            return "mind_information"

        if family in {"elemental_authority", "martial_combat"}:
            return "force_conflict"

        if family in {"institutional_authority", "social_influence"}:
            return "social_system_power"

        if family in {"healing_restoration", "curse_affliction"}:
            return "body_spirit_condition"

        if family in {"adaptive_limit_system"}:
            return "meta_growth"

        return "general_capability"

    def _range_model(self, text: str, family: str) -> str:
        if any(term in text for term in ["area", "army", "city", "kingdom", "world"]):
            return "area_or_societal_scale"

        if any(term in text for term in ["touch", "contact"]):
            return "contact_range"

        if family in {"cognitive_inference", "social_influence", "institutional_authority"}:
            return "social_or_contextual_range"

        if family in {"elemental_authority", "martial_combat"}:
            return "physical_scene_range"

        return "contextual_range"

    def _resource_model(self, cost_family: List[str]) -> str:
        if "mental_fatigue" in cost_family:
            return "cognitive_resource"

        if "stamina_drain" in cost_family or "physical_strain" in cost_family:
            return "physical_resource"

        if "social_visibility" in cost_family or "legitimacy_risk" in cost_family:
            return "social_resource"

        if "moral_corrosion" in cost_family:
            return "ethical_resource"

        return "mixed_resource"

    def _visibility_model(self, text: str, skill_profile: Dict[str, Any], power_scale: str) -> str:
        if power_scale in {"mythic_or_anomalous", "reality_scale"}:
            return "impossible_to_hide_after_major_use"

        if "hidden" in text or "secret" in text:
            return "hidden_until_consequence"

        if skill_profile.get("social_visibility"):
            return skill_profile["social_visibility"]

        return "visible_when_demonstrated"

    def _abuse_risk_model(self, family: str, text: str) -> str:
        risks = {
            "cognitive_inference": "dehumanizing_people_as_patterns",
            "institutional_authority": "law_as_weapon",
            "social_influence": "consent_and_manipulation_risk",
            "adaptive_limit_system": "chasing_breakthrough_over_recovery",
            "curse_affliction": "harm_as_identity",
            "healing_restoration": "savior_control_complex",
            "elemental_authority": "collateral_damage",
        }
        return risks.get(family, "power_without_consequence")

    def _similarity_tags(
        self,
        family: str,
        subtype: str,
        activation_model: str,
        growth_model: str,
        text: str,
    ) -> List[str]:
        tags = {
            family,
            subtype,
            activation_model,
            growth_model,
            self._domain_cluster(family),
        }

        for term in [
            "inference",
            "dream",
            "fire",
            "healing",
            "curse",
            "law",
            "adaptation",
            "combat",
            "social",
            "technology",
            "destiny",
            "memory",
        ]:
            if term in text:
                tags.add(term)

        return sorted(tags)

    def _adaptability_compatibility(
        self,
        text: str,
        family: str,
        growth_model: str,
        seed: Dict[str, Any],
    ) -> float:
        score = 0.35

        if family == "adaptive_limit_system":
            score += 0.42

        if "threshold" in growth_model or "pressure" in text or seed.get("breakthrough_condition"):
            score += 0.24

        if family in {"cognitive_inference", "martial_combat"}:
            score += 0.12

        return self._clamp(score)

    def _destiny_compatibility(self, text: str, family: str, seed: Dict[str, Any]) -> float:
        score = 0.3

        if seed.get("destiny_type") or "fate" in text or "prophecy" in text:
            score += 0.32

        if family in {"cognitive_inference", "adaptive_limit_system", "psychic_cognitive_mapping"}:
            score += 0.18

        if family in {"elemental_authority", "healing_restoration", "curse_affliction"}:
            score += 0.12

        return self._clamp(score)

    def _generation_constraints(self, costs: List[str], counters: List[str], power_scale: str) -> List[str]:
        constraints = [
            "must include explicit cost",
            "must include at least one counterplay route",
            "must include failure mode",
            "must not solve all conflicts automatically",
        ]

        if power_scale in {"mythic_or_anomalous", "reality_scale"}:
            constraints.append("must include severe consequence and social/world visibility")

        for cost in costs[:3]:
            constraints.append(f"must respect cost family: {cost}")

        for counter in counters[:3]:
            constraints.append(f"must allow counter family: {counter}")

        return constraints

    def _retrieval_queries(self, skill_name: str, family: str, subtype: str, tags: List[str]) -> List[str]:
        return [
            f"skill ontology similar to {skill_name}",
            f"{family} {subtype} ability examples",
            f"cost counterplay growth model for {family}",
            " ".join(tags[:6]),
        ]

    def _novelty_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.45

        if any(term in text for term in ["dream", "causality", "memory", "oath", "thread", "anomaly"]):
            score += 0.18

        if family not in {"general_adaptive_skill", "martial_combat"}:
            score += 0.12

        if subtype not in {"generalized_skill", "technique_execution"}:
            score += 0.08

        return self._clamp(score)

    def _originality_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.5

        if "cost" in text or "limit" in text or "counter" in text:
            score += 0.1

        if any(term in text for term in ["institution", "oath", "memory", "threshold", "family", "reputation"]):
            score += 0.12

        if family == "general_adaptive_skill":
            score -= 0.08

        return self._clamp(score)

    def _confidence_score(self, text: str, family: str, subtype: str) -> float:
        score = 0.55

        if family != "general_adaptive_skill":
            score += 0.18

        if subtype != "generalized_skill":
            score += 0.12

        if len(text.split()) >= 20:
            score += 0.08

        return self._clamp(score)

    def _build_ontology_record(
        self,
        *,
        skill_name: str,
        skill_description: str,
        inferred: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="skill",
            name=skill_name,
            family=inferred["skill_family"],
            subtype=inferred["skill_subtype"],
            description=skill_description,
            axes={
                "domain_cluster": inferred["domain_cluster"],
                "activation_model": inferred["activation_model"],
                "range_model": inferred["range_model"],
                "resource_model": inferred["resource_model"],
                "cost_family": inferred["cost_family"],
                "counter_family": inferred["counter_family"],
                "growth_model": inferred["growth_model"],
                "power_scale": inferred["power_scale"],
                "world_legality_family": inferred["world_legality_family"],
                "visibility_model": inferred["visibility_model"],
                "abuse_risk_model": inferred["abuse_risk_model"],
                "adaptability_compatibility": inferred["adaptability_compatibility"],
                "destiny_compatibility": inferred["destiny_compatibility"],
            },
            tags=inferred["similarity_tags"],
            examples=[skill_name],
            counterexamples=inferred["counter_family"],
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
        quality = min(
            inferred["confidence_score"],
            inferred["originality_score"],
            0.95,
        )

        human_approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is not None and float(user_rating) >= 8

        eligible = human_approved_source and provenance.usage_allowed and quality >= 0.7 and (
            user_rating is None or high_rating
        )

        rejection_reasons = []

        if not human_approved_source:
            rejection_reasons.append("source mode is not approved for training")

        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")

        if quality < 0.7:
            rejection_reasons.append("quality score below threshold")

        if user_rating is not None and not high_rating:
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
                "Ontology labels generated for future retrieval/training.",
                "Training eligibility is conservative until provenance and review are clear.",
            ],
        )

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        skill_profile: Dict[str, Any],
        power_limits: Dict[str, Any],
        inferred: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["skill_ontology"] = inferred
        merged_seed["skill_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "adaptability_engine_payload": {
                "character_seed": merged_seed,
                "skill_profile": skill_profile,
                "power_limits": power_limits,
                "skill_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "destiny_engine_payload": {
                "character_seed": merged_seed,
                "skill_profile": skill_profile,
                "skill_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "character_type_ontology_payload": {
                "character_seed": merged_seed,
                "skill_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "chunk8_training_payload_later": {
                "target_type": "character_skill",
                "skill_ontology": inferred,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
