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


class DestinyLegacyEngine(BaseEngine):
    """Builds destiny, prophecy, inheritance, and legacy pressure.

    Destiny is not a fixed victory condition.
    It is a system of pressure, interpretation, social consequence,
    inheritance, misreading, and agency conflict.

    This engine makes destiny usable for complex stories without removing
    character choice.
    """

    engine_name = "character.destiny_legacy_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        adaptability_profile = payload.get("adaptability_profile") or character_seed.get("adaptability_profile", {})
        limit_break_rules = payload.get("limit_break_rules") or character_seed.get("limit_break_rules", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        world_state = payload.get("world_state", {})
        world_constraints = payload.get("world_constraints", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; destiny engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or goal_profile.get("character_id")
            or moral_profile.get("character_id")
            or adaptability_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        destiny_profile = self._build_destiny_profile(
            character_id=character_id,
            character_seed=character_seed,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            world_state=world_state,
            world_constraints=world_constraints,
        )

        prophecy_model = self._build_prophecy_model(
            destiny_profile=destiny_profile,
            character_seed=character_seed,
            character_type_ontology=character_type_ontology,
            world_state=world_state,
        )

        legacy_model = self._build_legacy_model(
            destiny_profile=destiny_profile,
            character_seed=character_seed,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
        )

        agency_conflict_model = self._build_agency_conflict_model(
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
        )

        destiny_diagnostics = self._build_diagnostics(
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
            agency_conflict_model=agency_conflict_model,
        )

        ontology_record = self._build_ontology_record(
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
            agency_conflict_model=agency_conflict_model,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_destiny",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=destiny_profile["similarity_tags"],
            novelty_score=destiny_profile["novelty_score"],
            originality_score=destiny_profile["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            destiny_profile=destiny_profile,
            destiny_diagnostics=destiny_diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=destiny_profile["destiny_name"],
            type_family="destiny",
            type_subfamily=destiny_profile["destiny_family"],
            type_scope="character_destiny",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=destiny_profile["similarity_tags"],
            generation_constraints=agency_conflict_model["destiny_generation_constraints"],
            counter_patterns=prophecy_model["misinterpretation_vectors"],
            learned_axes={
                "destiny_profile": destiny_profile,
                "prophecy_model": prophecy_model,
                "legacy_model": legacy_model,
                "agency_conflict_model": agency_conflict_model,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_destiny",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=destiny_profile["retrieval_context_queries"],
            generated_training_labels={
                "destiny_family": destiny_profile["destiny_family"],
                "destiny_subtype": destiny_profile["destiny_subtype"],
                "prophecy_structure": prophecy_model["prophecy_structure"],
                "interpretation_risk": prophecy_model["interpretation_risk"],
                "legacy_pressure_type": legacy_model["legacy_pressure_type"],
                "agency_conflict_type": agency_conflict_model["agency_conflict_type"],
                "destiny_is_absolute": destiny_profile["destiny_is_absolute"],
                "training_ready_schema": destiny_diagnostics["training_ready_schema"],
            },
            learning_notes=[
                "Destiny is modeled as pressure and interpretation, not guaranteed outcome.",
                "Future training should learn prophecy ambiguity, legacy burden, and agency-conflict patterns.",
                "Destiny must preserve character agency and create consequences for interpretation.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
            agency_conflict_model=agency_conflict_model,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "destiny_profile": destiny_profile,
                "prophecy_model": prophecy_model,
                "legacy_model": legacy_model,
                "agency_conflict_model": agency_conflict_model,
                "destiny_diagnostics": destiny_diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "destiny_summary": {
                    "character_id": character_id,
                    "destiny_family": destiny_profile["destiny_family"],
                    "destiny_subtype": destiny_profile["destiny_subtype"],
                    "destiny_is_absolute": destiny_profile["destiny_is_absolute"],
                    "prophecy_structure": prophecy_model["prophecy_structure"],
                    "legacy_pressure_type": legacy_model["legacy_pressure_type"],
                    "agency_conflict_type": agency_conflict_model["agency_conflict_type"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_relationship_readiness_engine": True,
                    "ready_for_dialogue_voice_engine": True,
                    "ready_for_plot_engine_later": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "Destiny creates pressure; it must not remove agency.",
                    "Prophecy should be ambiguous, socially interpreted, and possibly weaponized.",
                    "Legacy can empower, trap, distort, or burden the character.",
                    "Future model training should use destiny labels to avoid generic chosen-one outputs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                destiny_profile["destiny_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_destiny_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        world_state: Dict[str, Any],
        world_constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        destiny_family, destiny_subtype = self._destiny_family_and_subtype(
            character_seed=character_seed,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
        )

        destiny_name = self._destiny_name(character_seed, destiny_family, destiny_subtype)
        pressure_model = self._pressure_model(character_seed, destiny_family, goal_profile, moral_profile)
        social_interpretation = self._social_interpretation(character_seed, destiny_family, character_type_ontology)
        destiny_is_absolute = self._destiny_is_absolute(character_seed, world_constraints)
        similarity_tags = self._similarity_tags(
            destiny_family=destiny_family,
            destiny_subtype=destiny_subtype,
            pressure_model=pressure_model,
            social_interpretation=social_interpretation,
            character_seed=character_seed,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
        )

        return {
            "destiny_id": f"dest_{uuid4().hex[:12]}",
            "character_id": character_id,
            "destiny_name": destiny_name,
            "destiny_family": destiny_family,
            "destiny_subtype": destiny_subtype,
            "destiny_marker": character_seed.get("destiny_type") or destiny_name,
            "destiny_is_absolute": destiny_is_absolute,
            "pressure_model": pressure_model,
            "social_interpretation": social_interpretation,
            "chosen_by": self._chosen_by(character_seed, world_state),
            "destiny_benefits": self._destiny_benefits(destiny_family, skill_ontology, character_type_ontology),
            "destiny_burdens": self._destiny_burdens(destiny_family, character_seed, moral_profile, goal_profile),
            "destiny_visibility": self._destiny_visibility(character_seed, destiny_family, skill_ontology),
            "destiny_failure_mode": self._destiny_failure_mode(destiny_family, moral_profile, goal_profile),
            "destiny_success_cost": self._destiny_success_cost(destiny_family, character_seed, goal_profile),
            "similarity_tags": similarity_tags,
            "retrieval_context_queries": self._retrieval_queries(destiny_family, destiny_subtype, similarity_tags),
            "novelty_score": self._novelty_score(destiny_family, destiny_subtype, character_seed),
            "originality_score": self._originality_score(destiny_family, pressure_model, social_interpretation),
            "confidence_score": self._confidence_score(destiny_family, destiny_subtype, character_seed),
        }

    def _destiny_family_and_subtype(
        self,
        *,
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
    ) -> tuple[str, str]:
        text = " ".join([str(character_seed), str(skill_ontology), str(character_type_ontology), str(adaptability_profile)]).lower()

        if "hidden_kingmaker" in text or "kingmaker" in text or "power_redirector" in text:
            return "power_flow_destiny", "hidden_kingmaker_fate"

        # Adaptive / threshold destiny must be checked before generic "marked" logic.
        # Example: "threshold_marked" is not automatically a curse mark.
        if (
            "adapt" in text
            or "limit_break" in text
            or "breakthrough" in text
            or "threshold" in text
            or "adaptive_limit_system" in text
        ):
            return "adaptive_threshold_destiny", "rule_breaking_pressure"

        if "banished heir" in text or "legacy" in text or "bloodline" in text:
            return "inherited_legacy_destiny", "disputed_inheritance"

        if "false saint" in text or "saint" in text or "sacred" in text:
            return "sacred_misinterpretation_destiny", "false_or_burdened_saint"

        if "curse" in text or "marked" in text:
            return "curse_mark_destiny", "burdened_mark"

        if "prophecy" in text or "chosen" in text:
            return "prophetic_selection_destiny", "ambiguous_chosen_one"

        return "emergent_choice_destiny", "agency_created_path"

    def _destiny_name(self, seed: Dict[str, Any], family: str, subtype: str) -> str:
        if seed.get("destiny_name"):
            return seed["destiny_name"]

        if seed.get("destiny_type"):
            return str(seed["destiny_type"])

        names = {
            "power_flow_destiny": "Hidden Kingmaker Fate",
            "inherited_legacy_destiny": "Disputed Legacy Inheritance",
            "sacred_misinterpretation_destiny": "Burdened Sacred Misreading",
            "curse_mark_destiny": "Burdened Mark",
            "adaptive_threshold_destiny": "Threshold-Breaking Fate",
            "prophetic_selection_destiny": "Ambiguous Prophetic Selection",
            "emergent_choice_destiny": "Agency-Created Path",
        }

        return names.get(family, subtype.replace("_", " ").title())

    def _pressure_model(self, seed: Dict[str, Any], family: str, goal: Dict[str, Any], moral: Dict[str, Any]) -> Dict[str, Any]:
        pressures = []

        if family == "power_flow_destiny":
            pressures.extend(["others try to use the character's influence", "every choice changes who can gain power"])

        if family == "adaptive_threshold_destiny":
            pressures.extend(["fate appears during impossible thresholds", "rule-breaking creates aftermath"])

        if family == "inherited_legacy_destiny":
            pressures.extend(["bloodline or inheritance creates expectations", "legacy may not match personal ethics"])

        if seed.get("breakthrough_condition"):
            pressures.append(f"moral trigger pressure: {seed['breakthrough_condition']}")

        if goal.get("true_need"):
            pressures.append(f"true need pressure: {goal['true_need']}")

        if moral.get("dominant_moral_value"):
            pressures.append(f"moral value pressure: {moral['dominant_moral_value']}")

        if not pressures:
            pressures.append("choice creates destiny retroactively")

        return {
            "pressure_sources": pressures,
            "pressure_tier": "high_destiny_pressure" if len(pressures) >= 3 else "moderate_destiny_pressure",
            "pressure_resolution_need": "character must choose meaning, not merely fulfill label",
        }

    def _social_interpretation(
        self,
        seed: Dict[str, Any],
        family: str,
        type_ontology: Dict[str, Any],
    ) -> Dict[str, Any]:
        interpretations = []

        if family == "power_flow_destiny":
            interpretations.extend(["useful tool", "secret threat", "future kingmaker"])

        if family == "prophetic_selection_destiny":
            interpretations.extend(["chosen one", "public symbol", "political asset"])

        if family == "sacred_misinterpretation_destiny":
            interpretations.extend(["saint", "fraud", "holy weapon"])

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            interpretations.append("unreliable claimant")

        if type_ontology.get("social_position"):
            interpretations.append(f"filtered through {type_ontology['social_position']}")

        return {
            "public_interpretations": interpretations or ["unclear omen", "socially unclassified sign"],
            "who_weaponizes_it": ["institutions", "enemies", "factions", "family", "romantic or rival witnesses"],
            "interpretation_risk": "high" if len(interpretations) >= 3 else "medium",
        }

    def _destiny_is_absolute(self, seed: Dict[str, Any], world_constraints: Dict[str, Any]) -> bool:
        if seed.get("destiny_is_absolute") is not None:
            return bool(seed["destiny_is_absolute"])

        if world_constraints.get("destiny_controls_everything"):
            return True

        return False

    def _chosen_by(self, seed: Dict[str, Any], world_state: Dict[str, Any]) -> List[str]:
        chosen_by = []

        if seed.get("destiny_source"):
            chosen_by.append(seed["destiny_source"])

        world_text = str(world_state).lower()

        if "oath" in world_text:
            chosen_by.append("oath system")

        if "archive" in world_text:
            chosen_by.append("sealed archive interpretation")

        if "empire" in world_text:
            chosen_by.append("imperial myth machinery")

        if not chosen_by:
            chosen_by.append("ambiguous pattern of events")

        return sorted(set(chosen_by))

    def _destiny_benefits(self, family: str, skill_ontology: Dict[str, Any], type_ontology: Dict[str, Any]) -> List[str]:
        benefits = []

        if family == "power_flow_destiny":
            benefits.append("can identify who should hold power before others see it")

        if skill_ontology.get("destiny_compatibility", 0.0) >= 0.6:
            benefits.append("skill resonates with destiny pressure")

        if type_ontology.get("destiny_relevance", 0.0) >= 0.6:
            benefits.append("character type naturally supports destiny-scale consequence")

        if not benefits:
            benefits.append("destiny gives symbolic weight to choices")

        return benefits

    def _destiny_burdens(self, family: str, seed: Dict[str, Any], moral: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        burdens = []

        if family == "power_flow_destiny":
            burdens.append("others may treat the character as a means to power")

        if family == "adaptive_threshold_destiny":
            burdens.append("breakthrough moments attract fear and interpretation")

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            burdens.append("destiny claim is harder to believe because name is low-trust")

        if moral.get("corruption_risk", 0.0) >= 0.55:
            burdens.append("destiny can become self-justification for harm")

        if goal.get("false_need"):
            burdens.append(f"destiny may reward false need: {goal['false_need']}")

        if not burdens:
            burdens.append("destiny creates expectation before identity is ready")

        return burdens

    def _destiny_visibility(self, seed: Dict[str, Any], family: str, skill_ontology: Dict[str, Any]) -> str:
        if skill_ontology.get("power_scale") in {"mythic_or_anomalous", "reality_scale"}:
            return "visible_after_major_manifestation"

        if family == "power_flow_destiny":
            return "visible_through_consequences_before_symbols"

        if seed.get("hidden_destiny"):
            return "hidden_until_interpreted"

        return "socially_interpreted_after_pattern_repeats"

    def _destiny_failure_mode(self, family: str, moral: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if moral.get("corruption_risk", 0.0) >= 0.55:
            return "uses destiny as permission to harm"

        if family == "power_flow_destiny":
            return "chooses the wrong person or system to empower"

        if family == "adaptive_threshold_destiny":
            return "breaks a rule without accepting aftermath"

        if goal.get("false_need"):
            return f"mistakes false need for destiny: {goal['false_need']}"

        return "confuses external label with personal truth"

    def _destiny_success_cost(self, family: str, seed: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if seed.get("adaptation_cost"):
            return seed["adaptation_cost"]

        if family == "power_flow_destiny":
            return "becomes visible to those who want power redirected"

        if goal.get("true_need"):
            return f"must live by true need even when destiny label is easier: {goal['true_need']}"

        return "success increases attention and responsibility"

    def _build_prophecy_model(
        self,
        *,
        destiny_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        family = destiny_profile["destiny_family"]

        structure = {
            "power_flow_destiny": "causal_pattern_prophecy",
            "adaptive_threshold_destiny": "threshold_event_prophecy",
            "inherited_legacy_destiny": "bloodline_or_name_prophecy",
            "sacred_misinterpretation_destiny": "symbolic_sacred_prophecy",
            "prophetic_selection_destiny": "ambiguous_chosen_figure_prophecy",
            "emergent_choice_destiny": "retrospective_choice_prophecy",
        }.get(family, "ambiguous_symbolic_prophecy")

        prophecy_text = self._prophecy_text(destiny_profile, structure)

        return {
            "prophecy_id": f"prop_{uuid4().hex[:12]}",
            "prophecy_structure": structure,
            "prophecy_text": prophecy_text,
            "literal_reading": self._literal_reading(destiny_profile, structure),
            "dangerous_reading": self._dangerous_reading(destiny_profile, structure),
            "agency_preserving_reading": self._agency_preserving_reading(destiny_profile, structure),
            "misinterpretation_vectors": self._misinterpretation_vectors(destiny_profile, character_seed),
            "interpretation_risk": destiny_profile["social_interpretation"]["interpretation_risk"],
            "prophecy_is_complete": False,
            "prophecy_requires_choice": True,
        }

    def _prophecy_text(self, destiny: Dict[str, Any], structure: str) -> str:
        if structure == "causal_pattern_prophecy":
            return "The one unseen at the table will decide who keeps the crown, not by wearing it, but by making power answer."

        if structure == "threshold_event_prophecy":
            return "When the rule fails the powerless, the marked one will break before the world does."

        if structure == "bloodline_or_name_prophecy":
            return "The erased name returns not as proof of blood, but as a debt history refused to pay."

        if structure == "symbolic_sacred_prophecy":
            return "The saint is not the pure one, but the one whose lie reveals what the altar consumes."

        return "The sign names a pressure, not an ending."

    def _literal_reading(self, destiny: Dict[str, Any], structure: str) -> str:
        return "people assume the prophecy identifies a fixed role or guaranteed outcome"

    def _dangerous_reading(self, destiny: Dict[str, Any], structure: str) -> str:
        return "institutions or enemies weaponize the prophecy to remove agency"

    def _agency_preserving_reading(self, destiny: Dict[str, Any], structure: str) -> str:
        return "prophecy identifies pressure, but the character chooses meaning and cost"

    def _misinterpretation_vectors(self, destiny: Dict[str, Any], seed: Dict[str, Any]) -> List[str]:
        vectors = [
            "chosen-one simplification",
            "institutional ownership",
            "enemy preemption",
            "family exploitation",
            "romantic idealization",
        ]

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            vectors.append("false-claim accusation")

        if destiny["destiny_family"] == "power_flow_destiny":
            vectors.append("treating influence as control")

        return vectors

    def _build_legacy_model(
        self,
        *,
        destiny_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        family_status = character_seed.get("family_name_status", "unknown")

        if destiny_profile["destiny_family"] == "inherited_legacy_destiny":
            pressure_type = "bloodline_or_name_burden"
        elif family_status in {"distrusted", "erased", "unknown"}:
            pressure_type = "contested_name_legacy"
        elif destiny_profile["destiny_family"] == "power_flow_destiny":
            pressure_type = "influence_without_crown_legacy"
        else:
            pressure_type = "choice_created_legacy"

        return {
            "legacy_id": f"leg_{uuid4().hex[:12]}",
            "legacy_pressure_type": pressure_type,
            "inherited_burdens": destiny_profile["destiny_burdens"],
            "legacy_assets": destiny_profile["destiny_benefits"],
            "legacy_lie": self._legacy_lie(character_seed, goal_profile),
            "legacy_truth": self._legacy_truth(character_seed, goal_profile),
            "legacy_repair_actions": [
                "separate inherited label from chosen action",
                "accept cost without demanding worship",
                "repair harm caused by destiny interpretation",
            ],
            "who_claims_the_legacy": ["family", "institution", "enemy", "future followers"],
        }

    def _legacy_lie(self, seed: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if goal.get("false_need"):
            return goal["false_need"]

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            return "a name must be trusted before a person can matter"

        return "destiny proves worth"

    def _legacy_truth(self, seed: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if goal.get("true_need"):
            return goal["true_need"]

        return "legacy becomes real only through chosen responsibility"

    def _build_agency_conflict_model(
        self,
        *,
        destiny_profile: Dict[str, Any],
        prophecy_model: Dict[str, Any],
        legacy_model: Dict[str, Any],
        adaptability_profile: Dict[str, Any],
        limit_break_rules: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        if destiny_profile["destiny_is_absolute"]:
            conflict_type = "agency_under_absolute_fate"
        elif destiny_profile["destiny_family"] == "power_flow_destiny":
            conflict_type = "agency_vs_being_used_as_power_tool"
        elif adaptability_profile:
            conflict_type = "agency_vs_rule_breaking_expectation"
        else:
            conflict_type = "agency_vs_social_interpretation"

        return {
            "agency_conflict_id": f"dconf_{uuid4().hex[:12]}",
            "agency_conflict_type": conflict_type,
            "central_question": self._central_question(destiny_profile, conflict_type),
            "agency_protection_rules": [
                "destiny must not decide without character choice",
                "prophecy must allow at least two valid interpretations",
                "legacy must create burden and benefit",
                "fulfillment must cost something real",
                "refusal must also be a valid path with consequence",
            ],
            "destiny_generation_constraints": [
                "do not write destiny as guaranteed victory",
                "do not remove character agency",
                "include misinterpretation risk",
                "include social or institutional weaponization",
                "include legacy burden",
                "include refusal or reinterpretation path",
            ],
            "refusal_path": self._refusal_path(destiny_profile, legacy_model),
            "reinterpretation_path": self._reinterpretation_path(prophecy_model, goal_profile),
            "corruption_path": self._corruption_path(destiny_profile, moral_profile),
            "fulfillment_path": self._fulfillment_path(destiny_profile, goal_profile, limit_break_rules),
        }

    def _central_question(self, destiny: Dict[str, Any], conflict_type: str) -> str:
        if conflict_type == "agency_vs_being_used_as_power_tool":
            return "Will the character redirect power without becoming power's instrument?"

        if conflict_type == "agency_vs_rule_breaking_expectation":
            return "Will the character break limits for protection or for identity?"

        if conflict_type == "agency_under_absolute_fate":
            return "Can choice still matter inside an absolute fate system?"

        return "Will the character define destiny or be defined by interpretation?"

    def _refusal_path(self, destiny: Dict[str, Any], legacy: Dict[str, Any]) -> List[str]:
        return [
            "reject public label",
            "lose immediate support or protection",
            "face consequence of refusing inherited pressure",
            "choose smaller personal truth over grand interpretation",
        ]

    def _reinterpretation_path(self, prophecy: Dict[str, Any], goal: Dict[str, Any]) -> List[str]:
        return [
            "identify dangerous literal reading",
            "find agency-preserving reading",
            "act from true need rather than external label",
            "force others to update interpretation through consequence",
        ]

    def _corruption_path(self, destiny: Dict[str, Any], moral: Dict[str, Any]) -> List[str]:
        return [
            "accepts destiny as proof of superiority",
            "uses prophecy to avoid accountability",
            "turns benefit into entitlement",
            "harms someone and calls it fate",
        ]

    def _fulfillment_path(self, destiny: Dict[str, Any], goal: Dict[str, Any], limit_rules: Dict[str, Any]) -> List[str]:
        path = [
            "recognizes pressure pattern",
            "chooses cost consciously",
            "protects agency of others",
            "fulfills meaning without obeying simplistic label",
        ]

        if limit_rules.get("limit_break_allowed"):
            path.insert(2, "uses limit-break only under valid condition")

        return path

    def _build_diagnostics(
        self,
        *,
        destiny_profile: Dict[str, Any],
        prophecy_model: Dict[str, Any],
        legacy_model: Dict[str, Any],
        agency_conflict_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(destiny_profile["destiny_family"]),
                bool(destiny_profile["pressure_model"]),
                bool(destiny_profile["social_interpretation"]),
                bool(destiny_profile["destiny_burdens"]),
                bool(prophecy_model["prophecy_text"]),
                bool(prophecy_model["misinterpretation_vectors"]),
                bool(legacy_model["legacy_pressure_type"]),
                bool(legacy_model["legacy_lie"]),
                bool(legacy_model["legacy_truth"]),
                bool(agency_conflict_model["agency_protection_rules"]),
                bool(agency_conflict_model["refusal_path"]),
                bool(agency_conflict_model["reinterpretation_path"]),
            ]
        ) / 12

        return {
            "destiny_completeness_score": round(completeness, 3),
            "has_prophecy": bool(prophecy_model["prophecy_text"]),
            "has_misinterpretation": bool(prophecy_model["misinterpretation_vectors"]),
            "has_legacy_burden": bool(legacy_model["inherited_burdens"]),
            "has_agency_protection": bool(agency_conflict_model["agency_protection_rules"]),
            "has_refusal_path": bool(agency_conflict_model["refusal_path"]),
            "has_reinterpretation_path": bool(agency_conflict_model["reinterpretation_path"]),
            "destiny_is_not_generic_chosen_one": destiny_profile["destiny_family"] != "prophetic_selection_destiny" or len(prophecy_model["misinterpretation_vectors"]) >= 3,
            "plot_ready": completeness >= 0.9,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        destiny_profile: Dict[str, Any],
        prophecy_model: Dict[str, Any],
        legacy_model: Dict[str, Any],
        agency_conflict_model: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="destiny",
            name=destiny_profile["destiny_name"],
            family=destiny_profile["destiny_family"],
            subtype=destiny_profile["destiny_subtype"],
            description=agency_conflict_model["central_question"],
            axes={
                "pressure_model": destiny_profile["pressure_model"],
                "social_interpretation": destiny_profile["social_interpretation"],
                "chosen_by": destiny_profile["chosen_by"],
                "destiny_benefits": destiny_profile["destiny_benefits"],
                "destiny_burdens": destiny_profile["destiny_burdens"],
                "prophecy_model": prophecy_model,
                "legacy_model": legacy_model,
                "agency_conflict_model": agency_conflict_model,
            },
            tags=destiny_profile["similarity_tags"],
            examples=[destiny_profile["destiny_name"]],
            counterexamples=agency_conflict_model["destiny_generation_constraints"],
            confidence_score=destiny_profile["confidence_score"],
            novelty_score=destiny_profile["novelty_score"],
            quality_score=destiny_profile["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        destiny_profile: Dict[str, Any],
        destiny_diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(
            destiny_profile["confidence_score"],
            destiny_profile["originality_score"],
            destiny_diagnostics["destiny_completeness_score"],
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
            consistency_score=destiny_profile["confidence_score"],
            originality_score=destiny_profile["originality_score"],
            safety_score=0.86,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Destiny schema includes pressure, ambiguity, legacy, refusal, and reinterpretation labels.",
                "Training eligibility requires approved source and sufficient quality.",
            ],
        )

    def _similarity_tags(
        self,
        *,
        destiny_family: str,
        destiny_subtype: str,
        pressure_model: Dict[str, Any],
        social_interpretation: Dict[str, Any],
        character_seed: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
    ) -> List[str]:
        tags = {
            destiny_family,
            destiny_subtype,
            pressure_model["pressure_tier"],
            social_interpretation["interpretation_risk"],
            skill_ontology.get("skill_family", "unknown_skill_family"),
            character_type_ontology.get("type_family", "unknown_type_family"),
        }

        if character_seed.get("destiny_type"):
            tags.add(str(character_seed["destiny_type"]))

        if character_seed.get("family_name_status"):
            tags.add(f"name_{character_seed['family_name_status']}")

        return sorted(tags)

    def _retrieval_queries(self, family: str, subtype: str, tags: List[str]) -> List[str]:
        return [
            f"destiny ontology {family} {subtype}",
            f"prophecy ambiguity legacy burden {family}",
            f"agency preserving destiny model {subtype}",
            " ".join(tags[:8]),
        ]

    def _novelty_score(self, family: str, subtype: str, seed: Dict[str, Any]) -> float:
        score = 0.5

        if family in {"power_flow_destiny", "sacred_misinterpretation_destiny", "adaptive_threshold_destiny"}:
            score += 0.16

        if seed.get("family_name_status") in {"distrusted", "erased", "unknown"}:
            score += 0.08

        return self._clamp(score)

    def _originality_score(self, family: str, pressure_model: Dict[str, Any], social: Dict[str, Any]) -> float:
        score = 0.52

        if len(pressure_model.get("pressure_sources", [])) >= 3:
            score += 0.12

        if social.get("interpretation_risk") == "high":
            score += 0.08

        if family != "prophetic_selection_destiny":
            score += 0.08

        return self._clamp(score)

    def _confidence_score(self, family: str, subtype: str, seed: Dict[str, Any]) -> float:
        score = 0.58

        if family != "emergent_choice_destiny":
            score += 0.14

        if subtype:
            score += 0.08

        if seed.get("destiny_type"):
            score += 0.08

        return self._clamp(score)

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        destiny_profile: Dict[str, Any],
        prophecy_model: Dict[str, Any],
        legacy_model: Dict[str, Any],
        agency_conflict_model: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["destiny_profile"] = destiny_profile
        merged_seed["prophecy_model"] = prophecy_model
        merged_seed["legacy_model"] = legacy_model
        merged_seed["destiny_agency_conflict_model"] = agency_conflict_model
        merged_seed["destiny_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "relationship_readiness_payload": {
                "character_seed": merged_seed,
                "destiny_profile": destiny_profile,
                "legacy_model": legacy_model,
                "agency_conflict_model": agency_conflict_model,
            },
            "dialogue_voice_payload": {
                "character_seed": merged_seed,
                "destiny_profile": destiny_profile,
                "prophecy_model": prophecy_model,
                "legacy_model": legacy_model,
            },
            "plot_engine_payload_later": {
                "character_id": destiny_profile["character_id"],
                "destiny_profile": destiny_profile,
                "prophecy_model": prophecy_model,
                "legacy_model": legacy_model,
                "agency_conflict_model": agency_conflict_model,
            },
            "chunk8_training_payload_later": {
                "target_type": "character_destiny",
                "destiny_profile": destiny_profile,
                "prophecy_model": prophecy_model,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
