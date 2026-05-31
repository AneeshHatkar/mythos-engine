# MythOS Engine

MythOS Engine is a simulation-driven AI/ML story-universe, character, adaptation, franchise, and IP intelligence platform.

It is not a simple prompt-to-story generator. The system is designed as a unified creative intelligence engine where worlds, characters, destinies, emotions, memories, relationships, events, plots, scenes, adaptation reports, and research metrics are represented as structured data.

## Phase 1: Foundation Skeleton

Current milestone:

- FastAPI backend
- Health endpoint
- Root metadata endpoint
- Foundation schemas
- Test setup
- Local venv workflow

## Local Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run Tests

```bash
PYTHONPATH=. pytest backend/app/tests -q
```

## Run Backend

```bash
uvicorn backend.app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```


## Stage 1 Completion Status

Stage 1 is the foundation operating system for MythOS Engine. It includes project management, universe management, registry types, versioning, audit records, feedback records, canon locks, branching timelines, engine contracts, SQLite persistence, and multi-format exports.

### Verified Foundation Workflow

The foundation smoke test validates the following live backend flow:

- Health check
- Project creation
- Universe creation
- Foundation registry seeding
- Canon lock creation
- Branch timeline creation
- Version record creation
- Audit record creation
- Feedback record creation
- JSON export creation
- CSV export creation
- Markdown export creation
- DB snapshot metadata export creation
- Export listing

Run the smoke test with:

```bash
uvicorn backend.app.main:app --reload
```

Then in a second terminal:

```bash
source .venv/bin/activate
python scripts/smoke_test_foundation_api.py
```

Expected final line:

```text
Foundation smoke test passed.
```

---

<<<<<<< HEAD
# Stage 2: World Intelligence Layer

Stage 2 upgrades MythOS Engine from a foundation backend into a full world-generation, world-evaluation, world-persistence, and world-export system.
=======
# Chunk 3: Character Intelligence Layer

Chunk 3 upgrades MythOS Engine from a world-generation platform into a full character-intelligence system. It defines the people who live inside MythOS worlds: their origin, psychology, trauma, memories, goals, morality, skills, adaptability, destiny, relationships, dialogue voice, consistency, originality, quality, persistence, API access, benchmark validation, and Character Bible export.
>>>>>>> 98e65c5 (Update README for Chunk 3 character intelligence layer)

Chunk 3 is designed so characters are not simple archetypes or prompt-generated descriptions. They become structured, inspectable, testable, persistent, exportable, and future-training-ready intelligence objects.

<<<<<<< HEAD
Stage 2 focuses specifically on the **World Intelligence Layer**.
=======
## Chunk 3 Completion Status
>>>>>>> 98e65c5 (Update README for Chunk 3 character intelligence layer)

Chunk 3 implements the first complete version of the **Character Intelligence Layer**.

```text
DONE  3.1   Deep Character Schemas
DONE  3.2   Character Registry Seed Pack
DONE  3.3   Character API + Basic Store Foundation
DONE  3.4   Character Population Engine
DONE  3.5   People Type Engine
DONE  3.6   World-to-Character Constraint Mapper
DONE  3.7   Character Agent State Engine
DONE  3.8   Character Genesis Engine
DONE  3.9   Origin + Social Class Engine
DONE  3.10  Family Foundation Engine
DONE  3.11  Psychology Engine
DONE  3.12  Trauma + Healing Engine
DONE  3.13  Emotion Engine
DONE  3.14  Emotional Arc Engine
DONE  3.15  Memory Engine
DONE  3.16  Skill + Power Engine
DONE  3.17  Skill Ontology Engine
DONE  3.18  Character Type Ontology Engine
DONE  3.19  Adaptability + Limit-Break Engine
DONE  3.20  Destiny / Prophecy / Legacy Engine
DONE  3.21  Relationship Readiness Engine
DONE  3.22  Dialogue Voice / Speech Pattern Engine
DONE  3.23  Character Consistency Validator
DONE  3.24  Character Originality / Similarity Engine
DONE  3.25  Character Quality Scorer
DONE  3.26  Character Full Profile Orchestrator
DONE  3.27  Character Persistence / Run Store
DONE  3.28  Character Engine API Routes
DONE  3.29  Character Benchmark Pack + Smoke Test
DONE  3.30  Character Bible Export Engine
DONE  3.31  README Update + Final Verification
```

## What Chunk 3 Does

Chunk 3 creates a full backend character intelligence pipeline.

The complete Chunk 3 pipeline is:

