# Chunk 1–5 Deep World Hook Contract

## Purpose

This contract defines how Chunk 6 deep-world systems plug into Chunks 1–5.

Chunk 6 must not bypass the existing story generation pipeline. It must provide structured packets that the Chunk 1–5 bridge converts into story context, generation hints, memory candidates, benchmark expectations, smoke-test expectations, and learning feedback tags.

## Supported Packet Families

- deep_world
- geography
- ecology
- civilization
- species
- culture
- settlement
- object_artifact
- weather
- travel_constraint
- daily_life
- secret_location

## Required Outputs From Future Chunk 6 Engines

Each future Chunk 6 engine should be able to produce packets with:

- packet_id
- packet_type
- title
- summary
- priority
- tags
- references
- metadata

## Story Pipeline Injection Points

Future packets can influence:

- story_context
- scene blueprinting
- dialogue context
- character pressure
- world pressure
- plot causality
- memory updates
- long-form continuity
- benchmark checks
- smoke tests
- learning feedback

## Hard Rule

Chunk 6 must extend the system through the bridge. It must not rewrite Chunk 1–5 engines.
