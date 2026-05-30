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