```text
character seed / world context
→ registry seed
→ population context
→ people type modeling
→ world-character constraints
→ agent state
→ genesis
→ origin and social class
→ family foundation
→ psychology
→ trauma and healing
→ emotion state
→ emotional arc
→ memory
→ skill and power
→ skill ontology
→ character type ontology
→ adaptability / limit-break logic
→ destiny / prophecy / legacy
→ relationship readiness
→ dialogue voice
→ consistency validation
→ originality / similarity scoring
→ quality scoring
→ full profile orchestration
→ persistence
→ API routes
→ benchmark validation
→ Character Bible export
```

The output is a structured `character_full_profile` object that can be inspected, saved, scored, exported, benchmarked, and later used for relationship simulation, plot simulation, RAG retrieval, embeddings, and training workflows.

---

# Character Intelligence Capabilities

Chunk 3 supports deep character modeling across these dimensions:

```text
identity
role
archetype / people type
social class
family name status
origin profile
education access
family foundation
psychological wound
false need
true need
surface goal
hidden goal
morality
forbidden lines
trauma records
healing conditions
emotion state
emotional arc
memory records
skill profile
skill ontology
skill cost
skill counterplay
skill growth
character type ontology
adaptability profile
limit-break conditions
adaptation costs
hard prohibitions
destiny type
prophecy model
legacy pressure
agency conflict
relationship readiness
attachment model
trust model
compatibility vectors
relationship boundaries
dialogue voice
speech rhythm
subtext density
emotional dialogue rules
relationship-specific dialogue variants
forbidden generic dialogue patterns
consistency report
originality report
anti-genericity report
quality score
franchise potential score
full profile orchestration
learning metadata
training eligibility
character bible export
```

---

# Important Chunk 3 Files

```text
backend/app/schemas/character.py

backend/app/engines/character/character_registry_seed.py
backend/app/engines/character/population_engine.py
backend/app/engines/character/people_type_engine.py
backend/app/engines/character/world_character_constraint_engine.py
backend/app/engines/character/character_agent_state_engine.py
backend/app/engines/character/character_genesis_engine.py
backend/app/engines/character/origin_social_class_engine.py
backend/app/engines/character/family_foundation_engine.py
backend/app/engines/character/psychology_engine.py
backend/app/engines/character/trauma_healing_engine.py
backend/app/engines/character/emotion_engine.py
backend/app/engines/character/emotional_arc_engine.py
backend/app/engines/character/memory_engine.py
backend/app/engines/character/skill_power_engine.py
backend/app/engines/character/skill_ontology_engine.py
backend/app/engines/character/character_type_ontology_engine.py
backend/app/engines/character/adaptability_engine.py
backend/app/engines/character/destiny_legacy_engine.py
backend/app/engines/character/relationship_readiness_engine.py
backend/app/engines/character/dialogue_voice_engine.py
backend/app/engines/character/character_consistency_validator.py
backend/app/engines/character/character_originality_engine.py
backend/app/engines/character/character_quality_scorer.py
backend/app/engines/character/character_full_profile_orchestrator.py
backend/app/engines/character/character_bible_export_engine.py

backend/app/services/character_store.py
backend/app/services/character_run_store.py

backend/app/api/routes_characters.py
backend/app/api/routes_character_engines.py

backend/app/benchmarks/character_benchmark_pack.py

scripts/smoke_test_chunk3_character_pipeline.py
```

---

<<<<<<< HEAD
# What Stage 2 Does

Stage 2 creates a complete backend world intelligence pipeline.

The full pipeline is:

```text
template/raw seed
→ identity
→ rules
→ chronology
→ geography/environment/infrastructure
→ demographics/society
→ power/factions/military
→ economy/law
→ belief/culture
→ knowledge/institutions
→ technology/species
→ artifacts/aesthetic
→ civilization pressure/causality
→ quality scoring
→ dataset metadata
→ snapshot/version metadata
→ world bible export
→ persistence
→ embedding-style originality scoring
```

The result is a structured `world_state` object that can be inspected, saved, compared, scored, exported, and later used for training/research workflows.

---

# World Engine API

Stage 2 exposes the world engines through FastAPI.
=======
# Character Engine API

Chunk 3 exposes character engines through FastAPI.
>>>>>>> 98e65c5 (Update README for Chunk 3 character intelligence layer)

## Health

```http
GET /character/engines/health
```

Checks that the character engine API is available.

## Adaptability Engine

```http
POST /character/engines/adaptability
```

Runs the adaptability and limit-break engine.

Returns:

```text
adaptability profile
trigger model
cost model
limit-break rules
adaptation pathways
failure/cost metadata
learning metadata
training eligibility
```

