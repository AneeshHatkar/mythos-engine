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


class DialogueVoiceEngine(BaseEngine):
    """Builds character dialogue voice and speech pattern metadata.

    This does not generate final scenes yet. It creates the reusable voice model
    future dialogue, relationship, plot, and training systems need.

    A voice is not just "formal" or "sarcastic." It is built from:
    - social class
    - education
    - wound
    - secrets
    - agency level
    - morality
    - relationship context
    - emotional state
    - destiny/legacy pressure
    - memory triggers
    - power/skill ontology
    """

    engine_name = "character.dialogue_voice_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin_profile", {})
        family_profile = payload.get("family_profile") or character_seed.get("family_profile", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        emotional_state_profile = payload.get("emotional_state_profile") or character_seed.get("emotional_state_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        destiny_profile = payload.get("destiny_profile") or character_seed.get("destiny_profile", {})
        prophecy_model = payload.get("prophecy_model") or character_seed.get("prophecy_model", {})
        legacy_model = payload.get("legacy_model") or character_seed.get("legacy_model", {})
        relationship_readiness_profile = payload.get("relationship_readiness_profile") or character_seed.get("relationship_readiness_profile", {})
        attachment_and_conflict_model = payload.get("attachment_and_conflict_model") or character_seed.get("attachment_and_conflict_model", {})
        boundary_model = payload.get("boundary_model") or character_seed.get("relationship_boundary_model", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; dialogue voice engine used draft defaults.")

        character_id = (
            character_seed.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or relationship_readiness_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        dialogue_voice_profile = self._build_dialogue_voice_profile(
            character_id=character_id,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            origin_profile=origin_profile,
            family_profile=family_profile,
            moral_profile=moral_profile,
            goal_profile=goal_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            destiny_profile=destiny_profile,
            relationship_readiness_profile=relationship_readiness_profile,
        )

        speech_pattern_model = self._build_speech_pattern_model(
            dialogue_voice_profile=dialogue_voice_profile,
            character_seed=character_seed,
            origin_profile=origin_profile,
            psychology_profile=psychology_profile,
            emotional_state_profile=emotional_state_profile,
            memory_records=memory_records,
        )

        emotional_dialogue_rules = self._build_emotional_dialogue_rules(
            dialogue_voice_profile=dialogue_voice_profile,
            psychology_profile=psychology_profile,
            emotional_state_profile=emotional_state_profile,
            attachment_and_conflict_model=attachment_and_conflict_model,
            moral_profile=moral_profile,
        )

        relationship_dialogue_variants = self._build_relationship_dialogue_variants(
            dialogue_voice_profile=dialogue_voice_profile,
            relationship_readiness_profile=relationship_readiness_profile,
            attachment_and_conflict_model=attachment_and_conflict_model,
            boundary_model=boundary_model,
        )

        destiny_dialogue_layer = self._build_destiny_dialogue_layer(
            dialogue_voice_profile=dialogue_voice_profile,
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
        )

        forbidden_dialogue_patterns = self._build_forbidden_dialogue_patterns(
            dialogue_voice_profile=dialogue_voice_profile,
            character_seed=character_seed,
            boundary_model=boundary_model,
        )

        dialogue_diagnostics = self._build_diagnostics(
            dialogue_voice_profile=dialogue_voice_profile,
            speech_pattern_model=speech_pattern_model,
            emotional_dialogue_rules=emotional_dialogue_rules,
            relationship_dialogue_variants=relationship_dialogue_variants,
            destiny_dialogue_layer=destiny_dialogue_layer,
            forbidden_dialogue_patterns=forbidden_dialogue_patterns,
        )

        ontology_record = self._build_ontology_record(
            dialogue_voice_profile=dialogue_voice_profile,
            speech_pattern_model=speech_pattern_model,
            emotional_dialogue_rules=emotional_dialogue_rules,
            relationship_dialogue_variants=relationship_dialogue_variants,
            destiny_dialogue_layer=destiny_dialogue_layer,
            forbidden_dialogue_patterns=forbidden_dialogue_patterns,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_dialogue_voice",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=dialogue_voice_profile["similarity_tags"],
            novelty_score=dialogue_voice_profile["novelty_score"],
            originality_score=dialogue_voice_profile["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            dialogue_voice_profile=dialogue_voice_profile,
            diagnostics=dialogue_diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=dialogue_voice_profile["voice_name"],
            type_family="dialogue_voice",
            type_subfamily=dialogue_voice_profile["voice_family"],
            type_scope="character_dialogue",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=dialogue_voice_profile["similarity_tags"],
            generation_constraints=forbidden_dialogue_patterns["dialogue_generation_constraints"],
            counter_patterns=forbidden_dialogue_patterns["generic_voice_failure_modes"],
            learned_axes={
                "dialogue_voice_profile": dialogue_voice_profile,
                "speech_pattern_model": speech_pattern_model,
                "emotional_dialogue_rules": emotional_dialogue_rules,
                "relationship_dialogue_variants": relationship_dialogue_variants,
                "destiny_dialogue_layer": destiny_dialogue_layer,
                "forbidden_dialogue_patterns": forbidden_dialogue_patterns,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_dialogue_voice",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=dialogue_voice_profile["retrieval_context_queries"],
            generated_training_labels={
                "voice_family": dialogue_voice_profile["voice_family"],
                "voice_subtype": dialogue_voice_profile["voice_subtype"],
                "formality_level": speech_pattern_model["formality_level"],
                "sentence_rhythm": speech_pattern_model["sentence_rhythm"],
                "subtext_density": speech_pattern_model["subtext_density"],
                "emotional_leakage_model": emotional_dialogue_rules["emotional_leakage_model"],
                "relationship_voice_ready": dialogue_diagnostics["relationship_voice_ready"],
                "dialogue_training_ready": dialogue_diagnostics["training_ready_schema"],
            },
            learning_notes=[
                "Dialogue voice is represented as structured speech axes, not generic style labels.",
                "Future dialogue generation should retrieve similar voice families and relationship variants.",
                "Future training should learn voice patterns from licensed dialogue/story datasets and human-approved synthetic examples.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            dialogue_voice_profile=dialogue_voice_profile,
            speech_pattern_model=speech_pattern_model,
            emotional_dialogue_rules=emotional_dialogue_rules,
            relationship_dialogue_variants=relationship_dialogue_variants,
            destiny_dialogue_layer=destiny_dialogue_layer,
            forbidden_dialogue_patterns=forbidden_dialogue_patterns,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "dialogue_voice_profile": dialogue_voice_profile,
                "speech_pattern_model": speech_pattern_model,
                "emotional_dialogue_rules": emotional_dialogue_rules,
                "relationship_dialogue_variants": relationship_dialogue_variants,
                "destiny_dialogue_layer": destiny_dialogue_layer,
                "forbidden_dialogue_patterns": forbidden_dialogue_patterns,
                "dialogue_diagnostics": dialogue_diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "dialogue_voice_summary": {
                    "character_id": character_id,
                    "voice_family": dialogue_voice_profile["voice_family"],
                    "voice_subtype": dialogue_voice_profile["voice_subtype"],
                    "formality_level": speech_pattern_model["formality_level"],
                    "sentence_rhythm": speech_pattern_model["sentence_rhythm"],
                    "subtext_density": speech_pattern_model["subtext_density"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_character_validator": True,
                    "ready_for_character_bible_export": True,
                    "ready_for_chunk4_dialogue_simulation": True,
                    "ready_for_chunk8_training_later": True,
                },
                "training_notes": [
                    "Dialogue must vary by relationship context and emotional pressure.",
                    "A character voice should preserve social origin, wound, agency, morality, and secrets.",
                    "Generic witty/formal/sarcastic dialogue is forbidden unless supported by ontology axes.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                dialogue_voice_profile["dialogue_voice_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_dialogue_voice_profile(
        self,
        *,
        character_id: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        origin_profile: Dict[str, Any],
        family_profile: Dict[str, Any],
        moral_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        destiny_profile: Dict[str, Any],
        relationship_readiness_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        voice_family, voice_subtype = self._voice_family_and_subtype(
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            origin_profile=origin_profile,
            character_type_ontology=character_type_ontology,
            relationship_readiness_profile=relationship_readiness_profile,
        )

        voice_name = self._voice_name(character_seed, voice_family, voice_subtype)
        core_voice_principle = self._core_voice_principle(
            voice_family=voice_family,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            destiny_profile=destiny_profile,
        )
        similarity_tags = self._similarity_tags(
            voice_family=voice_family,
            voice_subtype=voice_subtype,
            character_seed=character_seed,
            psychology_profile=psychology_profile,
            origin_profile=origin_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            relationship_readiness_profile=relationship_readiness_profile,
        )

        return {
            "dialogue_voice_id": f"dvoice_{uuid4().hex[:12]}",
            "character_id": character_id,
            "voice_name": voice_name,
            "voice_family": voice_family,
            "voice_subtype": voice_subtype,
            "core_voice_principle": core_voice_principle,
            "voice_social_root": self._voice_social_root(character_seed, origin_profile, family_profile),
            "voice_wound_root": self._voice_wound_root(psychology_profile, goal_profile),
            "voice_power_root": self._voice_power_root(skill_ontology, character_type_ontology),
            "voice_destiny_root": self._voice_destiny_root(destiny_profile),
            "voice_relationship_root": self._voice_relationship_root(relationship_readiness_profile),
            "signature_tension": self._signature_tension(psychology_profile, goal_profile, relationship_readiness_profile),
            "voice_strength": self._voice_strength(voice_family, psychology_profile, character_type_ontology),
            "voice_risk": self._voice_risk(psychology_profile, relationship_readiness_profile, destiny_profile),
            "similarity_tags": similarity_tags,
            "retrieval_context_queries": self._retrieval_queries(voice_family, voice_subtype, similarity_tags),
            "novelty_score": self._novelty_score(voice_family, voice_subtype, destiny_profile),
            "originality_score": self._originality_score(voice_family, core_voice_principle, relationship_readiness_profile),
            "confidence_score": self._confidence_score(voice_family, psychology_profile, origin_profile, character_type_ontology),
        }

    def _voice_family_and_subtype(
        self,
        *,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        origin_profile: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        relationship_readiness_profile: Dict[str, Any],
    ) -> tuple[str, str]:
        text = " ".join([
            str(character_seed),
            str(psychology_profile),
            str(origin_profile),
            str(character_type_ontology),
            str(relationship_readiness_profile),
        ]).lower()

        if "power_broker" in text or "kingmaker" in text or "power_redirector" in text:
            return "controlled_subtext_voice", "strategic_understatement"

        if "villain" in text or "institutional" in text or "magister" in text:
            return "institutional_authority_voice", "procedural_threat"

        if "rival" in text or "prodigy" in text:
            return "competitive_pressure_voice", "sharp_comparison"

        if "love_interest" in text or "romantic_agency" in text:
            return "independent_intimacy_voice", "boundary_aware_warmth"

        if "erased" in text or "underclass" in text or "low-trust" in text:
            return "guarded_survival_voice", "careful_minimal_disclosure"

        if "saint" in text or "sacred" in text:
            return "sacred_contradiction_voice", "public_grace_private_strain"

        return "contextual_character_voice", "adaptive_plain_speech"

    def _voice_name(self, seed: Dict[str, Any], family: str, subtype: str) -> str:
        if seed.get("voice_name"):
            return seed["voice_name"]
        return f"{family}:{subtype}"

    def _core_voice_principle(
        self,
        *,
        voice_family: str,
        psychology_profile: Dict[str, Any],
        goal_profile: Dict[str, Any],
        destiny_profile: Dict[str, Any],
    ) -> str:
        if voice_family == "controlled_subtext_voice":
            return "says less than they know and tests whether others can read consequence"

        if voice_family == "institutional_authority_voice":
            return "turns procedure, hierarchy, and certainty into pressure"

        if voice_family == "competitive_pressure_voice":
            return "speaks through comparison, challenge, and concealed respect hunger"

        if voice_family == "independent_intimacy_voice":
            return "offers warmth without surrendering agency or personal mission"

        if psychology_profile.get("core_wound"):
            return f"protects wound through speech: {psychology_profile['core_wound']}"

        if goal_profile.get("hidden_goal"):
            return f"speaks around hidden goal: {goal_profile['hidden_goal']}"

        if destiny_profile.get("destiny_family"):
            return f"speech carries destiny pressure: {destiny_profile['destiny_family']}"

        return "speech adapts to pressure while preserving identity"

    def _voice_social_root(self, seed: Dict[str, Any], origin: Dict[str, Any], family: Dict[str, Any]) -> str:
        social_class = seed.get("social_class") or origin.get("social_class") or "unknown"
        family_status = seed.get("family_name_status") or origin.get("family_name_status") or "unknown"

        if social_class == "academy_sponsored":
            return "educated but conditional; careful with authority and proof"

        if social_class in {"old_nobility", "imperial_elite"}:
            return "trained for status, implication, and command"

        if family_status in {"distrusted", "erased", "unknown"}:
            return "careful with claims because name does not protect speech"

        return f"social class {social_class}; family status {family_status}"

    def _voice_wound_root(self, psychology: Dict[str, Any], goal: Dict[str, Any]) -> str:
        if psychology.get("shame_trigger"):
            return f"shame trigger shapes speech: {psychology['shame_trigger']}"

        if psychology.get("core_wound"):
            return psychology["core_wound"]

        if goal.get("false_need"):
            return f"false need leaks into speech: {goal['false_need']}"

        return "wound not fully specified; voice should reveal pressure indirectly"

    def _voice_power_root(self, skill_ontology: Dict[str, Any], type_ontology: Dict[str, Any]) -> str:
        skill_family = skill_ontology.get("skill_family")
        type_family = type_ontology.get("type_family")

        if skill_family == "cognitive_inference":
            return "speech notices patterns but rarely states all evidence at once"

        if skill_family == "institutional_authority":
            return "speech uses rule language and procedural leverage"

        if type_family == "power_redirector":
            return "speech redirects choices instead of demanding obedience"

        return "power influence is contextual and should not dominate every line"

    def _voice_destiny_root(self, destiny: Dict[str, Any]) -> str:
        if destiny.get("destiny_family") == "power_flow_destiny":
            return "speaks as if every choice may redirect power"

        if destiny.get("destiny_family") == "adaptive_threshold_destiny":
            return "speech tightens around thresholds and moral pressure"

        if destiny.get("destiny_burdens"):
            return f"destiny burden shapes speech: {destiny['destiny_burdens'][0]}"

        return "destiny pressure is subtle or not yet voiced"

    def _voice_relationship_root(self, readiness: Dict[str, Any]) -> str:
        if readiness.get("trust_model"):
            return f"trust model shapes disclosure: {readiness['trust_model']}"

        if readiness.get("attachment_pattern"):
            return f"attachment pattern shapes pauses: {readiness['attachment_pattern']}"

        return "relationship voice changes with trust level"

    def _signature_tension(self, psychology: Dict[str, Any], goal: Dict[str, Any], readiness: Dict[str, Any]) -> str:
        if goal.get("hidden_goal") and readiness.get("trust_model"):
            return f"wants {goal['hidden_goal']} but trust requires {readiness['trust_model']}"

        if psychology.get("healing_condition"):
            return f"needs {psychology['healing_condition']} but resists being known"

        return "wants connection but protects control"

    def _voice_strength(self, family: str, psychology: Dict[str, Any], type_ontology: Dict[str, Any]) -> float:
        score = 0.55

        if family != "contextual_character_voice":
            score += 0.16

        if psychology:
            score += 0.1

        if type_ontology:
            score += 0.08

        return self._clamp(score)

    def _voice_risk(self, psychology: Dict[str, Any], readiness: Dict[str, Any], destiny: Dict[str, Any]) -> float:
        score = 0.25
        text = " ".join([str(psychology), str(readiness), str(destiny)]).lower()

        if "secret" in text:
            score += 0.18
        if "betrayal" in text:
            score += 0.12
        if "destiny" in text or destiny.get("destiny_family"):
            score += 0.08

        return self._clamp(score)

    def _build_speech_pattern_model(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        origin_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        emotional_state_profile: Dict[str, Any],
        memory_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        family = dialogue_voice_profile["voice_family"]

        return {
            "speech_pattern_id": f"speech_{uuid4().hex[:12]}",
            "formality_level": self._formality_level(family, character_seed, origin_profile),
            "sentence_rhythm": self._sentence_rhythm(family, psychology_profile),
            "subtext_density": self._subtext_density(family, psychology_profile, memory_records),
            "directness_level": self._directness_level(family, psychology_profile),
            "metaphor_source": self._metaphor_source(character_seed, origin_profile, dialogue_voice_profile),
            "pause_behavior": self._pause_behavior(psychology_profile, family),
            "question_style": self._question_style(family, psychology_profile),
            "conflict_syntax": self._conflict_syntax(family),
            "comfort_syntax": self._comfort_syntax(family),
            "signature_phrasing_rules": self._signature_phrasing_rules(family, dialogue_voice_profile),
        }

    def _formality_level(self, family: str, seed: Dict[str, Any], origin: Dict[str, Any]) -> str:
        if family == "institutional_authority_voice":
            return "high_formality"
        if seed.get("social_class") in {"old_nobility", "imperial_elite"}:
            return "controlled_formal"
        if seed.get("social_class") == "academy_sponsored":
            return "educated_controlled"
        return "contextual_formality"

    def _sentence_rhythm(self, family: str, psychology: Dict[str, Any]) -> str:
        if family == "controlled_subtext_voice":
            return "short_precise_lines_with_held_back_explanations"
        if family == "institutional_authority_voice":
            return "measured_declarative_sentences"
        if family == "competitive_pressure_voice":
            return "sharp_compressed_challenges"
        if family == "independent_intimacy_voice":
            return "warm_but_boundary_marked_sentences"
        if psychology.get("anxiety_pattern"):
            return "fragmented_under_pressure"
        return "adaptive_mid_length_sentences"

    def _subtext_density(self, family: str, psychology: Dict[str, Any], memories: List[Dict[str, Any]]) -> str:
        if family in {"controlled_subtext_voice", "guarded_survival_voice"}:
            return "high_subtext"
        if "secret" in str(psychology).lower() or "secret" in str(memories).lower():
            return "high_subtext"
        if family == "institutional_authority_voice":
            return "medium_high_subtext"
        return "medium_subtext"

    def _directness_level(self, family: str, psychology: Dict[str, Any]) -> str:
        if family == "institutional_authority_voice":
            return "direct_about_power_indirect_about_wound"
        if family == "controlled_subtext_voice":
            return "indirect_until_moral_threshold"
        if family == "competitive_pressure_voice":
            return "direct_in_challenge_indirect_in_vulnerability"
        return "contextual_directness"

    def _metaphor_source(self, seed: Dict[str, Any], origin: Dict[str, Any], voice: Dict[str, Any]) -> List[str]:
        sources = []
        if "academy" in str(seed).lower() or seed.get("social_class") == "academy_sponsored":
            sources.extend(["exams", "rankings", "archives", "lessons"])
        if "oath" in str(seed).lower():
            sources.append("oaths")
        if "destiny" in str(voice).lower():
            sources.append("patterns and consequences")
        if not sources:
            sources.append("daily survival details")
        return sorted(set(sources))

    def _pause_behavior(self, psychology: Dict[str, Any], family: str) -> str:
        if "secret" in str(psychology).lower():
            return "pauses before truth-adjacent statements"
        if family == "controlled_subtext_voice":
            return "uses silence as information control"
        return "pauses under emotional pressure"

    def _question_style(self, family: str, psychology: Dict[str, Any]) -> str:
        if family == "controlled_subtext_voice":
            return "asks questions that reveal what others missed"
        if family == "institutional_authority_voice":
            return "asks questions as procedural traps"
        if family == "competitive_pressure_voice":
            return "asks questions as challenges"
        return "asks questions to test safety"

    def _conflict_syntax(self, family: str) -> List[str]:
        if family == "controlled_subtext_voice":
            return ["short correction", "precise accusation", "withheld full explanation"]
        if family == "institutional_authority_voice":
            return ["formal address", "rule citation", "consequence framing"]
        if family == "competitive_pressure_voice":
            return ["comparison", "challenge", "refusal to soften"]
        return ["specific boundary", "emotional truth under restraint"]

    def _comfort_syntax(self, family: str) -> List[str]:
        if family == "controlled_subtext_voice":
            return ["practical help", "quiet presence", "truth without spectacle"]
        if family == "institutional_authority_voice":
            return ["rare concession", "controlled protection", "formalized promise"]
        if family == "independent_intimacy_voice":
            return ["warmth plus boundary", "direct reassurance", "mutual agency"]
        return ["specific reassurance", "small concrete offer", "non-demanding presence"]

    def _signature_phrasing_rules(self, family: str, voice: Dict[str, Any]) -> List[str]:
        rules = [
            "voice must reveal what the character notices",
            "voice must hide what the character is not ready to disclose",
            "voice must shift under relationship pressure",
        ]

        if family == "controlled_subtext_voice":
            rules.append("avoid overexplaining; imply through precise observation")

        if family == "institutional_authority_voice":
            rules.append("use formal certainty and procedural framing")

        if family == "competitive_pressure_voice":
            rules.append("turn vulnerability into challenge until trust changes")

        return rules

    def _build_emotional_dialogue_rules(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        emotional_state_profile: Dict[str, Any],
        attachment_and_conflict_model: Dict[str, Any],
        moral_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "emotional_dialogue_id": f"emodial_{uuid4().hex[:12]}",
            "emotional_leakage_model": self._emotional_leakage_model(dialogue_voice_profile, psychology_profile),
            "anger_voice": self._anger_voice(dialogue_voice_profile, psychology_profile),
            "fear_voice": self._fear_voice(dialogue_voice_profile, psychology_profile),
            "love_voice": self._love_voice(dialogue_voice_profile, psychology_profile),
            "betrayal_voice": self._betrayal_voice(dialogue_voice_profile, psychology_profile, attachment_and_conflict_model),
            "guilt_voice": self._guilt_voice(dialogue_voice_profile, moral_profile),
            "healing_voice": self._healing_voice(dialogue_voice_profile, psychology_profile),
            "emotional_forbidden_shortcuts": [
                "do not make emotional confession too early",
                "do not use generic trauma dumping",
                "do not make love instantly heal the wound",
                "do not erase established boundaries for dramatic effect",
            ],
        }

    def _emotional_leakage_model(self, voice: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if voice["voice_family"] == "controlled_subtext_voice":
            return "emotion leaks through precision, silence, and what is not answered"
        if psychology.get("shame_trigger"):
            return f"emotion leaks when shame trigger appears: {psychology['shame_trigger']}"
        return "emotion leaks through rhythm changes and defensive phrasing"

    def _anger_voice(self, voice: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if voice["voice_family"] == "controlled_subtext_voice":
            return "cold specificity; fewer words; exact memory of harm"
        return "boundary becomes sharper and less negotiable"

    def _fear_voice(self, voice: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if psychology.get("core_fear"):
            return f"fear voice circles around: {psychology['core_fear']}"
        return "fear appears as control and preparation"

    def _love_voice(self, voice: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if psychology.get("love_response"):
            return f"{psychology['love_response']}; practical protection appears before direct confession"
        return "love appears through practical protection before direct confession"

    def _betrayal_voice(self, voice: Dict[str, Any], psychology: Dict[str, Any], attachment: Dict[str, Any]) -> str:
        if psychology.get("betrayal_response"):
            return psychology["betrayal_response"]
        if attachment.get("betrayal_sensitivity", 0.0) >= 0.6:
            return "turns calm, exact, and difficult to reach"
        return "withdraws and tests whether repair is real"

    def _guilt_voice(self, voice: Dict[str, Any], moral: Dict[str, Any]) -> str:
        if moral.get("dominant_moral_value"):
            return f"guilt names failure against {moral['dominant_moral_value']}"
        return "guilt appears as overcorrection and quiet responsibility"

    def _healing_voice(self, voice: Dict[str, Any], psychology: Dict[str, Any]) -> str:
        if psychology.get("healing_condition"):
            return f"healing voice allows: {psychology['healing_condition']}"
        return "healing voice becomes more direct without losing boundaries"

    def _build_relationship_dialogue_variants(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        relationship_readiness_profile: Dict[str, Any],
        attachment_and_conflict_model: Dict[str, Any],
        boundary_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "relationship_dialogue_id": f"reldial_{uuid4().hex[:12]}",
            "stranger_voice": "measured, observant, non-disclosing",
            "friend_voice": "practical warmth; more context but still careful",
            "rival_voice": "sharper, comparative, truth through challenge",
            "romance_voice": "softens through specific trust, not generic confession",
            "family_voice": "guarded around name, duty, debt, and old interpretations",
            "mentor_voice": "tests whether guidance is control or liberation",
            "enemy_voice": "minimal disclosure; precise threat assessment",
            "betrayal_voice_variant": "calm becomes colder; details become exact",
            "repair_voice_variant": "repair requires specific admission and changed behavior",
            "boundary_voice_variant": self._boundary_voice_variant(boundary_model),
        }

    def _boundary_voice_variant(self, boundary_model: Dict[str, Any]) -> str:
        if boundary_model.get("boundary_strength", 0.0) >= 0.65:
            return "states boundary directly without overexplaining"
        return "signals discomfort before stating boundary clearly"

    def _build_destiny_dialogue_layer(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        destiny_profile: Dict[str, Any],
        prophecy_model: Dict[str, Any],
        legacy_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "destiny_dialogue_id": f"destdial_{uuid4().hex[:12]}",
            "prophecy_response_voice": self._prophecy_response_voice(destiny_profile, prophecy_model),
            "legacy_pressure_voice": self._legacy_pressure_voice(legacy_model),
            "destiny_denial_voice": "rejects simplistic labels and asks who benefits from the interpretation",
            "destiny_acceptance_voice": "accepts responsibility without surrendering agency",
            "destiny_forbidden_voice": "must not speak as if destiny guarantees victory or ownership of others",
        }

    def _prophecy_response_voice(self, destiny: Dict[str, Any], prophecy: Dict[str, Any]) -> str:
        if destiny.get("destiny_family") == "power_flow_destiny":
            return "questions who wants the prophecy to mean power transfer"
        if prophecy.get("prophecy_text"):
            return "treats prophecy as pressure, not command"
        return "responds to destiny with suspicion and agency"

    def _legacy_pressure_voice(self, legacy: Dict[str, Any]) -> str:
        if legacy.get("legacy_pressure_type"):
            return f"voice tightens around legacy pressure: {legacy['legacy_pressure_type']}"
        return "voice resists inherited labels"

    def _build_forbidden_dialogue_patterns(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        character_seed: Dict[str, Any],
        boundary_model: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "forbidden_dialogue_id": f"forbidvoice_{uuid4().hex[:12]}",
            "generic_voice_failure_modes": [
                "generic witty banter disconnected from wound",
                "overexplaining hidden motives too early",
                "same voice in every relationship context",
                "therapy-speak without world grounding",
                "instant confession without earned trust",
                "villain monologue without ideology or pressure",
            ],
            "dialogue_generation_constraints": [
                "preserve character-specific subtext",
                "vary voice by relationship context",
                "respect boundaries and independent goals",
                "make emotional disclosure earned",
                "tie speech to social origin and wound",
                "avoid generic anime/prose archetype voice unless ontology supports it",
            ] + boundary_model.get("relationship_generation_constraints", []),
            "must_not_say_rules": [
                "must not reveal secrets unless trust/pressure condition is met",
                "must not collapse into exposition machine",
                "must not speak with omniscient author voice",
                "must not flatten into trope label",
            ],
        }

    def _build_diagnostics(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        speech_pattern_model: Dict[str, Any],
        emotional_dialogue_rules: Dict[str, Any],
        relationship_dialogue_variants: Dict[str, Any],
        destiny_dialogue_layer: Dict[str, Any],
        forbidden_dialogue_patterns: Dict[str, Any],
    ) -> Dict[str, Any]:
        completeness = sum(
            [
                bool(dialogue_voice_profile["voice_family"]),
                bool(dialogue_voice_profile["core_voice_principle"]),
                bool(speech_pattern_model["formality_level"]),
                bool(speech_pattern_model["sentence_rhythm"]),
                bool(speech_pattern_model["subtext_density"]),
                bool(emotional_dialogue_rules["emotional_leakage_model"]),
                bool(relationship_dialogue_variants["friend_voice"]),
                bool(relationship_dialogue_variants["romance_voice"]),
                bool(destiny_dialogue_layer["destiny_denial_voice"]),
                bool(forbidden_dialogue_patterns["generic_voice_failure_modes"]),
                bool(forbidden_dialogue_patterns["dialogue_generation_constraints"]),
            ]
        ) / 11

        return {
            "dialogue_voice_completeness_score": round(completeness, 3),
            "has_voice_family": bool(dialogue_voice_profile["voice_family"]),
            "has_speech_pattern": bool(speech_pattern_model["sentence_rhythm"]),
            "has_emotional_rules": bool(emotional_dialogue_rules["emotional_leakage_model"]),
            "has_relationship_variants": bool(relationship_dialogue_variants["friend_voice"]),
            "has_destiny_layer": bool(destiny_dialogue_layer["destiny_denial_voice"]),
            "has_forbidden_patterns": bool(forbidden_dialogue_patterns["generic_voice_failure_modes"]),
            "relationship_voice_ready": True,
            "character_bible_ready": completeness >= 0.9,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        speech_pattern_model: Dict[str, Any],
        emotional_dialogue_rules: Dict[str, Any],
        relationship_dialogue_variants: Dict[str, Any],
        destiny_dialogue_layer: Dict[str, Any],
        forbidden_dialogue_patterns: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="dialogue_voice",
            name=dialogue_voice_profile["voice_name"],
            family=dialogue_voice_profile["voice_family"],
            subtype=dialogue_voice_profile["voice_subtype"],
            description=dialogue_voice_profile["core_voice_principle"],
            axes={
                "dialogue_voice_profile": dialogue_voice_profile,
                "speech_pattern_model": speech_pattern_model,
                "emotional_dialogue_rules": emotional_dialogue_rules,
                "relationship_dialogue_variants": relationship_dialogue_variants,
                "destiny_dialogue_layer": destiny_dialogue_layer,
                "forbidden_dialogue_patterns": forbidden_dialogue_patterns,
            },
            tags=dialogue_voice_profile["similarity_tags"],
            examples=[dialogue_voice_profile["voice_name"]],
            counterexamples=forbidden_dialogue_patterns["generic_voice_failure_modes"],
            confidence_score=dialogue_voice_profile["confidence_score"],
            novelty_score=dialogue_voice_profile["novelty_score"],
            quality_score=dialogue_voice_profile["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        dialogue_voice_profile: Dict[str, Any],
        diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(
            dialogue_voice_profile["confidence_score"],
            dialogue_voice_profile["originality_score"],
            diagnostics["dialogue_voice_completeness_score"],
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
            consistency_score=dialogue_voice_profile["confidence_score"],
            originality_score=dialogue_voice_profile["originality_score"],
            safety_score=0.88,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Dialogue voice schema includes speech rhythm, emotional rules, relationship variants, and forbidden generic patterns.",
                "Training eligibility requires approved source and sufficient quality.",
            ],
        )

    def _similarity_tags(
        self,
        *,
        voice_family: str,
        voice_subtype: str,
        character_seed: Dict[str, Any],
        psychology_profile: Dict[str, Any],
        origin_profile: Dict[str, Any],
        skill_ontology: Dict[str, Any],
        character_type_ontology: Dict[str, Any],
        relationship_readiness_profile: Dict[str, Any],
    ) -> List[str]:
        tags = {
            voice_family,
            voice_subtype,
            skill_ontology.get("skill_family", "unknown_skill_family"),
            character_type_ontology.get("type_family", "unknown_type_family"),
            relationship_readiness_profile.get("relationship_readiness_family", "unknown_relationship_readiness"),
        }

        for key in ["role", "social_class", "family_name_status", "destiny_type"]:
            if character_seed.get(key):
                tags.add(str(character_seed[key]))

        for term in ["secret", "shame", "betrayal", "academy", "kingmaker", "rival", "villain", "romance"]:
            if term in " ".join([str(character_seed), str(psychology_profile), str(origin_profile)]).lower():
                tags.add(term)

        return sorted(tags)

    def _retrieval_queries(self, family: str, subtype: str, tags: List[str]) -> List[str]:
        return [
            f"dialogue voice ontology {family} {subtype}",
            f"speech rhythm subtext emotional leakage {family}",
            f"relationship dialogue variants {subtype}",
            " ".join(tags[:8]),
        ]

    def _novelty_score(self, family: str, subtype: str, destiny: Dict[str, Any]) -> float:
        score = 0.5
        if family not in {"contextual_character_voice"}:
            score += 0.12
        if destiny.get("destiny_family"):
            score += 0.06
        return self._clamp(score)

    def _originality_score(self, family: str, principle: str, readiness: Dict[str, Any]) -> float:
        score = 0.52
        if family not in {"contextual_character_voice"}:
            score += 0.1
        if "trust" in str(readiness).lower() or "secret" in principle.lower():
            score += 0.08
        if len(principle.split()) >= 8:
            score += 0.06
        return self._clamp(score)

    def _confidence_score(self, family: str, psychology: Dict[str, Any], origin: Dict[str, Any], type_ontology: Dict[str, Any]) -> float:
        score = 0.56
        if family != "contextual_character_voice":
            score += 0.14
        if psychology:
            score += 0.08
        if origin or type_ontology:
            score += 0.08
        return self._clamp(score)

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        dialogue_voice_profile: Dict[str, Any],
        speech_pattern_model: Dict[str, Any],
        emotional_dialogue_rules: Dict[str, Any],
        relationship_dialogue_variants: Dict[str, Any],
        destiny_dialogue_layer: Dict[str, Any],
        forbidden_dialogue_patterns: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["dialogue_voice_profile"] = dialogue_voice_profile
        merged_seed["speech_pattern_model"] = speech_pattern_model
        merged_seed["emotional_dialogue_rules"] = emotional_dialogue_rules
        merged_seed["relationship_dialogue_variants"] = relationship_dialogue_variants
        merged_seed["destiny_dialogue_layer"] = destiny_dialogue_layer
        merged_seed["forbidden_dialogue_patterns"] = forbidden_dialogue_patterns
        merged_seed["dialogue_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "character_validator_payload": {
                "character_seed": merged_seed,
                "dialogue_voice_profile": dialogue_voice_profile,
                "speech_pattern_model": speech_pattern_model,
                "forbidden_dialogue_patterns": forbidden_dialogue_patterns,
            },
            "character_bible_export_payload": {
                "character_seed": merged_seed,
                "dialogue_voice_profile": dialogue_voice_profile,
                "relationship_dialogue_variants": relationship_dialogue_variants,
                "destiny_dialogue_layer": destiny_dialogue_layer,
            },
            "chunk4_dialogue_simulation_payload_later": {
                "character_id": dialogue_voice_profile["character_id"],
                "dialogue_voice_profile": dialogue_voice_profile,
                "speech_pattern_model": speech_pattern_model,
                "emotional_dialogue_rules": emotional_dialogue_rules,
                "relationship_dialogue_variants": relationship_dialogue_variants,
            },
            "chunk8_training_payload_later": {
                "target_type": "dialogue_voice",
                "dialogue_voice_profile": dialogue_voice_profile,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
