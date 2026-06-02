# MythOS Engine File Tracker

Generated at UTC: 2026-06-02T06:26:53.105331+00:00
Total tracked files: 463

This file records every current project file, what it does, and what it connects to.

## chunk_1

### `backend/app/api/routes_foundation.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_foundation.py
- Line count: 363
- Imports:
  - `backend.app.registry_seed.foundation_seed`
  - `backend.app.schemas.foundation`
  - `backend.app.services.export_service`
  - `backend.app.services.foundation_store`
  - `fastapi`
  - `typing`
- Connected files:
  - `backend/app/registry_seed/foundation_seed.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/services/export_service.py`
  - `backend/app/services/foundation_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/engines/foundation/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/foundation/registry_validation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 59
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_engine_contract.py`

### `backend/app/registry_seed/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/registry_seed/foundation_seed.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: foundation_seed.py
- Line count: 196
- Likely dependents:
  - `backend/app/api/routes_foundation.py`

### `backend/app/schemas/foundation.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 205
- Imports:
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_foundation.py`
  - `backend/app/engines/base.py`
  - `backend/app/engines/character/adaptability_engine.py`
  - `backend/app/engines/character/character_agent_state_engine.py`
  - `backend/app/engines/character/character_bible_export_engine.py`
  - `backend/app/engines/character/character_consistency_validator.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/engines/character/character_genesis_engine.py`
  - `backend/app/engines/character/character_originality_engine.py`
  - `backend/app/engines/character/character_quality_scorer.py`
  - `backend/app/engines/character/character_registry_seed.py`
  - `backend/app/engines/character/character_type_ontology_engine.py`
  - `backend/app/engines/character/destiny_legacy_engine.py`
  - `backend/app/engines/character/dialogue_voice_engine.py`
  - `backend/app/engines/character/emotion_engine.py`
  - `backend/app/engines/character/emotional_arc_engine.py`
  - `backend/app/engines/character/family_foundation_engine.py`
  - `backend/app/engines/character/goal_motivation_engine.py`
  - `backend/app/engines/character/memory_engine.py`
  - `backend/app/engines/character/moral_compass_engine.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
  - `backend/app/tests/test_family_foundation_engine.py`
  - `backend/app/tests/test_foundation_api.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/services/artifact_registry_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: artifact_registry_store.py
- Line count: 105
- Imports:
  - `backend.app.schemas.artifacts`
  - `backend.app.schemas.global_refs`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/services/embedding_registry_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: embedding_registry_store.py
- Line count: 495
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_learning.py`
  - `backend/app/services/learning_integration.py`
  - `backend/app/tests/test_embedding_registry_store.py`
- Related tests:
  - `backend/app/tests/test_embedding_registry_store.py`

### `backend/app/services/foundation_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: foundation_store.py
- Line count: 618
- Imports:
  - `backend.app.db.database`
  - `backend.app.schemas.foundation`
  - `datetime`
  - `json`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/db/database.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/api/routes_foundation.py`
  - `backend/app/api/routes_world.py`
  - `backend/app/services/export_service.py`
  - `backend/app/services/world_store.py`
  - `backend/app/tests/test_sqlite_persistence.py`

### `backend/app/services/learning_registry_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: learning_registry_store.py
- Line count: 610
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_learning.py`
  - `backend/app/services/learning_integration.py`
  - `backend/app/tests/test_learning_registry_store.py`
- Related tests:
  - `backend/app/tests/test_learning_registry_store.py`

### `backend/app/tests/test_cross_chunk_foundation_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 296
- Imports:
  - `backend.app.schemas.artifacts`
  - `backend.app.schemas.canon`
  - `backend.app.schemas.engine_ops`
  - `backend.app.schemas.evaluation`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.handoffs`
  - `backend.app.schemas.human_review`
  - `backend.app.schemas.timeline`
- Connected files:
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/canon.py`
  - `backend/app/schemas/engine_ops.py`
  - `backend/app/schemas/evaluation.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/handoffs.py`
  - `backend/app/schemas/human_review.py`
  - `backend/app/schemas/timeline.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`

### `backend/app/tests/test_embedding_registry_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 285
- Imports:
  - `backend.app.services.embedding_registry_store`
  - `pathlib`
  - `pytest`
- Connected files:
  - `backend/app/services/embedding_registry_store.py`
- Related tests:
  - `backend/app/tests/test_embedding_registry_store.py`

### `backend/app/tests/test_family_foundation_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 265
- Imports:
  - `backend.app.engines.character.family_foundation_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/family_foundation_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_family_foundation_engine.py`

### `backend/app/tests/test_foundation_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 116
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_foundation_api.py`

### `backend/app/tests/test_health.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 32
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_health.py`

### `backend/app/tests/test_learning_registry_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 280
- Imports:
  - `backend.app.services.learning_registry_store`
  - `pathlib`
  - `pytest`
- Connected files:
  - `backend/app/services/learning_registry_store.py`
- Related tests:
  - `backend/app/tests/test_learning_registry_store.py`

### `backend/app/tests/test_pass_e_core_foundation_services.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 110
- Imports:
  - `backend.app.schemas.artifacts`
  - `backend.app.schemas.canon`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.human_review`
  - `backend.app.services.artifact_registry_store`
  - `backend.app.services.canon_lock_service`
  - `backend.app.services.engine_config_store`
  - `backend.app.services.human_review_store`
- Connected files:
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/canon.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/human_review.py`
  - `backend/app/services/artifact_registry_store.py`
  - `backend/app/services/canon_lock_service.py`
  - `backend/app/services/engine_config_store.py`
  - `backend/app/services/human_review_store.py`
- Related tests:
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/tests/test_registry_seed.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 55
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_character_registry_seed.py`
  - `backend/app/tests/test_registry_seed.py`

### `scripts/smoke_test_foundation_api.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 198
- Imports:
  - `httpx`
  - `json`
  - `pathlib`
  - `sys`
  - `typing`
- Related tests:
  - `backend/app/tests/test_foundation_api.py`

## chunk_2

### `backend/app/api/routes_world.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_world.py
- Line count: 68
- Imports:
  - `backend.app.schemas.world`
  - `backend.app.services.foundation_store`
  - `backend.app.services.world_store`
  - `fastapi`
  - `typing`
- Connected files:
  - `backend/app/schemas/world.py`
  - `backend/app/services/foundation_store.py`
  - `backend/app/services/world_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/api/routes_world_engines.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_world_engines.py
- Line count: 358
- Imports:
  - `backend.app.engines.world.embedding_originality_engine`
  - `backend.app.engines.world.world_orchestrator_engine`
  - `backend.app.engines.world.world_quality_engine`
  - `backend.app.engines.world.world_template_engine`
  - `backend.app.services.world_learning_adapter`
  - `backend.app.services.world_run_store`
  - `datetime`
  - `fastapi`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/world/embedding_originality_engine.py`
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/engines/world/world_quality_engine.py`
  - `backend/app/engines/world/world_template_engine.py`
  - `backend/app/services/world_learning_adapter.py`
  - `backend/app/services/world_run_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/engines/world/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/world/artifact_aesthetic_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 513
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_artifact_aesthetic_engine.py`
- Related tests:
  - `backend/app/tests/test_artifact_aesthetic_engine.py`

### `backend/app/engines/world/belief_culture_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 400
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_belief_culture_engine.py`
- Related tests:
  - `backend/app/tests/test_belief_culture_engine.py`

### `backend/app/engines/world/chronology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 553
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_chronology_engine.py`
- Related tests:
  - `backend/app/tests/test_chronology_engine.py`

### `backend/app/engines/world/civilization_pressure_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 441
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_civilization_pressure_engine.py`
- Related tests:
  - `backend/app/tests/test_civilization_pressure_engine.py`

### `backend/app/engines/world/dataset_metadata_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 436
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_dataset_metadata_engine.py`
- Related tests:
  - `backend/app/tests/test_dataset_metadata_engine.py`

### `backend/app/engines/world/demographics_society_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 495
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_demographics_society_engine.py`
- Related tests:
  - `backend/app/tests/test_demographics_society_engine.py`

### `backend/app/engines/world/economy_law_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 495
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_economy_law_engine.py`
- Related tests:
  - `backend/app/tests/test_economy_law_engine.py`

### `backend/app/engines/world/embedding_originality_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 348
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.services.world_run_store`
  - `collections`
  - `math`
  - `re`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/services/world_run_store.py`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/tests/test_embedding_originality_engine.py`
- Related tests:
  - `backend/app/tests/test_embedding_originality_engine.py`

### `backend/app/engines/world/faction_institution_resource_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 139
- Imports:
  - `backend.app.schemas.global_refs`
  - `dataclasses`
  - `typing`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_world_hardening.py`

### `backend/app/engines/world/geography_environment_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 614
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_geography_environment_engine.py`
- Related tests:
  - `backend/app/tests/test_geography_environment_engine.py`

### `backend/app/engines/world/knowledge_institution_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 626
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_knowledge_institution_engine.py`
- Related tests:
  - `backend/app/tests/test_knowledge_institution_engine.py`

### `backend/app/engines/world/power_faction_military_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 607
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_power_faction_military_engine.py`
- Related tests:
  - `backend/app/tests/test_power_faction_military_engine.py`

### `backend/app/engines/world/technology_species_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 364
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_technology_species_engine.py`
- Related tests:
  - `backend/app/tests/test_technology_species_engine.py`

### `backend/app/engines/world/world_benchmark_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 373
- Imports:
  - `backend.app.engines.base`
  - `backend.app.engines.world.world_orchestrator_engine`
  - `backend.app.engines.world.world_template_engine`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/engines/world/world_template_engine.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_world_benchmark_engine.py`
- Related tests:
  - `backend/app/tests/test_world_benchmark_engine.py`

### `backend/app/engines/world/world_bible_export_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 485
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `datetime`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_bible_export_engine.py`
- Related tests:
  - `backend/app/tests/test_world_bible_export_engine.py`

### `backend/app/engines/world/world_diff_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 433
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_world_diff_engine.py`
- Related tests:
  - `backend/app/tests/test_world_diff_engine.py`

### `backend/app/engines/world/world_identity_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 409
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_identity_engine.py`
- Related tests:
  - `backend/app/tests/test_world_identity_engine.py`

### `backend/app/engines/world/world_location_access_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 123
- Imports:
  - `backend.app.schemas.global_refs`
  - `dataclasses`
  - `typing`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_world_hardening.py`

### `backend/app/engines/world/world_orchestrator_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 558
- Imports:
  - `backend.app.engines.base`
  - `backend.app.engines.world.artifact_aesthetic_engine`
  - `backend.app.engines.world.belief_culture_engine`
  - `backend.app.engines.world.chronology_engine`
  - `backend.app.engines.world.civilization_pressure_engine`
  - `backend.app.engines.world.dataset_metadata_engine`
  - `backend.app.engines.world.demographics_society_engine`
  - `backend.app.engines.world.economy_law_engine`
  - `backend.app.engines.world.geography_environment_engine`
  - `backend.app.engines.world.knowledge_institution_engine`
  - `backend.app.engines.world.power_faction_military_engine`
  - `backend.app.engines.world.technology_species_engine`
  - `backend.app.engines.world.world_bible_export_engine`
  - `backend.app.engines.world.world_identity_engine`
  - `backend.app.engines.world.world_quality_engine`
  - `backend.app.engines.world.world_rules_engine`
  - `backend.app.engines.world.world_snapshot_engine`
  - `backend.app.engines.world.world_template_engine`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/engines/world/artifact_aesthetic_engine.py`
  - `backend/app/engines/world/belief_culture_engine.py`
  - `backend/app/engines/world/chronology_engine.py`
  - `backend/app/engines/world/civilization_pressure_engine.py`
  - `backend/app/engines/world/dataset_metadata_engine.py`
  - `backend/app/engines/world/demographics_society_engine.py`
  - `backend/app/engines/world/economy_law_engine.py`
  - `backend/app/engines/world/geography_environment_engine.py`
  - `backend/app/engines/world/knowledge_institution_engine.py`
  - `backend/app/engines/world/power_faction_military_engine.py`
  - `backend/app/engines/world/technology_species_engine.py`
  - `backend/app/engines/world/world_bible_export_engine.py`
  - `backend/app/engines/world/world_identity_engine.py`
  - `backend/app/engines/world/world_quality_engine.py`
  - `backend/app/engines/world/world_rules_engine.py`
  - `backend/app/engines/world/world_snapshot_engine.py`
  - `backend/app/engines/world/world_template_engine.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/engines/world/world_benchmark_engine.py`
  - `backend/app/tests/test_world_orchestrator_engine.py`
- Related tests:
  - `backend/app/tests/test_world_orchestrator_engine.py`

### `backend/app/engines/world/world_quality_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 631
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_quality_engine.py`
- Related tests:
  - `backend/app/tests/test_world_quality_engine.py`

### `backend/app/engines/world/world_rule_conflict_detector.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 80
- Imports:
  - `dataclasses`
  - `typing`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_world_hardening.py`

### `backend/app/engines/world/world_rules_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 735
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_rules_engine.py`
- Related tests:
  - `backend/app/tests/test_world_rules_engine.py`

### `backend/app/engines/world/world_snapshot_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 354
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `datetime`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_snapshot_engine.py`
- Related tests:
  - `backend/app/tests/test_world_snapshot_engine.py`

### `backend/app/engines/world/world_template_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 449
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/engines/world/world_benchmark_engine.py`
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/tests/test_world_template_engine.py`
- Related tests:
  - `backend/app/tests/test_world_template_engine.py`

### `backend/app/schemas/world.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 665
- Imports:
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_world.py`
  - `backend/app/engines/world/artifact_aesthetic_engine.py`
  - `backend/app/engines/world/belief_culture_engine.py`
  - `backend/app/engines/world/chronology_engine.py`
  - `backend/app/engines/world/civilization_pressure_engine.py`
  - `backend/app/engines/world/demographics_society_engine.py`
  - `backend/app/engines/world/economy_law_engine.py`
  - `backend/app/engines/world/geography_environment_engine.py`
  - `backend/app/engines/world/knowledge_institution_engine.py`
  - `backend/app/engines/world/power_faction_military_engine.py`
  - `backend/app/engines/world/technology_species_engine.py`
  - `backend/app/engines/world/world_identity_engine.py`
  - `backend/app/engines/world/world_rules_engine.py`
  - `backend/app/services/world_store.py`
  - `backend/app/tests/test_artifact_aesthetic_engine.py`
  - `backend/app/tests/test_belief_culture_engine.py`
  - `backend/app/tests/test_chronology_engine.py`
  - `backend/app/tests/test_civilization_pressure_engine.py`
  - `backend/app/tests/test_demographics_society_engine.py`
  - `backend/app/tests/test_economy_law_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_world_schemas.py`
  - `backend/app/tests/test_multi_world_multi_cast_scaling_controller.py`
  - `backend/app/tests/test_pass_e_world_hardening.py`
  - `backend/app/tests/test_world_api.py`
  - `backend/app/tests/test_world_api_learning_registration.py`
  - `backend/app/tests/test_world_benchmark_engine.py`
  - `backend/app/tests/test_world_bible_export_engine.py`
  - `backend/app/tests/test_world_character_constraint_engine.py`
  - `backend/app/tests/test_world_detail_injection_engine.py`
  - `backend/app/tests/test_world_diff_engine.py`
  - `backend/app/tests/test_world_engine_api.py`
  - `backend/app/tests/test_world_identity_engine.py`
  - `backend/app/tests/test_world_learning_adapter.py`
  - `backend/app/tests/test_world_learning_metadata_verifier.py`
  - `backend/app/tests/test_world_orchestrator_engine.py`
  - `backend/app/tests/test_world_quality_engine.py`
  - `backend/app/tests/test_world_rules_engine.py`
  - `backend/app/tests/test_world_run_persistence.py`
  - `backend/app/tests/test_world_run_store_learning_trace.py`
  - `backend/app/tests/test_world_schemas.py`

### `backend/app/services/world_learning_adapter.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_learning_adapter.py
- Line count: 678
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.handoffs`
  - `backend.app.services.learning_integration`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/handoffs.py`
  - `backend/app/services/learning_integration.py`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/world_learning_metadata_verifier.py`
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`
  - `backend/app/tests/test_world_learning_adapter.py`
  - `scripts/smoke_test_chunk2_world_learning_pipeline.py`
