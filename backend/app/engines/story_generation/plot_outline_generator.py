from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
)


class PlotOutlineGenerator:
    """Builds structured plot outlines from generated story material.

    This is the locked 5.24 step. It turns scenes/chapters/continuity anchors
    into a reusable outline that future formatters, revision engines, memory
    systems, and long-form generators can follow.
    """

    engine_name = "story_generation.plot_outline_generator"

    def generate_plot_outline(
        self,
        *,
        source_id: str,
        title: str | None = None,
        chapters: List[GeneratedChapter] | None = None,
        assembled_scenes: List[AssembledScene] | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        story_context: Dict[str, Any] | None = None,
        outline_format: str = "chapter_outline",
    ) -> Dict[str, Any]:
        chapters = chapters or []
        assembled_scenes = assembled_scenes or []
        story_context = story_context or {}

        premise = self._premise(
            title=title,
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
            story_context=story_context,
        )
        scene_sequence = self._scene_sequence(chapters=chapters, assembled_scenes=assembled_scenes)
        act_structure = self._act_structure(scene_sequence=scene_sequence, chapters=chapters, story_context=story_context)
        turning_points = self._major_turning_points(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )

        character_threads = self._character_arc_threads(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        relationship_threads = self._relationship_arc_threads(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        secret_threads = self._secret_threads(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        causal_threads = self._causal_threads(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        world_threads = self._world_state_threads(
            chapters=chapters,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        open_loops = self._open_loops(chapters=chapters, continuation_anchor=continuation_anchor)
        payoff_setups = self._payoff_setups(
            secret_threads=secret_threads,
            causal_threads=causal_threads,
            relationship_threads=relationship_threads,
            open_loops=open_loops,
        )

        outline = PlotOutline(
            outline_id=f"plot_outline_{source_id}",
            source_id=source_id,
            title=title or self._title_from_sources(chapters=chapters, story_context=story_context),
            outline_format=outline_format,
            premise=premise,
            act_structure=act_structure,
            scene_sequence=scene_sequence,
            major_turning_points=turning_points,
            character_arc_threads=character_threads,
            relationship_arc_threads=relationship_threads,
            secret_threads=secret_threads,
            causal_threads=causal_threads,
            world_state_threads=world_threads,
            open_loops=open_loops,
            payoff_setups=payoff_setups,
            next_outline_hooks=self._next_outline_hooks(chapters=chapters, continuation_anchor=continuation_anchor, open_loops=open_loops),
            continuity_requirements=self._continuity_requirements(
                character_threads=character_threads,
                relationship_threads=relationship_threads,
                secret_threads=secret_threads,
                causal_threads=causal_threads,
                world_threads=world_threads,
                open_loops=open_loops,
            ),
            warnings=self._warnings(
                chapters=chapters,
                assembled_scenes=assembled_scenes,
                act_structure=act_structure,
                scene_sequence=scene_sequence,
                character_threads=character_threads,
                causal_threads=causal_threads,
                open_loops=open_loops,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "plot_outline": outline,
            "plot_outline_dict": outline.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.long_form_continuation_anchor",
                "payload_keys": [
                    "plot_outline",
                    "generated_chapters",
                    "assembled_scenes",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def build_outline_text(self, *, outline: PlotOutline) -> Dict[str, Any]:
        lines = [
            f"# {outline.title or outline.outline_id}",
            "",
            "## Premise",
            outline.premise,
            "",
            "## Act Structure",
        ]

        for act in outline.act_structure:
            lines.append(f"### Act {act.get('act_number')}: {act.get('act_purpose')}")
            lines.append(act.get("description", ""))

        lines.append("")
        lines.append("## Scene Sequence")
        for scene in outline.scene_sequence:
            lines.append(f"- {scene.get('sequence_index')}. {scene.get('scene_id')}: {scene.get('purpose')}")

        lines.append("")
        lines.append("## Major Turning Points")
        for turn in outline.major_turning_points:
            lines.append(f"- {turn.get('turning_point_type')}: {turn.get('description')}")

        lines.append("")
        lines.append("## Open Loops")
        for loop in outline.open_loops:
            lines.append(f"- {loop.get('loop_id')}: {loop.get('description')}")

        lines.append("")
        lines.append("## Payoff Setups")
        for payoff in outline.payoff_setups:
            lines.append(f"- {payoff.get('payoff_id')}: {payoff.get('description')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "outline_text": "\n".join(lines),
        }

    def validate_plot_outline(self, *, outline: PlotOutline) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not outline.outline_id:
            blockers.append("outline_id missing")
        else:
            passed.append("outline_id_present")

        if not outline.source_id:
            blockers.append("source_id missing")
        else:
            passed.append("source_id_present")

        if outline.premise:
            passed.append("premise_present")
        else:
            warnings.append("premise missing")

        if outline.act_structure:
            passed.append("act_structure_present")
        else:
            blockers.append("act structure missing")

        if outline.scene_sequence:
            passed.append("scene_sequence_present")
        else:
            blockers.append("scene sequence missing")

        if outline.major_turning_points:
            passed.append("turning_points_present")
        else:
            warnings.append("major turning points missing")

        if outline.character_arc_threads:
            passed.append("character_arc_threads_present")
        else:
            warnings.append("character arc threads missing")

        if outline.causal_threads:
            passed.append("causal_threads_present")
        else:
            warnings.append("causal threads missing")

        if outline.continuity_requirements:
            passed.append("continuity_requirements_present")
        else:
            warnings.append("continuity requirements missing")

        if outline.warnings:
            warnings.extend(outline.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_plot_outline(self, *, outline: PlotOutline) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "outline_id": outline.outline_id,
                "source_id": outline.source_id,
                "title": outline.title,
                "outline_format": outline.outline_format,
                "act_count": len(outline.act_structure),
                "scene_count": len(outline.scene_sequence),
                "turning_point_count": len(outline.major_turning_points),
                "character_thread_count": len(outline.character_arc_threads),
                "relationship_thread_count": len(outline.relationship_arc_threads),
                "secret_thread_count": len(outline.secret_threads),
                "causal_thread_count": len(outline.causal_threads),
                "world_thread_count": len(outline.world_state_threads),
                "open_loop_count": len(outline.open_loops),
                "payoff_setup_count": len(outline.payoff_setups),
                "warning_count": len(outline.warnings),
            },
        }

    def _premise(
        self,
        *,
        title: str | None,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> str:
        if story_context.get("premise"):
            return str(story_context["premise"])

        if chapters:
            first = chapters[0]
            hook = first.next_chapter_hooks[0] if first.next_chapter_hooks else "an unresolved consequence"
            return f"{title or first.title or 'The story'} follows {', '.join(first.used_character_ids[:3])} as {hook}"

        if assembled_scenes:
            first_scene = assembled_scenes[0]
            objective = first_scene.continuity_trace.get("scene_objective") or "a central conflict escalates"
            return f"{title or first_scene.title or 'The story'} begins with {objective}."

        if continuation_anchor:
            hook = continuation_anchor.next_chapter_hooks[0] if continuation_anchor.next_chapter_hooks else "open loops"
            return f"The story continues from {continuation_anchor.chapter_id}, driven by {hook}."

        return title or "A structured story outline built from available generation context."

    def _scene_sequence(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
    ) -> List[Dict[str, Any]]:
        sequence: List[Dict[str, Any]] = []

        for chapter in chapters:
            for index, section in enumerate(chapter.sections, start=1):
                scene_id = section.get("scene_id") or f"{chapter.chapter_id}_section_{index}"
                sequence.append(
                    {
                        "sequence_index": len(sequence) + 1,
                        "chapter_id": chapter.chapter_id,
                        "scene_id": scene_id,
                        "source_type": "chapter_section",
                        "purpose": section.get("title") or section.get("scene_objective") or "Continue chapter plot pressure.",
                        "used_character_ids": section.get("used_character_ids", chapter.used_character_ids),
                        "used_secret_ids": section.get("used_secret_ids", chapter.used_secret_ids),
                        "used_causal_ids": section.get("used_causal_ids", chapter.used_causal_ids),
                        "used_world_details": section.get("used_world_details", chapter.used_world_details),
                    }
                )

            if not chapter.sections:
                for scene_id in chapter.scene_ids:
                    sequence.append(
                        {
                            "sequence_index": len(sequence) + 1,
                            "chapter_id": chapter.chapter_id,
                            "scene_id": scene_id,
                            "source_type": "chapter_scene_id",
                            "purpose": "Represent chapter scene in outline sequence.",
                            "used_character_ids": chapter.used_character_ids,
                            "used_secret_ids": chapter.used_secret_ids,
                            "used_causal_ids": chapter.used_causal_ids,
                            "used_world_details": chapter.used_world_details,
                        }
                    )

        for scene in assembled_scenes:
            if any(item.get("scene_id") == scene.scene_id for item in sequence):
                continue
            sequence.append(
                {
                    "sequence_index": len(sequence) + 1,
                    "chapter_id": None,
                    "scene_id": scene.scene_id,
                    "source_type": "assembled_scene",
                    "purpose": scene.continuity_trace.get("scene_objective") or scene.title or "Scene pressure continues.",
                    "used_character_ids": scene.used_character_ids,
                    "used_secret_ids": scene.used_secret_ids,
                    "used_causal_ids": scene.used_causal_ids,
                    "used_world_details": scene.used_world_details,
                }
            )

        return sequence

    def _act_structure(
        self,
        *,
        scene_sequence: List[Dict[str, Any]],
        chapters: List[GeneratedChapter],
        story_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        if story_context.get("act_structure") and isinstance(story_context["act_structure"], list):
            return story_context["act_structure"]

        if not scene_sequence:
            return []

        act_count = 3
        if len(scene_sequence) >= 8:
            act_count = 4

        acts = []
        purposes = [
            "Setup the central conflict, world pressure, and active character goals.",
            "Complicate the conflict through secrets, relationships, reversals, or failed choices.",
            "Force consequences, payoff setup, and a hook into the next long-form unit.",
            "Escalate into a larger arc turn or season/book-level cliffhanger.",
        ]

        for act_number in range(1, act_count + 1):
            start_idx = int((act_number - 1) * len(scene_sequence) / act_count)
            end_idx = int(act_number * len(scene_sequence) / act_count)
            assigned = scene_sequence[start_idx:end_idx] or scene_sequence[-1:]

            acts.append(
                {
                    "act_number": act_number,
                    "act_purpose": purposes[act_number - 1],
                    "description": f"Act {act_number} covers scenes {assigned[0]['scene_id']} through {assigned[-1]['scene_id']}.",
                    "scene_ids": [item["scene_id"] for item in assigned],
                    "turn_requirement": "increase pressure or change the story state",
                }
            )

        return acts

    def _major_turning_points(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        turns: List[Dict[str, Any]] = []

        for chapter in chapters:
            for hook in chapter.next_chapter_hooks:
                turns.append(
                    {
                        "turning_point_id": f"turn_{chapter.chapter_id}_{len(turns) + 1}",
                        "turning_point_type": "chapter_hook",
                        "source_id": chapter.chapter_id,
                        "description": hook,
                    }
                )

            for loop in chapter.open_loops:
                if loop.get("description"):
                    turns.append(
                        {
                            "turning_point_id": f"turn_{chapter.chapter_id}_{loop.get('loop_id', len(turns) + 1)}",
                            "turning_point_type": loop.get("loop_type", "open_loop"),
                            "source_id": chapter.chapter_id,
                            "description": loop["description"],
                        }
                    )

        for scene in assembled_scenes:
            hook = scene.continuity_trace.get("ending_hook")
            if hook:
                turns.append(
                    {
                        "turning_point_id": f"turn_{scene.scene_id}_ending_hook",
                        "turning_point_type": "scene_ending_hook",
                        "source_id": scene.scene_id,
                        "description": hook,
                    }
                )

        if continuation_anchor:
            for hook in continuation_anchor.next_chapter_hooks:
                turns.append(
                    {
                        "turning_point_id": f"turn_{continuation_anchor.anchor_id}_{len(turns) + 1}",
                        "turning_point_type": "continuation_hook",
                        "source_id": continuation_anchor.anchor_id,
                        "description": hook,
                    }
                )

        return self._unique_dicts(turns, key="turning_point_id")

    def _character_arc_threads(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        character_ids: List[str] = []
        for chapter in chapters:
            character_ids.extend(chapter.used_character_ids)
        for scene in assembled_scenes:
            character_ids.extend(scene.used_character_ids)
        if continuation_anchor:
            character_ids.extend(continuation_anchor.active_character_ids)

        return [
            {
                "thread_id": f"character_arc_{character_id}",
                "character_id": character_id,
                "thread_type": "character_arc",
                "description": f"Track {character_id}'s goal, emotion, knowledge, voice, and consequence state across the outline.",
                "required_in_future": True,
            }
            for character_id in self._unique(character_ids)
        ]

    def _relationship_arc_threads(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        relationship_ids: List[str] = []
        for chapter in chapters:
            relationship_ids.extend(chapter.used_relationship_ids)
        for scene in assembled_scenes:
            relationship_ids.extend(scene.used_relationship_ids)
        if continuation_anchor:
            relationship_ids.extend(continuation_anchor.active_relationship_ids)

        return [
            {
                "thread_id": f"relationship_arc_{relationship_id}",
                "relationship_id": relationship_id,
                "thread_type": "relationship_arc",
                "description": f"Track trust, resentment, betrayal risk, repair potential, and emotional pressure for {relationship_id}.",
                "required_in_future": True,
            }
            for relationship_id in self._unique(relationship_ids)
        ]

    def _secret_threads(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        secret_ids: List[str] = []
        for chapter in chapters:
            secret_ids.extend(chapter.used_secret_ids)
        for scene in assembled_scenes:
            secret_ids.extend(scene.used_secret_ids)
        if continuation_anchor:
            secret_ids.extend(continuation_anchor.active_secret_ids)

        return [
            {
                "thread_id": f"secret_thread_{secret_id}",
                "secret_id": secret_id,
                "thread_type": "secret_or_mystery",
                "description": f"Control reveal timing, partial evidence, misdirection, and who-knows-what for {secret_id}.",
                "reveal_status": "active",
            }
            for secret_id in self._unique(secret_ids)
        ]

    def _causal_threads(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        causal_ids: List[str] = []
        for chapter in chapters:
            causal_ids.extend(chapter.used_causal_ids)
        for scene in assembled_scenes:
            causal_ids.extend(scene.used_causal_ids)
        if continuation_anchor:
            causal_ids.extend(continuation_anchor.active_causal_ids)

        return [
            {
                "thread_id": f"causal_thread_{causal_id}",
                "causal_id": causal_id,
                "thread_type": "cause_effect_or_payoff",
                "description": f"Preserve setup, choice, consequence, and payoff chain for {causal_id}.",
                "payoff_required": causal_id.startswith("cause_"),
            }
            for causal_id in self._unique(causal_ids)
        ]

    def _world_state_threads(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        details: List[str] = []
        for chapter in chapters:
            details.extend(chapter.used_world_details)
        for scene in assembled_scenes:
            details.extend(scene.used_world_details)
        if continuation_anchor:
            details.extend(continuation_anchor.active_world_details)

        return [
            {
                "thread_id": f"world_thread_{self._safe_id(detail)}",
                "world_detail": detail,
                "thread_type": "world_state",
                "description": f"Keep world rule/detail consistent and reusable: {detail}.",
            }
            for detail in self._unique(details)
        ]

    def _open_loops(
        self,
        *,
        chapters: List[GeneratedChapter],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        loops: List[Dict[str, Any]] = []

        for chapter in chapters:
            loops.extend(chapter.open_loops)

        if continuation_anchor:
            loops.extend(continuation_anchor.open_loops)

        return self._unique_dicts(loops, key="loop_id")

    def _payoff_setups(
        self,
        *,
        secret_threads: List[Dict[str, Any]],
        causal_threads: List[Dict[str, Any]],
        relationship_threads: List[Dict[str, Any]],
        open_loops: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        payoffs: List[Dict[str, Any]] = []

        for thread in secret_threads:
            secret_id = thread["secret_id"]
            payoffs.append(
                {
                    "payoff_id": f"payoff_secret_{secret_id}",
                    "source_thread_id": thread["thread_id"],
                    "payoff_type": "secret_reveal_or_partial_reveal",
                    "description": f"Plan a controlled payoff for {secret_id}; avoid accidental reveal.",
                }
            )

        for thread in causal_threads:
            if thread.get("payoff_required"):
                causal_id = thread["causal_id"]
                payoffs.append(
                    {
                        "payoff_id": f"payoff_causal_{causal_id}",
                        "source_thread_id": thread["thread_id"],
                        "payoff_type": "cause_effect_consequence",
                        "description": f"Pay off or escalate causal setup {causal_id}.",
                    }
                )

        for thread in relationship_threads:
            relationship_id = thread["relationship_id"]
            payoffs.append(
                {
                    "payoff_id": f"payoff_relationship_{relationship_id}",
                    "source_thread_id": thread["thread_id"],
                    "payoff_type": "relationship_shift",
                    "description": f"Show a measurable relationship shift for {relationship_id}.",
                }
            )

        for loop in open_loops:
            loop_id = loop.get("loop_id")
            if loop_id:
                payoffs.append(
                    {
                        "payoff_id": f"payoff_open_loop_{loop_id}",
                        "source_thread_id": loop_id,
                        "payoff_type": "open_loop_resolution_or_reinforcement",
                        "description": f"Resolve, complicate, or reinforce open loop {loop_id}.",
                    }
                )

        return self._unique_dicts(payoffs, key="payoff_id")

    def _next_outline_hooks(
        self,
        *,
        chapters: List[GeneratedChapter],
        continuation_anchor: LongFormContinuationAnchor | None,
        open_loops: List[Dict[str, Any]],
    ) -> List[str]:
        hooks: List[str] = []

        for chapter in chapters:
            hooks.extend(chapter.next_chapter_hooks)

        if continuation_anchor:
            hooks.extend(continuation_anchor.next_chapter_hooks)

        for loop in open_loops:
            if loop.get("description"):
                hooks.append(loop["description"])

        return self._unique(hooks)

    def _continuity_requirements(
        self,
        *,
        character_threads: List[Dict[str, Any]],
        relationship_threads: List[Dict[str, Any]],
        secret_threads: List[Dict[str, Any]],
        causal_threads: List[Dict[str, Any]],
        world_threads: List[Dict[str, Any]],
        open_loops: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "required_character_ids": [item["character_id"] for item in character_threads],
            "required_relationship_ids": [item["relationship_id"] for item in relationship_threads],
            "required_secret_ids": [item["secret_id"] for item in secret_threads],
            "required_causal_ids": [item["causal_id"] for item in causal_threads],
            "required_world_details": [item["world_detail"] for item in world_threads],
            "open_loop_ids": [item.get("loop_id") for item in open_loops if item.get("loop_id")],
            "rules": [
                "Do not contradict known world rules.",
                "Do not reveal secrets without planned reveal timing.",
                "Do not orphan causal events without consequences.",
                "Carry character, relationship, and open-loop state into future generation.",
            ],
        }

    def _warnings(
        self,
        *,
        chapters: List[GeneratedChapter],
        assembled_scenes: List[AssembledScene],
        act_structure: List[Dict[str, Any]],
        scene_sequence: List[Dict[str, Any]],
        character_threads: List[Dict[str, Any]],
        causal_threads: List[Dict[str, Any]],
        open_loops: List[Dict[str, Any]],
    ) -> List[str]:
        warnings: List[str] = []

        if not chapters and not assembled_scenes:
            warnings.append("No chapters or assembled scenes supplied.")

        if not act_structure:
            warnings.append("No act structure generated.")

        if not scene_sequence:
            warnings.append("No scene sequence generated.")

        if not character_threads:
            warnings.append("No character arc threads generated.")

        if not causal_threads:
            warnings.append("No causal threads generated.")

        if len(open_loops) > 12:
            warnings.append("Many open loops are active; future outline may become overloaded.")

        return self._unique(warnings)

    def _title_from_sources(self, *, chapters: List[GeneratedChapter], story_context: Dict[str, Any]) -> str:
        if story_context.get("title"):
            return str(story_context["title"])
        if chapters and chapters[0].title:
            return f"Outline: {chapters[0].title}"
        return "Generated Plot Outline"

    def _safe_id(self, value: str) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:60] or "item"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _unique_dicts(self, values: List[Dict[str, Any]], *, key: str) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for value in values:
            marker = value.get(key) or str(value)
            if marker not in seen:
                seen.add(marker)
                result.append(value)
        return result
