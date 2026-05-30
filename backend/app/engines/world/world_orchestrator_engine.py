from typing import Any, Dict, List, Optional

from backend.app.engines.base import BaseEngine
from backend.app.engines.world.artifact_aesthetic_engine import ArtifactAestheticEngine
from backend.app.engines.world.belief_culture_engine import BeliefCultureEngine
from backend.app.engines.world.chronology_engine import ChronologyEngine
from backend.app.engines.world.civilization_pressure_engine import CivilizationPressureEngine
from backend.app.engines.world.dataset_metadata_engine import DatasetMetadataEngine
from backend.app.engines.world.demographics_society_engine import DemographicsSocietyEngine
from backend.app.engines.world.economy_law_engine import EconomyLawEngine
from backend.app.engines.world.geography_environment_engine import GeographyEnvironmentEngine
from backend.app.engines.world.knowledge_institution_engine import KnowledgeInstitutionEngine
from backend.app.engines.world.power_faction_military_engine import PowerFactionMilitaryEngine
from backend.app.engines.world.technology_species_engine import TechnologySpeciesEngine
from backend.app.engines.world.world_bible_export_engine import WorldBibleExportEngine
from backend.app.engines.world.world_identity_engine import WorldIdentityEngine
from backend.app.engines.world.world_quality_engine import WorldQualityEngine
from backend.app.engines.world.world_rules_engine import WorldRulesEngine
from backend.app.engines.world.world_snapshot_engine import WorldSnapshotEngine
from backend.app.engines.world.world_template_engine import WorldTemplateEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldOrchestratorEngine(BaseEngine):
    """Runs the full Chunk 2 world-generation pipeline.

    This is the engine that turns many separate world modules into one
    connected research-grade world intelligence system.

    Pipeline:
    template/raw seed
    -> identity
    -> rules
    -> chronology
    -> geography/environment/infrastructure
    -> demographics/society
    -> power/factions/military
    -> economy/law
    -> belief/culture
    -> knowledge/institutions
    -> technology/species
    -> artifacts/aesthetic
    -> civilization pressure/causality
    -> quality scoring
    -> dataset metadata
    -> snapshot
    -> world bible export

    The orchestrator does not train models. It creates structured world output
    that can later be reviewed, benchmarked, exported, versioned, and used for
    future curated datasets.
    """

    engine_name = "world.orchestrator_engine"

    def __init__(self) -> None:
        self.template_engine = WorldTemplateEngine()
        self.identity_engine = WorldIdentityEngine()
        self.rules_engine = WorldRulesEngine()
        self.chronology_engine = ChronologyEngine()
        self.geography_engine = GeographyEnvironmentEngine()
        self.demographics_engine = DemographicsSocietyEngine()
        self.power_engine = PowerFactionMilitaryEngine()
        self.economy_law_engine = EconomyLawEngine()
        self.belief_culture_engine = BeliefCultureEngine()
        self.knowledge_engine = KnowledgeInstitutionEngine()
        self.technology_species_engine = TechnologySpeciesEngine()
        self.artifact_aesthetic_engine = ArtifactAestheticEngine()
        self.civilization_pressure_engine = CivilizationPressureEngine()
        self.quality_engine = WorldQualityEngine()
        self.dataset_metadata_engine = DatasetMetadataEngine()
        self.snapshot_engine = WorldSnapshotEngine()
        self.world_bible_export_engine = WorldBibleExportEngine()

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        warnings: List[str] = []
        errors: List[str] = []
        engine_runs: List[Dict[str, Any]] = []

        normalized_payload = self._normalize_payload(payload, warnings)

        if not normalized_payload.get("seed_premise"):
            warnings.append(
                "No seed_premise provided; orchestrator will generate from broad defaults."
            )

        world_state: Dict[str, Any] = {}
        generated_object_ids: List[str] = []

        # 1. Identity / DNA / scale
        identity_result = self._safe_run(
            engine=self.identity_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_identity(world_state, identity_result.data)
        warnings.extend(identity_result.warnings)
        errors.extend(identity_result.errors)

        # 2. Rules / boundaries / contradiction intent
        rules_result = self._safe_run(
            engine=self.rules_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_rules(world_state, rules_result.data)
        warnings.extend(rules_result.warnings)
        errors.extend(rules_result.errors)

        # 3. Chronology / historical wounds / memory
        chronology_result = self._safe_run(
            engine=self.chronology_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            chronology_result.data,
            ["chronology", "memory_archive"],
        )
        warnings.extend(chronology_result.warnings)
        errors.extend(chronology_result.errors)

        # 4. Geography / environment / infrastructure
        geography_result = self._safe_run(
            engine=self.geography_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            geography_result.data,
            ["geography", "environment", "infrastructure"],
        )
        warnings.extend(geography_result.warnings)
        errors.extend(geography_result.errors)

        # 5. Demographics / society
        demographics_result = self._safe_run(
            engine=self.demographics_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            demographics_result.data,
            ["demographics", "society"],
        )
        warnings.extend(demographics_result.warnings)
        errors.extend(demographics_result.errors)

        # 6. Power / military
        power_result = self._safe_run(
            engine=self.power_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            power_result.data,
            ["power_structure", "military_security"],
        )
        warnings.extend(power_result.warnings)
        errors.extend(power_result.errors)

        # 7. Economy / law
        economy_result = self._safe_run(
            engine=self.economy_law_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            economy_result.data,
            ["economy", "law"],
        )
        warnings.extend(economy_result.warnings)
        errors.extend(economy_result.errors)

        # 8. Belief / culture
        belief_result = self._safe_run(
            engine=self.belief_culture_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            belief_result.data,
            ["belief", "culture"],
        )
        warnings.extend(belief_result.warnings)
        errors.extend(belief_result.errors)

        # 9. Knowledge / institutions
        knowledge_result = self._safe_run(
            engine=self.knowledge_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            knowledge_result.data,
            ["knowledge_education", "institutions"],
        )
        warnings.extend(knowledge_result.warnings)
        errors.extend(knowledge_result.errors)

        # 10. Technology / species
        technology_result = self._safe_run(
            engine=self.technology_species_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            technology_result.data,
            ["technology_magic_science", "species_creatures"],
        )
        warnings.extend(technology_result.warnings)
        errors.extend(technology_result.errors)

        # 11. Artifacts / aesthetic
        artifact_result = self._safe_run(
            engine=self.artifact_aesthetic_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            artifact_result.data,
            ["artifacts", "aesthetic_texture"],
        )
        warnings.extend(artifact_result.warnings)
        errors.extend(artifact_result.errors)

        # 12. Civilization pressure / causality
        civilization_result = self._safe_run(
            engine=self.civilization_pressure_engine,
            payload=normalized_payload,
            engine_runs=engine_runs,
        )
        self._merge_keys(
            world_state,
            civilization_result.data,
            ["civilization_pressure", "causality_graph"],
        )
        warnings.extend(civilization_result.warnings)
        errors.extend(civilization_result.errors)

        # 13. Quality scoring
        quality_result = self._safe_run(
            engine=self.quality_engine,
            payload={
                "world_state": world_state,
                "desired_complexity": normalized_payload.get("desired_complexity", "high"),
            },
            engine_runs=engine_runs,
        )
        world_state["quality_summary"] = quality_result.data.get("quality_summary", {})
        world_state["quality_report"] = {
            key: value
            for key, value in quality_result.data.items()
            if key != "quality_summary"
        }
        warnings.extend(quality_result.warnings)
        errors.extend(quality_result.errors)

        # 14. Dataset metadata
        dataset_result = self._safe_run(
            engine=self.dataset_metadata_engine,
            payload={
                "world_state": world_state,
                "quality_summary": world_state["quality_summary"],
                "desired_complexity": normalized_payload.get("desired_complexity", "high"),
                "source_mode": normalized_payload.get("source_mode", "synthetic_engine_generated"),
                "user_rating": normalized_payload.get("user_rating"),
            },
            engine_runs=engine_runs,
        )
        world_state["dataset_metadata"] = dataset_result.data.get("dataset_metadata", {})
        warnings.extend(dataset_result.warnings)
        errors.extend(dataset_result.errors)

        # 15. Snapshot
        snapshot_result = self._safe_run(
            engine=self.snapshot_engine,
            payload={
                "world_state": world_state,
                "project_id": normalized_payload.get("project_id"),
                "universe_id": normalized_payload.get("universe_id"),
                "snapshot_type": normalized_payload.get("snapshot_type", "initial_generation"),
                "snapshot_label": normalized_payload.get("snapshot_label"),
                "parent_snapshot_id": normalized_payload.get("parent_snapshot_id"),
                "change_summary": normalized_payload.get("change_summary", "Full world generated through Chunk 2 orchestrator."),
                "quality_summary": world_state["quality_summary"],
                "dataset_metadata": world_state["dataset_metadata"],
                "created_by": self.engine_name,
                "tags": normalized_payload.get("tags", []),
            },
            engine_runs=engine_runs,
        )
        snapshot_data = dict(snapshot_result.data.get("snapshot", {}))

        # Important:
        # The snapshot engine stores a full world_state for standalone snapshot export.
        # If we place that full snapshot back inside world_state, it creates:
        # world_state -> snapshot -> world_state -> snapshot ...
        # That recursion breaks downstream markdown/json export.
        # So the orchestrator stores a lightweight snapshot reference inside world_state.
        snapshot_data.pop("world_state", None)

        world_state["snapshot"] = snapshot_data
        world_state["version_timeline_entry"] = snapshot_result.data.get("version_timeline_entry", {})
        generated_object_ids.extend(snapshot_result.generated_object_ids)
        warnings.extend(snapshot_result.warnings)
        errors.extend(snapshot_result.errors)

        # 16. World Bible export payload
        export_result = self._safe_run(
            engine=self.world_bible_export_engine,
            payload={
                "world_state": world_state,
                "export_format": normalized_payload.get("export_format", "markdown_and_json"),
                "export_title": normalized_payload.get("export_title"),
                "audience": normalized_payload.get("audience", "internal_research_and_development"),
                "include_training_metadata": normalized_payload.get("include_training_metadata", True),
                "include_snapshot_metadata": normalized_payload.get("include_snapshot_metadata", True),
            },
            engine_runs=engine_runs,
        )
        world_state["world_bible_export"] = export_result.data.get("export_package", {})
        generated_object_ids.extend(export_result.generated_object_ids)
        warnings.extend(export_result.warnings)
        errors.extend(export_result.errors)

        orchestration_summary = self._build_orchestration_summary(
            world_state=world_state,
            engine_runs=engine_runs,
            warnings=warnings,
            errors=errors,
        )

        return self.build_result(
            success=len(errors) == 0,
            data={
                "world_state": world_state,
                "orchestration_summary": orchestration_summary,
                "engine_runs": engine_runs,
                "training_notes": [
                    "The orchestrator produces structured world state but does not train any model.",
                    "All generated world outputs should go through quality, metadata, snapshot, and export stages before use.",
                    "Dataset metadata intentionally blocks blind self-learning unless quality, provenance, and review requirements pass.",
                    "This pipeline is the foundation for later ML/RAG/fine-tuning chunks, but those are not implemented in Chunk 2.",
                ],
            },
            warnings=warnings,
            errors=errors,
            generated_object_ids=generated_object_ids,
        )

    def _normalize_payload(self, payload: Dict[str, Any], warnings: List[str]) -> Dict[str, Any]:
        normalized = dict(payload)

        template_id = payload.get("template_id")

        if template_id:
            template_result = self.template_engine.run(
                {
                    "template_id": template_id,
                    "seed_premise": payload.get("seed_premise", ""),
                    "overrides": payload.get("template_overrides", {}),
                }
            )

            if template_result.success:
                orchestrator_payload = template_result.data.get("orchestrator_payload", {})
                merged = {**orchestrator_payload, **normalized}

                # Preserve expanded template seed unless user explicitly wants raw only.
                if not payload.get("use_raw_seed_only", False):
                    merged["seed_premise"] = orchestrator_payload.get(
                        "seed_premise",
                        payload.get("seed_premise", ""),
                    )

                merged["template"] = template_result.data.get("template", {})
                normalized = merged
                warnings.extend(template_result.warnings)
            else:
                warnings.append(
                    f"Template '{template_id}' could not be applied; using raw payload."
                )

        normalized.setdefault("world_name", normalized.get("name", "Velmora"))
        normalized.setdefault("genre_tags", [])
        normalized.setdefault("tone_tags", [])
        normalized.setdefault("desired_complexity", "high")
        normalized.setdefault("target_format", "world_bible")

        # Convert target_formats from templates into a single target_format if needed.
        if "target_formats" in normalized and "target_format" not in payload:
            target_formats = normalized.get("target_formats") or []
            if isinstance(target_formats, list) and target_formats:
                normalized["target_format"] = target_formats[0]

        return normalized

    def _safe_run(
        self,
        *,
        engine: BaseEngine,
        payload: Dict[str, Any],
        engine_runs: List[Dict[str, Any]],
    ) -> EngineRunResult:
        try:
            result = engine.run(payload)
            engine_runs.append(
                {
                    "engine_name": result.engine_name,
                    "success": result.success,
                    "warning_count": len(result.warnings),
                    "error_count": len(result.errors),
                    "data_keys": sorted(result.data.keys()),
                }
            )
            return result
        except Exception as exc:  # pragma: no cover - defensive safety net
            engine_name = getattr(engine, "engine_name", engine.__class__.__name__)
            error_message = f"{engine_name} failed: {exc}"
            engine_runs.append(
                {
                    "engine_name": engine_name,
                    "success": False,
                    "warning_count": 0,
                    "error_count": 1,
                    "data_keys": [],
                }
            )
            return self.build_result(
                success=False,
                data={},
                warnings=[],
                errors=[error_message],
                generated_object_ids=[],
            )

    def _merge_keys(
        self,
        world_state: Dict[str, Any],
        data: Dict[str, Any],
        keys: List[str],
    ) -> None:
        for key in keys:
            if key in data:
                world_state[key] = data[key]

    def _merge_identity(self, world_state: Dict[str, Any], data: Dict[str, Any]) -> None:
        # Support multiple possible data names in case earlier engines evolve.
        mapping = {
            "identity": ["identity", "world_identity"],
            "world_dna": ["world_dna", "dna"],
            "scale_granularity": ["scale_granularity", "scale"],
        }

        for target_key, possible_keys in mapping.items():
            for source_key in possible_keys:
                if source_key in data:
                    world_state[target_key] = data[source_key]
                    break

        # Store remaining useful identity engine outputs without overwriting.
        if "training_notes" in data:
            world_state.setdefault("identity_training_notes", data["training_notes"])

    def _merge_rules(self, world_state: Dict[str, Any], data: Dict[str, Any]) -> None:
        mapping = {
            "rules": ["rules", "world_rules"],
            "boundary_constraints": ["boundary_constraints", "boundaries"],
            "contradiction_intent": ["contradiction_intent", "contradictions"],
        }

        for target_key, possible_keys in mapping.items():
            for source_key in possible_keys:
                if source_key in data:
                    world_state[target_key] = data[source_key]
                    break

        if "training_notes" in data:
            world_state.setdefault("rules_training_notes", data["training_notes"])

    def _build_orchestration_summary(
        self,
        *,
        world_state: Dict[str, Any],
        engine_runs: List[Dict[str, Any]],
        warnings: List[str],
        errors: List[str],
    ) -> Dict[str, Any]:
        successful_runs = [run for run in engine_runs if run["success"]]
        failed_runs = [run for run in engine_runs if not run["success"]]

        quality_summary = world_state.get("quality_summary", {})
        dataset_metadata = world_state.get("dataset_metadata", {})
        export_package = world_state.get("world_bible_export", {})

        expected_core_sections = [
            "identity",
            "rules",
            "chronology",
            "geography",
            "demographics",
            "society",
            "power_structure",
            "economy",
            "law",
            "belief",
            "culture",
            "knowledge_education",
            "technology_magic_science",
            "artifacts",
            "civilization_pressure",
            "causality_graph",
            "quality_summary",
            "dataset_metadata",
            "snapshot",
            "world_bible_export",
        ]

        completed_sections = [
            section
            for section in expected_core_sections
            if world_state.get(section) not in (None, {}, [], "")
        ]

        return {
            "pipeline_name": "chunk2_world_intelligence_pipeline",
            "engine_count": len(engine_runs),
            "successful_engine_count": len(successful_runs),
            "failed_engine_count": len(failed_runs),
            "warning_count": len(warnings),
            "error_count": len(errors),
            "completed_core_sections": completed_sections,
            "core_section_completion_ratio": round(
                len(completed_sections) / len(expected_core_sections),
                3,
            ),
            "quality_tier": quality_summary.get("quality_tier"),
            "training_eligible": dataset_metadata.get("training_eligible"),
            "do_not_train": dataset_metadata.get("do_not_train"),
            "export_readiness": export_package.get("export_readiness", {}),
            "snapshot_id": world_state.get("snapshot", {}).get("snapshot_id"),
            "world_bible_export_id": export_package.get("export_id"),
            "next_recommended_step": (
                "review_world_bible_export"
                if len(errors) == 0
                else "fix_failed_engines_before_review"
            ),
        }
