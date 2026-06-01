from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    ChapterExpansionPlan,
    FormatAdaptationPlan,
    GeneratedChapter,
    LongFormContinuationAnchor,
    SeriesEpisodeStructure,
)


class ChapterExpansionEngine:
    """Builds chapter expansion plans for richer long-form generation.

    This engine does not blindly add words. It decides where expansion should
    happen: scene texture, emotional interiority, dialogue, world rules,
    relationship pressure, secrets, causality, and payoff.
    """

    engine_name = "story_generation.chapter_expansion_engine"

    def build_expansion_plan(
        self,
        *,
        chapter: GeneratedChapter,
        target_word_count: int,
        format_plan: FormatAdaptationPlan | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        episode_structure: SeriesEpisodeStructure | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}
        source_word_count = len(chapter.chapter_text.split())
        expansion_ratio = round(target_word_count / max(1, source_word_count), 3)

        scene_targets = self._scene_expansion_targets(chapter=chapter, target_word_count=target_word_count)
        emotional_targets = self._emotional_expansion_targets(chapter=chapter, continuation_anchor=continuation_anchor)
        world_targets = self._world_expansion_targets(chapter=chapter)
        dialogue_targets = self._dialogue_expansion_targets(chapter=chapter, format_plan=format_plan)
        relationship_targets = self._relationship_expansion_targets(chapter=chapter, continuation_anchor=continuation_anchor)
        secret_targets = self._secret_expansion_targets(chapter=chapter, continuation_anchor=continuation_anchor)
        causal_targets = self._causal_expansion_targets(chapter=chapter, continuation_anchor=continuation_anchor)

        all_targets = (
            scene_targets
            + emotional_targets
            + world_targets
            + dialogue_targets
            + relationship_targets
            + secret_targets
            + causal_targets
        )

        plan = ChapterExpansionPlan(
            expansion_plan_id=f"chapter_expansion_{chapter.chapter_id}",
            chapter_id=chapter.chapter_id,
            source_word_count=source_word_count,
            target_word_count=target_word_count,
            expansion_ratio=expansion_ratio,
            expansion_targets=all_targets,
            scene_expansion_targets=scene_targets,
            emotional_expansion_targets=emotional_targets,
            world_expansion_targets=world_targets,
            dialogue_expansion_targets=dialogue_targets,
            relationship_expansion_targets=relationship_targets,
            secret_expansion_targets=secret_targets,
            causal_expansion_targets=causal_targets,
            format_specific_rules=self._format_specific_rules(
                format_plan=format_plan,
                episode_structure=episode_structure,
            ),
            revision_prompt_payload=self._revision_prompt_payload(
                chapter=chapter,
                target_word_count=target_word_count,
                expansion_targets=all_targets,
                format_plan=format_plan,
                continuation_anchor=continuation_anchor,
                episode_structure=episode_structure,
            ),
            warnings=self._warnings(
                chapter=chapter,
                target_word_count=target_word_count,
                expansion_ratio=expansion_ratio,
                format_plan=format_plan,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "chapter_expansion_plan": plan,
            "chapter_expansion_plan_dict": plan.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.multi_scene_pacing_engine",
                "payload_keys": [
                    "generated_chapter",
                    "chapter_expansion_plan",
                    "format_adaptation_plan",
                    "continuation_anchor",
                    "episode_structure",
                    "story_context",
                ],
            },
        }

    def build_expanded_chapter_skeleton(
        self,
        *,
        chapter: GeneratedChapter,
        plan: ChapterExpansionPlan,
    ) -> Dict[str, Any]:
        lines = [
            f"# Expanded Skeleton: {chapter.title}",
            "",
            f"Target word count: {plan.target_word_count}",
            f"Source word count: {plan.source_word_count}",
            "",
            "## Expansion Targets",
        ]

        for target in plan.expansion_targets:
            lines.append(f"- [{target.get('priority')}] {target.get('target_type')}: {target.get('instruction')}")

        lines.append("")
        lines.append("## Chapter Text To Expand")
        lines.append(chapter.chapter_text)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "expanded_chapter_skeleton": "\n".join(lines),
        }

    def validate_expansion_plan(self, *, plan: ChapterExpansionPlan) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not plan.expansion_plan_id:
            blockers.append("expansion_plan_id missing")
        else:
            passed.append("expansion_plan_id_present")

        if not plan.chapter_id:
            blockers.append("chapter_id missing")
        else:
            passed.append("chapter_id_present")

        if plan.target_word_count > plan.source_word_count:
            passed.append("target_expands_source")
        else:
            warnings.append("target word count does not expand source chapter")

        if plan.expansion_targets:
            passed.append("expansion_targets_present")
        else:
            blockers.append("no expansion targets created")

        if plan.revision_prompt_payload:
            passed.append("revision_prompt_payload_present")
        else:
            warnings.append("revision prompt payload missing")

        if plan.warnings:
            warnings.extend(plan.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_expansion_plan(self, *, plan: ChapterExpansionPlan) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "expansion_plan_id": plan.expansion_plan_id,
                "chapter_id": plan.chapter_id,
                "source_word_count": plan.source_word_count,
                "target_word_count": plan.target_word_count,
                "expansion_ratio": plan.expansion_ratio,
                "total_target_count": len(plan.expansion_targets),
                "scene_target_count": len(plan.scene_expansion_targets),
                "emotional_target_count": len(plan.emotional_expansion_targets),
                "world_target_count": len(plan.world_expansion_targets),
                "dialogue_target_count": len(plan.dialogue_expansion_targets),
                "relationship_target_count": len(plan.relationship_expansion_targets),
                "secret_target_count": len(plan.secret_expansion_targets),
                "causal_target_count": len(plan.causal_expansion_targets),
                "warning_count": len(plan.warnings),
            },
        }

    def _scene_expansion_targets(self, *, chapter: GeneratedChapter, target_word_count: int) -> List[Dict[str, Any]]:
        targets: List[Dict[str, Any]] = []
        scene_count = max(1, len(chapter.scene_ids))
        words_per_scene = max(200, target_word_count // scene_count)

        for scene_id in chapter.scene_ids:
            targets.append(
                {
                    "target_type": "scene_expansion",
                    "target_id": scene_id,
                    "priority": "high",
                    "desired_word_count": words_per_scene,
                    "instruction": f"Expand {scene_id} with concrete action, reaction, setting pressure, and turn logic.",
                }
            )

        return targets

    def _emotional_expansion_targets(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        character_ids = continuation_anchor.active_character_ids if continuation_anchor else chapter.used_character_ids
        targets = []

        for character_id in character_ids:
            targets.append(
                {
                    "target_type": "emotional_expansion",
                    "target_id": character_id,
                    "priority": "medium",
                    "instruction": f"Show {character_id}'s emotional state through behavior, choice, silence, and reaction.",
                }
            )

        return targets

    def _world_expansion_targets(self, *, chapter: GeneratedChapter) -> List[Dict[str, Any]]:
        targets = []

        for detail in chapter.used_world_details[:10]:
            targets.append(
                {
                    "target_type": "world_expansion",
                    "target_id": detail,
                    "priority": "medium",
                    "instruction": f"Make world detail concrete in the scene: {detail}.",
                }
            )

        return targets

    def _dialogue_expansion_targets(
        self,
        *,
        chapter: GeneratedChapter,
        format_plan: FormatAdaptationPlan | None,
    ) -> List[Dict[str, Any]]:
        density = "balanced"
        if format_plan:
            density = format_plan.dialogue_rules.get("dialogue_density", "balanced")

        targets = []

        for character_id in chapter.used_character_ids:
            targets.append(
                {
                    "target_type": "dialogue_expansion",
                    "target_id": character_id,
                    "priority": "medium" if density != "high" else "high",
                    "instruction": f"Add dialogue for {character_id} using subtext, distinct voice, and format density {density}.",
                }
            )

        return targets

    def _relationship_expansion_targets(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        relationship_ids = continuation_anchor.active_relationship_ids if continuation_anchor else chapter.used_relationship_ids
        targets = []

        for relationship_id in relationship_ids:
            targets.append(
                {
                    "target_type": "relationship_expansion",
                    "target_id": relationship_id,
                    "priority": "high",
                    "instruction": f"Expand relationship pressure for {relationship_id}; show trust, resentment, repair, betrayal risk, or longing changing.",
                }
            )

        return targets

    def _secret_expansion_targets(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        secret_ids = continuation_anchor.active_secret_ids if continuation_anchor else chapter.used_secret_ids
        targets = []

        for secret_id in secret_ids:
            targets.append(
                {
                    "target_type": "secret_expansion",
                    "target_id": secret_id,
                    "priority": "high",
                    "instruction": f"Keep {secret_id} active through tension, misdirection, avoidance, or partial evidence without unsafe reveal.",
                }
            )

        return targets

    def _causal_expansion_targets(
        self,
        *,
        chapter: GeneratedChapter,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        causal_ids = continuation_anchor.active_causal_ids if continuation_anchor else chapter.used_causal_ids
        targets = []

        for causal_id in causal_ids:
            targets.append(
                {
                    "target_type": "causal_expansion",
                    "target_id": causal_id,
                    "priority": "high",
                    "instruction": f"Make cause/effect visible for {causal_id}; connect action to consequence and future obligation.",
                }
            )

        return targets

    def _format_specific_rules(
        self,
        *,
        format_plan: FormatAdaptationPlan | None,
        episode_structure: SeriesEpisodeStructure | None,
    ) -> Dict[str, Any]:
        if not format_plan:
            return {
                "target_format": "chapter",
                "expansion_style": "balanced long-form prose",
            }

        rules = {
            "target_format": format_plan.target_format,
            "structure_rules": format_plan.structure_rules,
            "prose_rules": format_plan.prose_rules,
            "dialogue_rules": format_plan.dialogue_rules,
            "pacing_rules": format_plan.pacing_rules,
            "forbidden_patterns": format_plan.forbidden_patterns,
        }

        if episode_structure:
            rules["episode_structure_id"] = episode_structure.episode_structure_id
            rules["act_count"] = len(episode_structure.act_structure)
            rules["plot_lanes"] = list(episode_structure.plot_lanes.keys())
            rules["episode_cliffhanger"] = episode_structure.episode_cliffhanger

        return rules

    def _revision_prompt_payload(
        self,
        *,
        chapter: GeneratedChapter,
        target_word_count: int,
        expansion_targets: List[Dict[str, Any]],
        format_plan: FormatAdaptationPlan | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        episode_structure: SeriesEpisodeStructure | None,
    ) -> Dict[str, Any]:
        return {
            "revision_payload_id": f"revision_payload_{chapter.chapter_id}",
            "chapter_id": chapter.chapter_id,
            "source_text": chapter.chapter_text,
            "target_word_count": target_word_count,
            "target_format": format_plan.target_format if format_plan else "chapter",
            "expansion_targets": expansion_targets,
            "continuity_requirements": {
                "characters": continuation_anchor.active_character_ids if continuation_anchor else chapter.used_character_ids,
                "relationships": continuation_anchor.active_relationship_ids if continuation_anchor else chapter.used_relationship_ids,
                "secrets": continuation_anchor.active_secret_ids if continuation_anchor else chapter.used_secret_ids,
                "causal_ids": continuation_anchor.active_causal_ids if continuation_anchor else chapter.used_causal_ids,
                "open_loops": continuation_anchor.open_loops if continuation_anchor else chapter.open_loops,
            },
            "episode_requirements": {
                "episode_structure_id": episode_structure.episode_structure_id,
                "act_structure": episode_structure.act_structure,
                "plot_lanes": episode_structure.plot_lanes,
            } if episode_structure else {},
        }

    def _warnings(
        self,
        *,
        chapter: GeneratedChapter,
        target_word_count: int,
        expansion_ratio: float,
        format_plan: FormatAdaptationPlan | None,
    ) -> List[str]:
        warnings = list(chapter.warnings)

        if target_word_count <= len(chapter.chapter_text.split()):
            warnings.append("Target word count is not larger than source chapter word count.")

        if expansion_ratio > 8.0:
            warnings.append("Expansion ratio is very high; expansion may require multiple passes.")

        if format_plan and format_plan.warnings:
            warnings.extend(format_plan.warnings)

        if not chapter.used_character_ids:
            warnings.append("Chapter has no tracked characters; expansion may become generic.")

        if not chapter.used_causal_ids:
            warnings.append("Chapter has no tracked causal IDs; expansion may lose cause/effect.")

        return self._unique(warnings)

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
