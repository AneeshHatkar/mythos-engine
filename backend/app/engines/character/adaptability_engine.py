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


class AdaptabilityEngine(BaseEngine):
    """Builds adaptability and limit-break logic.

    Adaptability is not "the character can do anything."
    It is a governed exception system with:
    - trigger model
    - boundary model
    - cost model
    - recovery model
    - failure model
    - moral condition
    - world-rule exception type
    - learning metadata for future training
    """

    engine_name = "character.adaptability_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        skill_profile = payload.get("skill_profile") or character_seed.get("skill_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        power_limits = payload.get("power_limits") or character_seed.get("power_limits", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        agency_rules = payload.get("agency_rules") or character_seed.get("agency_rules", {})
        world_state = payload.get("world_state", {})
        world_constraints = payload.get("world_constraints", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; adaptability engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or skill_profile.get("character_id")
            or goal_profile.get("character_id")
            or moral_profile.get("character_id")
            or character_type_ontology.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        adaptability_profile = self._build_adaptability_profile(
            character_id=character_id,
            character_seed=character_seed,
            skill_profile=skill_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            goal_profile=goal_profile,
            moral_profile=moral_profile,
            world_constraints=world_constraints,
        )

        limit_break_rules = self._build_limit_break_rules(
            adaptability_profile=adaptability_profile,
            character_seed=character_seed,
            skill_ontology=skill_ontology,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            agency_rules=agency_rules,
        )

        adaptation_pathways = self._build_adaptation_pathways(
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            power_limits=power_limits,
        )

        failure_and_cost_model = self._build_failure_and_cost_model(
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            power_limits=power_limits,
            moral_profile=moral_profile,
            character_seed=character_seed,
        )

        adaptation_diagnostics = self._build_diagnostics(
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            adaptation_pathways=adaptation_pathways,
            failure_and_cost_model=failure_and_cost_model,
        )

        ontology_record = self._build_ontology_record(
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            adaptation_pathways=adaptation_pathways,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_adaptability",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=adaptability_profile["similarity_tags"],
            novelty_score=adaptability_profile["novelty_score"],
            originality_score=adaptability_profile["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            adaptability_profile=adaptability_profile,
            adaptation_diagnostics=adaptation_diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=adaptability_profile["adaptability_name"],
            type_family="adaptability",
            type_subfamily=adaptability_profile["adaptability_family"],
            type_scope="character_adaptability",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=adaptability_profile["similarity_tags"],
            generation_constraints=limit_break_rules["generation_constraints"],
            counter_patterns=failure_and_cost_model["counter_adaptation_patterns"],
            learned_axes={
                "adaptability_profile": adaptability_profile,
                "limit_break_rules": limit_break_rules,
                "adaptation_pathways": adaptation_pathways,
                "failure_and_cost_model": failure_and_cost_model,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_adaptability",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=adaptability_profile["retrieval_context_queries"],
            generated_training_labels={
                "adaptability_family": adaptability_profile["adaptability_family"],
                "adaptability_subtype": adaptability_profile["adaptability_subtype"],
                "trigger_model": adaptability_profile["trigger_model"],
                "cost_model": adaptability_profile["cost_model"],
                "recovery_model": adaptability_profile["recovery_model"],
                "world_rule_exception_type": adaptability_profile["world_rule_exception_type"],
                "limit_break_allowed": limit_break_rules["limit_break_allowed"],
                "adaptation_safety_tier": adaptation_diagnostics["adaptation_safety_tier"],
            },
            learning_notes=[
                "Adaptability is represented as a governed exception system, not unlimited power.",
                "Future training should learn trigger/cost/recovery/failure patterns from curated story outcomes.",
                "Future retrieval should compare adaptability family, trigger model, and failure model.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            adaptation_pathways=adaptation_pathways,
            failure_and_cost_model=failure_and_cost_model,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "adaptability_profile": adaptability_profile,
                "limit_break_rules": limit_break_rules,
                "adaptation_pathways": adaptation_pathways,
                "failure_and_cost_model": failure_and_cost_model,
                "adaptation_diagnostics": adaptation_diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "adaptability_summary": {
                    "character_id": character_id,
                    "adaptability_family": adaptability_profile["adaptability_family"],
                    "adaptability_subtype": adaptability_profile["adaptability_subtype"],
                    "trigger_model": adaptability_profile["trigger_model"],
                    "limit_break_allowed": limit_break_rules["limit_break_allowed"],
                    "cost_model": adaptability_profile["cost_model"],
                    "recovery_model": adaptability_profile["recovery_model"],
                    "world_rule_exception_type": adaptability_profile["world_rule_exception_type"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_destiny_engine": True,
                    "ready_for_relationship_readiness_engine": True,
                    "ready_for_plot_engine_later": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "Adaptability should create new possibilities while preserving cost and consequence.",
                    "Limit-breaks must require condition, cost, recovery, and post-break fallout.",
                    "This engine prepares rule-breaking characters for destiny, plot, relationship, and training systems.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                adaptability_profile["adaptability_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_adaptability_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        skill_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        goal_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        adaptability_family, adaptability_subtype = self._adaptability_family_and_subtype(
            character_seed=character_seed,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
        )

        trigger_model = self._trigger_model(character_seed, skill_ontology, goal_profile, moral_profile)
        boundary_model = self._boundary_model(character_seed, skill_profile, skill_ontology, world_constraints)
        cost_model = self._cost_model(character_seed, skill_ontology, moral_profile)
        recovery_model = self._recovery_model(character_seed, skill_ontology, cost_model)
        exception_type = self._world_rule_exception_type(character_seed, skill_ontology, world_constraints)
        similarity_tags = self._similarity_tags(
            adaptability_family=adaptability_family,
            adaptability_subtype=adaptability_subtype,
            trigger_model=trigger_model,
            cost_model=cost_model,
            recovery_model=recovery_model,
            exception_type=exception_type,
            character_seed=character_seed,
            skill_ontology=skill_ontology,
        )

        return {
            "adaptability_id": f"adapt_{uuid4().hex[:12]}",
            "character_id": character_id,
            "adaptability_name": self._adaptability_name(character_seed, adaptability_family, adaptability_subtype),
            "adaptability_family": adaptability_family,
            "adaptability_subtype": adaptability_subtype,
            "trigger_model": trigger_model,
            "boundary_model": boundary_model,
            "cost_model": cost_model,
            "recovery_model": recovery_model,
            "world_rule_exception_type": exception_type,
            "adaptation_scope": self._adaptation_scope(skill_ontology, character_seed),
            "adaptation_ceiling": self._adaptation_ceiling(skill_ontology, character_type_ontology, character_seed),
            "adaptation_control_score": self._adaptation_control_score(skill_ontology, moral_profile, character_seed),
            "instability_score": self._instability_score(skill_ontology, character_seed, cost_model),
            "relationship_risk": self._relationship_risk(character_seed, skill_ontology, cost_model),
            "story_function": self._story_function(adaptability_family, trigger_model, character_seed),
            "similarity_tags": similarity_tags,
            "retrieval_context_queries": self._retrieval_queries(adaptability_family, adaptability_subtype, similarity_tags),
            "novelty_score": self._novelty_score(adaptability_family, adaptability_subtype, skill_ontology, character_seed),
            "originality_score": self._originality_score(adaptability_family, trigger_model, cost_model),
            "confidence_score": self._confidence_score(adaptability_family, trigger_model, skill_ontology),
        }

    def _adaptability_family_and_subtype(
        self,
        *,
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
    ) -> tuple[str, str]:
        text = " ".join([str(character_seed), str(skill_ontology), str(character_type_ontology)]).lower()

        if "limit_break_anomaly" in text or "anomaly" in text:
            return "limit_break_anomaly", "unstable_boundary_exceedance"

        if "earned_breakthrough" in text or "protects someone weaker" in text:
            return "earned_moral_breakthrough", "protection_triggered_exceedance"

        if skill_ontology.get("skill_family") == "adaptive_limit_system":
            return "adaptive_power_evolution", "pressure_evolution"

        if "destiny" in text or character_seed.get("destiny_type"):
            return "destiny_resonant_adaptation", "fate_pressure_response"

        if character_type_ontology.get("type_family") in {"status_fall_character", "mirror_pressure_character"}:
            return "pressure_growth_adaptation", "rivalry_or_failure_growth"

        return "contextual_learning_adaptation", "experience_based_adjustment"

    def _adaptability_name(self, seed: Dict[str, Any], family: str, subtype: str) -> str:
        if seed.get("adaptability_name"):
            return seed["adaptability_name"]

        if seed.get("adaptability_type"):
            return str(seed["adaptability_type"])

        names = {
            "earned_moral_breakthrough": "Earned Moral Breakthrough",
            "limit_break_anomaly": "Limit-Break Anomaly",
            "adaptive_power_evolution": "Adaptive Power Evolution",
            "destiny_resonant_adaptation": "Destiny-Resonant Adaptation",
            "pressure_growth_adaptation": "Pressure Growth Adaptation",
            "contextual_learning_adaptation": "Contextual Learning Adaptation",
        }

        return names.get(family, subtype.replace("_", " ").title())

    def _trigger_model(
        self,
        seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        goal: Dict[str, Any],
        moral: Dict[str, Any],
    ) -> str:
        if seed.get("breakthrough_condition"):
            return f"moral_threshold: {seed['breakthrough_condition']}"

        if skill_ontology.get("activation_model") == "pressure_triggered":
            return "pressure_triggered"

        if goal.get("choice_pressure"):
            return f"goal_choice_pressure: {goal['choice_pressure']}"

        if moral.get("mercy_triggers"):
            return f"mercy_trigger: {moral['mercy_triggers'][0]}"

        return "high_pressure_learning_event"

    def _boundary_model(
        self,
        seed: Dict[str, Any],
        skill_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        boundaries = [
            "cannot exceed limits without stated trigger",
            "cannot bypass cost or recovery",
            "cannot erase emotional, social, or moral consequence",
        ]

        if skill_ontology.get("counter_family"):
            boundaries.append("must remain counterable by ontology-defined counter families")

        if skill_ontology.get("world_legality_family") in {"forbidden_or_illegal", "restricted_or_taboo", "class_restricted"}:
            boundaries.append("public use can trigger legal or institutional consequences")

        if world_constraints.get("destiny_is_not_absolute"):
            boundaries.append("adaptation cannot make destiny meaningless")

        return {
            "hard_boundaries": boundaries,
            "soft_boundaries": [
                "repeated use increases instability",
                "audience interpretation changes after visible use",
                "enemy learning risk increases after each use",
            ],
            "counterplay_required": True,
            "world_consistency_required": True,
        }

    def _cost_model(self, seed: Dict[str, Any], skill_ontology: Dict[str, Any], moral: Dict[str, Any]) -> Dict[str, Any]:
        cost_families = set(skill_ontology.get("cost_family", []))

        if seed.get("adaptation_cost"):
            cost_families.add(str(seed["adaptation_cost"]))

        if moral.get("corruption_risk", 0.0) >= 0.55:
            cost_families.add("moral_corrosion_risk")

        if not cost_families:
            cost_families.add("fatigue_and_visibility")

        return {
            "cost_families": sorted(cost_families),
            "immediate_cost": self._immediate_cost(cost_families),
            "delayed_cost": self._delayed_cost(cost_families),
            "social_cost": self._social_cost(cost_families),
            "moral_cost": self._moral_cost(cost_families),
        }

    def _immediate_cost(self, costs: set[str]) -> str:
        joined = " ".join(costs).lower()

        if "identity" in joined or "instability" in joined:
            return "identity or emotional instability immediately after adaptation"

        if "mental" in joined or "fatigue" in joined:
            return "cognitive exhaustion and degraded judgment"

        if "stamina" in joined or "physical" in joined:
            return "physical exhaustion or injury risk"

        return "energy loss and reduced control"

    def _delayed_cost(self, costs: set[str]) -> str:
        joined = " ".join(costs).lower()

        if "social" in joined or "visibility" in joined or "anonymity" in joined:
            return "future reputation damage and enemy attention"

        if "memory" in joined:
            return "memory distortion or unreliable recall"

        if "moral" in joined:
            return "slow normalization of harmful exception-making"

        return "recovery debt that must be paid in later scenes"

    def _social_cost(self, costs: set[str]) -> str:
        joined = " ".join(costs).lower()

        if "visibility" in joined or "anonymity" in joined:
            return "the character becomes harder to hide or explain"

        return "witnesses reinterpret the character after adaptation"

    def _moral_cost(self, costs: set[str]) -> str:
        joined = " ".join(costs).lower()

        if "moral" in joined or "corrosion" in joined:
            return "adaptation can become permission to break ethics"

        return "adaptation must remain tied to a justifiable condition"

    def _recovery_model(self, seed: Dict[str, Any], skill_ontology: Dict[str, Any], cost_model: Dict[str, Any]) -> Dict[str, Any]:
        costs = " ".join(cost_model["cost_families"]).lower()

        if "identity" in costs or "instability" in costs:
            recovery_type = "identity_stabilization"

        elif "mental" in costs or "fatigue" in costs:
            recovery_type = "cognitive_rest_and_recalibration"

        elif "social" in costs or "visibility" in costs or "anonymity" in costs:
            recovery_type = "reputation_repair_and_cover_story"

        else:
            recovery_type = "standard_energy_recovery"

        return {
            "recovery_type": recovery_type,
            "recovery_window": "scene_to_arc_scale" if recovery_type == "identity_stabilization" else "scene_scale",
            "required_repair_actions": [
                "acknowledge cost",
                "handle social or emotional fallout",
                "avoid repeated limit-break before recovery",
            ],
            "relationship_repair_needed": True,
        }

    def _world_rule_exception_type(
        self,
        seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> str:
        if seed.get("world_rule_exception_type"):
            return seed["world_rule_exception_type"]

        if skill_ontology.get("skill_family") == "adaptive_limit_system":
            return "power_system_boundary_exception"

        if seed.get("destiny_type"):
            return "destiny_pressure_exception"

        if skill_ontology.get("world_legality_family") in {"forbidden_or_illegal", "restricted_or_taboo"}:
            return "legal_or_taboo_exception"

        return "localized_rule_stress_exception"

    def _adaptation_scope(self, skill_ontology: Dict[str, Any], seed: Dict[str, Any]) -> str:
        scale = skill_ontology.get("power_scale", "")

        if scale in {"mythic_or_anomalous", "reality_scale"}:
            return "major_scene_or_arc_scale"

        if seed.get("breakthrough_condition"):
            return "decisive_scene_scale"

        return "localized_behavior_or_skill_adjustment"

    def _adaptation_ceiling(self, skill_ontology: Dict[str, Any], type_ontology: Dict[str, Any], seed: Dict[str, Any]) -> float:
        score = 0.45

        score += float(skill_ontology.get("adaptability_compatibility", 0.0)) * 0.3
        score += float(type_ontology.get("adaptability_potential", 0.0)) * 0.25

        if seed.get("adaptability_type"):
            score += 0.12

        return self._clamp(score)

    def _adaptation_control_score(self, skill_ontology: Dict[str, Any], moral: Dict[str, Any], seed: Dict[str, Any]) -> float:
        score = 0.5

        if moral.get("moral_flexibility", 0.0) >= 0.55:
            score += 0.08

        if moral.get("corruption_risk", 0.0) >= 0.6:
            score -= 0.14

        if skill_ontology.get("activation_model") == "pressure_triggered":
            score -= 0.08

        if seed.get("limitation") or seed.get("adaptation_cost"):
            score += 0.08

        return self._clamp(score)

    def _instability_score(self, skill_ontology: Dict[str, Any], seed: Dict[str, Any], cost_model: Dict[str, Any]) -> float:
        score = 0.25

        if skill_ontology.get("power_scale") in {"mythic_or_anomalous", "reality_scale"}:
            score += 0.25

        if "instability" in " ".join(cost_model["cost_families"]).lower():
            score += 0.22

        if seed.get("adaptability_type") == "limit_break_anomaly":
            score += 0.2

        if skill_ontology.get("activation_model") == "pressure_triggered":
            score += 0.08

        return self._clamp(score)

    def _relationship_risk(self, seed: Dict[str, Any], skill_ontology: Dict[str, Any], cost_model: Dict[str, Any]) -> float:
        score = 0.3

        if "social" in " ".join(cost_model["cost_families"]).lower() or "visibility" in " ".join(cost_model["cost_families"]).lower():
            score += 0.18

        if skill_ontology.get("skill_family") in {"cognitive_inference", "psychic_cognitive_mapping"}:
            score += 0.12

        if seed.get("breakthrough_condition"):
            score += 0.1

        return self._clamp(score)

    def _story_function(self, family: str, trigger_model: str, seed: Dict[str, Any]) -> str:
        if family == "earned_moral_breakthrough":
            return "turns moral pressure into costly growth and consequence"

        if family == "limit_break_anomaly":
            return "creates awe, danger, instability, and post-break fallout"

        if family == "destiny_resonant_adaptation":
            return "tests whether destiny enables agency or traps the character"

        return "lets the character learn beyond normal pattern while preserving limits"

    def _build_limit_break_rules(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        agency_rules: Dict[str, Any],
    ) -> Dict[str, Any]:
        allowed = adaptability_profile["adaptability_family"] in {
            "earned_moral_breakthrough",
            "limit_break_anomaly",
            "adaptive_power_evolution",
            "destiny_resonant_adaptation",
        }

        trigger = adaptability_profile["trigger_model"]

        return {
            "limit_break_allowed": allowed,
            "activation_conditions": [
                trigger,
                "ordinary options have failed",
                "cost is paid in same or following scene",
                "counterplay remains possible",
            ],
            "hard_prohibitions": [
                "cannot activate for convenience",
                "cannot erase prior consequences",
                "cannot instantly master every future use",
                "cannot invalidate world rules without creating world reaction",
            ],
            "required_costs": adaptability_profile["cost_model"]["cost_families"],
            "required_aftermath": [
                "physical/emotional/social recovery",
                "relationship reaction",
                "enemy or institution learns something",
                "future instability or reputation shift",
            ],
            "growth_after_break": [
                "new capability is narrower than the breakthrough moment",
                "training is required before safe reuse",
                "new counterplay becomes available to enemies",
            ],
            "generation_constraints": [
                "limit-break requires condition",
                "limit-break requires cost",
                "limit-break requires consequence",
                "limit-break requires counterplay",
                "limit-break cannot solve every future problem",
                "limit-break must change relationships or reputation",
            ],
        }

    def _build_adaptation_pathways(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        power_limits: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "pathway_id": f"adpath_{uuid4().hex[:12]}",
            "short_term_pathway": [
                "trigger pressure appears",
                "normal strategy fails",
                "adaptation activates with instability",
                "scene resolves with new consequence",
            ],
            "medium_term_pathway": [
                "character attempts to understand what changed",
                "training narrows the breakthrough into a repeatable but limited technique",
                "relationships react to the cost or danger",
                "enemy develops counter-adaptation",
            ],
            "long_term_pathway": [
                "adaptation becomes part of identity but not a free solution",
                "character learns when not to adapt",
                "final mastery requires accepting cost and protecting agency",
            ],
            "skill_family_interactions": {
                "skill_family": skill_ontology.get("skill_family", "unknown"),
                "growth_model": skill_ontology.get("growth_model", "unknown"),
                "counter_family": skill_ontology.get("counter_family", []),
            },
            "character_type_interactions": {
                "type_family": character_type_ontology.get("type_family", "unknown"),
                "relationship_function": character_type_ontology.get("relationship_function", "unknown"),
                "plot_function": character_type_ontology.get("plot_function", "unknown"),
            },
            "counter_adaptation_needed": True,
        }

    def _build_failure_and_cost_model(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        power_limits: Dict[str, Any],
        moral_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        counter_patterns = set()

        counter_patterns.update(power_limits.get("cannot_do", []))
        counter_patterns.update(power_limits.get("limitations", []))

        if not counter_patterns:
            counter_patterns.update([
                "deny trigger condition",
                "attack recovery window",
                "force repeated activation",
                "weaponize public visibility",
            ])

        return {
            "failure_modes": [
                "adaptation activates too late",
                "adaptation succeeds but creates worse social consequence",
                "enemy learns the activation pattern",
                "character over-identifies with breakthrough",
                "cost goes unpaid and returns later",
            ],
            "cost_escalation_ladder": [
                "fatigue",
                "loss of control",
                "public visibility",
                "relationship strain",
                "identity instability",
                "moral corrosion",
            ],
            "counter_adaptation_patterns": sorted(counter_patterns),
            "misuse_risks": [
                "using adaptation to avoid emotional repair",
                "using breakthrough as proof of superiority",
                "treating cost as aesthetic instead of consequential",
            ],
            "safety_gates": [
                "human review required for extreme trauma or identity erosion variants",
                "do not train unreviewed harmful power fantasy outputs",
                "preserve agency and consequence in all adaptation records",
            ],
        }

    def _build_diagnostics(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        adaptation_pathways: Dict[str, Any],
        failure_and_cost_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(adaptability_profile["adaptability_family"]),
                bool(adaptability_profile["trigger_model"]),
                bool(adaptability_profile["boundary_model"]),
                bool(adaptability_profile["cost_model"]),
                bool(adaptability_profile["recovery_model"]),
                bool(adaptability_profile["world_rule_exception_type"]),
                bool(limit_break_rules["activation_conditions"]),
                bool(limit_break_rules["hard_prohibitions"]),
                bool(adaptation_pathways["short_term_pathway"]),
                bool(adaptation_pathways["medium_term_pathway"]),
                bool(adaptation_pathways["long_term_pathway"]),
                bool(failure_and_cost_model["failure_modes"]),
                bool(failure_and_cost_model["counter_adaptation_patterns"]),
            ]
        ) / 13

        instability = adaptability_profile["instability_score"]

        if instability >= 0.7:
            safety_tier = "high_review_needed"
        elif instability >= 0.45:
            safety_tier = "moderate_review_recommended"
        else:
            safety_tier = "standard_review"

        return {
            "adaptability_completeness_score": round(completeness, 3),
            "has_trigger": bool(adaptability_profile["trigger_model"]),
            "has_cost": bool(adaptability_profile["cost_model"]["cost_families"]),
            "has_recovery": bool(adaptability_profile["recovery_model"]),
            "has_counterplay": bool(failure_and_cost_model["counter_adaptation_patterns"]),
            "has_hard_prohibitions": bool(limit_break_rules["hard_prohibitions"]),
            "has_growth_path": bool(adaptation_pathways["long_term_pathway"]),
            "is_not_unlimited_power": completeness >= 0.9 and bool(limit_break_rules["hard_prohibitions"]),
            "adaptation_safety_tier": safety_tier,
            "plot_ready": completeness >= 0.9,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        adaptation_pathways: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="adaptability",
            name=adaptability_profile["adaptability_name"],
            family=adaptability_profile["adaptability_family"],
            subtype=adaptability_profile["adaptability_subtype"],
            description=adaptability_profile["story_function"],
            axes={
                "trigger_model": adaptability_profile["trigger_model"],
                "boundary_model": adaptability_profile["boundary_model"],
                "cost_model": adaptability_profile["cost_model"],
                "recovery_model": adaptability_profile["recovery_model"],
                "world_rule_exception_type": adaptability_profile["world_rule_exception_type"],
                "adaptation_scope": adaptability_profile["adaptation_scope"],
                "adaptation_ceiling": adaptability_profile["adaptation_ceiling"],
                "adaptation_control_score": adaptability_profile["adaptation_control_score"],
                "instability_score": adaptability_profile["instability_score"],
                "relationship_risk": adaptability_profile["relationship_risk"],
                "limit_break_rules": limit_break_rules,
                "adaptation_pathways": adaptation_pathways,
            },
            tags=adaptability_profile["similarity_tags"],
            examples=[adaptability_profile["adaptability_name"]],
            counterexamples=limit_break_rules["hard_prohibitions"],
            confidence_score=adaptability_profile["confidence_score"],
            novelty_score=adaptability_profile["novelty_score"],
            quality_score=adaptability_profile["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        adaptability_profile: Dict[str, Any],
        adaptation_diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(
            adaptability_profile["confidence_score"],
            adaptability_profile["originality_score"],
            adaptation_diagnostics["adaptability_completeness_score"],
            0.95,
        )

        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8
        safety_ok = adaptation_diagnostics["adaptation_safety_tier"] != "high_review_needed"

        eligible = approved_source and provenance.usage_allowed and quality >= 0.75 and high_rating and safety_ok

        rejection_reasons = []

        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if quality < 0.75:
            rejection_reasons.append("quality score below threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")
        if not safety_ok:
            rejection_reasons.append("high instability requires human review before training")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=round(quality, 3),
            consistency_score=adaptability_profile["confidence_score"],
            originality_score=adaptability_profile["originality_score"],
            safety_score=0.84 if safety_ok else 0.62,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Adaptability schema includes trigger, cost, recovery, counterplay, and prohibition labels.",
                "Training eligibility is conservative for high-instability adaptations.",
            ],
        )

    def _similarity_tags(
        self,
        *,
        adaptability_family: str,
        adaptability_subtype: str,
        trigger_model: str,
        cost_model: Dict[str, Any],
        recovery_model: Dict[str, Any],
        exception_type: str,
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
    ) -> List[str]:
        tags = {
            adaptability_family,
            adaptability_subtype,
            trigger_model.split(":")[0],
            recovery_model["recovery_type"],
            exception_type,
            skill_ontology.get("skill_family", "unknown_skill_family"),
        }

        for cost in cost_model.get("cost_families", []):
            tags.add(str(cost).replace(" ", "_"))

        if character_seed.get("destiny_type"):
            tags.add("destiny_linked")

        if character_seed.get("breakthrough_condition"):
            tags.add("moral_threshold")

        return sorted(tags)

    def _retrieval_queries(self, family: str, subtype: str, tags: List[str]) -> List[str]:
        return [
            f"adaptability ontology {family} {subtype}",
            f"limit break trigger cost recovery model {family}",
            f"counterplay and consequence for {subtype}",
            " ".join(tags[:8]),
        ]

    def _novelty_score(self, family: str, subtype: str, skill_ontology: Dict[str, Any], seed: Dict[str, Any]) -> float:
        score = 0.48

        if family in {"earned_moral_breakthrough", "limit_break_anomaly", "destiny_resonant_adaptation"}:
            score += 0.16

        if skill_ontology.get("skill_family") in {"cognitive_inference", "psychic_cognitive_mapping", "adaptive_limit_system"}:
            score += 0.1

        if seed.get("breakthrough_condition"):
            score += 0.08

        return self._clamp(score)

    def _originality_score(self, family: str, trigger_model: str, cost_model: Dict[str, Any]) -> float:
        score = 0.52

        if "moral_threshold" in trigger_model:
            score += 0.12

        if len(cost_model.get("cost_families", [])) >= 2:
            score += 0.1

        if family != "contextual_learning_adaptation":
            score += 0.08

        return self._clamp(score)

    def _confidence_score(self, family: str, trigger_model: str, skill_ontology: Dict[str, Any]) -> float:
        score = 0.56

        if family != "contextual_learning_adaptation":
            score += 0.16

        if trigger_model:
            score += 0.1

        if skill_ontology:
            score += 0.08

        return self._clamp(score)

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        adaptation_pathways: Dict[str, Any],
        failure_and_cost_model: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["adaptability_profile"] = adaptability_profile
        merged_seed["limit_break_rules"] = limit_break_rules
        merged_seed["adaptation_pathways"] = adaptation_pathways
        merged_seed["adaptability_failure_and_cost_model"] = failure_and_cost_model
        merged_seed["adaptability_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "destiny_engine_payload": {
                "character_seed": merged_seed,
                "adaptability_profile": adaptability_profile,
                "limit_break_rules": limit_break_rules,
                "learning_metadata": learning_metadata.model_dump(),
            },
            "relationship_readiness_payload": {
                "character_seed": merged_seed,
                "adaptability_profile": adaptability_profile,
                "failure_and_cost_model": failure_and_cost_model,
            },
            "plot_engine_payload_later": {
                "character_id": adaptability_profile["character_id"],
                "adaptability_profile": adaptability_profile,
                "limit_break_rules": limit_break_rules,
                "adaptation_pathways": adaptation_pathways,
                "failure_and_cost_model": failure_and_cost_model,
            },
            "chunk8_training_payload_later": {
                "target_type": "character_adaptability",
                "adaptability_profile": adaptability_profile,
                "limit_break_rules": limit_break_rules,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