## Destiny Engine

```http
POST /character/engines/destiny
```

Runs destiny, prophecy, legacy, and agency-conflict modeling.

Returns:

```text
destiny profile
prophecy model
legacy model
agency conflict model
destiny burdens
choice/refusal paths
future Chunk 4 and Chunk 8 payloads
```

## Relationship Readiness Engine

```http
POST /character/engines/relationship-readiness
```

Prepares a character for future relationship simulation.

Returns:

```text
relationship readiness profile
relationship hooks
compatibility vectors
attachment and conflict model
boundary model
Chunk 4 relationship simulation payload
learning metadata
```

## Dialogue Voice Engine

```http
POST /character/engines/dialogue-voice
```

Builds character-specific voice and speech-pattern metadata.

Returns:

```text
dialogue voice profile
speech pattern model
emotional dialogue rules
relationship dialogue variants
destiny dialogue layer
forbidden dialogue patterns
future dialogue simulation payload
```

## Consistency Validator

```http
POST /character/engines/consistency-validator
```

Checks cross-engine character consistency.

Validates:

```text
identity consistency
world-origin consistency
family-origin consistency
psychology-goal consistency
morality-goal consistency
memory-psychology consistency
skill-limit consistency
adaptability consistency
destiny-agency consistency
relationship-boundary consistency
dialogue-voice consistency
training metadata readiness
```

Returns:

```text
consistency report
validation checks
repair plan
validator diagnostics
training eligibility
```

## Originality Engine

```http
POST /character/engines/originality
```

Runs deterministic originality and similarity-risk scoring.

Returns:

```text
character originality feature vector
similarity report
originality report
anti-genericity report
originality improvement plan
future embedding upgrade tasks
```

This is intentionally deterministic for Chunk 3. Real embeddings, vector retrieval, nearest-neighbor search, and learned originality scoring belong in Chunk 8.

## Quality Scorer

```http
POST /character/engines/quality-scorer
```

Scores the character across all major quality axes.

Quality axes include:

```text
consistency
originality
world grounding
psychological depth
goal agency
skill integrity
adaptability integrity
destiny agency
relationship readiness
dialogue voice
repair status
```

Returns:

```text
axis scores
overall quality score
quality tier
franchise potential score
readiness report
recommendations
training eligibility
```

## Full Profile Orchestrator

```http
POST /character/engines/full-profile-orchestrator
```

Builds the final `character_full_profile`.

Returns:

```text
character_full_profile
orchestration report
export manifest
missing component report
orchestrator diagnostics
learning metadata
Chunk 4 handoff payload
Chunk 8 training payload
```

Optional persistence:

```json
{
  "persist": true,
  "project_id": "proj_api",
  "universe_id": "velmora_api",
  "payload": {
    "character_seed": {
      "character_id": "char_kael",
      "name": "Kael Veyran"
    }
  }
}
```

---

# Character Store API

## Save Profile

```http
POST /character/engines/save-profile
```

Saves a character profile to the JSON-backed run store.

## Get Profile

```http
GET /character/engines/profiles/{character_id}
```

Loads a stored character profile.

## List Profiles

```http
GET /character/engines/profiles
```

Optional filters:

```text
project_id
universe_id
min_quality_score
```

## List Runs

```http
GET /character/engines/runs
```

Optional filters:

```text
character_id
engine_name
project_id
```

## Store Summary

```http
GET /character/engines/store-summary
```

Returns store-level metadata:

```text
profile count
run count
average quality score
latest character updated timestamp
latest run timestamp
index path
```

---

# Character Persistence

Chunk 3 stores character profiles and engine runs through:

```text
backend/app/services/character_run_store.py
```

The JSON-backed storage location is:

```text
reports/characters/profiles/
reports/characters/runs/
reports/characters/character_index.json
```

Stored character profile records include:

```text
record_id
character_id
project_id
universe_id
created_at
updated_at
profile
orchestration_report
quality_report
learning_metadata
store metadata
```

Stored engine run records include:

```text
run_id
run_label
engine_name
character_id
project_id
universe_id
created_at
input_payload
result_payload
run_metadata
```

This makes generated characters persistent and usable for:

```text
future review
future comparison
future exports
future relationship simulation
future plot simulation
future embeddings
future dataset curation
future training workflows
future audit trails
```

---

# Character Benchmark Pack

Chunk 3 includes a deterministic character benchmark pack:

```text
backend/app/benchmarks/character_benchmark_pack.py
```

Benchmark cases include:

```text
char_bench_hidden_kingmaker
char_bench_institutional_villain
char_bench_independent_love_interest
char_bench_failed_prodigy_rival
char_bench_generic_baseline
```

The benchmark pack checks that the system can handle:

```text
high-quality protagonist construction
institutional villain construction
independent romance-axis character construction
rival construction
generic weak baseline detection
full profile orchestration
quality thresholding
relationship/dialogue readiness
future Chunk 4 payload readiness
future Chunk 8 training metadata readiness
```

---

# Character Bible Export

Chunk 3 adds a structured Character Bible export engine:

```text
backend/app/engines/character/character_bible_export_engine.py
```

The export includes:

```text
identity
one-page summary
origin and world grounding
psychology and goals
morality and memory
skills, power, and adaptability
destiny, prophecy, and legacy
relationship readiness
dialogue voice
validation, quality, and originality
learning and training metadata
Chunk 4 handoff
Chunk 8 handoff
```

The export engine produces:

```text
character_bible
character_bible_markdown
export_report
export_diagnostics
file_outputs
learning_metadata
```

Optional disk export writes:

```text
reports/character_bibles/{character_id}_character_bible.json
reports/character_bibles/{character_id}_character_bible.md
```

Physical PDF/DOCX export is planned for a later export/reporting phase after the whole-project frontend/export system is stable.

---

# Chunk 3 Smoke Test

Run the local Chunk 3 smoke test:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. python scripts/smoke_test_chunk3_character_pipeline.py
```

This runs the benchmark cases through the full profile orchestrator and persists smoke-test profiles.

It writes smoke-test output to:

```text
reports/characters_smoke/chunk3_character_smoke_summary.json
```

API mode is also supported after starting the backend:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --reload
```

Then in a second terminal:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
MYTHOS_CHARACTER_SMOKE_MODE=api PYTHONPATH=. python scripts/smoke_test_chunk3_character_pipeline.py
```

---

# Chunk 3 Test Status

After completing Chunk 3, run:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. pytest backend/app/tests -q
```

Expected final status:

```text
All backend tests passing
Only known non-blocking FastAPI/Starlette TestClient warning may appear
```

Run the character smoke test:

```bash
PYTHONPATH=. python scripts/smoke_test_chunk3_character_pipeline.py
```

Expected final line:

```text
Chunk 3 character pipeline smoke test passed.
```

---

# Dataset, Learning, and Training Direction

Chunk 3 does not perform final model training yet.

Instead, it adds the structure required for safe future training:

```text
ontology records
learned type candidates
provenance records
embedding metadata placeholders
training eligibility
do-not-train flags
source mode
human review requirements
quality scores
originality scores
consistency scores
future retrieval queries
future Chunk 8 training payloads
```

This is intentional. MythOS should not blindly train on generated content. The future ML/RAG layer must use:

```text
licensed datasets
user-owned datasets
human-approved synthetic records
quality-reviewed outputs
deduplicated / originality-checked records
provenance-safe artifacts
```

Actual ML/RAG training, real embeddings, vector databases, retrieval-augmented generation, model registry, and learned scoring belong in Chunk 8.

---

# How MythOS Differs From Simple Story Generators

MythOS Engine is not a basic prompt-to-story tool.

A simple story generator usually works like:

```text
prompt
→ generated text
```

MythOS is being designed as:

```text
world data
→ character intelligence
→ relationship simulation
→ plot causality
→ scene generation
→ adaptation strategy
→ franchise/IP evaluation
→ quality/originality scoring
→ provenance-safe training loops
```

Chunk 3 reinforces this by making characters:

```text
structured
world-grounded
psychologically modeled
relationship-aware
voice-aware
consistency-checked
originality-scored
quality-scored
persistent
exportable
benchmarkable
training-metadata-ready
```

A normal generator might output a character description.

MythOS outputs a character intelligence object with:

```text
why they exist
where they come from
what society allows or blocks
what wound drives them
what false need traps them
what true need changes them
what skill they have
what the skill costs
what counters the skill
what destiny pressures them
where they can refuse destiny
how they build trust
how they betray or repair
how they speak under pressure
why they are not generic
whether they are consistent
whether they are export-ready
whether they are training-eligible
```

---

# What Belongs Later

The following are important but intentionally not completed inside Chunk 3:

```text
real PDF/DOCX physical export
whole-project frontend
real embeddings/vector database
large-scale dataset ingestion
actual ML/RAG training
async job queue
model registry
human feedback dashboard
relationship simulation engine
plot/event/scene engine
```

Planned placement:

```text
Physical PDF/DOCX export       → later export/reporting phase
Frontend                       → later full-project frontend phase
Real embeddings/vector DB       → Chunk 8
Actual ML/RAG training          → Chunk 8
Large-scale dataset ingestion   → Chunk 8
Async job queue                 → production/long-running jobs phase
Relationship simulation         → Chunk 4
Plot/event/scene intelligence   → later story/plot chunks
```

---

# Next Steps After Chunk 3

Before starting Chunk 4, the approved upgrade plan is:

```text
Upgrade Pass A: Chunk 1 global learning schemas + stores
Upgrade Pass B: Chunk 2 world ontology / provenance / learning metadata integration
Upgrade Pass C: Chunk 3 orchestrator integration with learning metadata
Full test suite
Push
Then start Chunk 4
```

Chunk 1 defines the platform foundation.

Chunk 2 defines the worlds.

Chunk 3 defines the characters.

Chunk 4 should focus on relationships, interaction dynamics, ensemble simulation, trust/betrayal, romance/rivalry/family/friendship mechanics, and multi-character story pressure.

---

## Upgrade Pass B — Chunk 2 World Learning Integration

Upgrade Pass B connects the Chunk 2 world intelligence layer to the global learning foundation added in Upgrade Pass A.

This pass does not train real ML models and does not compute real embeddings yet. Instead, it makes world outputs globally registered, provenance-aware, embedding-ready, training-queue-ready, and reusable by later character, relationship, plot, RAG, and training systems.

### Why Upgrade Pass B Exists

Before this pass, Chunk 2 world engines could generate structured world outputs, world bibles, originality checks, and benchmark data.

After this pass, world outputs can flow into the global learning registry, provenance store, embedding registry, training queue, and future Chunk 8 learning/RAG/training pipeline.

### New World Learning Adapter

File:

`backend/app/services/world_learning_adapter.py`

The adapter can normalize world engine results, synthesize missing world learning metadata, register world outputs into global learning stores, build world-to-character dependency contracts, apply world learning quality gates, and block low-quality or unsafe world outputs.

### World-to-Character Dependency Contract

Upgrade Pass B adds a formal contract that tells later chunks what the world requires.

The contract extracts social classes, power laws, legal constraints, faction constraints, education/access constraints, economy/resource constraints, religion/culture constraints, geography/travel constraints, and character permission boundaries.

This ensures Chunk 3 characters, Chunk 4 relationships, and later plot/scene systems obey the world instead of generating disconnected content.

### World Learning Quality Gates

World outputs are checked before they enter the global learning pipeline.

The gate checks source provenance approval, world quality score, world originality score, world consistency score, world-to-character contract usability, training eligibility, human review requirements, and do_not_train flags.

### World Learning Metadata Verifier

File:

`backend/app/services/world_learning_metadata_verifier.py`

The verifier checks whether world outputs contain or can synthesize EngineLearningMetadata-style payloads, ontology records, learned type candidates, provenance records, embedding metadata, training eligibility, world-to-character contract, Chunk 3/4 readiness labels, and future Chunk 8 readiness labels.

### Updated World API Learning Routes

Upgrade Pass B adds safe, backward-compatible learning routes:

`POST /world/engines/learning/register-result`

`POST /world/engines/learning/register-profile`

`POST /world/engines/learning/contract`

These routes do not break older world routes.

### World Run Store Learning Trace Helpers

File updated:

`backend/app/services/world_run_store.py`

The world run store now has helper support for attaching global learning trace data, including learning metadata IDs, provenance IDs, embedding IDs, training queue IDs, learning registration summaries, and world-to-character contracts.

### World Learning Smoke Test

New script:

`scripts/smoke_test_chunk2_world_learning_pipeline.py`

Run it with:

`PYTHONPATH=. python scripts/smoke_test_chunk2_world_learning_pipeline.py`

The smoke test proves that world output normalization, contract creation, metadata verification, global learning registration, provenance storage, embedding registration, and training queue registration work end-to-end.

### Tests Added

Upgrade Pass B adds tests for world learning adapter, world API learning registration, world run store learning trace helpers, world learning metadata verifier, and the Chunk 2 world learning smoke script.

### Upgrade Pass B Verification

Run:

`PYTHONPATH=. pytest backend/app/tests -q`

`PYTHONPATH=. python scripts/smoke_test_chunk2_world_learning_pipeline.py`

### Upgrade Pass B Status

Upgrade Pass B completes the world layer’s global learning integration.

Next:

Upgrade Pass C — Chunk 3 character orchestrator/API/export integration with global learning.

Then Chunk 4 — relationship and ensemble simulation.