- Related tests:
  - `backend/app/tests/test_world_learning_adapter.py`

### `backend/app/services/world_learning_metadata_verifier.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_learning_metadata_verifier.py
- Line count: 306
- Imports:
  - `backend.app.services.world_learning_adapter`
  - `typing`
- Connected files:
  - `backend/app/services/world_learning_adapter.py`
- Likely dependents:
  - `backend/app/tests/test_world_learning_metadata_verifier.py`
  - `scripts/smoke_test_chunk2_world_learning_pipeline.py`
- Related tests:
  - `backend/app/tests/test_world_learning_metadata_verifier.py`

### `backend/app/services/world_run_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_run_store.py
- Line count: 346
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `sqlite3`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/engines/world/embedding_originality_engine.py`
  - `backend/app/tests/test_embedding_originality_engine.py`
  - `backend/app/tests/test_world_run_persistence.py`
  - `backend/app/tests/test_world_run_store_learning_trace.py`
- Related tests:
  - `backend/app/tests/test_world_run_store_learning_trace.py`

### `backend/app/services/world_state_snapshot_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_state_snapshot_service.py
- Line count: 88
- Imports:
  - `backend.app.schemas.global_refs`
  - `hashlib`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_world_hardening.py`

### `backend/app/services/world_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_store.py
- Line count: 211
- Imports:
  - `backend.app.db.database`
  - `backend.app.schemas.world`
  - `backend.app.services.foundation_store`
  - `datetime`
  - `json`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/db/database.py`
  - `backend/app/schemas/world.py`
  - `backend/app/services/foundation_store.py`
- Likely dependents:
  - `backend/app/api/routes_world.py`

### `backend/app/tests/test_civilization_pressure_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 123
- Imports:
  - `backend.app.engines.world.civilization_pressure_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/civilization_pressure_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_civilization_pressure_engine.py`

### `backend/app/tests/test_constraint_satisfaction_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 328
- Imports:
  - `backend.app.engines.story_generation.constraint_satisfaction_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/constraint_satisfaction_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_constraint_satisfaction_engine.py`

### `backend/app/tests/test_demographics_society_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 125
- Imports:
  - `backend.app.engines.world.demographics_society_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/demographics_society_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_demographics_society_engine.py`

### `backend/app/tests/test_multi_world_multi_cast_scaling_controller.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 273
- Imports:
  - `backend.app.engines.story_generation.multi_world_multi_cast_scaling_controller`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/multi_world_multi_cast_scaling_controller.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_multi_world_multi_cast_scaling_controller.py`

### `backend/app/tests/test_pass_e_world_hardening.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 113
- Imports:
  - `backend.app.engines.world.faction_institution_resource_engine`
  - `backend.app.engines.world.world_location_access_engine`
  - `backend.app.engines.world.world_rule_conflict_detector`
  - `backend.app.services.world_state_snapshot_service`
- Connected files:
  - `backend/app/engines/world/faction_institution_resource_engine.py`
  - `backend/app/engines/world/world_location_access_engine.py`
  - `backend/app/engines/world/world_rule_conflict_detector.py`
  - `backend/app/services/world_state_snapshot_service.py`
- Related tests:
  - `backend/app/tests/test_pass_e_world_hardening.py`

### `backend/app/tests/test_power_faction_military_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 125
- Imports:
  - `backend.app.engines.world.power_faction_military_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/power_faction_military_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_power_faction_military_engine.py`

### `backend/app/tests/test_world_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 152
- Imports:
  - `backend.app.main`
  - `backend.app.schemas.world`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_world_api.py`
  - `backend/app/tests/test_world_api_learning_registration.py`

### `backend/app/tests/test_world_api_learning_registration.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 242
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_world_api.py`
  - `backend/app/tests/test_world_api_learning_registration.py`

### `backend/app/tests/test_world_benchmark_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 99
- Imports:
  - `backend.app.engines.world.world_benchmark_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_benchmark_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_benchmark_engine.py`

### `backend/app/tests/test_world_bible_export_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 148
- Imports:
  - `backend.app.engines.world.world_bible_export_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_bible_export_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_bible_export_engine.py`

### `backend/app/tests/test_world_detail_injection_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 159
- Imports:
  - `backend.app.engines.story_generation.world_detail_injection_engine`
- Connected files:
  - `backend/app/engines/story_generation/world_detail_injection_engine.py`
- Related tests:
  - `backend/app/tests/test_world_detail_injection_engine.py`

### `backend/app/tests/test_world_diff_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 152
- Imports:
  - `backend.app.engines.world.world_diff_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_diff_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_diff_engine.py`

### `backend/app/tests/test_world_engine_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 120
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_world_engine_api.py`

### `backend/app/tests/test_world_identity_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 132
- Imports:
  - `backend.app.engines.world.world_identity_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/world_identity_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_world_identity_engine.py`

### `backend/app/tests/test_world_learning_adapter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 289
- Imports:
  - `backend.app.services.learning_integration`
  - `backend.app.services.world_learning_adapter`
- Connected files:
  - `backend/app/services/learning_integration.py`
  - `backend/app/services/world_learning_adapter.py`
- Related tests:
  - `backend/app/tests/test_world_learning_adapter.py`

### `backend/app/tests/test_world_learning_metadata_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 237
- Imports:
  - `backend.app.services.world_learning_metadata_verifier`
- Connected files:
  - `backend/app/services/world_learning_metadata_verifier.py`
- Related tests:
  - `backend/app/tests/test_world_learning_metadata_verifier.py`

### `backend/app/tests/test_world_orchestrator_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 159
- Imports:
  - `backend.app.engines.world.world_orchestrator_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_orchestrator_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_orchestrator_engine.py`

### `backend/app/tests/test_world_quality_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 184
- Imports:
  - `backend.app.engines.world.world_quality_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_quality_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_quality_engine.py`

### `backend/app/tests/test_world_rules_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 119
- Imports:
  - `backend.app.engines.world.world_rules_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/world_rules_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_world_rules_engine.py`

### `backend/app/tests/test_world_run_persistence.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 144
- Imports:
  - `backend.app.main`
  - `backend.app.services.world_run_store`
  - `fastapi.testclient`
  - `pathlib`
- Connected files:
  - `backend/app/main.py`
  - `backend/app/services/world_run_store.py`
- Related tests:
  - `backend/app/tests/test_world_run_persistence.py`

### `backend/app/tests/test_world_run_store_learning_trace.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 98
- Imports:
  - `backend.app.services.world_run_store`
  - `pytest`
- Connected files:
  - `backend/app/services/world_run_store.py`
- Related tests:
  - `backend/app/tests/test_world_run_store_learning_trace.py`

### `backend/app/tests/test_world_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 141
- Imports:
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_world_schemas.py`
  - `backend/app/tests/test_world_schemas.py`

### `backend/app/tests/test_world_snapshot_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 147
- Imports:
  - `backend.app.engines.world.world_snapshot_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_snapshot_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_snapshot_engine.py`

### `backend/app/tests/test_world_template_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 94
- Imports:
  - `backend.app.engines.world.world_template_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/world_template_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_template_engine.py`

### `scripts/smoke_test_chunk2_world_learning_pipeline.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 146
- Imports:
  - `backend.app.services.learning_integration`
  - `backend.app.services.world_learning_adapter`
  - `backend.app.services.world_learning_metadata_verifier`
  - `json`
  - `pathlib`
  - `sys`
- Connected files:
  - `backend/app/services/learning_integration.py`
  - `backend/app/services/world_learning_adapter.py`
  - `backend/app/services/world_learning_metadata_verifier.py`

### `scripts/smoke_test_chunk2_world_pipeline.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 181
- Imports:
  - `httpx`
  - `json`
  - `pathlib`
  - `sys`

## chunk_3

### `backend/app/api/routes_character_engines.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_character_engines.py
- Line count: 405
- Imports:
  - `backend.app.engines.character.adaptability_engine`
  - `backend.app.engines.character.character_consistency_validator`
  - `backend.app.engines.character.character_full_profile_orchestrator`
  - `backend.app.engines.character.character_originality_engine`
  - `backend.app.engines.character.character_quality_scorer`
  - `backend.app.engines.character.destiny_legacy_engine`
  - `backend.app.engines.character.dialogue_voice_engine`
  - `backend.app.engines.character.relationship_readiness_engine`
  - `backend.app.services.character_learning_adapter`
  - `backend.app.services.character_learning_metadata_verifier`
  - `backend.app.services.character_run_store`
  - `fastapi`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/engines/character/adaptability_engine.py`
  - `backend/app/engines/character/character_consistency_validator.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/engines/character/character_originality_engine.py`
  - `backend/app/engines/character/character_quality_scorer.py`
  - `backend/app/engines/character/destiny_legacy_engine.py`
  - `backend/app/engines/character/dialogue_voice_engine.py`
  - `backend/app/engines/character/relationship_readiness_engine.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/character_learning_metadata_verifier.py`
  - `backend/app/services/character_run_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/api/routes_characters.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_characters.py
- Line count: 90
- Imports:
  - `backend.app.services.character_store`
  - `fastapi`
  - `typing`
- Connected files:
  - `backend/app/services/character_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/benchmarks/character_benchmark_pack.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_benchmark_pack.py
- Line count: 267
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_character_benchmark_pack.py`
  - `scripts/smoke_test_chunk3_character_pipeline.py`
- Related tests:
  - `backend/app/tests/test_character_benchmark_pack.py`

### `backend/app/engines/character/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/character/adaptability_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 995
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_adaptability_engine.py`
- Related tests:
  - `backend/app/tests/test_adaptability_engine.py`

### `backend/app/engines/character/character_agent_state_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 540
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_character_agent_state_engine.py`
- Related tests:
  - `backend/app/tests/test_character_agent_state_engine.py`

### `backend/app/engines/character/character_bible_export_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 780
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/tests/test_character_bible_export_engine.py`
- Related tests:
  - `backend/app/tests/test_character_bible_export_engine.py`

### `backend/app/engines/character/character_consistency_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 844
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_consistency_validator.py`
- Related tests:
  - `backend/app/tests/test_character_consistency_validator.py`

### `backend/app/engines/character/character_full_profile_orchestrator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 623
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_benchmark_pack.py`
  - `backend/app/tests/test_character_full_profile_orchestrator.py`
  - `scripts/smoke_test_chunk3_character_pipeline.py`
- Related tests:
  - `backend/app/tests/test_character_full_profile_orchestrator.py`

### `backend/app/engines/character/character_genesis_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 811
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_character_genesis_engine.py`
- Related tests:
  - `backend/app/tests/test_character_genesis_engine.py`

### `backend/app/engines/character/character_originality_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 645
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_originality_engine.py`
- Related tests:
  - `backend/app/tests/test_character_originality_engine.py`

### `backend/app/engines/character/character_quality_scorer.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 705
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_quality_scorer.py`
- Related tests:
  - `backend/app/tests/test_character_quality_scorer.py`

### `backend/app/engines/character/character_registry_seed.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 451
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/engines/character/people_type_engine.py`
  - `backend/app/tests/test_character_registry_seed.py`
- Related tests:
  - `backend/app/tests/test_character_registry_seed.py`
  - `backend/app/tests/test_registry_seed.py`

### `backend/app/engines/character/character_type_ontology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 994
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/tests/test_character_type_ontology_engine.py`
- Related tests:
  - `backend/app/tests/test_character_type_ontology_engine.py`

### `backend/app/engines/character/destiny_legacy_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 972
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_destiny_legacy_engine.py`
- Related tests:
  - `backend/app/tests/test_destiny_legacy_engine.py`

### `backend/app/engines/character/dialogue_voice_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 1023
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_dialogue_voice_engine.py`
- Related tests:
  - `backend/app/tests/test_dialogue_voice_engine.py`

### `backend/app/engines/character/emotion_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 473
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_emotion_engine.py`
- Related tests:
  - `backend/app/tests/test_emotion_engine.py`

### `backend/app/engines/character/emotional_arc_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 407
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_emotional_arc_engine.py`
- Related tests:
  - `backend/app/tests/test_emotional_arc_engine.py`

### `backend/app/engines/character/family_foundation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 660
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_family_foundation_engine.py`
- Related tests:
  - `backend/app/tests/test_family_foundation_engine.py`

### `backend/app/engines/character/goal_motivation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 725
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_goal_motivation_engine.py`
- Related tests:
  - `backend/app/tests/test_goal_motivation_engine.py`

### `backend/app/engines/character/memory_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 472
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_memory_engine.py`
- Related tests:
  - `backend/app/tests/test_memory_engine.py`

### `backend/app/engines/character/moral_compass_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 734
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_moral_compass_engine.py`
- Related tests:
  - `backend/app/tests/test_moral_compass_engine.py`

### `backend/app/engines/character/origin_social_class_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 550
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_origin_social_class_engine.py`
- Related tests:
  - `backend/app/tests/test_origin_social_class_engine.py`

### `backend/app/engines/character/people_type_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 550
- Imports:
  - `backend.app.engines.base`
  - `backend.app.engines.character.character_registry_seed`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/engines/character/character_registry_seed.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_people_type_engine.py`
- Related tests:
  - `backend/app/tests/test_people_type_engine.py`

### `backend/app/engines/character/population_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 396
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_population_engine.py`
- Related tests:
  - `backend/app/tests/test_population_engine.py`

### `backend/app/engines/character/psychology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 472
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_psychology_engine.py`
- Related tests:
  - `backend/app/tests/test_psychology_engine.py`

### `backend/app/engines/character/relationship_readiness_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 1106
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_relationship_readiness_engine.py`
- Related tests:
  - `backend/app/tests/test_relationship_readiness_engine.py`

### `backend/app/engines/character/reputation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 879
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_reputation_engine.py`
- Related tests:
  - `backend/app/tests/test_reputation_engine.py`

### `backend/app/engines/character/skill_ontology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 836
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Likely dependents:
  - `backend/app/tests/test_skill_ontology_engine.py`
- Related tests:
  - `backend/app/tests/test_skill_ontology_engine.py`

### `backend/app/engines/character/skill_power_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 847
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_skill_power_engine.py`
- Related tests:
  - `backend/app/tests/test_skill_power_engine.py`

### `backend/app/engines/character/trauma_healing_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 526
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_trauma_healing_engine.py`
- Related tests:
  - `backend/app/tests/test_trauma_healing_engine.py`

### `backend/app/engines/character/world_character_constraint_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 775
- Imports:
  - `backend.app.engines.base`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/engines/base.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_world_character_constraint_engine.py`
- Related tests:
  - `backend/app/tests/test_world_character_constraint_engine.py`

### `backend/app/schemas/character.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 542
- Imports:
  - `pydantic`
  - `typing`
