from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    GeneratedChapter,
    LongFormContinuationAnchor,
    LongFormMemoryBridgeReport,
    MultiScenePacingReport,
)


class LongFormMemoryBridge:
    """Converts generated long-form output into structured memory updates.

    This is the bridge between generation and persistent story memory.
    It does not permanently write to a database yet; it creates the clean,
    testable update package that a store/database layer can later persist.
    """

    engine_name = "story_generation.long_form_memory_bridge"

    def build_memory_bridge_report(
        self,
        *,
        source_id: str,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        pacing_report: MultiScenePacingReport | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        character_updates = self._character_memory_updates(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            story_context=story_context,
        )
        relationship_updates = self._relationship_memory_updates(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
        )
        secret_updates = self._secret_memory_updates(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
        )
        causal_updates = self._causal_memory_updates(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            pacing_report=pacing_report,
        )
        world_updates = self._world_memory_updates(chapter=chapter)
        open_loop_updates = self._open_loop_updates(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
        )
        ledger_entries = self._continuity_ledger_entries(
            chapter=chapter,
            character_updates=character_updates,
            relationship_updates=relationship_updates,
            secret_updates=secret_updates,
            causal_updates=causal_updates,
            world_updates=world_updates,
            open_loop_updates=open_loop_updates,
        )

        next_payload = self._next_generation_memory_payload(
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            pacing_report=pacing_report,
            ledger_entries=ledger_entries,
        )

        report = LongFormMemoryBridgeReport(
            memory_bridge_id=f"memory_bridge_{source_id}",
            source_id=source_id,
            chapter_id=chapter.chapter_id,
            character_memory_updates=character_updates,
            relationship_memory_updates=relationship_updates,
            secret_memory_updates=secret_updates,
            causal_memory_updates=causal_updates,
            world_memory_updates=world_updates,
            open_loop_updates=open_loop_updates,
            continuity_ledger_entries=ledger_entries,
            next_generation_memory_payload=next_payload,
            memory_risk_flags=self._memory_risk_flags(
                chapter=chapter,
                continuation_anchor=continuation_anchor,
                pacing_report=pacing_report,
                ledger_entries=ledger_entries,
            ),
            warnings=self._warnings(
                chapter=chapter,
                continuation_anchor=continuation_anchor,
                pacing_report=pacing_report,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "memory_bridge_report": report,
            "memory_bridge_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_memory_store",
                "payload_keys": [
                    "memory_bridge_report",
                    "generated_chapter",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def build_persistence_payload(self, *, report: LongFormMemoryBridgeReport) -> Dict[str, Any]:
        payload = {
            "persistence_payload_id": f"persist_{report.memory_bridge_id}",
            "source_id": report.source_id,
            "chapter_id": report.chapter_id,
            "updates": {
                "characters": report.character_memory_updates,
                "relationships": report.relationship_memory_updates,
                "secrets": report.secret_memory_updates,
                "causal_threads": report.causal_memory_updates,
                "world": report.world_memory_updates,
                "open_loops": report.open_loop_updates,
                "continuity_ledger": report.continuity_ledger_entries,
            },
            "next_generation_memory_payload": report.next_generation_memory_payload,
            "risk_flags": report.memory_risk_flags,
            "warnings": report.warnings,
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "persistence_payload": payload,
        }

    def validate_memory_bridge_report(self, *, report: LongFormMemoryBridgeReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.memory_bridge_id:
            blockers.append("memory_bridge_id missing")
        else:
            passed.append("memory_bridge_id_present")

        if not report.source_id:
            blockers.append("source_id missing")
        else:
            passed.append("source_id_present")

        if report.chapter_id:
            passed.append("chapter_id_present")
        else:
            warnings.append("chapter_id missing")

        if report.continuity_ledger_entries:
            passed.append("continuity_ledger_entries_present")
        else:
            blockers.append("continuity ledger entries missing")

        if report.next_generation_memory_payload:
            passed.append("next_generation_memory_payload_present")
        else:
            blockers.append("next generation memory payload missing")

        if report.character_memory_updates:
            passed.append("character_updates_present")
        else:
            warnings.append("no character memory updates")

        if report.open_loop_updates:
            passed.append("open_loop_updates_present")
        else:
            warnings.append("no open-loop memory updates")

        if report.memory_risk_flags:
            warnings.extend(report.memory_risk_flags)

        if report.warnings:
            warnings.extend(report.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_memory_bridge_report(self, *, report: LongFormMemoryBridgeReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "memory_bridge_id": report.memory_bridge_id,
                "source_id": report.source_id,
                "chapter_id": report.chapter_id,
                "character_update_count": len(report.character_memory_updates),
                "relationship_update_count": len(report.relationship_memory_updates),
                "secret_update_count": len(report.secret_memory_updates),
                "causal_update_count": len(report.causal_memory_updates),
                "world_update_count": len(report.world_memory_updates),
                "open_loop_update_count": len(report.open_loop_updates),
                "ledger_entry_count": len(report.continuity_ledger_entries),
                "risk_flag_count": len(report.memory_risk_flags),
                "warning_count": len(report.warnings),
            },
        }

    def _character_memory_updates(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        character_ids = continuation_anchor.active_character_ids if continuation_anchor else chapter.used_character_ids
        updates: List[Dict[str, Any]] = []

        for character_id in character_ids:
            updates.append(
                {
                    "update_id": f"character_memory_{chapter.chapter_id}_{character_id}",
                    "update_type": "character_progress",
                    "target_id": character_id,
                    "source_chapter_id": chapter.chapter_id,
                    "appeared_in_scene_ids": chapter.scene_ids,
                    "active_relationship_ids": [
                        rid for rid in chapter.used_relationship_ids if character_id.split("_")[-1] in rid
                    ],
                    "active_secret_ids": chapter.used_secret_ids,
                    "active_causal_ids": chapter.used_causal_ids,
                    "progress_note": f"{character_id} must carry forward state from {chapter.chapter_id}.",
                    "next_required_memory": {
                        "preserve_voice": True,
                        "preserve_known_secrets": True,
                        "preserve_emotional_consequences": True,
                    },
                }
            )

        return updates

    def _relationship_memory_updates(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        relationship_ids = continuation_anchor.active_relationship_ids if continuation_anchor else chapter.used_relationship_ids

        return [
            {
                "update_id": f"relationship_memory_{chapter.chapter_id}_{relationship_id}",
                "update_type": "relationship_progress",
                "target_id": relationship_id,
                "source_chapter_id": chapter.chapter_id,
                "active_character_ids": chapter.used_character_ids,
                "change_note": f"{relationship_id} appeared in {chapter.chapter_id}; trust, resentment, repair, and betrayal risk should be re-evaluated.",
                "next_required_memory": {
                    "preserve_trust_delta": True,
                    "preserve_resentment_delta": True,
                    "preserve_unresolved_tension": True,
                },
            }
            for relationship_id in relationship_ids
        ]

    def _secret_memory_updates(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        secret_ids = continuation_anchor.active_secret_ids if continuation_anchor else chapter.used_secret_ids

        updates = []
        for secret_id in secret_ids:
            status = "active"
            if any(secret_id in str(loop) for loop in chapter.open_loops):
                status = "open_loop_active"

            updates.append(
                {
                    "update_id": f"secret_memory_{chapter.chapter_id}_{secret_id}",
                    "update_type": "knowledge_or_secret_progress",
                    "target_id": secret_id,
                    "source_chapter_id": chapter.chapter_id,
                    "status": status,
                    "safe_reveal_required": True,
                    "change_note": f"{secret_id} remains relevant after {chapter.chapter_id}.",
                    "next_required_memory": {
                        "do_not_reveal_without_plan": True,
                        "track_who_knows": True,
                        "track_partial_evidence": True,
                    },
                }
            )

        return updates

    def _causal_memory_updates(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
        pacing_report: MultiScenePacingReport | None,
    ) -> List[Dict[str, Any]]:
        causal_ids = continuation_anchor.active_causal_ids if continuation_anchor else chapter.used_causal_ids
        pacing_score = pacing_report.causal_spacing_score if pacing_report else None

        return [
            {
                "update_id": f"causal_memory_{chapter.chapter_id}_{causal_id}",
                "update_type": "causal_progress",
                "target_id": causal_id,
                "source_chapter_id": chapter.chapter_id,
                "pacing_score": pacing_score,
                "change_note": f"{causal_id} must remain connected to setup, choice, consequence, or payoff.",
                "next_required_memory": {
                    "preserve_cause_effect": True,
                    "track_payoff_status": True,
                    "avoid_orphan_events": True,
                },
            }
            for causal_id in causal_ids
        ]

    def _world_memory_updates(self, *, chapter: GeneratedChapter) -> List[Dict[str, Any]]:
        updates = []

        for detail in chapter.used_world_details:
            updates.append(
                {
                    "update_id": f"world_memory_{chapter.chapter_id}_{self._safe_id(detail)}",
                    "update_type": "world_state_progress",
                    "target_id": detail,
                    "source_chapter_id": chapter.chapter_id,
                    "change_note": f"World detail appeared in {chapter.chapter_id}: {detail}.",
                    "next_required_memory": {
                        "preserve_world_rule": True,
                        "avoid_lore_contradiction": True,
                        "reuse_concretely_when_relevant": True,
                    },
                }
            )

        return updates

    def _open_loop_updates(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        loops = continuation_anchor.open_loops if continuation_anchor else chapter.open_loops
        updates = []

        for loop in loops:
            loop_id = loop.get("loop_id") or f"loop_{len(updates) + 1}"
            updates.append(
                {
                    "update_id": f"open_loop_memory_{chapter.chapter_id}_{loop_id}",
                    "update_type": "open_loop_progress",
                    "target_id": loop_id,
                    "source_chapter_id": chapter.chapter_id,
                    "status": loop.get("status", "open"),
                    "loop_type": loop.get("loop_type"),
                    "description": loop.get("description"),
                    "next_required_memory": {
                        "must_address_or_reinforce": True,
                        "avoid_forgetting": True,
                    },
                }
            )

        return updates

    def _continuity_ledger_entries(
        self,
        *,
        chapter: GeneratedChapter,
        character_updates: List[Dict[str, Any]],
        relationship_updates: List[Dict[str, Any]],
        secret_updates: List[Dict[str, Any]],
        causal_updates: List[Dict[str, Any]],
        world_updates: List[Dict[str, Any]],
        open_loop_updates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []

        for category, updates in [
            ("character", character_updates),
            ("relationship", relationship_updates),
            ("secret", secret_updates),
            ("causal", causal_updates),
            ("world", world_updates),
            ("open_loop", open_loop_updates),
        ]:
            for update in updates:
                entries.append(
                    {
                        "ledger_entry_id": f"ledger_{chapter.chapter_id}_{category}_{update['target_id']}",
                        "category": category,
                        "target_id": update["target_id"],
                        "source_chapter_id": chapter.chapter_id,
                        "update_id": update["update_id"],
                        "memory_priority": self._memory_priority(category=category),
                    }
                )

        return entries

    def _next_generation_memory_payload(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
        pacing_report: MultiScenePacingReport | None,
        ledger_entries: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "memory_payload_id": f"next_memory_payload_{chapter.chapter_id}",
            "source_chapter_id": chapter.chapter_id,
            "required_character_ids": continuation_anchor.active_character_ids if continuation_anchor else chapter.used_character_ids,
            "required_relationship_ids": continuation_anchor.active_relationship_ids if continuation_anchor else chapter.used_relationship_ids,
            "required_secret_ids": continuation_anchor.active_secret_ids if continuation_anchor else chapter.used_secret_ids,
            "required_causal_ids": continuation_anchor.active_causal_ids if continuation_anchor else chapter.used_causal_ids,
            "required_world_details": continuation_anchor.active_world_details if continuation_anchor else chapter.used_world_details,
            "open_loops_to_carry": continuation_anchor.open_loops if continuation_anchor else chapter.open_loops,
            "next_chapter_hooks": continuation_anchor.next_chapter_hooks if continuation_anchor else chapter.next_chapter_hooks,
            "continuity_reminders": continuation_anchor.continuity_reminders if continuation_anchor else [],
            "pacing_report_id": pacing_report.pacing_report_id if pacing_report else None,
            "pacing_repair_targets": pacing_report.pacing_repair_targets if pacing_report else [],
            "ledger_entry_ids": [entry["ledger_entry_id"] for entry in ledger_entries],
        }

    def _memory_risk_flags(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
        pacing_report: MultiScenePacingReport | None,
        ledger_entries: List[Dict[str, Any]],
    ) -> List[str]:
        flags: List[str] = []

        if not chapter.used_character_ids:
            flags.append("chapter has no character IDs for memory update")

        if not chapter.used_causal_ids:
            flags.append("chapter has no causal IDs for memory update")

        if continuation_anchor and continuation_anchor.risk_flags:
            flags.extend(continuation_anchor.risk_flags)

        if pacing_report and pacing_report.overall_pacing_score < 0.60:
            flags.append("pacing score is weak before memory persistence")

        if len(ledger_entries) == 0:
            flags.append("no continuity ledger entries were created")

        return self._unique(flags)

    def _warnings(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
        pacing_report: MultiScenePacingReport | None,
    ) -> List[str]:
        warnings = list(chapter.warnings)

        if continuation_anchor is None:
            warnings.append("No continuation anchor supplied; memory bridge uses chapter-only context.")

        if pacing_report is None:
            warnings.append("No pacing report supplied; memory bridge cannot include pacing repair targets.")

        if len(chapter.chapter_text.split()) < 250:
            warnings.append("Chapter is short; memory update may represent a partial draft.")

        return self._unique(warnings)

    def _memory_priority(self, *, category: str) -> str:
        if category in {"secret", "causal", "open_loop"}:
            return "high"
        if category in {"character", "relationship"}:
            return "medium_high"
        return "medium"

    def _safe_id(self, value: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:60] or "world_detail"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
