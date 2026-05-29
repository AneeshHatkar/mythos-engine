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
