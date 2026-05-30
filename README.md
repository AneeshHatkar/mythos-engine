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


## Chunk 1 Completion Status

Chunk 1 is the foundation operating system for MythOS Engine. It includes project management, universe management, registry types, versioning, audit records, feedback records, canon locks, branching timelines, engine contracts, SQLite persistence, and multi-format exports.

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

# Chunk 2: World Intelligence Layer

Chunk 2 upgrades MythOS Engine from a foundation backend into a full world-generation, world-evaluation, world-persistence, and world-export system.

MythOS Engine is not a simple prompt-to-story generator. It is being built as a research-grade creative intelligence platform where worlds, characters, plots, adaptations, franchises, and IP systems become structured, inspectable, persistent, testable data objects.

Chunk 2 focuses specifically on the **World Intelligence Layer**.

It can create worlds with:

```text
identity
world DNA
scale
rules
boundaries
contradiction intent
chronology
historical wounds
memory archives
geography
environment
infrastructure
demographics
society
class hierarchy
power structures
factions
military/security
economy
resources
law/justice
religion
belief
philosophy
myth
culture
language/naming
rituals
knowledge control
education
institutions
technology
magic
science
species
creatures
artifacts
symbolic objects
aesthetic/sensory texture
civilization pressure
causality graph
quality scoring
dataset metadata
training-readiness metadata
world snapshots
world version metadata
world bible export
database persistence
embedding-style originality scoring
```

## Current Test Status

Current verified test result:

```text
162 passed, 1 warning
```

The warning is from FastAPI/Starlette TestClient dependency behavior and does not currently affect project correctness.

Run tests with:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. pytest backend/app/tests -q
```

---

# Chunk 2 Milestone Completion

```text
DONE  2.1   Deep World Schemas
DONE  2.2   World API + Persistence
DONE  2.3   World Identity + DNA + Scale/Granularity Engine
DONE  2.4   World Rules + Boundaries + Contradiction Intent Engine
DONE  2.5   Chronology + Historical Wounds + World Memory Engine
DONE  2.6   Geography + Environment + Infrastructure Engine
DONE  2.7   Demographics + Society + Class/Hierarchy Engine
DONE  2.8   Power Structures + Factions + Military/Security Engine
DONE  2.9   Economy + Resources + Law/Justice Engine
DONE  2.10  Belief + Culture + Myth + Ritual Engine
DONE  2.11  Knowledge + Education + Institutions Engine
DONE  2.12  Technology/Magic/Science + Species/Creatures Engine
DONE  2.13  Artifacts + Symbolic Objects + Aesthetic/Sensory Texture Engine
DONE  2.14  Civilization Pressure + World Evolution + Causality Graph Engine
DONE  2.15  Consistency + Originality + Story Potential Scorer
DONE  2.16  Dataset Tagging + Training-Readiness Metadata Engine
DONE  2.17  World Template / Preset System
DONE  2.18  World Diff / Comparison System
DONE  2.19  World Snapshot / Version Integration
DONE  2.20  World Bible Export Engine
DONE  2.21  World Orchestrator Engine
DONE  2.22  Engine API + Audit Integration
DONE  2.23  World Quality Benchmark Pack
DONE  2.24  World Smoke Test Script
DONE  2.25A Orchestrated World Persistence
DONE  2.25B Embedding-Style Originality Similarity Engine
DONE  2.25C README Update + Final Chunk 2 Push
```

---

# What Chunk 2 Does

Chunk 2 creates a complete backend world intelligence pipeline.

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

Chunk 2 exposes the world engines through FastAPI.

## Health

```http
GET /world/engines/health
```

Checks that the world engine API is available.

## Templates

```http
GET /world/engines/templates
```

Returns available world templates.

## Full World Orchestration

```http
POST /world/engines/orchestrate
```

Runs the complete Chunk 2 world pipeline.

The orchestration response includes:

```text
world_state
orchestration_summary
engine_runs
quality_summary
dataset_metadata
snapshot
world_bible_export
audit_integration
persistence
```

## Quality Scoring

```http
POST /world/engines/quality
```

Runs the world quality engine and returns:

```text
consistency score
originality score
story potential score
franchise potential score
genericness risk score
training readiness score
missing systems
contradiction risks
improvement plan
```

## Embedding-Style Originality Scoring

```http
POST /world/engines/originality
```

Runs deterministic embedding-style originality scoring.

This compares a candidate world against stored world-generation runs and returns:

```text
originality score
nearest similarity
duplicate risk
nearest saved worlds
shared high-signal terms
training recommendation
```

This is not full ML embeddings yet. It is a safe Chunk 2 version that prepares the project for real vector embeddings in Chunk 8.

## Stored World Runs

```http
GET /world/engines/runs
```

Lists stored world-generation runs.

Supports optional filters:

```text
project_id
universe_id
template_id
limit
```

## Get Stored World Run

```http
GET /world/engines/runs/{run_id}
```

Returns a saved world-generation run, including world state, quality summary, dataset metadata, snapshot, world bible export metadata, and audit metadata.

---

# Available World Templates

Chunk 2 includes these templates:

```text
dark_academy_empire
civilization_simulation
dystopian_megacity
romance_kingdom
mythic_religious_world
movie_scale_world
seven_novel_saga
```

Templates are configuration presets. They are not hardcoded stories.

They help make generation:

```text
more controllable
more benchmarkable
less generic
easier to compare
easier to test
better for future model conditioning
```

---

# Example Orchestration Request

Send this JSON to:

```http
POST /world/engines/orchestrate
```

```json
{
  "template_id": "seven_novel_saga",
  "world_name": "Velmora",
  "seed_premise": "Velmora is a late imperial collapse world where noble academies, relic mines, oath law, sealed archives, family-name trust, class hierarchy, forbidden exams, and 27 destiny-bearing students destabilize civilization.",
  "user_rating": 9,
  "source_mode": "human_approved_synthetic",
  "export_format": "markdown_and_json",
  "audience": "internal_research_and_development"
}
```

---

# Running the Backend

From the project root:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

---

# Running Chunk 2 Smoke Test

Start the backend first:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
PYTHONPATH=. uvicorn backend.app.main:app --reload
```

