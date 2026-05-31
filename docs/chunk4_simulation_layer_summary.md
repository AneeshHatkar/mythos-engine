# Chunk 4 — Interaction Simulation Layer Summary

## Purpose

Chunk 4 is the simulation brain of MythOS Engine. It prepares the story world for actual generation by modeling how characters interact, make choices, trigger consequences, form relationships, carry emotional memory, create conflicts, and change the world state.

## Major systems added

### Simulation schemas

Core simulation schemas define world state, character state, relationship state, knowledge state, events, deltas, and delta batches.

### Relationship and social simulation

Chunk 4 models relationship graphs, relationship ontology, relationship arcs, opposite-nature chemistry, social influence, repair, resentment, betrayal, rivalry, affection, trust, and emotional carryover.

### Knowledge, secrets, evidence, rumors

Characters can know, suspect, hide, reveal, misunderstand, or weaponize secrets and evidence. Rumors can spread and change social perception.

### Promises, leverage, bargains

The system tracks oaths, debts, promises, blackmail, leverage, negotiation, bargains, fulfillment, and betrayal.

### Agency, choice, and consequence

Choices are evaluated for feasibility. Consequences are queued, resolved, and converted into state deltas. This makes decisions matter.

### Causal chain explanation

Simulation outputs can explain why something happened through causal graphs linking choices, events, consequences, and state changes.

### Stakes, tension, conflict

The system scores stakes, builds tension curves, creates conflict records, and checks whether the scene has useful pressure.

### Cast selection

The cast selection engine can choose from user-input characters and project-created characters. It supports large character pools and does not enforce fixed character-count limits.

### Handoff payloads

The handoff engine packages simulation outputs into scene, dialogue, and plot payloads for Chunk 5 generation.

### Genre, adaptation, and learning hooks

The project can prepare format-aware generation controls for novels, chapters, scenes, movies, screenplays, series episodes, season outlines, and more.

### Quality and anti-genericity

The quality scorer checks readiness. The anti-genericity validator catches generic plots, weak characters, vague conflicts, interchangeable relationships, and missing world specificity.

### Store, API routes, benchmark, smoke test

Simulation runs can be stored, bundled, tested through API routes, benchmarked, and smoke-tested.

### Learning metadata

The learning adapter produces safe abstract learning signals. The metadata verifier checks that signals are well-formed, bounded, safe, and complete.

## What this enables in Chunk 5

Chunk 5 can now use validated simulation payloads to generate actual story content:

- scenes
- dialogue
- chapters
- novel prose
- movie beats
- screenplay-style outputs
- series episode outlines
- season arcs
- character-driven story continuations

## Safety and learning rule

Learning metadata is abstract. It should not store raw source text, copyrighted text, or full PDF content. Future PDF/corpus learning should extract safe structural features such as pacing, character arc patterns, dialogue dynamics, and worldbuilding density.
