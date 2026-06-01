from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    ChapterExpansionPlan,
    GeneratedChapter,
    MultiScenePacingReport,
    SeriesEpisodeStructure,
)


class MultiScenePacingEngine:
    """Evaluates and repairs pacing across multiple scenes.

    This engine makes long-form output less generic by checking whether scene
    sequence, tension, emotion, secrets, relationships, causes, dialogue, and
    world details are spaced correctly instead of being dumped randomly.
    """

    engine_name = "story_generation.multi_scene_pacing_engine"

    def evaluate_pacing(
        self,
        *,
        source_id: str,
        assembled_scenes: List[AssembledScene] | None = None,
        chapter: GeneratedChapter | None = None,
        expansion_plan: ChapterExpansionPlan | None = None,
        episode_structure: SeriesEpisodeStructure | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        assembled_scenes = assembled_scenes or []
        story_context = story_context or {}

        scene_units = self._scene_units(
            assembled_scenes=assembled_scenes,
            chapter=chapter,
            episode_structure=episode_structure,
        )

        tension_curve_score = self._tension_curve_score(scene_units=scene_units)
        emotional_variety_score = self._emotional_variety_score(scene_units=scene_units, story_context=story_context)
        relationship_rhythm_score = self._relationship_rhythm_score(scene_units=scene_units, chapter=chapter)
        secret_pressure_spacing_score = self._secret_pressure_spacing_score(scene_units=scene_units, chapter=chapter)
        causal_spacing_score = self._causal_spacing_score(scene_units=scene_units, chapter=chapter)
        world_detail_spacing_score = self._world_detail_spacing_score(scene_units=scene_units, chapter=chapter)
        dialogue_action_balance_score = self._dialogue_action_balance_score(scene_units=scene_units)

        overall = self._overall_score(
            tension_curve_score=tension_curve_score,
            emotional_variety_score=emotional_variety_score,
            relationship_rhythm_score=relationship_rhythm_score,
            secret_pressure_spacing_score=secret_pressure_spacing_score,
            causal_spacing_score=causal_spacing_score,
            world_detail_spacing_score=world_detail_spacing_score,
            dialogue_action_balance_score=dialogue_action_balance_score,
        )

        scene_pacing_map = self._scene_pacing_map(scene_units=scene_units)
        act_break_recommendations = self._act_break_recommendations(
            scene_units=scene_units,
            episode_structure=episode_structure,
        )
        repair_targets = self._repair_targets(
            tension_curve_score=tension_curve_score,
            emotional_variety_score=emotional_variety_score,
            relationship_rhythm_score=relationship_rhythm_score,
            secret_pressure_spacing_score=secret_pressure_spacing_score,
            causal_spacing_score=causal_spacing_score,
            world_detail_spacing_score=world_detail_spacing_score,
            dialogue_action_balance_score=dialogue_action_balance_score,
            expansion_plan=expansion_plan,
        )

        report = MultiScenePacingReport(
            pacing_report_id=f"multi_scene_pacing_{source_id}",
            source_id=source_id,
            scene_count=len(scene_units),
            overall_pacing_score=overall,
            tension_curve_score=tension_curve_score,
            emotional_variety_score=emotional_variety_score,
            relationship_rhythm_score=relationship_rhythm_score,
            secret_pressure_spacing_score=secret_pressure_spacing_score,
            causal_spacing_score=causal_spacing_score,
            world_detail_spacing_score=world_detail_spacing_score,
            dialogue_action_balance_score=dialogue_action_balance_score,
            scene_pacing_map=scene_pacing_map,
            act_break_recommendations=act_break_recommendations,
            pacing_repair_targets=repair_targets,
            warnings=self._warnings(
                scene_units=scene_units,
                overall_score=overall,
                expansion_plan=expansion_plan,
                episode_structure=episode_structure,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "multi_scene_pacing_report": report,
            "multi_scene_pacing_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.long_form_memory_bridge",
                "payload_keys": [
                    "multi_scene_pacing_report",
                    "generated_chapter",
                    "assembled_scenes",
                    "chapter_expansion_plan",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def build_pacing_repair_plan(self, *, report: MultiScenePacingReport) -> Dict[str, Any]:
        repairs: List[str] = []

        for target in report.pacing_repair_targets:
            target_type = target.get("target_type")
            if target_type == "tension_curve":
                repairs.append("Reorder or revise scenes so tension rises, dips for breath, then peaks near the end.")
            elif target_type == "emotional_variety":
                repairs.append("Add emotional contrast between scenes instead of repeating the same emotional pressure.")
            elif target_type == "relationship_rhythm":
                repairs.append("Space relationship conflict, silence, repair, and escalation across multiple scenes.")
            elif target_type == "secret_pressure_spacing":
                repairs.append("Spread clues, misdirection, withholding, and partial reveal across the sequence.")
            elif target_type == "causal_spacing":
                repairs.append("Separate cause setup, choice, consequence, and payoff across distinct beats/scenes.")
            elif target_type == "world_detail_spacing":
                repairs.append("Distribute world rules and concrete setting details instead of dumping them in one scene.")
            elif target_type == "dialogue_action_balance":
                repairs.append("Balance dialogue-heavy scenes with action, reaction, and sensory scene movement.")
            else:
                repairs.append(f"Repair pacing target: {target_type}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "ready_for_memory_handoff": report.overall_pacing_score >= 0.60,
            "repair_count": len(self._unique(repairs)),
            "repairs": self._unique(repairs),
        }

    def validate_pacing_report(self, *, report: MultiScenePacingReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not report.pacing_report_id:
            blockers.append("pacing_report_id missing")
        else:
            passed.append("pacing_report_id_present")

        if report.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if report.scene_count > 0:
            passed.append("scene_units_present")
        else:
            blockers.append("no scene units found")

        scores = [
            report.overall_pacing_score,
            report.tension_curve_score,
            report.emotional_variety_score,
            report.relationship_rhythm_score,
            report.secret_pressure_spacing_score,
            report.causal_spacing_score,
            report.world_detail_spacing_score,
            report.dialogue_action_balance_score,
        ]

        if all(0.0 <= score <= 1.0 for score in scores):
            passed.append("scores_bounded")
        else:
            blockers.append("one or more pacing scores out of bounds")

        if report.scene_pacing_map:
            passed.append("scene_pacing_map_present")
        else:
            warnings.append("scene pacing map missing")

        if report.overall_pacing_score >= 0.60:
            passed.append("pacing_usable")
        else:
            warnings.append("overall pacing score is weak")

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

    def summarize_pacing_report(self, *, report: MultiScenePacingReport) -> Dict[str, Any]:
        weakest = self._weakest_dimension(report=report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "pacing_report_id": report.pacing_report_id,
                "source_id": report.source_id,
                "scene_count": report.scene_count,
                "overall_pacing_score": report.overall_pacing_score,
                "weakest_dimension": weakest["dimension"],
                "weakest_score": weakest["score"],
                "act_break_recommendation_count": len(report.act_break_recommendations),
                "repair_target_count": len(report.pacing_repair_targets),
                "warning_count": len(report.warnings),
            },
        }

    def _scene_units(
        self,
        *,
        assembled_scenes: List[AssembledScene],
        chapter: GeneratedChapter | None,
        episode_structure: SeriesEpisodeStructure | None,
    ) -> List[Dict[str, Any]]:
        units: List[Dict[str, Any]] = []

        if assembled_scenes:
            for index, scene in enumerate(assembled_scenes, start=1):
                text = scene.assembled_text or ""
                units.append(
                    {
                        "scene_id": scene.scene_id,
                        "source_type": "assembled_scene",
                        "index": index,
                        "text": text,
                        "word_count": len(text.split()),
                        "has_dialogue": bool(scene.dialogue_block_id) or ":" in text or '"' in text,
                        "character_ids": scene.used_character_ids,
                        "relationship_ids": scene.used_relationship_ids,
                        "secret_ids": scene.used_secret_ids,
                        "causal_ids": scene.used_causal_ids,
                        "world_details": scene.used_world_details,
                        "tension_hint": self._tension_hint_from_text(text=text, fallback=index / max(1, len(assembled_scenes))),
                    }
                )

        elif chapter and chapter.sections:
            for index, section in enumerate(chapter.sections, start=1):
                text = section.get("text", "")
                units.append(
                    {
                        "scene_id": section.get("scene_id") or f"chapter_section_{index}",
                        "source_type": "chapter_section",
                        "index": index,
                        "text": text,
                        "word_count": len(text.split()),
                        "has_dialogue": ":" in text or '"' in text,
                        "character_ids": section.get("used_character_ids", chapter.used_character_ids),
                        "relationship_ids": chapter.used_relationship_ids,
                        "secret_ids": section.get("used_secret_ids", chapter.used_secret_ids),
                        "causal_ids": section.get("used_causal_ids", chapter.used_causal_ids),
                        "world_details": section.get("used_world_details", chapter.used_world_details),
                        "tension_hint": self._tension_hint_from_text(text=text, fallback=index / max(1, len(chapter.sections))),
                    }
                )

        elif episode_structure:
            for index, act in enumerate(episode_structure.act_structure, start=1):
                text = " ".join([str(act.get("description", "")), str(act.get("act_break_hook", ""))])
                units.append(
                    {
                        "scene_id": f"episode_act_{index}",
                        "source_type": "episode_act",
                        "index": index,
                        "text": text,
                        "word_count": len(text.split()),
                        "has_dialogue": False,
                        "character_ids": [item.get("character_id") for item in episode_structure.character_continuity if item.get("character_id")],
                        "relationship_ids": [item.get("relationship_id") for item in episode_structure.relationship_continuity if item.get("relationship_id")],
                        "secret_ids": [],
                        "causal_ids": [beat.get("source_id") for beat in episode_structure.plot_lanes.get("A_plot", []) if beat.get("source_id")],
                        "world_details": [],
                        "tension_hint": index / max(1, len(episode_structure.act_structure)),
                    }
                )

        return units

    def _tension_curve_score(self, *, scene_units: List[Dict[str, Any]]) -> float:
        if not scene_units:
            return 0.0

        if len(scene_units) == 1:
            return 0.65

        tensions = [float(unit.get("tension_hint", 0.5)) for unit in scene_units]

        rising_pairs = sum(1 for earlier, later in zip(tensions, tensions[1:]) if later >= earlier)
        rise_score = rising_pairs / max(1, len(tensions) - 1)

        peak_near_end = 1.0 if tensions[-1] >= max(tensions[:-1]) else 0.55
        has_mid_variation = 1.0 if len(set(round(value, 2) for value in tensions)) > 1 else 0.45

        return self._bounded((rise_score * 0.45) + (peak_near_end * 0.35) + (has_mid_variation * 0.20))

    def _emotional_variety_score(self, *, scene_units: List[Dict[str, Any]], story_context: Dict[str, Any]) -> float:
        markers = ["guilt", "fear", "anger", "resolve", "grief", "trust", "resentment", "longing", "shame", "hope"]
        found = set()

        for unit in scene_units:
            text = unit.get("text", "").lower()
            for marker in markers:
                if marker in text:
                    found.add(marker)

        for item in story_context.get("emotional_pressure", []):
            emotion = item.get("dominant_emotion")
            if emotion:
                found.add(str(emotion).lower())

        if not scene_units:
            return 0.0

        return self._bounded(0.35 + min(0.65, len(found) * 0.12))

    def _relationship_rhythm_score(self, *, scene_units: List[Dict[str, Any]], chapter: GeneratedChapter | None) -> float:
        if not scene_units:
            return 0.0

        active_count = sum(1 for unit in scene_units if unit.get("relationship_ids"))
        text_markers = sum(
            1
            for unit in scene_units
            if any(marker in unit.get("text", "").lower() for marker in ["trust", "resentment", "relationship", "betrayal", "silence", "repair"])
        )

        if chapter and chapter.used_relationship_ids:
            base = 0.35
        else:
            base = 0.2

        return self._bounded(base + (active_count / len(scene_units)) * 0.35 + (text_markers / len(scene_units)) * 0.30)

    def _secret_pressure_spacing_score(self, *, scene_units: List[Dict[str, Any]], chapter: GeneratedChapter | None) -> float:
        if not scene_units:
            return 0.0

        scenes_with_secrets = sum(1 for unit in scene_units if unit.get("secret_ids"))
        text_secret_markers = sum(
            1
            for unit in scene_units
            if any(marker in unit.get("text", "").lower() for marker in ["secret", "hidden", "reveal", "cannot name", "does not know"])
        )

        if chapter and not chapter.used_secret_ids:
            return 0.7

        return self._bounded(0.25 + (scenes_with_secrets / len(scene_units)) * 0.40 + (text_secret_markers / len(scene_units)) * 0.35)

    def _causal_spacing_score(self, *, scene_units: List[Dict[str, Any]], chapter: GeneratedChapter | None) -> float:
        if not scene_units:
            return 0.0

        scenes_with_cause = sum(1 for unit in scene_units if unit.get("causal_ids"))
        text_markers = sum(
            1
            for unit in scene_units
            if any(marker in unit.get("text", "").lower() for marker in ["cause_", "cons_", "consequence", "choice", "because", "therefore"])
        )

        if chapter and not chapter.used_causal_ids:
            return 0.25

        return self._bounded(0.25 + (scenes_with_cause / len(scene_units)) * 0.45 + (text_markers / len(scene_units)) * 0.30)

    def _world_detail_spacing_score(self, *, scene_units: List[Dict[str, Any]], chapter: GeneratedChapter | None) -> float:
        if not scene_units:
            return 0.0

        scenes_with_world = sum(1 for unit in scene_units if unit.get("world_details"))

        if chapter and not chapter.used_world_details:
            return 0.25

        return self._bounded(0.35 + (scenes_with_world / len(scene_units)) * 0.65)

    def _dialogue_action_balance_score(self, *, scene_units: List[Dict[str, Any]]) -> float:
        if not scene_units:
            return 0.0

        dialogue_count = sum(1 for unit in scene_units if unit.get("has_dialogue"))
        dialogue_ratio = dialogue_count / len(scene_units)

        # Best pacing usually has some dialogue and some non-dialogue movement.
        if len(scene_units) == 1:
            return 0.65 if dialogue_ratio > 0 else 0.45

        return self._bounded(1.0 - abs(dialogue_ratio - 0.55))

    def _scene_pacing_map(self, *, scene_units: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []

        for unit in scene_units:
            result.append(
                {
                    "scene_id": unit.get("scene_id"),
                    "index": unit.get("index"),
                    "word_count": unit.get("word_count"),
                    "tension_hint": unit.get("tension_hint"),
                    "has_dialogue": unit.get("has_dialogue"),
                    "character_count": len(unit.get("character_ids", [])),
                    "relationship_count": len(unit.get("relationship_ids", [])),
                    "secret_count": len(unit.get("secret_ids", [])),
                    "causal_count": len(unit.get("causal_ids", [])),
                    "world_detail_count": len(unit.get("world_details", [])),
                    "pacing_role": self._pacing_role(index=unit.get("index", 1), total=len(scene_units)),
                }
            )

        return result

    def _act_break_recommendations(
        self,
        *,
        scene_units: List[Dict[str, Any]],
        episode_structure: SeriesEpisodeStructure | None,
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []

        if episode_structure and episode_structure.act_structure:
            for act in episode_structure.act_structure:
                recommendations.append(
                    {
                        "act_number": act.get("act_number"),
                        "recommended_break": act.get("act_break_hook"),
                        "description": act.get("description"),
                    }
                )
            return recommendations

        if len(scene_units) >= 3:
            midpoint = len(scene_units) // 2
            recommendations.append(
                {
                    "act_number": 1,
                    "recommended_break": scene_units[midpoint - 1].get("scene_id"),
                    "description": "Use this point for a complication or reversal.",
                }
            )
            recommendations.append(
                {
                    "act_number": 2,
                    "recommended_break": scene_units[-1].get("scene_id"),
                    "description": "Use the final scene as a hook or consequence turn.",
                }
            )

        return recommendations

    def _repair_targets(
        self,
        *,
        tension_curve_score: float,
        emotional_variety_score: float,
        relationship_rhythm_score: float,
        secret_pressure_spacing_score: float,
        causal_spacing_score: float,
        world_detail_spacing_score: float,
        dialogue_action_balance_score: float,
        expansion_plan: ChapterExpansionPlan | None,
    ) -> List[Dict[str, Any]]:
        targets = []

        score_map = {
            "tension_curve": tension_curve_score,
            "emotional_variety": emotional_variety_score,
            "relationship_rhythm": relationship_rhythm_score,
            "secret_pressure_spacing": secret_pressure_spacing_score,
            "causal_spacing": causal_spacing_score,
            "world_detail_spacing": world_detail_spacing_score,
            "dialogue_action_balance": dialogue_action_balance_score,
        }

        for target_type, score in score_map.items():
            if score < 0.65:
                targets.append(
                    {
                        "target_type": target_type,
                        "score": score,
                        "priority": "high" if score < 0.45 else "medium",
                        "source": "pacing_analysis",
                    }
                )

        if expansion_plan and expansion_plan.expansion_targets:
            targets.append(
                {
                    "target_type": "expansion_alignment",
                    "score": 1.0,
                    "priority": "medium",
                    "source": expansion_plan.expansion_plan_id,
                    "instruction": "Align pacing repair with chapter expansion targets.",
                }
            )

        return targets

    def _warnings(
        self,
        *,
        scene_units: List[Dict[str, Any]],
        overall_score: float,
        expansion_plan: ChapterExpansionPlan | None,
        episode_structure: SeriesEpisodeStructure | None,
    ) -> List[str]:
        warnings: List[str] = []

        if not scene_units:
            warnings.append("No scene units were available for pacing analysis.")

        if len(scene_units) == 1:
            warnings.append("Only one scene unit available; multi-scene pacing is limited.")

        if overall_score < 0.60:
            warnings.append("Overall pacing score is weak and should be repaired before memory handoff.")

        if expansion_plan and expansion_plan.expansion_ratio > 8.0:
            warnings.append("Expansion ratio is high; pacing should be checked again after expansion.")

        if episode_structure and not episode_structure.act_structure:
            warnings.append("Episode structure has no acts.")

        return self._unique(warnings)

    def _overall_score(
        self,
        *,
        tension_curve_score: float,
        emotional_variety_score: float,
        relationship_rhythm_score: float,
        secret_pressure_spacing_score: float,
        causal_spacing_score: float,
        world_detail_spacing_score: float,
        dialogue_action_balance_score: float,
    ) -> float:
        score = (
            tension_curve_score * 0.20
            + emotional_variety_score * 0.13
            + relationship_rhythm_score * 0.13
            + secret_pressure_spacing_score * 0.13
            + causal_spacing_score * 0.16
            + world_detail_spacing_score * 0.10
            + dialogue_action_balance_score * 0.15
        )
        return self._bounded(score)

    def _weakest_dimension(self, *, report: MultiScenePacingReport) -> Dict[str, Any]:
        values = [
            {"dimension": "tension_curve", "score": report.tension_curve_score},
            {"dimension": "emotional_variety", "score": report.emotional_variety_score},
            {"dimension": "relationship_rhythm", "score": report.relationship_rhythm_score},
            {"dimension": "secret_pressure_spacing", "score": report.secret_pressure_spacing_score},
            {"dimension": "causal_spacing", "score": report.causal_spacing_score},
            {"dimension": "world_detail_spacing", "score": report.world_detail_spacing_score},
            {"dimension": "dialogue_action_balance", "score": report.dialogue_action_balance_score},
        ]
        return min(values, key=lambda item: item["score"])

    def _tension_hint_from_text(self, *, text: str, fallback: float) -> float:
        lowered = text.lower()
        score = fallback

        high_markers = ["consequence", "betrayal", "reveal", "refuses", "choice", "danger", "trial", "war", "death"]
        low_markers = ["quiet", "breath", "afterward", "remember", "reflect", "softly"]

        score += sum(0.05 for marker in high_markers if marker in lowered)
        score -= sum(0.04 for marker in low_markers if marker in lowered)

        return self._bounded(score)

    def _pacing_role(self, *, index: int, total: int) -> str:
        if total <= 1:
            return "single_unit"
        if index == 1:
            return "opening_setup"
        if index == total:
            return "climax_or_hook"
        if index >= max(2, int(total * 0.65)):
            return "escalation"
        return "development"

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
