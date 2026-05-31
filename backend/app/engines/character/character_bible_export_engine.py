from pathlib import Path
from typing import Any, Dict, List, Optional
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


class CharacterBibleExportEngine(BaseEngine):
    """Exports a full character profile into a structured character bible.

    This is not the final PDF/DOCX export layer yet. This produces stable
    JSON/Markdown-ready content that later physical export engines can convert
    into PDF, DOCX, frontend views, or franchise bibles.
    """

    engine_name = "character.bible_export_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        full_profile = (
            payload.get("character_full_profile")
            or payload.get("full_profile")
            or payload.get("profile")
            or {}
        )

        character_seed = payload.get("character_seed", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")
        write_to_disk = bool(payload.get("write_to_disk", False))
        output_dir = payload.get("output_dir", "reports/character_bibles")

        warnings: List[str] = []

        if not full_profile:
            warnings.append("No character_full_profile provided; export engine built partial bible from character_seed.")
            full_profile = self._profile_from_seed(character_seed)

        character_id = (
            full_profile.get("character_id")
            or full_profile.get("identity", {}).get("character_id")
            or character_seed.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        bible = self._build_character_bible(
            character_id=character_id,
            full_profile=full_profile,
        )

        markdown = self._build_markdown_export(bible)
        export_report = self._build_export_report(bible=bible, markdown=markdown)
        export_diagnostics = self._build_diagnostics(bible=bible, export_report=export_report)

        file_outputs: Dict[str, Any] = {
            "written": False,
            "json_path": None,
            "markdown_path": None,
        }

        if write_to_disk:
            file_outputs = self._write_outputs(
                character_id=character_id,
                bible=bible,
                markdown=markdown,
                output_dir=output_dir,
            )

        ontology_record = self._build_ontology_record(
            bible=bible,
            export_report=export_report,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_bible_export",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=export_report["similarity_tags"],
            novelty_score=export_report["novelty_score"],
            originality_score=export_report["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            bible=bible,
            export_report=export_report,
            export_diagnostics=export_diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=export_report["export_name"],
            type_family="character_bible_export",
            type_subfamily=export_report["export_tier"],
            type_scope="character_artifact",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=export_report["similarity_tags"],
            generation_constraints=export_report["export_constraints"],
            counter_patterns=export_report["missing_sections"],
            learned_axes={
                "character_bible": bible,
                "export_report": export_report,
                "export_diagnostics": export_diagnostics,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_bible_export",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=export_report["retrieval_context_queries"],
            generated_training_labels={
                "export_tier": export_report["export_tier"],
                "export_completeness_score": export_report["export_completeness_score"],
                "markdown_ready": export_diagnostics["markdown_ready"],
                "json_ready": export_diagnostics["json_ready"],
                "physical_export_ready_later": export_diagnostics["physical_export_ready_later"],
                "chunk4_ready": export_diagnostics["chunk4_ready"],
                "training_queue_ready": export_diagnostics["training_queue_ready"],
            },
            learning_notes=[
                "Character Bible export is the final human-readable artifact layer for Chunk 3.",
                "PDF/DOCX physical export should be added later after the whole project frontend/export system is stable.",
                "This export preserves validation, originality, quality, relationship, dialogue, and learning metadata.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_id=character_id,
            bible=bible,
            markdown=markdown,
            export_report=export_report,
            learning_metadata=learning_metadata,
            file_outputs=file_outputs,
        )

        return self.build_result(
            success=True,
            data={
                "character_bible": bible,
                "character_bible_markdown": markdown,
                "export_report": export_report,
                "export_diagnostics": export_diagnostics,
                "file_outputs": file_outputs,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "character_bible_summary": {
                    "character_id": character_id,
                    "character_name": bible["identity"]["name"],
                    "export_tier": export_report["export_tier"],
                    "export_completeness_score": export_report["export_completeness_score"],
                    "markdown_ready": export_diagnostics["markdown_ready"],
                    "json_ready": export_diagnostics["json_ready"],
                    "physical_export_ready_later": export_diagnostics["physical_export_ready_later"],
                    "training_eligible": training_eligibility.training_eligible,
                    "written_to_disk": file_outputs["written"],
                },
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                bible["bible_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _profile_from_seed(self, seed: Dict[str, Any]) -> Dict[str, Any]:
        character_id = seed.get("character_id", f"char_{uuid4().hex[:12]}")
        return {
            "profile_id": f"charprofile_seed_{uuid4().hex[:8]}",
            "character_id": character_id,
            "identity": {
                "character_id": character_id,
                "name": seed.get("name", "Unnamed Character"),
                "role": seed.get("role", "unknown"),
                "archetype_label": seed.get("people_type", "unresolved"),
                "project_id": seed.get("project_id", "default_project"),
                "universe_id": seed.get("universe_id", "default_universe"),
            },
            "origin": {
                "social_class": seed.get("social_class"),
                "family_name_status": seed.get("family_name_status"),
                "origin_profile": seed.get("origin_profile", {}),
                "family_profile": seed.get("family_profile", {}),
            },
            "psychology": {
                "psychology_profile": seed.get("psychology", {}),
                "goal_profile": seed.get("goal_profile", {}),
                "moral_profile": seed.get("moral_profile", {}),
                "memory_records": seed.get("memories", []),
            },
            "power": {
                "skill_ontology": seed.get("skill_ontology", {}),
                "character_type_ontology": seed.get("character_type_ontology", {}),
                "adaptability_profile": seed.get("adaptability_profile", {}),
            },
            "destiny": {
                "destiny_profile": seed.get("destiny_profile", {}),
                "prophecy_model": seed.get("prophecy_model", {}),
                "legacy_model": seed.get("legacy_model", {}),
            },
            "relationships": {
                "relationship_readiness_profile": seed.get("relationship_readiness_profile", {}),
                "relationship_hooks": seed.get("relationship_hooks", {}),
                "compatibility_vectors": seed.get("compatibility_vectors", {}),
            },
            "dialogue": {
                "dialogue_voice_profile": seed.get("dialogue_voice_profile", {}),
                "speech_pattern_model": seed.get("speech_pattern_model", {}),
                "relationship_dialogue_variants": seed.get("relationship_dialogue_variants", {}),
            },
            "validation": {
                "consistency_report": seed.get("consistency_report", {}),
                "originality_report": seed.get("originality_report", {}),
                "quality_report": seed.get("quality_report", {}),
                "readiness_report": seed.get("readiness_report", {}),
            },
            "learning": {
                "learning_metadata_records": {},
            },
        }

    def _build_character_bible(self, *, character_id: str, full_profile: Dict[str, Any]) -> Dict[str, Any]:
        identity = full_profile.get("identity", {})
        origin = full_profile.get("origin", {})
        psychology = full_profile.get("psychology", {})
        power = full_profile.get("power", {})
        destiny = full_profile.get("destiny", {})
        relationships = full_profile.get("relationships", {})
        dialogue = full_profile.get("dialogue", {})
        validation = full_profile.get("validation", {})
        learning = full_profile.get("learning", {})

        return {
            "bible_id": f"charbible_{uuid4().hex[:12]}",
            "character_id": character_id,
            "identity": self._identity_section(identity, full_profile),
            "one_page_summary": self._one_page_summary(identity, origin, psychology, power, destiny, relationships, dialogue, validation),
            "origin_and_world_grounding": self._origin_section(origin),
            "psychology_and_goals": self._psychology_section(psychology),
            "morality_and_memory": self._morality_memory_section(psychology),
            "skills_power_and_adaptability": self._power_section(power),
            "destiny_prophecy_and_legacy": self._destiny_section(destiny),
            "relationship_readiness": self._relationship_section(relationships),
            "dialogue_voice": self._dialogue_section(dialogue),
            "validation_quality_and_originality": self._validation_section(validation),
            "learning_and_training_metadata": self._learning_section(learning),
            "chunk4_handoff": self._chunk4_handoff(full_profile),
            "chunk8_handoff": self._chunk8_handoff(full_profile),
        }

    def _identity_section(self, identity: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": identity.get("name", "Unnamed Character"),
            "character_id": identity.get("character_id") or profile.get("character_id", "unknown_character"),
            "role": identity.get("role", "unknown"),
            "archetype_label": identity.get("archetype_label", "unresolved"),
            "project_id": identity.get("project_id", "default_project"),
            "universe_id": identity.get("universe_id", "default_universe"),
            "profile_version": identity.get("profile_version", "v0.3.0-character-layer"),
        }

    def _one_page_summary(
        self,
        identity: Dict[str, Any],
        origin: Dict[str, Any],
        psychology: Dict[str, Any],
        power: Dict[str, Any],
        destiny: Dict[str, Any],
        relationships: Dict[str, Any],
        dialogue: Dict[str, Any],
        validation: Dict[str, Any],
    ) -> Dict[str, Any]:
        psych = psychology.get("psychology_profile", {})
        goals = psychology.get("goal_profile", {})
        skill = power.get("skill_ontology", {})
        ctype = power.get("character_type_ontology", {})
        dprof = destiny.get("destiny_profile", {})
        rel = relationships.get("relationship_readiness_profile", {})
        voice = dialogue.get("dialogue_voice_profile", {})
        quality = validation.get("quality_report", {})

        return {
            "logline": self._logline(identity, origin, psych, goals, skill, ctype, dprof),
            "core_contradiction": self._core_contradiction(psych, goals, dprof, rel),
            "main_story_function": self._main_story_function(identity, ctype, dprof),
            "why_the_character_is_not_generic": self._non_generic_reason(skill, ctype, dprof, rel, voice),
            "quality_tier": quality.get("quality_tier", "unknown"),
            "overall_quality_score": quality.get("overall_quality_score", 0.0),
        }

    def _origin_section(self, origin: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "social_class": origin.get("social_class"),
            "family_name_status": origin.get("family_name_status"),
            "origin_profile": origin.get("origin_profile", {}),
            "family_profile": origin.get("family_profile", {}),
            "world_character_constraints": origin.get("world_character_constraints", {}),
            "grounding_note": "Origin must explain what the character can access, what is forbidden, and what society assumes about them.",
        }

    def _psychology_section(self, psychology: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "psychology_profile": psychology.get("psychology_profile", {}),
            "goal_profile": psychology.get("goal_profile", {}),
            "emotional_state_profile": psychology.get("emotional_state_profile", {}),
            "emotional_arc_profile": psychology.get("emotional_arc_profile", {}),
            "trauma_records": psychology.get("trauma_records", []),
            "healing_profile": psychology.get("healing_profile", {}),
            "depth_note": "Psychology should connect wound, false need, true need, memory, and future choices.",
        }

    def _morality_memory_section(self, psychology: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "moral_profile": psychology.get("moral_profile", {}),
            "memory_records": psychology.get("memory_records", []),
            "memory_note": "Memories anchor psychology so emotional reactions are not arbitrary.",
        }

    def _power_section(self, power: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "skill_profile": power.get("skill_profile", {}),
            "skill_ontology": power.get("skill_ontology", {}),
            "character_type_ontology": power.get("character_type_ontology", {}),
            "adaptability_profile": power.get("adaptability_profile", {}),
            "limit_break_rules": power.get("limit_break_rules", {}),
            "adaptation_pathways": power.get("adaptation_pathways", {}),
            "failure_and_cost_model": power.get("failure_and_cost_model", {}),
            "power_note": "Every skill/adaptation must include cost, counterplay, growth, and narrative consequence.",
        }

    def _destiny_section(self, destiny: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "destiny_profile": destiny.get("destiny_profile", {}),
            "prophecy_model": destiny.get("prophecy_model", {}),
            "legacy_model": destiny.get("legacy_model", {}),
            "agency_conflict_model": destiny.get("agency_conflict_model", {}),
            "destiny_note": "Destiny is pressure and interpretation, not guaranteed victory.",
        }

    def _relationship_section(self, relationships: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_readiness_profile": relationships.get("relationship_readiness_profile", {}),
            "relationship_hooks": relationships.get("relationship_hooks", {}),
            "compatibility_vectors": relationships.get("compatibility_vectors", {}),
            "attachment_and_conflict_model": relationships.get("attachment_and_conflict_model", {}),
            "boundary_model": relationships.get("boundary_model", {}),
            "chunk4_note": "Chunk 4 should use these hooks for friendship, rivalry, romance, family, betrayal, and ensemble simulation.",
        }

    def _dialogue_section(self, dialogue: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "dialogue_voice_profile": dialogue.get("dialogue_voice_profile", {}),
            "speech_pattern_model": dialogue.get("speech_pattern_model", {}),
            "emotional_dialogue_rules": dialogue.get("emotional_dialogue_rules", {}),
            "relationship_dialogue_variants": dialogue.get("relationship_dialogue_variants", {}),
            "destiny_dialogue_layer": dialogue.get("destiny_dialogue_layer", {}),
            "forbidden_dialogue_patterns": dialogue.get("forbidden_dialogue_patterns", {}),
            "voice_note": "Dialogue should change by relationship and pressure while preserving character-specific subtext.",
        }

    def _validation_section(self, validation: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "consistency_report": validation.get("consistency_report", {}),
            "validation_checks": validation.get("validation_checks", []),
            "repair_plan": validation.get("repair_plan", {}),
            "originality_report": validation.get("originality_report", {}),
            "similarity_report": validation.get("similarity_report", {}),
            "anti_genericity_report": validation.get("anti_genericity_report", {}),
            "quality_report": validation.get("quality_report", {}),
            "readiness_report": validation.get("readiness_report", {}),
            "quality_recommendation_report": validation.get("quality_recommendation_report", {}),
            "quality_note": "Exported characters must preserve quality, consistency, and originality metadata.",
        }

    def _learning_section(self, learning: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "learning_metadata_records": learning.get("learning_metadata_records", {}),
            "training_queue_payloads": learning.get("training_queue_payloads", {}),
            "provenance_ready": learning.get("provenance_ready", False),
            "future_chunk8_training_ready": learning.get("future_chunk8_training_ready", False),
            "learning_note": "Training use requires approved provenance and future Chunk 8 learning pipeline.",
        }

    def _chunk4_handoff(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "character_id": profile.get("character_id"),
            "relationship_block": profile.get("relationships", {}),
            "dialogue_block": profile.get("dialogue", {}),
            "destiny_block": profile.get("destiny", {}),
            "psychology_block": profile.get("psychology", {}),
            "handoff_ready": bool(profile.get("relationships")) and bool(profile.get("dialogue")),
        }

    def _chunk8_handoff(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "character_id": profile.get("character_id"),
            "validation_block": profile.get("validation", {}),
            "learning_block": profile.get("learning", {}),
            "handoff_ready": bool(profile.get("validation", {}).get("quality_report")),
        }

    def _logline(self, identity: Dict[str, Any], origin: Dict[str, Any], psych: Dict[str, Any], goals: Dict[str, Any], skill: Dict[str, Any], ctype: Dict[str, Any], destiny: Dict[str, Any]) -> str:
        name = identity.get("name", "Unnamed Character")
        role = identity.get("role", "character")
        social = origin.get("social_class") or "unknown origin"
        skill_family = skill.get("skill_family", "unresolved skill")
        destiny_family = destiny.get("destiny_family", "unresolved destiny")
        true_need = goals.get("true_need") or psych.get("core_wound") or "an unresolved inner truth"

        return f"{name} is a {role} from {social} whose {skill_family} collides with {destiny_family} while they confront {true_need}."

    def _core_contradiction(self, psych: Dict[str, Any], goals: Dict[str, Any], destiny: Dict[str, Any], rel: Dict[str, Any]) -> str:
        false_need = goals.get("false_need")
        true_need = goals.get("true_need")
        wound = psych.get("core_wound")
        destiny_family = destiny.get("destiny_family")
        relationship_family = rel.get("relationship_readiness_family")

        parts = []
        if false_need and true_need:
            parts.append(f"believes '{false_need}' but needs '{true_need}'")
        elif wound:
            parts.append(f"wound: {wound}")
        if destiny_family:
            parts.append(f"destiny pressure: {destiny_family}")
        if relationship_family:
            parts.append(f"relationship pressure: {relationship_family}")

        return "; ".join(parts) if parts else "core contradiction not fully specified"

    def _main_story_function(self, identity: Dict[str, Any], ctype: Dict[str, Any], destiny: Dict[str, Any]) -> str:
        role = identity.get("role", "character")
        type_family = ctype.get("type_family")
        destiny_family = destiny.get("destiny_family")

        if type_family == "power_redirector":
            return "redirects power flow by changing who can act, win, or be trusted"
        if role == "villain":
            return "pressures the story through ideology, institutional force, or moral contradiction"
        if role == "rival":
            return "creates mirror pressure, comparison, and growth conflict"
        if destiny_family:
            return f"embodies and challenges {destiny_family}"
        return "supports the story through unresolved character pressure"

    def _non_generic_reason(self, skill: Dict[str, Any], ctype: Dict[str, Any], destiny: Dict[str, Any], rel: Dict[str, Any], voice: Dict[str, Any]) -> str:
        parts = []
        for label, source in [
            ("type", ctype.get("type_family")),
            ("skill", skill.get("skill_family")),
            ("destiny", destiny.get("destiny_family")),
            ("relationship", rel.get("relationship_readiness_family")),
            ("voice", voice.get("voice_family")),
        ]:
            if source:
                parts.append(f"{label}={source}")

        if not parts:
            return "Non-generic reason not yet established."

        return "The character combines " + ", ".join(parts) + " with validation and quality metadata."

    def _build_markdown_export(self, bible: Dict[str, Any]) -> str:
        identity = bible["identity"]
        summary = bible["one_page_summary"]

        lines = [
            f"# Character Bible: {identity['name']}",
            "",
            f"**Character ID:** {identity['character_id']}",
            f"**Role:** {identity['role']}",
            f"**Archetype:** {identity['archetype_label']}",
            f"**Project:** {identity['project_id']}",
            f"**Universe:** {identity['universe_id']}",
            "",
            "## One-Page Summary",
            "",
            f"**Logline:** {summary['logline']}",
            "",
            f"**Core Contradiction:** {summary['core_contradiction']}",
            "",
            f"**Main Story Function:** {summary['main_story_function']}",
            "",
            f"**Why This Character Is Not Generic:** {summary['why_the_character_is_not_generic']}",
            "",
            f"**Quality Tier:** {summary['quality_tier']}",
            f"**Overall Quality Score:** {summary['overall_quality_score']}",
            "",
            "## Origin and World Grounding",
            self._section_blob(bible["origin_and_world_grounding"]),
            "",
            "## Psychology and Goals",
            self._section_blob(bible["psychology_and_goals"]),
            "",
            "## Morality and Memory",
            self._section_blob(bible["morality_and_memory"]),
            "",
            "## Skills, Power, and Adaptability",
            self._section_blob(bible["skills_power_and_adaptability"]),
            "",
            "## Destiny, Prophecy, and Legacy",
            self._section_blob(bible["destiny_prophecy_and_legacy"]),
            "",
            "## Relationship Readiness",
            self._section_blob(bible["relationship_readiness"]),
            "",
            "## Dialogue Voice",
            self._section_blob(bible["dialogue_voice"]),
            "",
            "## Validation, Quality, and Originality",
            self._section_blob(bible["validation_quality_and_originality"]),
            "",
            "## Learning and Training Metadata",
            self._section_blob(bible["learning_and_training_metadata"]),
            "",
            "## Chunk 4 Handoff",
            self._section_blob(bible["chunk4_handoff"]),
            "",
            "## Chunk 8 Handoff",
            self._section_blob(bible["chunk8_handoff"]),
            "",
        ]

        return "\n".join(lines)

    def _section_blob(self, value: Any) -> str:
        if isinstance(value, dict):
            lines = []
            for key, item in value.items():
                lines.append(f"- **{key}:** {item}")
            return "\n".join(lines)
        return str(value)

    def _build_export_report(self, *, bible: Dict[str, Any], markdown: str) -> Dict[str, Any]:
        required_sections = [
            "identity",
            "one_page_summary",
            "origin_and_world_grounding",
            "psychology_and_goals",
            "morality_and_memory",
            "skills_power_and_adaptability",
            "destiny_prophecy_and_legacy",
            "relationship_readiness",
            "dialogue_voice",
            "validation_quality_and_originality",
            "learning_and_training_metadata",
            "chunk4_handoff",
            "chunk8_handoff",
        ]

        missing = [section for section in required_sections if not bible.get(section)]
        completeness = self._clamp((len(required_sections) - len(missing)) / len(required_sections))

        if completeness >= 0.95:
            tier = "complete_character_bible"
        elif completeness >= 0.8:
            tier = "usable_character_bible"
        elif completeness >= 0.6:
            tier = "partial_character_bible"
        else:
            tier = "incomplete_character_bible"

        identity = bible.get("identity", {})
        validation = bible.get("validation_quality_and_originality", {})
        quality = validation.get("quality_report", {})

        return {
            "export_report_id": f"bibleexport_{uuid4().hex[:12]}",
            "export_name": f"character_bible_export:{tier}",
            "export_tier": tier,
            "export_completeness_score": completeness,
            "markdown_length": len(markdown),
            "missing_sections": missing,
            "quality_score_used": quality.get("overall_quality_score", 0.0),
            "similarity_tags": [
                "character_bible_export",
                tier,
                identity.get("role", "unknown_role"),
                identity.get("universe_id", "unknown_universe"),
            ],
            "retrieval_context_queries": [
                f"character bible export {tier}",
                f"character bible {identity.get('name', 'unnamed')} {identity.get('role', 'unknown')}",
                "character bible identity origin psychology skill destiny relationship dialogue validation",
            ],
            "novelty_score": validation.get("originality_report", {}).get("novelty_score", 0.62),
            "originality_score": validation.get("originality_report", {}).get("overall_originality_score", 0.62),
            "export_constraints": [
                "include validation and quality sections",
                "include relationship and dialogue handoff sections",
                "do not omit power costs, destiny agency, or relationship boundaries",
                "preserve training/provenance metadata",
                "future physical PDF/DOCX export must use this structured bible as source",
            ],
        }

    def _build_diagnostics(self, *, bible: Dict[str, Any], export_report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "export_engine_completeness_score": export_report["export_completeness_score"],
            "json_ready": bool(bible.get("bible_id")),
            "markdown_ready": export_report["markdown_length"] > 500,
            "physical_export_ready_later": export_report["export_completeness_score"] >= 0.8,
            "chunk4_ready": bible.get("chunk4_handoff", {}).get("handoff_ready", False),
            "training_queue_ready": bible.get("chunk8_handoff", {}).get("handoff_ready", False),
            "training_ready_schema": True,
        }

    def _write_outputs(self, *, character_id: str, bible: Dict[str, Any], markdown: str, output_dir: str) -> Dict[str, Any]:
        import json

        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        safe_id = self._safe_name(character_id)
        json_path = root / f"{safe_id}_character_bible.json"
        markdown_path = root / f"{safe_id}_character_bible.md"

        json_path.write_text(
            json.dumps(bible, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        markdown_path.write_text(markdown, encoding="utf-8")

        return {
            "written": True,
            "json_path": str(json_path),
            "markdown_path": str(markdown_path),
        }

    def _build_ontology_record(self, *, bible: Dict[str, Any], export_report: Dict[str, Any]) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="character_bible_export",
            name=export_report["export_name"],
            family="character_bible_export",
            subtype=export_report["export_tier"],
            description=f"Character bible export completeness {export_report['export_completeness_score']}",
            axes={
                "character_bible": bible,
                "export_report": export_report,
            },
            tags=export_report["similarity_tags"],
            examples=[export_report["export_name"]],
            counterexamples=export_report["missing_sections"],
            confidence_score=export_report["export_completeness_score"],
            novelty_score=export_report["novelty_score"],
            quality_score=export_report["quality_score_used"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        bible: Dict[str, Any],
        export_report: Dict[str, Any],
        export_diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality_score = float(export_report.get("quality_score_used", 0.0))
        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8

        eligible = (
            approved_source
            and provenance.usage_allowed
            and export_diagnostics["training_queue_ready"]
            and export_report["export_completeness_score"] >= 0.8
            and quality_score >= 0.78
            and high_rating
        )

        rejection_reasons = []
        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if not export_diagnostics["training_queue_ready"]:
            rejection_reasons.append("bible not training-queue ready")
        if export_report["export_completeness_score"] < 0.8:
            rejection_reasons.append("export completeness below threshold")
        if quality_score < 0.78:
            rejection_reasons.append("quality score below training threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=quality_score,
            consistency_score=export_report["export_completeness_score"],
            originality_score=export_report["originality_score"],
            safety_score=0.88 if export_diagnostics["physical_export_ready_later"] else 0.72,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Character bible export is a training/export artifact, not raw scraped text.",
                "Training eligibility requires quality, completeness, provenance, and Chunk 8 handoff readiness.",
            ],
        )

    def _build_next_engine_payload(
        self,
        *,
        character_id: str,
        bible: Dict[str, Any],
        markdown: str,
        export_report: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
        file_outputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "character_id": character_id,
            "character_bible": bible,
            "character_bible_markdown": markdown,
            "export_report": export_report,
            "file_outputs": file_outputs,
            "frontend_payload_later": {
                "character_id": character_id,
                "title": bible["identity"]["name"],
                "sections": list(bible.keys()),
            },
            "physical_pdf_docx_export_payload_later": {
                "character_id": character_id,
                "source_artifact": "character_bible",
                "character_bible": bible,
                "markdown": markdown,
            },
            "chunk4_relationship_payload_later": bible["chunk4_handoff"],
            "chunk8_training_payload_later": {
                "target_type": "character_bible_export",
                "character_bible": bible,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _safe_name(self, value: str) -> str:
        allowed = []
        for char in str(value):
            if char.isalnum() or char in {"_", "-"}:
                allowed.append(char)
            else:
                allowed.append("_")
        return "".join(allowed).strip("_") or "unnamed"

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