- Likely dependents:
  - `backend/app/engines/character/character_agent_state_engine.py`
  - `backend/app/engines/character/character_genesis_engine.py`
  - `backend/app/engines/character/emotion_engine.py`
  - `backend/app/engines/character/emotional_arc_engine.py`
  - `backend/app/engines/character/family_foundation_engine.py`
  - `backend/app/engines/character/memory_engine.py`
  - `backend/app/engines/character/origin_social_class_engine.py`
  - `backend/app/engines/character/people_type_engine.py`
  - `backend/app/engines/character/population_engine.py`
  - `backend/app/engines/character/psychology_engine.py`
  - `backend/app/engines/character/trauma_healing_engine.py`
  - `backend/app/services/character_store.py`
  - `backend/app/tests/test_character_agent_state_engine.py`
  - `backend/app/tests/test_character_genesis_engine.py`
  - `backend/app/tests/test_character_schemas.py`
  - `backend/app/tests/test_emotion_engine.py`
  - `backend/app/tests/test_emotional_arc_engine.py`
  - `backend/app/tests/test_family_foundation_engine.py`
  - `backend/app/tests/test_memory_engine.py`
  - `backend/app/tests/test_origin_social_class_engine.py`
- Related tests:
  - `backend/app/tests/test_character_agent_state_engine.py`
  - `backend/app/tests/test_character_api.py`
  - `backend/app/tests/test_character_api_learning_registration.py`
  - `backend/app/tests/test_character_benchmark_pack.py`
  - `backend/app/tests/test_character_bible_export_engine.py`
  - `backend/app/tests/test_character_consistency_validator.py`
  - `backend/app/tests/test_character_engine_routes.py`
  - `backend/app/tests/test_character_full_profile_orchestrator.py`
  - `backend/app/tests/test_character_genesis_engine.py`
  - `backend/app/tests/test_character_learning_adapter.py`
  - `backend/app/tests/test_character_learning_metadata_verifier.py`
  - `backend/app/tests/test_character_originality_engine.py`
  - `backend/app/tests/test_character_quality_scorer.py`
  - `backend/app/tests/test_character_registry_seed.py`
  - `backend/app/tests/test_character_run_store.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`
  - `backend/app/tests/test_character_schemas.py`
  - `backend/app/tests/test_character_type_ontology_engine.py`
  - `backend/app/tests/test_character_voice_engine.py`
  - `backend/app/tests/test_chunk3_character_learning_smoke_script_exists.py`

### `backend/app/services/character_agency_state_updater.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_agency_state_updater.py
- Line count: 121
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/services/character_consistency_invariant_checker.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_consistency_invariant_checker.py
- Line count: 126
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/services/character_contrast_matrix_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_contrast_matrix_service.py
- Line count: 133
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/services/character_emotion_carryover_adapter.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_emotion_carryover_adapter.py
- Line count: 113
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/services/character_learning_adapter.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_learning_adapter.py
- Line count: 858
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.handoffs`
  - `backend.app.services.learning_integration`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/handoffs.py`
  - `backend/app/services/learning_integration.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/services/character_learning_metadata_verifier.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/tests/test_character_learning_adapter.py`
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`
  - `scripts/smoke_test_chunk3_character_learning_pipeline.py`
- Related tests:
  - `backend/app/tests/test_character_learning_adapter.py`

### `backend/app/services/character_learning_metadata_verifier.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_learning_metadata_verifier.py
- Line count: 433
- Imports:
  - `backend.app.services.character_learning_adapter`
  - `typing`
- Connected files:
  - `backend/app/services/character_learning_adapter.py`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_learning_metadata_verifier.py`
  - `scripts/smoke_test_chunk3_character_learning_pipeline.py`
- Related tests:
  - `backend/app/tests/test_character_learning_metadata_verifier.py`

### `backend/app/services/character_memory_update_adapter.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_memory_update_adapter.py
- Line count: 132
- Imports:
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/services/character_run_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_run_store.py
- Line count: 405
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/tests/test_character_run_store.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`
  - `scripts/smoke_test_chunk3_character_pipeline.py`
- Related tests:
  - `backend/app/tests/test_character_run_store.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`

### `backend/app/services/character_state_snapshot_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_state_snapshot_store.py
- Line count: 94
- Imports:
  - `backend.app.schemas.global_refs`
  - `hashlib`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/services/character_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: character_store.py
- Line count: 112
- Imports:
  - `backend.app.schemas.character`
  - `datetime`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/character.py`
- Likely dependents:
  - `backend/app/api/routes_characters.py`
  - `backend/app/tests/test_character_api.py`

### `backend/app/services/emotional_resonance_seed_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: emotional_resonance_seed_service.py
- Line count: 92
- Imports:
  - `backend.app.schemas.story_dna`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_dna.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/services/world_character_pressure_matrix_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: world_character_pressure_matrix_service.py
- Line count: 135
- Imports:
  - `backend.app.schemas.story_dna`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_dna.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/tests/test_character_agent_state_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 202
- Imports:
  - `backend.app.engines.character.character_agent_state_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/character_agent_state_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_character_agent_state_engine.py`

### `backend/app/tests/test_character_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 197
- Imports:
  - `backend.app.main`
  - `backend.app.services.character_store`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
  - `backend/app/services/character_store.py`
- Related tests:
  - `backend/app/tests/test_character_api.py`
  - `backend/app/tests/test_character_api_learning_registration.py`

### `backend/app/tests/test_character_api_learning_registration.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 347
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_character_api.py`
  - `backend/app/tests/test_character_api_learning_registration.py`

### `backend/app/tests/test_character_benchmark_pack.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 83
- Imports:
  - `backend.app.benchmarks.character_benchmark_pack`
  - `backend.app.engines.character.character_full_profile_orchestrator`
- Connected files:
  - `backend/app/benchmarks/character_benchmark_pack.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
- Related tests:
  - `backend/app/tests/test_character_benchmark_pack.py`

### `backend/app/tests/test_character_bible_export_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 296
- Imports:
  - `backend.app.engines.character.character_bible_export_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
  - `pathlib`
- Connected files:
  - `backend/app/engines/character/character_bible_export_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_bible_export_engine.py`

### `backend/app/tests/test_character_consistency_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 353
- Imports:
  - `backend.app.engines.character.character_consistency_validator`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/character_consistency_validator.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_consistency_validator.py`

### `backend/app/tests/test_character_engine_routes.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 361
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_character_engine_routes.py`

### `backend/app/tests/test_character_full_profile_orchestrator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 228
- Imports:
  - `backend.app.engines.character.character_full_profile_orchestrator`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_full_profile_orchestrator.py`

### `backend/app/tests/test_character_genesis_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 281
- Imports:
  - `backend.app.engines.character.character_genesis_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/character_genesis_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_character_genesis_engine.py`

### `backend/app/tests/test_character_learning_adapter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 405
- Imports:
  - `backend.app.services.character_learning_adapter`
  - `backend.app.services.learning_integration`
- Connected files:
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/learning_integration.py`
- Related tests:
  - `backend/app/tests/test_character_learning_adapter.py`

### `backend/app/tests/test_character_learning_metadata_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 356
- Imports:
  - `backend.app.services.character_learning_metadata_verifier`
- Connected files:
  - `backend/app/services/character_learning_metadata_verifier.py`
- Related tests:
  - `backend/app/tests/test_character_learning_metadata_verifier.py`

### `backend/app/tests/test_character_originality_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 199
- Imports:
  - `backend.app.engines.character.character_originality_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/character_originality_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_originality_engine.py`

### `backend/app/tests/test_character_quality_scorer.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 293
- Imports:
  - `backend.app.engines.character.character_quality_scorer`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/character_quality_scorer.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_quality_scorer.py`

### `backend/app/tests/test_character_registry_seed.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 119
- Imports:
  - `backend.app.engines.character.character_registry_seed`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/character_registry_seed.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_character_registry_seed.py`
  - `backend/app/tests/test_registry_seed.py`

### `backend/app/tests/test_character_run_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 295
- Imports:
  - `backend.app.services.character_run_store`
  - `pathlib`
  - `pytest`
- Connected files:
  - `backend/app/services/character_run_store.py`
- Related tests:
  - `backend/app/tests/test_character_run_store.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`

### `backend/app/tests/test_character_run_store_learning_trace.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 110
- Imports:
  - `backend.app.services.character_run_store`
  - `pytest`
- Connected files:
  - `backend/app/services/character_run_store.py`
- Related tests:
  - `backend/app/tests/test_character_run_store.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`

### `backend/app/tests/test_character_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 409
- Imports:
  - `backend.app.schemas.character`
  - `pydantic`
  - `pytest`
- Connected files:
  - `backend/app/schemas/character.py`
- Related tests:
  - `backend/app/tests/test_character_schemas.py`

### `backend/app/tests/test_character_type_ontology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 303
- Imports:
  - `backend.app.engines.character.character_type_ontology_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/character_type_ontology_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_character_type_ontology_engine.py`

### `backend/app/tests/test_character_voice_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 158
- Imports:
  - `backend.app.engines.story_generation.character_voice_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/character_voice_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_character_voice_engine.py`

### `backend/app/tests/test_chunk3_character_learning_smoke_script_exists.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 12
- Imports:
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_chunk3_character_learning_smoke_script_exists.py`

### `backend/app/tests/test_chunk3_character_smoke_script_exists.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 9
- Imports:
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_chunk3_character_smoke_script_exists.py`

### `backend/app/tests/test_destiny_legacy_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 316
- Imports:
  - `backend.app.engines.character.destiny_legacy_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/destiny_legacy_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_destiny_legacy_engine.py`

### `backend/app/tests/test_emotion_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 222
- Imports:
  - `backend.app.engines.character.emotion_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/emotion_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_emotion_engine.py`

### `backend/app/tests/test_emotional_arc_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 258
- Imports:
  - `backend.app.engines.character.emotional_arc_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/emotional_arc_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_emotional_arc_engine.py`

### `backend/app/tests/test_emotional_subtext_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 182
- Imports:
  - `backend.app.engines.story_generation.character_voice_engine`
  - `backend.app.engines.story_generation.emotional_subtext_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/character_voice_engine.py`
  - `backend/app/engines/story_generation/emotional_subtext_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_emotional_subtext_engine.py`

### `backend/app/tests/test_long_form_memory_bridge.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 248
- Imports:
  - `backend.app.engines.story_generation.long_form_memory_bridge`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/long_form_memory_bridge.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_long_form_memory_bridge.py`

### `backend/app/tests/test_memory_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 285
- Imports:
  - `backend.app.engines.character.memory_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/memory_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_memory_engine.py`

### `backend/app/tests/test_pass_e_character_hardening.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 173
- Imports:
  - `backend.app.services.character_agency_state_updater`
  - `backend.app.services.character_consistency_invariant_checker`
  - `backend.app.services.character_emotion_carryover_adapter`
  - `backend.app.services.character_memory_update_adapter`
  - `backend.app.services.character_state_snapshot_store`
- Connected files:
  - `backend/app/services/character_agency_state_updater.py`
  - `backend/app/services/character_consistency_invariant_checker.py`
  - `backend/app/services/character_emotion_carryover_adapter.py`
  - `backend/app/services/character_memory_update_adapter.py`
  - `backend/app/services/character_state_snapshot_store.py`
- Related tests:
  - `backend/app/tests/test_pass_e_character_hardening.py`

### `backend/app/tests/test_story_memory_update_contract.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 167
- Imports:
  - `backend.app.engines.story_generation.story_memory_update_contract`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_memory_update_contract.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_memory_update_contract.py`

### `backend/app/tests/test_world_character_constraint_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 341
- Imports:
  - `backend.app.engines.character.world_character_constraint_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/world_character_constraint_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_world_character_constraint_engine.py`

### `docs/mythos_project_memory.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 70

### `scripts/smoke_test_chunk3_character_learning_pipeline.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 206
- Imports:
  - `backend.app.services.character_learning_adapter`
  - `backend.app.services.character_learning_metadata_verifier`
  - `backend.app.services.learning_integration`
  - `json`
  - `pathlib`
  - `sys`
- Connected files:
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/character_learning_metadata_verifier.py`
  - `backend/app/services/learning_integration.py`

### `scripts/smoke_test_chunk3_character_pipeline.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 175
- Imports:
  - `backend.app.benchmarks.character_benchmark_pack`
  - `backend.app.engines.character.character_full_profile_orchestrator`
  - `backend.app.services.character_run_store`
  - `httpx`
  - `json`
  - `os`
  - `pathlib`
  - `sys`
- Connected files:
  - `backend/app/benchmarks/character_benchmark_pack.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/services/character_run_store.py`

## chunk_4

### `backend/app/api/simulation_routes.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: simulation_routes.py
- Line count: 328
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `backend.app.engines.simulation.simulation_run_store`
  - `backend.app.schemas.simulation`
  - `fastapi`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
  - `backend/app/engines/simulation/simulation_run_store.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/engines/simulation/agency_model_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 592
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/engines/simulation/choice_feasibility_engine.py`
  - `backend/app/tests/test_chunk4_agency_model_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_agency_model_engine.py`

### `backend/app/engines/simulation/canon_branch_timeline_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 425
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`
- Related tests:
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`

### `backend/app/engines/simulation/cast_selection_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 732
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_cast_selection_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_cast_selection_engine.py`

### `backend/app/engines/simulation/causal_chain_explanation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 743
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_causal_chain_explanation_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_causal_chain_explanation_engine.py`

### `backend/app/engines/simulation/choice_architecture_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 600
- Imports:
  - `backend.app.engines.simulation.choice_feasibility_engine`
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/choice_feasibility_engine.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_choice_architecture_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_choice_architecture_engine.py`

### `backend/app/engines/simulation/choice_feasibility_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 576
- Imports:
  - `backend.app.engines.simulation.agency_model_engine`
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/agency_model_engine.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/engines/simulation/choice_architecture_engine.py`
  - `backend/app/tests/test_chunk4_choice_architecture_engine.py`
  - `backend/app/tests/test_chunk4_choice_feasibility_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_choice_feasibility_engine.py`

### `backend/app/engines/simulation/conflict_resolution_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 738
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_conflict_resolution_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_conflict_resolution_engine.py`

### `backend/app/engines/simulation/consequence_queue_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 602
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_consequence_queue_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_consequence_queue_engine.py`

### `backend/app/engines/simulation/consequence_resolver.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 512
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_causal_chain_explanation_engine.py`
  - `backend/app/tests/test_chunk4_consequence_resolver.py`
- Related tests:
  - `backend/app/tests/test_chunk4_consequence_resolver.py`

### `backend/app/engines/simulation/emotional_carryover_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 608
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_emotional_carryover_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_emotional_carryover_engine.py`

### `backend/app/engines/simulation/event_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 670
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_event_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_event_engine.py`

### `backend/app/engines/simulation/evidence_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 565
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_evidence_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_evidence_engine.py`

### `backend/app/engines/simulation/genre_adaptation_ml_hook_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 538
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_genre_adaptation_ml_hook_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_genre_adaptation_ml_hook_engine.py`

### `backend/app/engines/simulation/handoff_payload_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 705
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_handoff_payload_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_handoff_payload_engine.py`

### `backend/app/engines/simulation/interaction_simulation_orchestrator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 495
- Imports:
  - `backend.app.engines.simulation.cast_selection_engine`
  - `backend.app.engines.simulation.causal_chain_explanation_engine`
  - `backend.app.engines.simulation.conflict_resolution_engine`
  - `backend.app.engines.simulation.consequence_queue_engine`
  - `backend.app.engines.simulation.consequence_resolver`
  - `backend.app.engines.simulation.emotional_carryover_engine`
  - `backend.app.engines.simulation.event_engine`
  - `backend.app.engines.simulation.genre_adaptation_ml_hook_engine`
  - `backend.app.engines.simulation.handoff_payload_engine`
  - `backend.app.engines.simulation.stakes_engine`
  - `backend.app.engines.simulation.tension_curve_engine`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/cast_selection_engine.py`
  - `backend/app/engines/simulation/causal_chain_explanation_engine.py`
  - `backend/app/engines/simulation/conflict_resolution_engine.py`
  - `backend/app/engines/simulation/consequence_queue_engine.py`
  - `backend/app/engines/simulation/consequence_resolver.py`
  - `backend/app/engines/simulation/emotional_carryover_engine.py`
  - `backend/app/engines/simulation/event_engine.py`
  - `backend/app/engines/simulation/genre_adaptation_ml_hook_engine.py`
  - `backend/app/engines/simulation/handoff_payload_engine.py`
  - `backend/app/engines/simulation/stakes_engine.py`
  - `backend/app/engines/simulation/tension_curve_engine.py`
- Likely dependents:
  - `backend/app/api/simulation_routes.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `backend/app/tests/test_chunk4_simulation_quality_scorer.py`
  - `scripts/chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py`

