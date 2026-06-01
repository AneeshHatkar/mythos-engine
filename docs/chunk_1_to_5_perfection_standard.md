# Chunk 1–5 Perfection Standard

## Purpose

This document locks what Chunks 1–5 must guarantee before Chunk 6 begins. The goal is to make the existing system stable, extensible, and ready for deep world simulation without rewriting working code.

## Non-Breaking Rules

- Additive changes only.
- Do not rename existing schema fields.
- Do not remove existing schema fields.
- Do not replace existing engines.
- Do not weaken tests to hide failures.
- Do not start Chunk 6 engine implementation inside the pre-Chunk 6 upgrade.
- Future deep-world systems must enter through bridge packets and story context contracts.

## Required Guarantees

Chunks 1–5 must support:

- Stable foundation contracts.
- Character state and emotional continuity.
- World, society, faction, and institution context.
- Plot causality and memory state updates.
- Story generation, drafting, revision, export, benchmark, smoke-test, and learning feedback loops.
- Deep-world packet hooks for geography, ecology, weather, species, civilizations, settlements, culture, objects, daily life, travel, and secret places.
- Memory update candidates for world state changes.
- Generation hints that allow future engines to influence scenes without hardcoding.

## Perfection Definition

Chunks 1–5 are considered hardened when:

- Existing full test suite passes.
- Future compatibility bridge tests pass.
- Chunk 1–5 perfection verifier passes.
- Pre-Chunk 6 readiness verifier passes.
- README clearly states Chunk 6 is next.
- Master roadmap order is locked.