Then open a second terminal and run:

```bash
cd ~/Desktop/mythos-engine
source .venv/bin/activate
python scripts/smoke_test_chunk2_world_pipeline.py
```

The smoke test checks:

```text
world engine API health
template catalog
full world orchestration
quality summary
dataset metadata
snapshot metadata
world bible export
quality endpoint audit metadata
markdown export creation
JSON export creation
```

It writes sample smoke-test exports to:

```text
exports/world_bibles/chunk2_smoke_test_world_bible.md
exports/world_bibles/chunk2_smoke_test_world_bible.json
```

---

# World Persistence

Chunk 2 now stores orchestrated world runs in SQLite through:

```text
backend/app/services/world_run_store.py
```

Stored world-generation runs include:

```text
run_id
project_id
universe_id
world_name
template_id
seed_premise
status
quality_tier
training_eligible
do_not_train
snapshot_id
export_id
world_state_json
orchestration_summary_json
quality_summary_json
dataset_metadata_json
snapshot_json
world_bible_export_json
audit_metadata_json
created_at
```

This makes generated worlds persistent and usable for:

```text
future review
future comparison
future exports
future embeddings
future dataset curation
future training workflows
future audit trails
```

---

# Embedding-Style Originality Scoring

Chunk 2 includes a deterministic embedding-style originality engine:

```text
backend/app/engines/world/embedding_originality_engine.py
```

It performs weighted vector similarity over world text and compares a candidate world against stored world runs.

It returns:

```text
originality_score
nearest_similarity
duplicate_risk
detail_density
motif_diversity
unique_signal_terms
nearest_saved_worlds
training_recommendation
```

Risk tiers include:

```text
low_overlap
medium_overlap
high_overlap
near_duplicate
```

Training recommendations include:

```text
training_candidate_after_review
revise_before_training
needs_more_comparison_data
block_training_until_deduplicated
```

This is intentionally lightweight for Chunk 2. Real embeddings, vector databases, RAG retrieval, clustering, and learned originality scoring belong in Chunk 8.

---

# World Bible Export

The World Bible Export Engine produces export-ready payloads:

```text
world_bible_markdown
world_bible_json
executive summary
section completeness report
quality summary
dataset metadata summary
snapshot metadata
export readiness score
```

Physical PDF/DOCX export is planned for a later export/reporting phase.

---

# Dataset and Training Safety

Chunk 2 does not train models.

Instead, it prepares the future training pipeline safely with:

```text
quality scores
dataset tags
risk tags
human-review requirements
training eligibility flags
do-not-train flags
source/provenance metadata
benchmark labels
snapshot/version metadata
originality similarity checks
duplicate risk checks
```

This is intentional. MythOS should not blindly learn from generated content. Future ML/RAG training should only use curated, high-quality, reviewed, provenance-safe samples.

Actual ML/RAG training is planned for Chunk 8 and is considered a major project milestone.

---

# Benchmark Pack

Chunk 2 includes a world benchmark engine:

```text
backend/app/engines/world/world_benchmark_engine.py
```

It checks multiple world types:

```text
dark academy empire
civilization simulation
dystopian megacity
romance kingdom
mythic religious world
movie-scale world
seven-novel saga
```

This ensures the system is not overfit to one world like Velmora.

---

# Important Chunk 2 Files

```text
backend/app/schemas/world.py
backend/app/services/world_store.py
backend/app/services/world_run_store.py
backend/app/api/routes_world.py
backend/app/api/routes_world_engines.py

backend/app/engines/world/world_identity_engine.py
backend/app/engines/world/world_rules_engine.py
backend/app/engines/world/chronology_engine.py
backend/app/engines/world/geography_environment_engine.py
backend/app/engines/world/demographics_society_engine.py
backend/app/engines/world/power_faction_military_engine.py
backend/app/engines/world/economy_law_engine.py
backend/app/engines/world/belief_culture_engine.py
backend/app/engines/world/knowledge_institution_engine.py
backend/app/engines/world/technology_species_engine.py
backend/app/engines/world/artifact_aesthetic_engine.py
backend/app/engines/world/civilization_pressure_engine.py
backend/app/engines/world/world_quality_engine.py
backend/app/engines/world/dataset_metadata_engine.py
backend/app/engines/world/world_template_engine.py
backend/app/engines/world/world_diff_engine.py
backend/app/engines/world/world_snapshot_engine.py
backend/app/engines/world/world_bible_export_engine.py
backend/app/engines/world/world_orchestrator_engine.py
backend/app/engines/world/world_benchmark_engine.py
backend/app/engines/world/embedding_originality_engine.py

scripts/smoke_test_chunk2_world_pipeline.py
```

---

# What Belongs Later

The following are important, but intentionally not part of Chunk 2 final implementation:

```text
PDF/DOCX physical export
whole-project frontend
actual ML/RAG training
real embeddings/vector database
async job queue
large-scale dataset ingestion
model registry
long-running generation jobs
```

Planned placement:

```text
PDF/DOCX export           → later export/reporting phase
Frontend                  → later full-project frontend phase
ML/RAG training            → Chunk 8
Real embeddings/vector DB  → Chunk 8
Async job queue            → later production/long-running jobs phase
```

---

# Next Chunk: Character Intelligence Layer

Chunk 3 should focus on the people living inside the generated worlds.

Planned Chunk 3 direction:

```text
character identity
personality
psychology
trauma
goals
fears
flaws
desires
voice
agency
skills
social class
education background
family pressure
destiny relationship
moral logic
relationships to world systems
character growth arcs
character quality scoring
character orchestration
character API
character smoke test
```

Chunk 2 defines the world.

Chunk 3 defines the people who live, break, love, betray, grow, and change inside that world.