### `backend/app/engines/simulation/knowledge_secret_state_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 507
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_knowledge_secret_state_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_knowledge_secret_state_engine.py`

### `backend/app/engines/simulation/leverage_blackmail_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 770
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_leverage_blackmail_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_leverage_blackmail_engine.py`

### `backend/app/engines/simulation/location_presence_witness_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 519
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_location_presence_witness_validator.py`
- Related tests:
  - `backend/app/tests/test_chunk4_location_presence_witness_validator.py`

### `backend/app/engines/simulation/negotiation_bargain_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 773
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_negotiation_bargain_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_negotiation_bargain_engine.py`

### `backend/app/engines/simulation/opposite_nature_chemistry_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 538
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_chunk4_opposite_nature_chemistry_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_opposite_nature_chemistry_engine.py`

### `backend/app/engines/simulation/promise_oath_debt_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 636
- Imports:
  - `backend.app.schemas.simulation`
  - `copy`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_promise_oath_debt_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_promise_oath_debt_engine.py`

### `backend/app/engines/simulation/relationship_arc_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 553
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_relationship_arc_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_arc_engine.py`

### `backend/app/engines/simulation/relationship_graph_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 411
- Imports:
  - `backend.app.engines.simulation.relationship_ontology_engine`
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/relationship_ontology_engine.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_relationship_graph_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_graph_engine.py`

### `backend/app/engines/simulation/relationship_ontology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 428
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/relationship_graph_engine.py`
  - `backend/app/tests/test_chunk4_relationship_ontology_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_ontology_engine.py`

### `backend/app/engines/simulation/relationship_repair_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 705
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_chunk4_relationship_repair_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_repair_engine.py`

### `backend/app/engines/simulation/rumor_propagation_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 653
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_rumor_propagation_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_rumor_propagation_engine.py`

### `backend/app/engines/simulation/simulation_anti_genericity_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 571
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/api/simulation_routes.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `scripts/chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`

### `backend/app/engines/simulation/simulation_benchmark_pack.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 444
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_benchmark_pack.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `scripts/chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_benchmark_pack.py`

### `backend/app/engines/simulation/simulation_constraint_solver.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 497
- Imports:
  - `backend.app.schemas.simulation`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_constraint_solver.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_constraint_solver.py`

### `backend/app/engines/simulation/simulation_learning_adapter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 563
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`

### `backend/app/engines/simulation/simulation_learning_metadata_verifier.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 442
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`

### `backend/app/engines/simulation/simulation_quality_scorer.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 480
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/api/simulation_routes.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `backend/app/tests/test_chunk4_simulation_quality_scorer.py`
  - `scripts/chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_quality_scorer.py`

### `backend/app/engines/simulation/simulation_run_store.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 367
- Imports:
  - `json`
  - `pathlib`
  - `typing`
- Likely dependents:
  - `backend/app/api/simulation_routes.py`
  - `backend/app/tests/test_chunk4_simulation_run_store.py`
  - `scripts/chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_run_store.py`

### `backend/app/engines/simulation/simulation_state_delta_resolver.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 414
- Imports:
  - `backend.app.schemas.simulation`
  - `copy`
  - `typing`
- Connected files:
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_state_delta_resolver.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_state_delta_resolver.py`

### `backend/app/engines/simulation/social_network_influence_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 707
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_chunk4_social_network_influence_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_social_network_influence_engine.py`

### `backend/app/engines/simulation/stakes_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 469
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_stakes_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_stakes_engine.py`

### `backend/app/engines/simulation/tension_curve_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 577
- Imports:
  - `typing`
- Likely dependents:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_tension_curve_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_tension_curve_engine.py`

### `backend/app/schemas/simulation.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 702
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.handoffs`
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/handoffs.py`
- Likely dependents:
  - `backend/app/api/simulation_routes.py`
  - `backend/app/engines/simulation/agency_model_engine.py`
  - `backend/app/engines/simulation/canon_branch_timeline_validator.py`
  - `backend/app/engines/simulation/choice_architecture_engine.py`
  - `backend/app/engines/simulation/choice_feasibility_engine.py`
  - `backend/app/engines/simulation/consequence_resolver.py`
  - `backend/app/engines/simulation/evidence_engine.py`
  - `backend/app/engines/simulation/knowledge_secret_state_engine.py`
  - `backend/app/engines/simulation/leverage_blackmail_engine.py`
  - `backend/app/engines/simulation/location_presence_witness_validator.py`
  - `backend/app/engines/simulation/negotiation_bargain_engine.py`
  - `backend/app/engines/simulation/promise_oath_debt_engine.py`
  - `backend/app/engines/simulation/relationship_arc_engine.py`
  - `backend/app/engines/simulation/relationship_graph_engine.py`
  - `backend/app/engines/simulation/rumor_propagation_engine.py`
  - `backend/app/engines/simulation/simulation_constraint_solver.py`
  - `backend/app/engines/simulation/simulation_state_delta_resolver.py`
  - `backend/app/tests/test_chunk4_agency_model_engine.py`
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`
  - `backend/app/tests/test_chunk4_cast_selection_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py`
  - `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`
  - `backend/app/tests/test_chunk4_simulation_api_routes.py`
  - `backend/app/tests/test_chunk4_simulation_benchmark_pack.py`
  - `backend/app/tests/test_chunk4_simulation_constraint_solver.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `backend/app/tests/test_chunk4_simulation_quality_scorer.py`
  - `backend/app/tests/test_chunk4_simulation_run_store.py`
  - `backend/app/tests/test_chunk4_simulation_schemas.py`
  - `backend/app/tests/test_chunk4_simulation_smoke_test.py`
  - `backend/app/tests/test_chunk4_simulation_state_delta_resolver.py`
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`

### `backend/app/tests/test_chunk4_agency_model_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 245
- Imports:
  - `backend.app.engines.simulation.agency_model_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/agency_model_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_agency_model_engine.py`

### `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 313
- Imports:
  - `backend.app.engines.simulation.canon_branch_timeline_validator`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/canon_branch_timeline_validator.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`

### `backend/app/tests/test_chunk4_cast_selection_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 277
- Imports:
  - `backend.app.engines.simulation.cast_selection_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/cast_selection_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_cast_selection_engine.py`

### `backend/app/tests/test_chunk4_causal_chain_explanation_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 323
- Imports:
  - `backend.app.engines.simulation.causal_chain_explanation_engine`
  - `backend.app.engines.simulation.consequence_resolver`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/causal_chain_explanation_engine.py`
  - `backend/app/engines/simulation/consequence_resolver.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_causal_chain_explanation_engine.py`

### `backend/app/tests/test_chunk4_choice_architecture_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 284
- Imports:
  - `backend.app.engines.simulation.choice_architecture_engine`
  - `backend.app.engines.simulation.choice_feasibility_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/choice_architecture_engine.py`
  - `backend/app/engines/simulation/choice_feasibility_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_choice_architecture_engine.py`

### `backend/app/tests/test_chunk4_choice_feasibility_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 304
- Imports:
  - `backend.app.engines.simulation.choice_feasibility_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/choice_feasibility_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_choice_feasibility_engine.py`

### `backend/app/tests/test_chunk4_conflict_resolution_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 248
- Imports:
  - `backend.app.engines.simulation.conflict_resolution_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/conflict_resolution_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_conflict_resolution_engine.py`

### `backend/app/tests/test_chunk4_consequence_queue_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 307
- Imports:
  - `backend.app.engines.simulation.consequence_queue_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/consequence_queue_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_consequence_queue_engine.py`

### `backend/app/tests/test_chunk4_consequence_resolver.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 238
- Imports:
  - `backend.app.engines.simulation.consequence_resolver`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/consequence_resolver.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_consequence_resolver.py`

### `backend/app/tests/test_chunk4_emotional_carryover_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 223
- Imports:
  - `backend.app.engines.simulation.emotional_carryover_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/emotional_carryover_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_emotional_carryover_engine.py`

### `backend/app/tests/test_chunk4_event_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 266
- Imports:
  - `backend.app.engines.simulation.event_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/event_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_event_engine.py`

### `backend/app/tests/test_chunk4_evidence_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 319
- Imports:
  - `backend.app.engines.simulation.evidence_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/evidence_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_evidence_engine.py`

### `backend/app/tests/test_chunk4_genre_adaptation_ml_hook_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 193
- Imports:
  - `backend.app.engines.simulation.genre_adaptation_ml_hook_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/genre_adaptation_ml_hook_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_genre_adaptation_ml_hook_engine.py`

### `backend/app/tests/test_chunk4_handoff_payload_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 323
- Imports:
  - `backend.app.engines.simulation.handoff_payload_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/handoff_payload_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_handoff_payload_engine.py`

### `backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 255
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_interaction_simulation_orchestrator.py`

### `backend/app/tests/test_chunk4_knowledge_secret_state_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 274
- Imports:
  - `backend.app.engines.simulation.knowledge_secret_state_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/knowledge_secret_state_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_knowledge_secret_state_engine.py`

### `backend/app/tests/test_chunk4_leverage_blackmail_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 398
- Imports:
  - `backend.app.engines.simulation.leverage_blackmail_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/leverage_blackmail_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_leverage_blackmail_engine.py`

### `backend/app/tests/test_chunk4_location_presence_witness_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 313
- Imports:
  - `backend.app.engines.simulation.location_presence_witness_validator`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/location_presence_witness_validator.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_location_presence_witness_validator.py`

### `backend/app/tests/test_chunk4_negotiation_bargain_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 342
- Imports:
  - `backend.app.engines.simulation.negotiation_bargain_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/negotiation_bargain_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_negotiation_bargain_engine.py`

### `backend/app/tests/test_chunk4_opposite_nature_chemistry_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 231
- Imports:
  - `backend.app.engines.simulation.opposite_nature_chemistry_engine`
- Connected files:
  - `backend/app/engines/simulation/opposite_nature_chemistry_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_opposite_nature_chemistry_engine.py`

### `backend/app/tests/test_chunk4_promise_oath_debt_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 355
- Imports:
  - `backend.app.engines.simulation.promise_oath_debt_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/promise_oath_debt_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_promise_oath_debt_engine.py`

### `backend/app/tests/test_chunk4_relationship_arc_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 195
- Imports:
  - `backend.app.engines.simulation.relationship_arc_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/relationship_arc_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_arc_engine.py`

### `backend/app/tests/test_chunk4_relationship_graph_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 245
- Imports:
  - `backend.app.engines.simulation.relationship_graph_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/relationship_graph_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_graph_engine.py`

### `backend/app/tests/test_chunk4_relationship_ontology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 235
- Imports:
  - `backend.app.engines.simulation.relationship_ontology_engine`
- Connected files:
  - `backend/app/engines/simulation/relationship_ontology_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_ontology_engine.py`

### `backend/app/tests/test_chunk4_relationship_repair_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 212
- Imports:
  - `backend.app.engines.simulation.relationship_repair_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/relationship_repair_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_relationship_repair_engine.py`

### `backend/app/tests/test_chunk4_rumor_propagation_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 300
- Imports:
  - `backend.app.engines.simulation.rumor_propagation_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/rumor_propagation_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_rumor_propagation_engine.py`

### `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 241
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_anti_genericity_validator.py`

### `backend/app/tests/test_chunk4_simulation_api_routes.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 188
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_api_routes.py`

### `backend/app/tests/test_chunk4_simulation_benchmark_pack.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 192
- Imports:
  - `backend.app.engines.simulation.simulation_benchmark_pack`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_benchmark_pack.py`

### `backend/app/tests/test_chunk4_simulation_constraint_solver.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 344
- Imports:
  - `backend.app.engines.simulation.simulation_constraint_solver`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/simulation_constraint_solver.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_constraint_solver.py`

### `backend/app/tests/test_chunk4_simulation_learning_adapter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 301
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.engines.simulation.simulation_benchmark_pack`
  - `backend.app.engines.simulation.simulation_learning_adapter`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/engines/simulation/simulation_learning_adapter.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`

### `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 272
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.engines.simulation.simulation_benchmark_pack`
  - `backend.app.engines.simulation.simulation_learning_adapter`
  - `backend.app.engines.simulation.simulation_learning_metadata_verifier`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/engines/simulation/simulation_learning_adapter.py`
  - `backend/app/engines/simulation/simulation_learning_metadata_verifier.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`

### `backend/app/tests/test_chunk4_simulation_quality_scorer.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 204
- Imports:
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_quality_scorer.py`

### `backend/app/tests/test_chunk4_simulation_run_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 170
- Imports:
  - `backend.app.engines.simulation.simulation_run_store`
  - `backend.app.schemas.simulation`
  - `pathlib`
- Connected files:
  - `backend/app/engines/simulation/simulation_run_store.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_run_store.py`

### `backend/app/tests/test_chunk4_simulation_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 325
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_schemas.py`

### `backend/app/tests/test_chunk4_simulation_smoke_test.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 21
- Imports:
  - `pathlib`
  - `scripts.chunk4_simulation_smoke_test`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_smoke_test.py`

### `backend/app/tests/test_chunk4_simulation_state_delta_resolver.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 341
- Imports:
  - `backend.app.engines.simulation.simulation_state_delta_resolver`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/simulation_state_delta_resolver.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_state_delta_resolver.py`

### `backend/app/tests/test_chunk4_social_network_influence_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 233
- Imports:
  - `backend.app.engines.simulation.social_network_influence_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/social_network_influence_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_social_network_influence_engine.py`

### `backend/app/tests/test_chunk4_stakes_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 216
- Imports:
  - `backend.app.engines.simulation.stakes_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/stakes_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_stakes_engine.py`

### `backend/app/tests/test_chunk4_state_delta_models.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 299
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_state_delta_models.py`

### `backend/app/tests/test_chunk4_tension_curve_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 287
- Imports:
  - `backend.app.engines.simulation.tension_curve_engine`
  - `backend.app.schemas.simulation`
