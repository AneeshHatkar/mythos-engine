# Chunk 1 to 5 Engine Coverage Matrix

This matrix maps requirements to the chunk that owns them and the future chunk that may extend them.

| Area | Current Owner | Future Extension | Notes |
|---|---|---|---|
| Project foundation | Chunk 1 | Chunks 6 to 9 | Must remain stable. |
| Core schemas | Chunk 1 | Chunks 6 to 9 | Future additions should be additive. |
| Character identity | Chunk 2 | Chunk 6 | Species, culture, and environment hooks connect here. |
| Character emotion | Chunk 2 | Chunk 6 and 7 | Weather, culture, and genre can influence emotion. |
| Relationships | Chunk 2 | Chunk 6 and 7 | Society, culture, and settlement pressures can affect relationships. |
| Agency and motivation | Chunk 2 | Chunk 6 and 7 | Resources, environment, law, and survival can alter goals. |
| World foundations | Chunk 3 | Chunk 6 | Deep world expansion extends this. |
| Factions and society | Chunk 3 | Chunks 6 to 8 | Civilization, culture, legal, and product layers build on this. |
| Law, economy, and belief | Chunk 3 | Chunk 6 and 8 | Daily life and commercial adaptation use these. |
| Plot causality | Chunk 4 | Chunk 6 and 7 | Ecology and world events must affect plot. |
| Memory state | Chunk 4 | Chunk 6 and 9 | Deep world updates and ML feedback connect here. |
| Story context | Chunk 5 | Chunk 6 | Deep world packets enter generation here. |
| Scene and chapter generation | Chunk 5 | Chunk 6 and 7 | Richer world details improve scenes. |
| Revision loop | Chunk 5 | Chunk 7 and 9 | Genre and ML feedback can improve revision. |
| Provenance | Chunk 5 | Chunk 8 and 9 | Legal, IP, and ML audit depend on this. |
| Export store | Chunk 5 | Chunk 8 | Commercial outputs depend on export stability. |
| Benchmark and smoke tests | Chunk 5 | Chunks 6 to 9 | Every future chunk should add benchmarks. |
| Learning feedback | Chunk 5 | Chunk 9 | Dataset and ML training use this. |

## Coverage Decision

Chunks 1 to 5 cover the necessary foundation, character, world, plot, memory, generation, revision, export, benchmark, smoke, and feedback layers. Chunk 6 should extend them through contracts and packets, not replace them.
