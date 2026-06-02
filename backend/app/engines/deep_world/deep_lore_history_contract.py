from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import DeepLoreContract, HistoricalMemoryRecord


class DeepLoreHistoryContractBuilder:
    def build_lore_contract(self, *, source_id: str) -> Dict[str, Any]:
        return {
            "deep_lore_contract": DeepLoreContract(
                lore_contract_id=f"deep_lore_contract_{source_id}",
                source_id=source_id,
            )
        }

    def build_historical_memory_record(
        self,
        *,
        source_id: str,
        event_seed: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event_seed = event_seed or {}

        event_name = event_seed.get("event_name", "The Red Fog Disaster")
        era_name = event_seed.get("era_name", "The Bellfounding Era")

        record = HistoricalMemoryRecord(
            historical_record_id=f"historical_memory_{source_id}_{self._slug(event_name)}",
            source_id=source_id,
            event_name=event_name,
            event_type=event_seed.get("event_type", "regional_disaster"),
            era_name=era_name,
            public_version=event_seed.get(
                "public_version",
                "The city says the disaster was a natural fog surge that killed the old road crews.",
            ),
            secret_version=event_seed.get(
                "secret_version",
                "The fog surge was worsened when magistrates sealed the wrong bell tower to hide a treaty betrayal.",
            ),
            false_version=event_seed.get(
                "false_version",
                "Travel guilds blame forest spirits to protect surviving officials.",
            ),
            who_remembers=event_seed.get("who_remembers", ["bellkeeper families", "route orphans", "old road priests"]),
            who_lies_about_it=event_seed.get("who_lies_about_it", ["Bell Council archivists", "trade guild witnesses"]),
            who_benefits_from_forgetting=event_seed.get("who_benefits_from_forgetting", ["families who inherited sealed road rights"]),
            physical_evidence=event_seed.get("physical_evidence", ["cracked bell tower", "names scratched under salt bark", "sealed road stones"]),
            cultural_aftereffects=event_seed.get("cultural_aftereffects", [
                "bells cannot be rung without witnesses",
                "children learn fog-counting songs before road travel",
            ]),
            character_trauma_hooks=event_seed.get("character_trauma_hooks", [
                "descendants of route orphans distrust official maps",
                "bellkeeper heirs fear public testimony",
            ]),
            plot_conflict_hooks=event_seed.get("plot_conflict_hooks", [
                "finding the sealed road proves the public history is false",
                "a character family name becomes dangerous when the old witness list is found",
            ]),
            memory_state_updates=event_seed.get("memory_state_updates", [
                {
                    "update_type": "historical_truth_state",
                    "target": event_name,
                    "state": "public_false_secret_active",
                }
            ]),
            story_use="Creates buried motive, public lie, secret evidence, and present-day political tension.",
            character_effect="Characters inherit fear, shame, social status, family obligation, or distrust from the event.",
            plot_effect="The event can trigger investigation, betrayal reveal, route discovery, exile, or political collapse.",
            memory_effect="The simulation must remember who knows the public version, secret version, and evidence trail.",
            provenance={
                "generated_by_engine": "DeepLoreHistoryContractBuilder",
                "origin_type": "seeded_historical_memory",
                "source_id": source_id,
                "seed_keys": sorted(event_seed.keys()),
            },
            compression_summary=f"{event_name} during {era_name}: public lie, secret betrayal, physical evidence, present conflict.",
        )

        return {"historical_memory_record": record}

    def validate_historical_record(self, *, record: HistoricalMemoryRecord) -> Dict[str, Any]:
        blockers: List[str] = []
        if not record.public_version:
            blockers.append("Missing public history version.")
        if not record.secret_version:
            blockers.append("Missing secret history version.")
        if not record.physical_evidence:
            blockers.append("Missing physical evidence.")
        if not record.character_trauma_hooks:
            blockers.append("Missing character trauma hooks.")
        if not record.plot_conflict_hooks:
            blockers.append("Missing plot conflict hooks.")
        if not record.memory_state_updates:
            blockers.append("Missing memory state updates.")

        return {
            "passed": not blockers,
            "blockers": blockers,
            "historical_record_id": record.historical_record_id,
            "event_name": record.event_name,
        }

    def build_story_context_patch(self, *, record: HistoricalMemoryRecord) -> Dict[str, Any]:
        return {
            "story_context_patch": {
                "historical_record_id": record.historical_record_id,
                "event_name": record.event_name,
                "era_name": record.era_name,
                "public_version": record.public_version,
                "secret_version": record.secret_version,
                "false_version": record.false_version,
                "who_remembers": record.who_remembers,
                "physical_evidence": record.physical_evidence,
                "character_trauma_hooks": record.character_trauma_hooks,
                "plot_conflict_hooks": record.plot_conflict_hooks,
                "memory_state_updates": record.memory_state_updates,
                "generation_hints": [
                    "Let past events affect present behavior, dialogue, politics, and place atmosphere.",
                    "Do not reveal secret history unless discovery conditions are satisfied.",
                    "Use physical evidence to connect lore to plot action.",
                ],
            }
        }

    def summarize_historical_record(self, *, record: HistoricalMemoryRecord) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "historical_record_id": record.historical_record_id,
                "event_name": record.event_name,
                "era_name": record.era_name,
                "who_remembers_count": len(record.who_remembers),
                "evidence_count": len(record.physical_evidence),
                "plot_hook_count": len(record.plot_conflict_hooks),
                "compression_summary": record.compression_summary,
            },
        }

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)