- Connected files:
  - `backend/app/engines/simulation/tension_curve_engine.py`
  - `backend/app/schemas/simulation.py`
- Related tests:
  - `backend/app/tests/test_chunk4_tension_curve_engine.py`

### `backend/app/tests/test_cross_chunk_simulation_handoffs.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 176
- Imports:
  - `backend.app.schemas.handoffs`
  - `backend.app.services.character_learning_adapter`
  - `backend.app.services.world_learning_adapter`
- Connected files:
  - `backend/app/schemas/handoffs.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/world_learning_adapter.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`

### `docs/chunk4_simulation_layer_summary.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 77

### `scripts/chunk4_simulation_smoke_test.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 277
- Imports:
  - `__future__`
  - `backend.app.engines.simulation.interaction_simulation_orchestrator`
  - `backend.app.engines.simulation.simulation_anti_genericity_validator`
  - `backend.app.engines.simulation.simulation_benchmark_pack`
  - `backend.app.engines.simulation.simulation_quality_scorer`
  - `backend.app.engines.simulation.simulation_run_store`
  - `backend.app.schemas.simulation`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/engines/simulation/interaction_simulation_orchestrator.py`
  - `backend/app/engines/simulation/simulation_anti_genericity_validator.py`
  - `backend/app/engines/simulation/simulation_benchmark_pack.py`
  - `backend/app/engines/simulation/simulation_quality_scorer.py`
  - `backend/app/engines/simulation/simulation_run_store.py`
  - `backend/app/schemas/simulation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk4_simulation_smoke_test.py`
- Related tests:
  - `backend/app/tests/test_chunk4_simulation_smoke_test.py`

### `scripts/verify_chunk4_final.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 183
- Imports:
  - `__future__`
  - `importlib`
  - `json`
  - `pathlib`
  - `subprocess`

## chunk_5

### `backend/app/api/story_generation_routes.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: story_generation_routes.py
- Line count: 110
- Imports:
  - `__future__`
  - `backend.app.engines.story_generation.story_generation_orchestrator`
  - `backend.app.schemas.story_generation`
  - `fastapi`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/engines/story_generation/story_generation_orchestrator.py`
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/engines/story_generation/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/story_generation/adaptive_story_pattern_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 667
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_adaptive_story_pattern_engine.py`
- Related tests:
  - `backend/app/tests/test_adaptive_story_pattern_engine.py`

### `backend/app/engines/story_generation/causal_continuity_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 363
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_causal_continuity_validator.py`
- Related tests:
  - `backend/app/tests/test_causal_continuity_validator.py`

### `backend/app/engines/story_generation/chapter_expansion_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 435
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chapter_expansion_engine.py`
- Related tests:
  - `backend/app/tests/test_chapter_expansion_engine.py`

### `backend/app/engines/story_generation/chapter_generator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 402
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chapter_generator.py`
- Related tests:
  - `backend/app/tests/test_chapter_generator.py`

### `backend/app/engines/story_generation/character_voice_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 423
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_character_voice_engine.py`
  - `backend/app/tests/test_emotional_subtext_engine.py`
- Related tests:
  - `backend/app/tests/test_character_voice_engine.py`

### `backend/app/engines/story_generation/commercial_appeal_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 504
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_commercial_appeal_engine.py`
- Related tests:
  - `backend/app/tests/test_commercial_appeal_engine.py`

### `backend/app/engines/story_generation/consequence_payoff_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 334
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_consequence_payoff_engine.py`
- Related tests:
  - `backend/app/tests/test_consequence_payoff_engine.py`

### `backend/app/engines/story_generation/constraint_satisfaction_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 378
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_constraint_satisfaction_engine.py`
- Related tests:
  - `backend/app/tests/test_constraint_satisfaction_engine.py`

### `backend/app/engines/story_generation/dialogue_beat_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 356
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_dialogue_beat_engine.py`
- Related tests:
  - `backend/app/tests/test_dialogue_beat_engine.py`

### `backend/app/engines/story_generation/dialogue_line_generator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 343
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_dialogue_line_generator.py`
- Related tests:
  - `backend/app/tests/test_dialogue_line_generator.py`

### `backend/app/engines/story_generation/draft_comparison_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 755
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_draft_comparison_engine.py`
- Related tests:
  - `backend/app/tests/test_draft_comparison_engine.py`

### `backend/app/engines/story_generation/emotional_subtext_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 437
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_emotional_subtext_engine.py`
- Related tests:
  - `backend/app/tests/test_emotional_subtext_engine.py`

### `backend/app/engines/story_generation/format_adapter_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 615
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_format_adapter_engine.py`
- Related tests:
  - `backend/app/tests/test_format_adapter_engine.py`

### `backend/app/engines/story_generation/game_interactive_scene_formatter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 844
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_game_interactive_scene_formatter.py`
- Related tests:
  - `backend/app/tests/test_game_interactive_scene_formatter.py`

### `backend/app/engines/story_generation/generated_scene_delta_extractor.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 441
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_generated_scene_delta_extractor.py`
- Related tests:
  - `backend/app/tests/test_generated_scene_delta_extractor.py`

### `backend/app/engines/story_generation/generation_contract_resolver.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 526
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk5_generation_contract_resolver.py`
  - `backend/app/tests/test_chunk5_handoff_package_loader.py`
  - `backend/app/tests/test_story_context_builder.py`
- Related tests:
  - `backend/app/tests/test_chunk5_generation_contract_resolver.py`

### `backend/app/engines/story_generation/generation_improvement_loop.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 634
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_generation_improvement_loop.py`
- Related tests:
  - `backend/app/tests/test_generation_improvement_loop.py`

### `backend/app/engines/story_generation/generation_mode_controller.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 468
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk5_generation_contract_resolver.py`
  - `backend/app/tests/test_chunk5_generation_mode_controller.py`
  - `backend/app/tests/test_chunk5_handoff_package_loader.py`
  - `backend/app/tests/test_story_context_builder.py`
- Related tests:
  - `backend/app/tests/test_chunk5_generation_mode_controller.py`

### `backend/app/engines/story_generation/handoff_package_loader.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 563
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk5_handoff_package_loader.py`
  - `backend/app/tests/test_story_context_builder.py`
- Related tests:
  - `backend/app/tests/test_chunk5_handoff_package_loader.py`

### `backend/app/engines/story_generation/knowledge_boundary_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 390
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_knowledge_boundary_validator.py`
- Related tests:
  - `backend/app/tests/test_knowledge_boundary_validator.py`

### `backend/app/engines/story_generation/learning_feedback_adapter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 817
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `datetime`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_learning_feedback_adapter.py`
  - `scripts/verify_chunk_1_5_integration.py`
- Related tests:
  - `backend/app/tests/test_learning_feedback_adapter.py`

### `backend/app/engines/story_generation/long_form_continuation_anchor.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 361
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_long_form_continuation_anchor.py`
- Related tests:
  - `backend/app/tests/test_long_form_continuation_anchor.py`

### `backend/app/engines/story_generation/long_form_memory_bridge.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 507
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_long_form_memory_bridge.py`
- Related tests:
  - `backend/app/tests/test_long_form_memory_bridge.py`

### `backend/app/engines/story_generation/multi_scene_pacing_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 609
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_multi_scene_pacing_engine.py`
- Related tests:
  - `backend/app/tests/test_multi_scene_pacing_engine.py`

### `backend/app/engines/story_generation/multi_world_multi_cast_scaling_controller.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 779
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_multi_world_multi_cast_scaling_controller.py`
- Related tests:
  - `backend/app/tests/test_multi_world_multi_cast_scaling_controller.py`

### `backend/app/engines/story_generation/originality_copy_risk_guard.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 832
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_originality_copy_risk_guard.py`
- Related tests:
  - `backend/app/tests/test_originality_copy_risk_guard.py`

### `backend/app/engines/story_generation/plot_outline_generator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 759
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_plot_outline_generator.py`
- Related tests:
  - `backend/app/tests/test_plot_outline_generator.py`

### `backend/app/engines/story_generation/prose_style_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 520
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_prose_style_engine.py`
- Related tests:
  - `backend/app/tests/test_prose_style_engine.py`

### `backend/app/engines/story_generation/relationship_beat_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 452
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_relationship_beat_engine.py`
- Related tests:
  - `backend/app/tests/test_relationship_beat_engine.py`

### `backend/app/engines/story_generation/scene_assembly_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 345
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_scene_assembly_engine.py`
- Related tests:
  - `backend/app/tests/test_scene_assembly_engine.py`

### `backend/app/engines/story_generation/scene_beat_planner.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 345
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_dialogue_beat_engine.py`
  - `backend/app/tests/test_scene_beat_planner.py`
- Related tests:
  - `backend/app/tests/test_scene_beat_planner.py`

### `backend/app/engines/story_generation/scene_blueprint_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 422
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_scene_blueprint_engine.py`
- Related tests:
  - `backend/app/tests/test_scene_blueprint_engine.py`

### `backend/app/engines/story_generation/scene_draft_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 429
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_scene_draft_engine.py`
- Related tests:
  - `backend/app/tests/test_scene_draft_engine.py`

### `backend/app/engines/story_generation/scene_quality_gate.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 489
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_scene_quality_gate.py`
- Related tests:
  - `backend/app/tests/test_scene_quality_gate.py`

### `backend/app/engines/story_generation/screenplay_movie_formatter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 644
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_screenplay_movie_formatter.py`
- Related tests:
  - `backend/app/tests/test_screenplay_movie_formatter.py`

### `backend/app/engines/story_generation/series_episode_structure_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 472
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_series_episode_structure_engine.py`
- Related tests:
  - `backend/app/tests/test_series_episode_structure_engine.py`

### `backend/app/engines/story_generation/series_season_formatter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 775
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_series_season_formatter.py`
- Related tests:
  - `backend/app/tests/test_series_season_formatter.py`

### `backend/app/engines/story_generation/story_anti_genericity_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 847
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_anti_genericity_validator.py`
- Related tests:
  - `backend/app/tests/test_story_anti_genericity_validator.py`

### `backend/app/engines/story_generation/story_benchmark_pack.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 636
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `datetime`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_benchmark_pack.py`
  - `scripts/verify_chunk_1_5_integration.py`
- Related tests:
  - `backend/app/tests/test_story_benchmark_pack.py`

### `backend/app/engines/story_generation/story_context_builder.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 557
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_context_builder.py`
- Related tests:
  - `backend/app/tests/test_story_context_builder.py`

### `backend/app/engines/story_generation/story_continuity_validator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 721
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_continuity_validator.py`
- Related tests:
  - `backend/app/tests/test_story_continuity_validator.py`

### `backend/app/engines/story_generation/story_export_store.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 458
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_export_store.py`
  - `scripts/verify_chunk_1_5_integration.py`
- Related tests:
  - `backend/app/tests/test_story_export_store.py`

### `backend/app/engines/story_generation/story_generation_orchestrator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 704
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/api/story_generation_routes.py`
  - `backend/app/tests/test_story_generation_orchestrator.py`
  - `scripts/verify_chunk_1_5_integration.py`
- Related tests:
  - `backend/app/tests/test_story_generation_orchestrator.py`

### `backend/app/engines/story_generation/story_intent_interpreter.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 485
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `re`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk5_story_intent_interpreter.py`
- Related tests:
  - `backend/app/tests/test_chunk5_story_intent_interpreter.py`

### `backend/app/engines/story_generation/story_memory_update_contract.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 581
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_memory_update_contract.py`
- Related tests:
  - `backend/app/tests/test_story_memory_update_contract.py`

### `backend/app/engines/story_generation/story_provenance_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 729
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `datetime`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_provenance_engine.py`
- Related tests:
  - `backend/app/tests/test_story_provenance_engine.py`

### `backend/app/engines/story_generation/story_quality_scorer.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 657
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_quality_scorer.py`
- Related tests:
  - `backend/app/tests/test_story_quality_scorer.py`

### `backend/app/engines/story_generation/story_revision_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 727
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_revision_engine.py`
- Related tests:
  - `backend/app/tests/test_story_revision_engine.py`

### `backend/app/engines/story_generation/story_smoke_test.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 478
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_story_smoke_test.py`
  - `scripts/verify_chunk_1_5_integration.py`
- Related tests:
  - `backend/app/tests/test_story_smoke_test.py`

### `backend/app/engines/story_generation/world_detail_injection_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 503
- Imports:
  - `__future__`
  - `typing`
- Likely dependents:
  - `backend/app/tests/test_world_detail_injection_engine.py`
- Related tests:
  - `backend/app/tests/test_world_detail_injection_engine.py`

### `backend/app/schemas/story_generation.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 1446
- Imports:
  - `__future__`
  - `enum`
  - `pydantic`
  - `typing`
- Likely dependents:
  - `backend/app/api/story_generation_routes.py`
  - `backend/app/engines/story_generation/adaptive_story_pattern_engine.py`
  - `backend/app/engines/story_generation/causal_continuity_validator.py`
  - `backend/app/engines/story_generation/chapter_expansion_engine.py`
  - `backend/app/engines/story_generation/chapter_generator.py`
  - `backend/app/engines/story_generation/character_voice_engine.py`
  - `backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py`
  - `backend/app/engines/story_generation/commercial_appeal_engine.py`
  - `backend/app/engines/story_generation/consequence_payoff_engine.py`
  - `backend/app/engines/story_generation/constraint_satisfaction_engine.py`
  - `backend/app/engines/story_generation/dialogue_beat_engine.py`
  - `backend/app/engines/story_generation/dialogue_line_generator.py`
  - `backend/app/engines/story_generation/draft_comparison_engine.py`
  - `backend/app/engines/story_generation/emotional_subtext_engine.py`
  - `backend/app/engines/story_generation/format_adapter_engine.py`
  - `backend/app/engines/story_generation/game_interactive_scene_formatter.py`
  - `backend/app/engines/story_generation/generated_scene_delta_extractor.py`
  - `backend/app/engines/story_generation/generation_contract_resolver.py`
  - `backend/app/engines/story_generation/generation_improvement_loop.py`
  - `backend/app/engines/story_generation/generation_mode_controller.py`
- Related tests:
  - `backend/app/tests/test_chunk5_story_generation_schemas.py`
  - `backend/app/tests/test_story_generation_api_routes.py`
  - `backend/app/tests/test_story_generation_orchestrator.py`

### `backend/app/tests/test_chunk5_generation_contract_resolver.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 245
- Imports:
  - `backend.app.engines.story_generation.generation_contract_resolver`
  - `backend.app.engines.story_generation.generation_mode_controller`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generation_contract_resolver.py`
  - `backend/app/engines/story_generation/generation_mode_controller.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk5_generation_contract_resolver.py`

### `backend/app/tests/test_chunk5_generation_mode_controller.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 159
- Imports:
  - `backend.app.engines.story_generation.generation_mode_controller`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generation_mode_controller.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk5_generation_mode_controller.py`

### `backend/app/tests/test_chunk5_handoff_package_loader.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 218
- Imports:
  - `backend.app.engines.story_generation.generation_contract_resolver`
  - `backend.app.engines.story_generation.generation_mode_controller`
  - `backend.app.engines.story_generation.handoff_package_loader`
  - `backend.app.schemas.simulation`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generation_contract_resolver.py`
  - `backend/app/engines/story_generation/generation_mode_controller.py`
  - `backend/app/engines/story_generation/handoff_package_loader.py`
  - `backend/app/schemas/simulation.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk5_handoff_package_loader.py`

### `backend/app/tests/test_chunk5_story_generation_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 245
- Imports:
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk5_story_generation_schemas.py`

### `backend/app/tests/test_chunk5_story_intent_interpreter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 188
- Imports:
  - `backend.app.engines.story_generation.story_intent_interpreter`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_intent_interpreter.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk5_story_intent_interpreter.py`

### `backend/app/tests/test_final_chunk5_verification.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 15
- Imports:
  - `json`
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_final_chunk5_verification.py`

### `backend/app/tests/test_story_generation_api_routes.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 121
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_story_generation_api_routes.py`

### `backend/app/tests/test_story_generation_orchestrator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 291
- Imports:
  - `backend.app.engines.story_generation.story_generation_orchestrator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_generation_orchestrator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_generation_orchestrator.py`

