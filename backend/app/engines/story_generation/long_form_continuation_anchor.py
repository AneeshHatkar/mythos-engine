from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import GeneratedChapter, LongFormContinuationAnchor


class LongFormContinuationAnchorEngine:
    """Builds continuation anchors for long-form stories.

    This is the bridge from chapter output to future chapters, books, series,
    and long-running story memory. It preserves the active story state so the
    system can continue without forgetting what matters.
    """

    engine_name = "story_generation.long_form_continuation_anchor"

    def build_continuation_anchor(
        self,
        *,
        chapter: GeneratedChapter,
        story_context: Dict[str, Any] | None = None,
        previous_anchor: LongFormContinuationAnchor | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        open_loops = self._merge_open_loops(
            chapter_loops=chapter.open_loops,
            previous_anchor=previous_anchor,
            story_context=story_context,
        )

        anchor = LongFormContinuationAnchor(
            anchor_id=f"continuation_anchor_{chapter.chapter_id}",
            chapter_id=chapter.chapter_id,
            chapter_number=chapter.chapter_number,
            active_character_ids=self._merge_unique(
                chapter.used_character_ids,
                previous_anchor.active_character_ids if previous_anchor else [],
            ),
            active_relationship_ids=self._merge_unique(
                chapter.used_relationship_ids,
                previous_anchor.active_relationship_ids if previous_anchor else [],
            ),
            active_secret_ids=self._merge_unique(
                chapter.used_secret_ids,
                previous_anchor.active_secret_ids if previous_anchor else [],
            ),
            active_causal_ids=self._merge_unique(
                chapter.used_causal_ids,
                previous_anchor.active_causal_ids if previous_anchor else [],
            ),
            active_world_details=self._merge_unique(
                chapter.used_world_details,
                previous_anchor.active_world_details if previous_anchor else [],
            ),
            open_loops=open_loops,
            next_chapter_hooks=self._next_hooks(chapter=chapter, open_loops=open_loops),
            continuity_reminders=self._continuity_reminders(chapter=chapter, open_loops=open_loops),
            memory_update_candidates=self._memory_update_candidates(chapter=chapter, story_context=story_context),
            chapter_summary=self._chapter_summary(chapter=chapter),
            risk_flags=self._risk_flags(chapter=chapter, open_loops=open_loops),
            warnings=self._warnings(chapter=chapter, open_loops=open_loops),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "continuation_anchor": anchor,
            "continuation_anchor_dict": anchor.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.format_adapter_engine",
                "payload_keys": [
                    "continuation_anchor",
                    "generated_chapter",
                    "story_context",
                    "generation_contract",
                ],
            },
        }

    def validate_continuation_anchor(self, *, anchor: LongFormContinuationAnchor) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not anchor.anchor_id:
            blockers.append("anchor_id missing")
        else:
            passed.append("anchor_id_present")

        if not anchor.chapter_id:
            blockers.append("chapter_id missing")
        else:
            passed.append("chapter_id_present")

        if anchor.active_character_ids:
            passed.append("active_characters_present")
        else:
            warnings.append("no active characters in continuation anchor")

        if anchor.open_loops:
            passed.append("open_loops_tracked")
        else:
            warnings.append("no open loops tracked")

        if anchor.next_chapter_hooks:
            passed.append("next_chapter_hooks_present")
        else:
            warnings.append("no next chapter hooks present")

        if anchor.continuity_reminders:
            passed.append("continuity_reminders_present")
        else:
            warnings.append("no continuity reminders present")

        if anchor.risk_flags:
            warnings.extend(anchor.risk_flags)

        if anchor.warnings:
            warnings.extend(anchor.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_anchor(self, *, anchor: LongFormContinuationAnchor) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "anchor_id": anchor.anchor_id,
                "chapter_id": anchor.chapter_id,
                "chapter_number": anchor.chapter_number,
                "active_character_count": len(anchor.active_character_ids),
                "active_relationship_count": len(anchor.active_relationship_ids),
                "active_secret_count": len(anchor.active_secret_ids),
                "active_causal_count": len(anchor.active_causal_ids),
                "active_world_detail_count": len(anchor.active_world_details),
                "open_loop_count": len(anchor.open_loops),
                "next_chapter_hook_count": len(anchor.next_chapter_hooks),
                "memory_update_candidate_count": len(anchor.memory_update_candidates),
                "risk_flag_count": len(anchor.risk_flags),
                "warning_count": len(anchor.warnings),
            },
        }

    def build_next_chapter_seed(self, *, anchor: LongFormContinuationAnchor) -> Dict[str, Any]:
        seed = {
            "next_chapter_seed_id": f"next_chapter_seed_{anchor.chapter_id}",
            "source_anchor_id": anchor.anchor_id,
            "continue_after_chapter": anchor.chapter_number,
            "required_character_ids": anchor.active_character_ids,
            "required_relationship_ids": anchor.active_relationship_ids,
            "required_secret_ids": anchor.active_secret_ids,
            "required_causal_ids": anchor.active_causal_ids,
            "required_world_details": anchor.active_world_details[:10],
            "open_loops_to_address": anchor.open_loops,
            "preferred_hooks": anchor.next_chapter_hooks,
            "continuity_reminders": anchor.continuity_reminders,
            "memory_update_candidates": anchor.memory_update_candidates,
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "next_chapter_seed": seed,
        }

    def _merge_open_loops(
        self,
        *,
        chapter_loops: List[Dict[str, Any]],
        previous_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        loops: List[Dict[str, Any]] = []

        if previous_anchor:
            loops.extend(previous_anchor.open_loops)

        for item in story_context.get("open_loops", []):
            if isinstance(item, dict):
                loops.append(dict(item))

        loops.extend(chapter_loops)

        return self._unique_loops(loops)

    def _next_hooks(self, *, chapter: GeneratedChapter, open_loops: List[Dict[str, Any]]) -> List[str]:
        hooks = list(chapter.next_chapter_hooks)

        for loop in open_loops:
            description = loop.get("description")
            if description:
                hooks.append(description)

        if not hooks:
            hooks.append(f"Continue from chapter {chapter.chapter_number} with a consequence of the last scene.")

        return self._unique(hooks)

    def _continuity_reminders(self, *, chapter: GeneratedChapter, open_loops: List[Dict[str, Any]]) -> List[str]:
        reminders: List[str] = []

        for character_id in chapter.used_character_ids:
            reminders.append(f"Keep {character_id}'s emotional and goal state consistent after {chapter.chapter_id}.")

        for relationship_id in chapter.used_relationship_ids:
            reminders.append(f"Carry forward relationship changes for {relationship_id}.")

        for secret_id in chapter.used_secret_ids:
            reminders.append(f"Do not forget secret pressure around {secret_id}.")

        for causal_id in chapter.used_causal_ids:
            reminders.append(f"Respect causal thread {causal_id} in future scenes.")

        for loop in open_loops[:8]:
            if loop.get("description"):
                reminders.append(f"Open loop still active: {loop['description']}")

        return self._unique(reminders)

    def _memory_update_candidates(
        self,
        *,
        chapter: GeneratedChapter,
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []

        for character_id in chapter.used_character_ids:
            candidates.append(
                {
                    "update_type": "character_progress",
                    "target_id": character_id,
                    "source_chapter_id": chapter.chapter_id,
                    "reason": "Character appeared in generated chapter and may require progress update.",
                }
            )

        for relationship_id in chapter.used_relationship_ids:
            candidates.append(
                {
                    "update_type": "relationship_progress",
                    "target_id": relationship_id,
                    "source_chapter_id": chapter.chapter_id,
                    "reason": "Relationship appeared in generated chapter and may require state update.",
                }
            )

        for secret_id in chapter.used_secret_ids:
            candidates.append(
                {
                    "update_type": "knowledge_or_secret_progress",
                    "target_id": secret_id,
                    "source_chapter_id": chapter.chapter_id,
                    "reason": "Secret pressure appeared and should be tracked.",
                }
            )

        for causal_id in chapter.used_causal_ids:
            candidates.append(
                {
                    "update_type": "causal_progress",
                    "target_id": causal_id,
                    "source_chapter_id": chapter.chapter_id,
                    "reason": "Causal thread appeared and may need consequence tracking.",
                }
            )

        return candidates

    def _chapter_summary(self, *, chapter: GeneratedChapter) -> Dict[str, Any]:
        return {
            "chapter_id": chapter.chapter_id,
            "chapter_number": chapter.chapter_number,
            "title": chapter.title,
            "word_count": len(chapter.chapter_text.split()),
            "scene_count": len(chapter.scene_ids),
            "quality_summary": chapter.quality_summary,
            "scene_ids": chapter.scene_ids,
        }

    def _risk_flags(self, *, chapter: GeneratedChapter, open_loops: List[Dict[str, Any]]) -> List[str]:
        flags: List[str] = []

        if len(open_loops) > 12:
            flags.append("many open loops active; future chapters may become overloaded")

        if chapter.quality_summary.get("failed_scene_count", 0) > 0:
            flags.append("chapter includes scenes that failed quality gate")

        if not chapter.used_causal_ids:
            flags.append("chapter has no causal IDs; long-form continuity may weaken")

        if not chapter.next_chapter_hooks:
            flags.append("chapter has no next-chapter hooks")

        return flags

    def _warnings(self, *, chapter: GeneratedChapter, open_loops: List[Dict[str, Any]]) -> List[str]:
        warnings = list(chapter.warnings)

        if not open_loops:
            warnings.append("No open loops available for long-form continuation.")

        if len(chapter.chapter_text.split()) < 500:
            warnings.append("Chapter is short; long-form continuation may require expansion.")

        return self._unique(warnings)

    def _merge_unique(self, a: List[str], b: List[str]) -> List[str]:
        return self._unique(list(a) + list(b))

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _unique_loops(self, loops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for loop in loops:
            key = loop.get("loop_id") or str(loop)
            if key not in seen:
                seen.add(key)
                result.append(loop)
        return result