### `docs/chunk5_locked_step_tracker.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 93

### `scripts/final_chunk5_verification.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 79
- Imports:
  - `__future__`
  - `datetime`
  - `json`
  - `os`
  - `pathlib`
  - `subprocess`
  - `sys`
  - `typing`
- Related tests:
  - `backend/app/tests/test_final_chunk5_verification.py`

### `scripts/verify_chunk5_roadmap_integrity.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 315
- Imports:
  - `__future__`
  - `ast`
  - `json`
  - `pathlib`
  - `subprocess`
  - `sys`
  - `typing`

## chunk_6

### `backend/app/engines/deep_world/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/deep_world/climate_weather_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 374
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_climate_weather_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_climate_weather_engine.py`

### `backend/app/engines/deep_world/deep_lore_history_contract.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 143
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_deep_lore_history_contract.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_lore_history_contract.py`

### `backend/app/engines/deep_world/deep_world_design_contract.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 153
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_design_contract.py`

### `backend/app/engines/deep_world/ecology_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 389
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_ecology_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_ecology_engine.py`

### `backend/app/engines/deep_world/fauna_generator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 446
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_fauna_generator.py`
- Related tests:
  - `backend/app/tests/test_chunk6_fauna_generator.py`

### `backend/app/engines/deep_world/flora_generator.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 438
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_flora_generator.py`
  - `backend/app/tests/test_chunk6_flora_lifecycle_use_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_flora_generator.py`

### `backend/app/engines/deep_world/flora_lifecycle_use_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 409
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_flora_lifecycle_use_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_flora_lifecycle_use_engine.py`

### `backend/app/engines/deep_world/generated_identity_contract.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 184
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_generated_identity_contract.py`
- Related tests:
  - `backend/app/tests/test_chunk6_generated_identity_contract.py`

### `backend/app/engines/deep_world/geography_terrain_engine.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 243
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_geography_terrain_engine.py`
  - `backend/app/tests/test_chunk6_region_identity_system.py`
- Related tests:
  - `backend/app/tests/test_chunk6_geography_terrain_engine.py`

### `backend/app/engines/deep_world/region_identity_system.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 273
- Imports:
  - `__future__`
  - `backend.app.schemas.deep_world`
  - `typing`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Likely dependents:
  - `backend/app/tests/test_chunk6_region_identity_system.py`
- Related tests:
  - `backend/app/tests/test_chunk6_region_identity_system.py`

### `backend/app/schemas/deep_world.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 423
- Imports:
  - `__future__`
  - `enum`
  - `pydantic`
  - `typing`
- Likely dependents:
  - `backend/app/engines/deep_world/climate_weather_engine.py`
  - `backend/app/engines/deep_world/deep_lore_history_contract.py`
  - `backend/app/engines/deep_world/deep_world_design_contract.py`
  - `backend/app/engines/deep_world/ecology_engine.py`
  - `backend/app/engines/deep_world/fauna_generator.py`
  - `backend/app/engines/deep_world/flora_generator.py`
  - `backend/app/engines/deep_world/flora_lifecycle_use_engine.py`
  - `backend/app/engines/deep_world/generated_identity_contract.py`
  - `backend/app/engines/deep_world/geography_terrain_engine.py`
  - `backend/app/engines/deep_world/region_identity_system.py`
  - `backend/app/tests/test_chunk6_climate_weather_engine.py`
  - `backend/app/tests/test_chunk6_deep_lore_history_contract.py`
  - `backend/app/tests/test_chunk6_deep_world_schemas.py`
  - `backend/app/tests/test_chunk6_design_contract.py`
  - `backend/app/tests/test_chunk6_ecology_engine.py`
  - `backend/app/tests/test_chunk6_fauna_generator.py`
  - `backend/app/tests/test_chunk6_flora_generator.py`
  - `backend/app/tests/test_chunk6_generated_identity_contract.py`
  - `backend/app/tests/test_chunk6_geography_terrain_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_world_schemas.py`

### `backend/app/tests/test_chunk6_climate_weather_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 118
- Imports:
  - `backend.app.engines.deep_world.climate_weather_engine`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/climate_weather_engine.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_climate_weather_engine.py`

### `backend/app/tests/test_chunk6_deep_lore_history_contract.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 71
- Imports:
  - `backend.app.engines.deep_world.deep_lore_history_contract`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/deep_lore_history_contract.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_lore_history_contract.py`

### `backend/app/tests/test_chunk6_deep_world_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 97
- Imports:
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_deep_world_schemas.py`
  - `backend/app/tests/test_world_schemas.py`

### `backend/app/tests/test_chunk6_design_contract.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 62
- Imports:
  - `backend.app.engines.deep_world.deep_world_design_contract`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/deep_world_design_contract.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_design_contract.py`

### `backend/app/tests/test_chunk6_ecology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 121
- Imports:
  - `backend.app.engines.deep_world.ecology_engine`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/ecology_engine.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_ecology_engine.py`

### `backend/app/tests/test_chunk6_fauna_generator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 116
- Imports:
  - `backend.app.engines.deep_world.fauna_generator`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/fauna_generator.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_fauna_generator.py`

### `backend/app/tests/test_chunk6_flora_generator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 116
- Imports:
  - `backend.app.engines.deep_world.flora_generator`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/flora_generator.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_flora_generator.py`

### `backend/app/tests/test_chunk6_flora_lifecycle_use_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 151
- Imports:
  - `backend.app.engines.deep_world.flora_generator`
  - `backend.app.engines.deep_world.flora_lifecycle_use_engine`
- Connected files:
  - `backend/app/engines/deep_world/flora_generator.py`
  - `backend/app/engines/deep_world/flora_lifecycle_use_engine.py`
- Related tests:
  - `backend/app/tests/test_chunk6_flora_lifecycle_use_engine.py`

### `backend/app/tests/test_chunk6_generated_identity_contract.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 117
- Imports:
  - `backend.app.engines.deep_world.generated_identity_contract`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/generated_identity_contract.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_generated_identity_contract.py`

### `backend/app/tests/test_chunk6_geography_terrain_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 77
- Imports:
  - `backend.app.engines.deep_world.geography_terrain_engine`
  - `backend.app.schemas.deep_world`
- Connected files:
  - `backend/app/engines/deep_world/geography_terrain_engine.py`
  - `backend/app/schemas/deep_world.py`
- Related tests:
  - `backend/app/tests/test_chunk6_geography_terrain_engine.py`

### `backend/app/tests/test_chunk6_region_identity_system.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 93
- Imports:
  - `backend.app.engines.deep_world.geography_terrain_engine`
  - `backend.app.engines.deep_world.region_identity_system`
- Connected files:
  - `backend/app/engines/deep_world/geography_terrain_engine.py`
  - `backend/app/engines/deep_world/region_identity_system.py`
- Related tests:
  - `backend/app/tests/test_chunk6_region_identity_system.py`

## pre_chunk_6_upgrade

### `backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 201
- Imports:
  - `__future__`
  - `backend.app.schemas.story_generation`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_generation.py`
- Likely dependents:
  - `backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py`
- Related tests:
  - `backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py`

### `backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 73
- Imports:
  - `backend.app.engines.story_generation.chunk_1_to_5_future_compatibility_bridge`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/chunk_1_to_5_future_compatibility_bridge.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chunk_1_to_5_future_compatibility_bridge.py`

### `backend/app/tests/test_chunk_1_to_5_perfection.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 15
- Imports:
  - `json`
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_chunk_1_to_5_perfection.py`

### `backend/app/tests/test_pre_chunk6_readiness.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 15
- Imports:
  - `json`
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_pre_chunk6_readiness.py`

### `docs/chunk_1_to_5_compatibility_audit_before_chunk6.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 29

### `docs/chunk_1_to_5_deep_world_hook_contract.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 55

### `docs/chunk_1_to_5_engine_coverage_matrix.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 19

### `docs/chunk_1_to_5_perfection_standard.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 39
- Related tests:
  - `backend/app/tests/test_chunk_1_to_5_perfection.py`

### `scripts/verify_chunk_1_to_5_perfection.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 123
- Imports:
  - `__future__`
  - `datetime`
  - `json`
  - `pathlib`
  - `subprocess`
  - `sys`
- Related tests:
  - `backend/app/tests/test_chunk_1_to_5_perfection.py`

### `scripts/verify_pre_chunk6_readiness.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 91
- Imports:
  - `__future__`
  - `datetime`
  - `json`
  - `pathlib`
  - `subprocess`
  - `sys`
- Related tests:
  - `backend/app/tests/test_pre_chunk6_readiness.py`

## unknown_or_cross_chunk

### `.gitignore`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: .gitignore
- Line count: 39

### `README.md`

- Type: `readme`
- Status: `active_project_file`
- Purpose: Project file: README.md
- Line count: 1352

### `backend/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/api/__init__.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/api/routes_learning.py`

- Type: `api_router`
- Status: `active_project_file`
- Purpose: Project file: routes_learning.py
- Line count: 438
- Imports:
  - `backend.app.services.embedding_registry_store`
  - `backend.app.services.learning_integration`
  - `backend.app.services.learning_registry_store`
  - `backend.app.services.provenance_store`
  - `backend.app.services.training_queue_store`
  - `fastapi`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/services/embedding_registry_store.py`
  - `backend/app/services/learning_integration.py`
  - `backend/app/services/learning_registry_store.py`
  - `backend/app/services/provenance_store.py`
  - `backend/app/services/training_queue_store.py`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/benchmarks/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/core/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/core/config.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: config.py
- Line count: 11
- Imports:
  - `pydantic`
- Likely dependents:
  - `backend/app/main.py`

### `backend/app/db/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/db/database.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: database.py
- Line count: 97
- Imports:
  - `pathlib`
  - `sqlite3`
  - `sys`
  - `typing`
- Likely dependents:
  - `backend/app/services/foundation_store.py`
  - `backend/app/services/world_store.py`

### `backend/app/engines/__init__.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/engines/base.py`

- Type: `engine`
- Status: `active_project_file`
- Purpose: Implements MythOS engine logic for a story/world subsystem.
- Line count: 44
- Imports:
  - `abc`
  - `backend.app.schemas.foundation`
  - `typing`
- Connected files:
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/engines/character/adaptability_engine.py`
  - `backend/app/engines/character/character_agent_state_engine.py`
  - `backend/app/engines/character/character_bible_export_engine.py`
  - `backend/app/engines/character/character_consistency_validator.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/engines/character/character_genesis_engine.py`
  - `backend/app/engines/character/character_originality_engine.py`
  - `backend/app/engines/character/character_quality_scorer.py`
  - `backend/app/engines/character/character_registry_seed.py`
  - `backend/app/engines/character/character_type_ontology_engine.py`
  - `backend/app/engines/character/destiny_legacy_engine.py`
  - `backend/app/engines/character/dialogue_voice_engine.py`
  - `backend/app/engines/character/emotion_engine.py`
  - `backend/app/engines/character/emotional_arc_engine.py`
  - `backend/app/engines/character/family_foundation_engine.py`
  - `backend/app/engines/character/goal_motivation_engine.py`
  - `backend/app/engines/character/memory_engine.py`
  - `backend/app/engines/character/moral_compass_engine.py`
  - `backend/app/engines/character/origin_social_class_engine.py`
  - `backend/app/engines/character/people_type_engine.py`

### `backend/app/main.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: main.py
- Line count: 100
- Imports:
  - `backend.app.api.routes_character_engines`
  - `backend.app.api.routes_characters`
  - `backend.app.api.routes_foundation`
  - `backend.app.api.routes_learning`
  - `backend.app.api.routes_world`
  - `backend.app.api.routes_world_engines`
  - `backend.app.api.simulation_routes`
  - `backend.app.api.story_generation_routes`
  - `backend.app.core.config`
  - `backend.app.schemas.foundation`
  - `fastapi`
- Connected files:
  - `backend/app/api/routes_character_engines.py`
  - `backend/app/api/routes_characters.py`
  - `backend/app/api/routes_foundation.py`
  - `backend/app/api/routes_learning.py`
  - `backend/app/api/routes_world.py`
  - `backend/app/api/routes_world_engines.py`
  - `backend/app/api/simulation_routes.py`
  - `backend/app/api/story_generation_routes.py`
  - `backend/app/core/config.py`
  - `backend/app/schemas/foundation.py`
- Likely dependents:
  - `backend/app/tests/test_canon_branch_api.py`
  - `backend/app/tests/test_character_api.py`
  - `backend/app/tests/test_character_api_learning_registration.py`
  - `backend/app/tests/test_character_engine_routes.py`
  - `backend/app/tests/test_chunk4_simulation_api_routes.py`
  - `backend/app/tests/test_embedding_originality_api.py`
  - `backend/app/tests/test_export_files.py`
  - `backend/app/tests/test_foundation_api.py`
  - `backend/app/tests/test_health.py`
  - `backend/app/tests/test_learning_api.py`
  - `backend/app/tests/test_registry_seed.py`
  - `backend/app/tests/test_story_generation_api_routes.py`
  - `backend/app/tests/test_tracking_api.py`
  - `backend/app/tests/test_world_api.py`
  - `backend/app/tests/test_world_api_learning_registration.py`
  - `backend/app/tests/test_world_engine_api.py`
  - `backend/app/tests/test_world_run_persistence.py`

### `backend/app/schemas/__init__.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/schemas/artifacts.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 43
- Imports:
  - `backend.app.schemas.global_refs`
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/artifact_registry_store.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/schemas/canon.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 61
- Imports:
  - `backend.app.schemas.global_refs`
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/canon_lock_service.py`
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`
- Related tests:
  - `backend/app/tests/test_canon_branch_api.py`
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`

### `backend/app/schemas/engine_ops.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 79
- Imports:
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/engine_config_store.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`

### `backend/app/schemas/evaluation.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 74
- Imports:
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`

### `backend/app/schemas/global_refs.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 126
- Imports:
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/engines/simulation/canon_branch_timeline_validator.py`
  - `backend/app/engines/world/faction_institution_resource_engine.py`
  - `backend/app/engines/world/world_location_access_engine.py`
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/canon.py`
  - `backend/app/schemas/handoffs.py`
  - `backend/app/schemas/human_review.py`
  - `backend/app/schemas/simulation.py`
  - `backend/app/schemas/timeline.py`
  - `backend/app/services/artifact_registry_store.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/character_state_snapshot_store.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/services/human_review_store.py`
  - `backend/app/services/world_learning_adapter.py`
  - `backend/app/services/world_state_snapshot_service.py`
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`
  - `backend/app/tests/test_chunk4_simulation_constraint_solver.py`
  - `backend/app/tests/test_chunk4_simulation_schemas.py`

### `backend/app/schemas/handoffs.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 63
- Imports:
  - `backend.app.schemas.global_refs`
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/schemas/simulation.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/world_learning_adapter.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_simulation_handoffs.py`

### `backend/app/schemas/human_review.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 38
- Imports:
  - `backend.app.schemas.global_refs`
  - `datetime`
  - `enum`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/services/human_review_store.py`
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/schemas/learning.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 172
- Imports:
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/engines/character/adaptability_engine.py`
  - `backend/app/engines/character/character_bible_export_engine.py`
  - `backend/app/engines/character/character_consistency_validator.py`
  - `backend/app/engines/character/character_full_profile_orchestrator.py`
  - `backend/app/engines/character/character_originality_engine.py`
  - `backend/app/engines/character/character_quality_scorer.py`
  - `backend/app/engines/character/character_type_ontology_engine.py`
  - `backend/app/engines/character/destiny_legacy_engine.py`
  - `backend/app/engines/character/dialogue_voice_engine.py`
  - `backend/app/engines/character/relationship_readiness_engine.py`
  - `backend/app/engines/character/skill_ontology_engine.py`
  - `backend/app/tests/test_adaptability_engine.py`
  - `backend/app/tests/test_character_bible_export_engine.py`
  - `backend/app/tests/test_character_consistency_validator.py`
  - `backend/app/tests/test_character_full_profile_orchestrator.py`
  - `backend/app/tests/test_character_originality_engine.py`
  - `backend/app/tests/test_character_quality_scorer.py`
  - `backend/app/tests/test_character_type_ontology_engine.py`
  - `backend/app/tests/test_destiny_legacy_engine.py`
  - `backend/app/tests/test_dialogue_voice_engine.py`
- Related tests:
  - `backend/app/tests/test_character_api_learning_registration.py`
  - `backend/app/tests/test_character_learning_adapter.py`
  - `backend/app/tests/test_character_learning_metadata_verifier.py`
  - `backend/app/tests/test_character_run_store_learning_trace.py`
  - `backend/app/tests/test_chunk3_character_learning_smoke_script_exists.py`
  - `backend/app/tests/test_chunk4_simulation_learning_adapter.py`
  - `backend/app/tests/test_chunk4_simulation_learning_metadata_verifier.py`
  - `backend/app/tests/test_learning_api.py`
  - `backend/app/tests/test_learning_feedback_adapter.py`
  - `backend/app/tests/test_learning_integration.py`
  - `backend/app/tests/test_learning_registry_store.py`
  - `backend/app/tests/test_learning_schemas.py`
  - `backend/app/tests/test_world_api_learning_registration.py`
  - `backend/app/tests/test_world_learning_adapter.py`
  - `backend/app/tests/test_world_learning_metadata_verifier.py`
  - `backend/app/tests/test_world_run_store_learning_trace.py`

### `backend/app/schemas/story_dna.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 78
- Imports:
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/services/emotional_resonance_seed_service.py`
  - `backend/app/services/story_dna_seed_service.py`
  - `backend/app/services/world_character_pressure_matrix_service.py`
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/schemas/timeline.py`

- Type: `schema`
- Status: `active_project_file`
- Purpose: Defines structured data contracts and validation models.
- Line count: 45
- Imports:
  - `backend.app.schemas.global_refs`
  - `datetime`
  - `pydantic`
  - `typing`
  - `uuid`
- Connected files:
  - `backend/app/schemas/global_refs.py`
- Likely dependents:
  - `backend/app/tests/test_cross_chunk_foundation_schemas.py`
- Related tests:
  - `backend/app/tests/test_chunk4_canon_branch_timeline_validator.py`

### `backend/app/services/__init__.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: __init__.py
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/services/canon_lock_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: canon_lock_service.py
- Line count: 65
- Imports:
  - `backend.app.schemas.canon`
  - `typing`
- Connected files:
  - `backend/app/schemas/canon.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/services/cross_chunk_readiness_verifier.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: cross_chunk_readiness_verifier.py
- Line count: 384
- Imports:
  - `backend.app.schemas.artifacts`
  - `backend.app.schemas.engine_ops`
  - `backend.app.schemas.evaluation`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.handoffs`
  - `backend.app.services.character_learning_adapter`
  - `backend.app.services.world_learning_adapter`
  - `typing`
- Connected files:
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/engine_ops.py`
  - `backend/app/schemas/evaluation.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/handoffs.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/world_learning_adapter.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_cross_chunk_readiness_verifier.py`
  - `scripts/smoke_test_cross_chunk_readiness.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_readiness_verifier.py`

### `backend/app/services/deep_story_readiness_verifier.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: deep_story_readiness_verifier.py
- Line count: 454
- Imports:
  - `backend.app.engines.world.faction_institution_resource_engine`
  - `backend.app.engines.world.world_location_access_engine`
  - `backend.app.engines.world.world_rule_conflict_detector`
  - `backend.app.schemas.artifacts`
  - `backend.app.schemas.canon`
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.human_review`
  - `backend.app.services.artifact_registry_store`
  - `backend.app.services.canon_lock_service`
  - `backend.app.services.character_agency_state_updater`
  - `backend.app.services.character_consistency_invariant_checker`
  - `backend.app.services.character_contrast_matrix_service`
  - `backend.app.services.character_emotion_carryover_adapter`
  - `backend.app.services.character_memory_update_adapter`
  - `backend.app.services.character_state_snapshot_store`
  - `backend.app.services.cross_chunk_readiness_verifier`
  - `backend.app.services.emotional_resonance_seed_service`
  - `backend.app.services.engine_config_store`
  - `backend.app.services.human_review_store`
  - `backend.app.services.story_dna_seed_service`
- Connected files:
  - `backend/app/engines/world/faction_institution_resource_engine.py`
  - `backend/app/engines/world/world_location_access_engine.py`
  - `backend/app/engines/world/world_rule_conflict_detector.py`
  - `backend/app/schemas/artifacts.py`
  - `backend/app/schemas/canon.py`
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/human_review.py`
  - `backend/app/services/artifact_registry_store.py`
  - `backend/app/services/canon_lock_service.py`
  - `backend/app/services/character_agency_state_updater.py`
  - `backend/app/services/character_consistency_invariant_checker.py`
  - `backend/app/services/character_contrast_matrix_service.py`
  - `backend/app/services/character_emotion_carryover_adapter.py`
  - `backend/app/services/character_memory_update_adapter.py`
  - `backend/app/services/character_state_snapshot_store.py`
  - `backend/app/services/cross_chunk_readiness_verifier.py`
  - `backend/app/services/emotional_resonance_seed_service.py`
  - `backend/app/services/engine_config_store.py`
  - `backend/app/services/human_review_store.py`
  - `backend/app/services/story_dna_seed_service.py`
- Likely dependents:
  - `backend/app/tests/test_deep_story_readiness_verifier.py`
  - `scripts/smoke_test_deep_story_readiness.py`
- Related tests:
  - `backend/app/tests/test_deep_story_readiness_verifier.py`

### `backend/app/services/engine_config_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: engine_config_store.py
- Line count: 90
- Imports:
  - `backend.app.schemas.engine_ops`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/schemas/engine_ops.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/services/export_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: export_service.py
- Line count: 354
- Imports:
  - `backend.app.schemas.foundation`
  - `backend.app.services.foundation_store`
  - `csv`
  - `datetime`
  - `json`
  - `pathlib`
  - `pydantic`
  - `typing`
- Connected files:
  - `backend/app/schemas/foundation.py`
  - `backend/app/services/foundation_store.py`
- Likely dependents:
  - `backend/app/api/routes_foundation.py`

### `backend/app/services/human_review_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: human_review_store.py
- Line count: 93
- Imports:
  - `backend.app.schemas.global_refs`
  - `backend.app.schemas.human_review`
  - `json`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/schemas/global_refs.py`
  - `backend/app/schemas/human_review.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_core_foundation_services.py`

### `backend/app/services/learning_integration.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: learning_integration.py
- Line count: 274
- Imports:
  - `backend.app.services.embedding_registry_store`
  - `backend.app.services.learning_registry_store`
  - `backend.app.services.provenance_store`
  - `backend.app.services.training_queue_store`
  - `pathlib`
  - `typing`
- Connected files:
  - `backend/app/services/embedding_registry_store.py`
  - `backend/app/services/learning_registry_store.py`
  - `backend/app/services/provenance_store.py`
  - `backend/app/services/training_queue_store.py`
- Likely dependents:
  - `backend/app/api/routes_learning.py`
  - `backend/app/services/character_learning_adapter.py`
  - `backend/app/services/world_learning_adapter.py`
  - `backend/app/tests/test_character_learning_adapter.py`
  - `backend/app/tests/test_learning_integration.py`
  - `backend/app/tests/test_world_learning_adapter.py`
  - `scripts/smoke_test_chunk2_world_learning_pipeline.py`
  - `scripts/smoke_test_chunk3_character_learning_pipeline.py`
- Related tests:
  - `backend/app/tests/test_learning_integration.py`

### `backend/app/services/provenance_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: provenance_store.py
- Line count: 330
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_learning.py`
  - `backend/app/services/learning_integration.py`
  - `backend/app/tests/test_provenance_store.py`
- Related tests:
  - `backend/app/tests/test_provenance_store.py`

### `backend/app/services/story_dna_seed_service.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: story_dna_seed_service.py
- Line count: 138
- Imports:
  - `backend.app.schemas.story_dna`
  - `typing`
- Connected files:
  - `backend/app/schemas/story_dna.py`
- Likely dependents:
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/services/training_queue_store.py`

- Type: `project_file`
- Status: `active_project_file`
- Purpose: Project file: training_queue_store.py
- Line count: 323
- Imports:
  - `datetime`
  - `json`
  - `pathlib`
  - `typing`
  - `uuid`
- Likely dependents:
  - `backend/app/api/routes_learning.py`
  - `backend/app/services/learning_integration.py`
  - `backend/app/tests/test_training_queue_store.py`
- Related tests:
  - `backend/app/tests/test_training_queue_store.py`

### `backend/app/tests/__init__.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 0
- Related tests:
  - `backend/app/tests/__init__.py`

### `backend/app/tests/test_adaptability_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 315
- Imports:
  - `backend.app.engines.character.adaptability_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/adaptability_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_adaptability_engine.py`

### `backend/app/tests/test_adaptive_story_pattern_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 288
- Imports:
  - `backend.app.engines.story_generation.adaptive_story_pattern_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/adaptive_story_pattern_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_adaptive_story_pattern_engine.py`

### `backend/app/tests/test_artifact_aesthetic_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 125
- Imports:
  - `backend.app.engines.world.artifact_aesthetic_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/artifact_aesthetic_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_artifact_aesthetic_engine.py`

### `backend/app/tests/test_belief_culture_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 122
- Imports:
  - `backend.app.engines.world.belief_culture_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/belief_culture_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_belief_culture_engine.py`

### `backend/app/tests/test_canon_branch_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 134
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_canon_branch_api.py`

### `backend/app/tests/test_causal_continuity_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 283
- Imports:
  - `backend.app.engines.story_generation.causal_continuity_validator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/causal_continuity_validator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_causal_continuity_validator.py`

### `backend/app/tests/test_chapter_expansion_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 224
- Imports:
  - `backend.app.engines.story_generation.chapter_expansion_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/chapter_expansion_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chapter_expansion_engine.py`

### `backend/app/tests/test_chapter_generator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 197
- Imports:
  - `backend.app.engines.story_generation.chapter_generator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/chapter_generator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_chapter_generator.py`

### `backend/app/tests/test_chronology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 143
- Imports:
  - `backend.app.engines.world.chronology_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/chronology_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_chronology_engine.py`

### `backend/app/tests/test_chunk2_smoke_script_exists.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 14
- Imports:
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_chunk2_smoke_script_exists.py`

### `backend/app/tests/test_chunk_1_5_integration_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 16
- Imports:
  - `json`
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_chunk_1_5_integration_verifier.py`

### `backend/app/tests/test_commercial_appeal_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 305
- Imports:
  - `backend.app.engines.story_generation.commercial_appeal_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/commercial_appeal_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_commercial_appeal_engine.py`

### `backend/app/tests/test_consequence_payoff_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 220
- Imports:
  - `backend.app.engines.story_generation.consequence_payoff_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/consequence_payoff_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_consequence_payoff_engine.py`

### `backend/app/tests/test_cross_chunk_readiness_smoke_script_exists.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 11
- Imports:
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_cross_chunk_readiness_smoke_script_exists.py`

### `backend/app/tests/test_cross_chunk_readiness_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 174
- Imports:
  - `backend.app.services.cross_chunk_readiness_verifier`
- Connected files:
  - `backend/app/services/cross_chunk_readiness_verifier.py`
- Related tests:
  - `backend/app/tests/test_cross_chunk_readiness_verifier.py`

### `backend/app/tests/test_dataset_metadata_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 160
- Imports:
  - `backend.app.engines.world.dataset_metadata_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/world/dataset_metadata_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_dataset_metadata_engine.py`

### `backend/app/tests/test_deep_story_readiness_smoke_script_exists.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 11
- Imports:
  - `pathlib`
- Related tests:
  - `backend/app/tests/test_deep_story_readiness_smoke_script_exists.py`

### `backend/app/tests/test_deep_story_readiness_verifier.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 172
- Imports:
  - `backend.app.services.artifact_registry_store`
  - `backend.app.services.character_state_snapshot_store`
  - `backend.app.services.deep_story_readiness_verifier`
  - `backend.app.services.human_review_store`
  - `backend.app.services.world_state_snapshot_service`
- Connected files:
  - `backend/app/services/artifact_registry_store.py`
  - `backend/app/services/character_state_snapshot_store.py`
  - `backend/app/services/deep_story_readiness_verifier.py`
  - `backend/app/services/human_review_store.py`
  - `backend/app/services/world_state_snapshot_service.py`
- Related tests:
  - `backend/app/tests/test_deep_story_readiness_verifier.py`

### `backend/app/tests/test_dialogue_beat_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 199
- Imports:
  - `backend.app.engines.story_generation.dialogue_beat_engine`
  - `backend.app.engines.story_generation.scene_beat_planner`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/dialogue_beat_engine.py`
  - `backend/app/engines/story_generation/scene_beat_planner.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_dialogue_beat_engine.py`

### `backend/app/tests/test_dialogue_line_generator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 223
- Imports:
  - `backend.app.engines.story_generation.dialogue_line_generator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/dialogue_line_generator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_dialogue_line_generator.py`

### `backend/app/tests/test_dialogue_voice_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 383
- Imports:
  - `backend.app.engines.character.dialogue_voice_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/dialogue_voice_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_dialogue_voice_engine.py`

### `backend/app/tests/test_draft_comparison_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 251
- Imports:
  - `backend.app.engines.story_generation.draft_comparison_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/draft_comparison_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_draft_comparison_engine.py`

### `backend/app/tests/test_economy_law_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 120
- Imports:
  - `backend.app.engines.world.economy_law_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/economy_law_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_economy_law_engine.py`

### `backend/app/tests/test_embedding_originality_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 31
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_embedding_originality_api.py`

### `backend/app/tests/test_embedding_originality_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 107
- Imports:
  - `backend.app.engines.world.embedding_originality_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.services.world_run_store`
- Connected files:
  - `backend/app/engines/world/embedding_originality_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/services/world_run_store.py`
- Related tests:
  - `backend/app/tests/test_embedding_originality_engine.py`

### `backend/app/tests/test_engine_contract.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 77
- Imports:
  - `backend.app.engines.foundation.registry_validation_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/foundation/registry_validation_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_engine_contract.py`

### `backend/app/tests/test_export_files.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 163
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
  - `json`
  - `pathlib`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_export_files.py`

### `backend/app/tests/test_format_adapter_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 275
- Imports:
  - `backend.app.engines.story_generation.format_adapter_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/format_adapter_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_format_adapter_engine.py`

### `backend/app/tests/test_game_interactive_scene_formatter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 284
- Imports:
  - `backend.app.engines.story_generation.game_interactive_scene_formatter`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/game_interactive_scene_formatter.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_game_interactive_scene_formatter.py`

### `backend/app/tests/test_generated_scene_delta_extractor.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 147
- Imports:
  - `backend.app.engines.story_generation.generated_scene_delta_extractor`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generated_scene_delta_extractor.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_generated_scene_delta_extractor.py`

### `backend/app/tests/test_generation_improvement_loop.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 280
- Imports:
  - `backend.app.engines.story_generation.generation_improvement_loop`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generation_improvement_loop.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_generation_improvement_loop.py`

### `backend/app/tests/test_geography_environment_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 145
- Imports:
  - `backend.app.engines.world.geography_environment_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/geography_environment_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_geography_environment_engine.py`

### `backend/app/tests/test_goal_motivation_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 306
- Imports:
  - `backend.app.engines.character.goal_motivation_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/goal_motivation_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_goal_motivation_engine.py`

### `backend/app/tests/test_knowledge_boundary_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 264
- Imports:
  - `backend.app.engines.story_generation.knowledge_boundary_validator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/knowledge_boundary_validator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_knowledge_boundary_validator.py`

### `backend/app/tests/test_knowledge_institution_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 127
- Imports:
  - `backend.app.engines.world.knowledge_institution_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/knowledge_institution_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_knowledge_institution_engine.py`

### `backend/app/tests/test_learning_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 335
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_learning_api.py`

### `backend/app/tests/test_learning_feedback_adapter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 230
- Imports:
  - `backend.app.engines.story_generation.learning_feedback_adapter`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/learning_feedback_adapter.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_learning_feedback_adapter.py`

### `backend/app/tests/test_learning_integration.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 255
- Imports:
  - `backend.app.services.learning_integration`
- Connected files:
  - `backend/app/services/learning_integration.py`
- Related tests:
  - `backend/app/tests/test_learning_integration.py`

### `backend/app/tests/test_learning_schemas.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 220
- Imports:
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_learning_schemas.py`

### `backend/app/tests/test_long_form_continuation_anchor.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 225
- Imports:
  - `backend.app.engines.story_generation.long_form_continuation_anchor`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/long_form_continuation_anchor.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_long_form_continuation_anchor.py`

### `backend/app/tests/test_moral_compass_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 278
- Imports:
  - `backend.app.engines.character.moral_compass_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/moral_compass_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_moral_compass_engine.py`

### `backend/app/tests/test_multi_scene_pacing_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 260
- Imports:
  - `backend.app.engines.story_generation.multi_scene_pacing_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/multi_scene_pacing_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_multi_scene_pacing_engine.py`

### `backend/app/tests/test_origin_social_class_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 236
- Imports:
  - `backend.app.engines.character.origin_social_class_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/origin_social_class_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_origin_social_class_engine.py`

### `backend/app/tests/test_originality_copy_risk_guard.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 248
- Imports:
  - `backend.app.engines.story_generation.originality_copy_risk_guard`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/originality_copy_risk_guard.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_originality_copy_risk_guard.py`

### `backend/app/tests/test_pass_e_deep_story_layers.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 164
- Imports:
  - `backend.app.schemas.story_dna`
  - `backend.app.services.character_contrast_matrix_service`
  - `backend.app.services.emotional_resonance_seed_service`
  - `backend.app.services.story_dna_seed_service`
  - `backend.app.services.world_character_pressure_matrix_service`
- Connected files:
  - `backend/app/schemas/story_dna.py`
  - `backend/app/services/character_contrast_matrix_service.py`
  - `backend/app/services/emotional_resonance_seed_service.py`
  - `backend/app/services/story_dna_seed_service.py`
  - `backend/app/services/world_character_pressure_matrix_service.py`
- Related tests:
  - `backend/app/tests/test_pass_e_deep_story_layers.py`

### `backend/app/tests/test_people_type_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 214
- Imports:
  - `backend.app.engines.character.people_type_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/people_type_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_people_type_engine.py`

### `backend/app/tests/test_plot_outline_generator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 244
- Imports:
  - `backend.app.engines.story_generation.plot_outline_generator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/plot_outline_generator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_plot_outline_generator.py`

### `backend/app/tests/test_population_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 168
- Imports:
  - `backend.app.engines.character.population_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/population_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_population_engine.py`

### `backend/app/tests/test_prose_style_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 285
- Imports:
  - `backend.app.engines.story_generation.prose_style_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/prose_style_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_prose_style_engine.py`

### `backend/app/tests/test_provenance_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 181
- Imports:
  - `backend.app.services.provenance_store`
  - `pathlib`
  - `pytest`
- Connected files:
  - `backend/app/services/provenance_store.py`
- Related tests:
  - `backend/app/tests/test_provenance_store.py`

### `backend/app/tests/test_psychology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 285
- Imports:
  - `backend.app.engines.character.psychology_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/psychology_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_psychology_engine.py`

### `backend/app/tests/test_relationship_beat_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 247
- Imports:
  - `backend.app.engines.story_generation.relationship_beat_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/relationship_beat_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_relationship_beat_engine.py`

### `backend/app/tests/test_relationship_readiness_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 405
- Imports:
  - `backend.app.engines.character.relationship_readiness_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/relationship_readiness_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_relationship_readiness_engine.py`

### `backend/app/tests/test_reputation_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 354
- Imports:
  - `backend.app.engines.character.reputation_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/reputation_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_reputation_engine.py`

### `backend/app/tests/test_scene_assembly_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 260
- Imports:
  - `backend.app.engines.story_generation.scene_assembly_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/scene_assembly_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_scene_assembly_engine.py`

### `backend/app/tests/test_scene_beat_planner.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 172
- Imports:
  - `backend.app.engines.story_generation.scene_beat_planner`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/scene_beat_planner.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_scene_beat_planner.py`

### `backend/app/tests/test_scene_blueprint_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 244
- Imports:
  - `backend.app.engines.story_generation.scene_blueprint_engine`
- Connected files:
  - `backend/app/engines/story_generation/scene_blueprint_engine.py`
- Related tests:
  - `backend/app/tests/test_scene_blueprint_engine.py`

### `backend/app/tests/test_scene_draft_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 291
- Imports:
  - `backend.app.engines.story_generation.scene_draft_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/scene_draft_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_scene_draft_engine.py`

### `backend/app/tests/test_scene_quality_gate.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 201
- Imports:
  - `backend.app.engines.story_generation.scene_quality_gate`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/scene_quality_gate.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_scene_quality_gate.py`

### `backend/app/tests/test_screenplay_movie_formatter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 259
- Imports:
  - `backend.app.engines.story_generation.screenplay_movie_formatter`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/screenplay_movie_formatter.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_screenplay_movie_formatter.py`

### `backend/app/tests/test_series_episode_structure_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 199
- Imports:
  - `backend.app.engines.story_generation.series_episode_structure_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/series_episode_structure_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_series_episode_structure_engine.py`

### `backend/app/tests/test_series_season_formatter.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 284
- Imports:
  - `backend.app.engines.story_generation.series_season_formatter`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/series_season_formatter.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_series_season_formatter.py`

### `backend/app/tests/test_skill_ontology_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 264
- Imports:
  - `backend.app.engines.character.skill_ontology_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.learning`
- Connected files:
  - `backend/app/engines/character/skill_ontology_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/learning.py`
- Related tests:
  - `backend/app/tests/test_skill_ontology_engine.py`

### `backend/app/tests/test_skill_power_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 317
- Imports:
  - `backend.app.engines.character.skill_power_engine`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/skill_power_engine.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_skill_power_engine.py`

### `backend/app/tests/test_sqlite_persistence.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 159
- Imports:
  - `backend.app.schemas.foundation`
  - `backend.app.services.foundation_store`
  - `pathlib`
- Connected files:
  - `backend/app/schemas/foundation.py`
  - `backend/app/services/foundation_store.py`
- Related tests:
  - `backend/app/tests/test_sqlite_persistence.py`

### `backend/app/tests/test_story_anti_genericity_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 284
- Imports:
  - `backend.app.engines.story_generation.story_anti_genericity_validator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_anti_genericity_validator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_anti_genericity_validator.py`

### `backend/app/tests/test_story_benchmark_pack.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 218
- Imports:
  - `backend.app.engines.story_generation.story_benchmark_pack`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_benchmark_pack.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_benchmark_pack.py`

### `backend/app/tests/test_story_context_builder.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 233
- Imports:
  - `backend.app.engines.story_generation.generation_contract_resolver`
  - `backend.app.engines.story_generation.generation_mode_controller`
  - `backend.app.engines.story_generation.handoff_package_loader`
  - `backend.app.engines.story_generation.story_context_builder`
  - `backend.app.schemas.simulation`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/generation_contract_resolver.py`
  - `backend/app/engines/story_generation/generation_mode_controller.py`
  - `backend/app/engines/story_generation/handoff_package_loader.py`
  - `backend/app/engines/story_generation/story_context_builder.py`
  - `backend/app/schemas/simulation.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_context_builder.py`

### `backend/app/tests/test_story_continuity_validator.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 336
- Imports:
  - `backend.app.engines.story_generation.story_continuity_validator`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_continuity_validator.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_continuity_validator.py`

### `backend/app/tests/test_story_export_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 197
- Imports:
  - `backend.app.engines.story_generation.story_export_store`
  - `backend.app.schemas.story_generation`
  - `pathlib`
- Connected files:
  - `backend/app/engines/story_generation/story_export_store.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_export_store.py`

### `backend/app/tests/test_story_provenance_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 248
- Imports:
  - `backend.app.engines.story_generation.story_provenance_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_provenance_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_provenance_engine.py`

### `backend/app/tests/test_story_quality_scorer.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 318
- Imports:
  - `backend.app.engines.story_generation.story_quality_scorer`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_quality_scorer.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_quality_scorer.py`

### `backend/app/tests/test_story_revision_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 282
- Imports:
  - `backend.app.engines.story_generation.story_revision_engine`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_revision_engine.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_revision_engine.py`

### `backend/app/tests/test_story_smoke_test.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 166
- Imports:
  - `backend.app.engines.story_generation.story_smoke_test`
  - `backend.app.schemas.story_generation`
- Connected files:
  - `backend/app/engines/story_generation/story_smoke_test.py`
  - `backend/app/schemas/story_generation.py`
- Related tests:
  - `backend/app/tests/test_story_smoke_test.py`

### `backend/app/tests/test_technology_species_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 122
- Imports:
  - `backend.app.engines.world.technology_species_engine`
  - `backend.app.schemas.foundation`
  - `backend.app.schemas.world`
- Connected files:
  - `backend/app/engines/world/technology_species_engine.py`
  - `backend/app/schemas/foundation.py`
  - `backend/app/schemas/world.py`
- Related tests:
  - `backend/app/tests/test_technology_species_engine.py`

### `backend/app/tests/test_tracking_api.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 145
- Imports:
  - `backend.app.main`
  - `fastapi.testclient`
- Connected files:
  - `backend/app/main.py`
- Related tests:
  - `backend/app/tests/test_tracking_api.py`

### `backend/app/tests/test_training_queue_store.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 250
- Imports:
  - `backend.app.services.training_queue_store`
  - `pathlib`
  - `pytest`
- Connected files:
  - `backend/app/services/training_queue_store.py`
- Related tests:
  - `backend/app/tests/test_training_queue_store.py`

### `backend/app/tests/test_trauma_healing_engine.py`

- Type: `test`
- Status: `active_project_file`
- Purpose: Tests related MythOS functionality.
- Line count: 273
- Imports:
  - `backend.app.engines.character.trauma_healing_engine`
  - `backend.app.schemas.character`
  - `backend.app.schemas.foundation`
- Connected files:
  - `backend/app/engines/character/trauma_healing_engine.py`
  - `backend/app/schemas/character.py`
  - `backend/app/schemas/foundation.py`
- Related tests:
  - `backend/app/tests/test_trauma_healing_engine.py`

### `docs/master_project_roadmap_chunks_1_to_9.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 21

### `docs/mythos_file_manifest.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 23014

### `docs/mythos_file_tracker.json`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 10947

### `docs/mythos_file_tracker.md`

- Type: `documentation`
- Status: `active_project_file`
- Purpose: Documentation, roadmap, memory, or tracker file.
- Line count: 7933

### `requirements.txt`

- Type: `dependency_file`
- Status: `active_project_file`
- Purpose: Project file: requirements.txt
- Line count: 23

### `scripts/smoke_test_cross_chunk_readiness.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 118
- Imports:
  - `backend.app.services.cross_chunk_readiness_verifier`
  - `json`
  - `pathlib`
  - `sys`
- Connected files:
  - `backend/app/services/cross_chunk_readiness_verifier.py`

### `scripts/smoke_test_deep_story_readiness.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 120
- Imports:
  - `backend.app.services.deep_story_readiness_verifier`
  - `json`
  - `pathlib`
  - `sys`
- Connected files:
  - `backend/app/services/deep_story_readiness_verifier.py`

### `scripts/update_project_file_tracker.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 328
- Imports:
  - `__future__`
  - `ast`
  - `datetime`
  - `json`
  - `pathlib`

### `scripts/verify_chunk_1_5_integration.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 422
- Imports:
  - `__future__`
  - `backend.app.engines.story_generation.learning_feedback_adapter`
  - `backend.app.engines.story_generation.story_benchmark_pack`
  - `backend.app.engines.story_generation.story_export_store`
  - `backend.app.engines.story_generation.story_generation_orchestrator`
  - `backend.app.engines.story_generation.story_smoke_test`
  - `backend.app.schemas.story_generation`
  - `datetime`
  - `importlib`
  - `json`
  - `os`
  - `pathlib`
  - `subprocess`
  - `sys`
  - `typing`
- Connected files:
  - `backend/app/engines/story_generation/learning_feedback_adapter.py`
  - `backend/app/engines/story_generation/story_benchmark_pack.py`
  - `backend/app/engines/story_generation/story_export_store.py`
  - `backend/app/engines/story_generation/story_generation_orchestrator.py`
  - `backend/app/engines/story_generation/story_smoke_test.py`
  - `backend/app/schemas/story_generation.py`

### `scripts/verify_chunks_1_to_4_integrity.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 315
- Imports:
  - `__future__`
  - `compileall`
  - `importlib`
  - `json`
  - `pathlib`
  - `subprocess`
  - `sys`

### `scripts/verify_main_code_integrity.py`

- Type: `script_or_verifier`
- Status: `active_project_file`
- Purpose: Runs automation, verification, report generation, or tracking.
- Line count: 303
- Imports:
  - `__future__`
  - `ast`
  - `importlib`
  - `json`
  - `pathlib`
  - `subprocess`
  - `sys`
  - `traceback`
  - `typing`
