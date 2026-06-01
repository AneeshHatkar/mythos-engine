from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    AssembledScene,
    FormatAdaptationPlan,
    GameInteractiveScenePackage,
    GeneratedChapter,
    LongFormContinuationAnchor,
    PlotOutline,
    SeriesSeasonFormatPackage,
)


class GameInteractiveSceneFormatter:
    """Formats story material into game/interactive scene structure.

    Locked Chunk 5.29. This converts story output into interactive gameplay
    structure: player objective, NPC dialogue, choices, branches, state deltas,
    quest updates, inventory/world hooks, and relationship/secret consequences.
    """

    engine_name = "story_generation.game_interactive_scene_formatter"

    def format_game_scene(
        self,
        *,
        source_id: str,
        scene_title: str | None = None,
        format_plan: FormatAdaptationPlan | None = None,
        plot_outline: PlotOutline | None = None,
        chapter: GeneratedChapter | None = None,
        assembled_scenes: List[AssembledScene] | None = None,
        continuation_anchor: LongFormContinuationAnchor | None = None,
        series_package: SeriesSeasonFormatPackage | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        assembled_scenes = assembled_scenes or []
        story_context = story_context or {}

        title = self._scene_title(
            scene_title=scene_title,
            plot_outline=plot_outline,
            chapter=chapter,
            story_context=story_context,
        )
        player_objective = self._player_objective(
            plot_outline=plot_outline,
            chapter=chapter,
            continuation_anchor=continuation_anchor,
            story_context=story_context,
        )
        scene_setup = self._scene_setup(
            title=title,
            player_objective=player_objective,
            plot_outline=plot_outline,
            chapter=chapter,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        npc_dialogue_blocks = self._npc_dialogue_blocks(
            chapter=chapter,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        choice_menu = self._choice_menu(
            player_objective=player_objective,
            plot_outline=plot_outline,
            chapter=chapter,
            continuation_anchor=continuation_anchor,
        )
        branching_outcomes = self._branching_outcomes(
            choice_menu=choice_menu,
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        state_deltas = self._state_deltas(
            branching_outcomes=branching_outcomes,
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        quest_log_updates = self._quest_log_updates(
            player_objective=player_objective,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        inventory_hooks = self._inventory_hooks(
            chapter=chapter,
            plot_outline=plot_outline,
            assembled_scenes=assembled_scenes,
        )
        relationship_hooks = self._relationship_state_hooks(
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        secret_hooks = self._secret_state_hooks(
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        causal_hooks = self._causal_state_hooks(
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )
        world_hooks = self._world_state_hooks(
            chapter=chapter,
            plot_outline=plot_outline,
            continuation_anchor=continuation_anchor,
        )

        formatted_text = self._formatted_text(
            title=title,
            player_objective=player_objective,
            scene_setup=scene_setup,
            npc_dialogue_blocks=npc_dialogue_blocks,
            choice_menu=choice_menu,
            branching_outcomes=branching_outcomes,
            state_deltas=state_deltas,
            quest_log_updates=quest_log_updates,
        )

        package = GameInteractiveScenePackage(
            game_package_id=f"game_interactive_scene_{source_id}",
            source_id=source_id,
            target_format="game_scene",
            scene_title=title,
            player_objective=player_objective,
            scene_setup=scene_setup,
            npc_dialogue_blocks=npc_dialogue_blocks,
            choice_menu=choice_menu,
            branching_outcomes=branching_outcomes,
            state_deltas=state_deltas,
            quest_log_updates=quest_log_updates,
            inventory_hooks=inventory_hooks,
            relationship_state_hooks=relationship_hooks,
            secret_state_hooks=secret_hooks,
            causal_state_hooks=causal_hooks,
            world_state_hooks=world_hooks,
            formatted_text=formatted_text,
            export_payload=self._export_payload(
                source_id=source_id,
                title=title,
                formatted_text=formatted_text,
                choice_menu=choice_menu,
                branching_outcomes=branching_outcomes,
                state_deltas=state_deltas,
            ),
            warnings=self._warnings(
                choice_menu=choice_menu,
                branching_outcomes=branching_outcomes,
                state_deltas=state_deltas,
                format_plan=format_plan,
                series_package=series_package,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "game_interactive_scene_package": package,
            "game_interactive_scene_package_dict": package.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.multi_world_multi_cast_scaling_controller",
                "payload_keys": [
                    "game_interactive_scene_package",
                    "series_season_format_package",
                    "plot_outline",
                    "generated_chapter",
                    "continuation_anchor",
                    "story_context",
                ],
            },
        }

    def validate_game_package(self, *, package: GameInteractiveScenePackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not package.game_package_id:
            blockers.append("game_package_id missing")
        else:
            passed.append("game_package_id_present")

        if package.player_objective:
            passed.append("player_objective_present")
        else:
            blockers.append("player objective missing")

        if package.scene_setup:
            passed.append("scene_setup_present")
        else:
            blockers.append("scene setup missing")

        if package.choice_menu:
            passed.append("choice_menu_present")
        else:
            blockers.append("choice menu missing")

        if package.branching_outcomes:
            passed.append("branching_outcomes_present")
        else:
            blockers.append("branching outcomes missing")

        if package.state_deltas:
            passed.append("state_deltas_present")
        else:
            warnings.append("state deltas missing")

        if package.quest_log_updates:
            passed.append("quest_log_updates_present")
        else:
            warnings.append("quest log updates missing")

        if package.formatted_text and len(package.formatted_text.strip()) >= 150:
            passed.append("formatted_text_present")
        else:
            blockers.append("formatted text missing or too short")

        if package.export_payload:
            passed.append("export_payload_present")
        else:
            warnings.append("export payload missing")

        if package.warnings:
            warnings.extend(package.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_game_package(self, *, package: GameInteractiveScenePackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "game_package_id": package.game_package_id,
                "source_id": package.source_id,
                "scene_title": package.scene_title,
                "choice_count": len(package.choice_menu),
                "branching_outcome_count": len(package.branching_outcomes),
                "state_delta_count": len(package.state_deltas),
                "quest_log_update_count": len(package.quest_log_updates),
                "inventory_hook_count": len(package.inventory_hooks),
                "relationship_hook_count": len(package.relationship_state_hooks),
                "secret_hook_count": len(package.secret_state_hooks),
                "causal_hook_count": len(package.causal_state_hooks),
                "world_hook_count": len(package.world_state_hooks),
                "formatted_word_count": len(package.formatted_text.split()),
                "warning_count": len(package.warnings),
            },
        }

    def build_export_text(self, *, package: GameInteractiveScenePackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "export_text": package.formatted_text,
            "export_metadata": {
                "game_package_id": package.game_package_id,
                "target_format": package.target_format,
                "scene_title": package.scene_title,
                "choice_count": len(package.choice_menu),
                "branching_outcome_count": len(package.branching_outcomes),
                "suggested_extension": ".md",
            },
        }

    def _scene_title(
        self,
        *,
        scene_title: str | None,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        story_context: Dict[str, Any],
    ) -> str:
        if scene_title:
            return scene_title
        if story_context.get("scene_title"):
            return str(story_context["scene_title"])
        if plot_outline and plot_outline.title:
            return f"Interactive: {plot_outline.title}"
        if chapter and chapter.title:
            return f"Interactive: {chapter.title}"
        return "Interactive Scene"

    def _player_objective(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
        story_context: Dict[str, Any],
    ) -> str:
        if story_context.get("player_objective"):
            return str(story_context["player_objective"])
        if plot_outline and plot_outline.next_outline_hooks:
            return f"Investigate the consequence behind: {plot_outline.next_outline_hooks[0]}"
        if chapter and chapter.next_chapter_hooks:
            return f"Respond to the unresolved hook: {chapter.next_chapter_hooks[0]}"
        if continuation_anchor and continuation_anchor.next_chapter_hooks:
            return f"Carry forward the active story pressure: {continuation_anchor.next_chapter_hooks[0]}"
        return "Make a choice that changes the story state."

    def _scene_setup(
        self,
        *,
        title: str,
        player_objective: str,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> Dict[str, Any]:
        world_details = self._collect_world_details(
            plot_outline=plot_outline,
            chapter=chapter,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )
        characters = self._collect_character_ids(
            plot_outline=plot_outline,
            chapter=chapter,
            assembled_scenes=assembled_scenes,
            continuation_anchor=continuation_anchor,
        )

        return {
            "scene_title": title,
            "player_objective": player_objective,
            "location_hint": world_details[0] if world_details else "active story location",
            "active_character_ids": characters,
            "active_world_details": world_details,
            "setup_text": f"{title} begins with a playable pressure point: {player_objective}",
        }

    def _npc_dialogue_blocks(
        self,
        *,
        chapter: GeneratedChapter | None,
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        character_ids: List[str] = []
        if chapter:
            character_ids.extend(chapter.used_character_ids)
        for scene in assembled_scenes:
            character_ids.extend(scene.used_character_ids)
        if continuation_anchor:
            character_ids.extend(continuation_anchor.active_character_ids)

        blocks = []
        for character_id in self._unique(character_ids)[:8]:
            line = "This choice will change what happens next."
            if "seren" in character_id.lower():
                line = "There are answers I cannot give you here."
            elif "kael" in character_id.lower():
                line = "Then we force the truth into the open."

            blocks.append(
                {
                    "dialogue_block_id": f"npc_dialogue_{character_id}",
                    "npc_id": character_id,
                    "line": line,
                    "subtext": "NPC dialogue exposes pressure while preserving interactive choice.",
                    "choice_relevance": "dialogue changes how the player reads the available options",
                }
            )

        return blocks

    def _choice_menu(
        self,
        *,
        player_objective: str,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        choices = [
            {
                "choice_id": "choice_push_truth",
                "label": "Push for the truth now.",
                "choice_type": "confront",
                "risk_level": "high",
                "description": "Force the hidden pressure into the open.",
            },
            {
                "choice_id": "choice_protect_secret",
                "label": "Protect the secret for now.",
                "choice_type": "withhold",
                "risk_level": "medium",
                "description": "Preserve the secret while increasing future pressure.",
            },
            {
                "choice_id": "choice_gather_evidence",
                "label": "Delay and gather evidence.",
                "choice_type": "investigate",
                "risk_level": "medium",
                "description": "Gain more context before triggering consequences.",
            },
        ]

        if plot_outline and plot_outline.open_loops:
            choices.append(
                {
                    "choice_id": "choice_follow_open_loop",
                    "label": "Follow the unresolved lead.",
                    "choice_type": "open_loop",
                    "risk_level": "variable",
                    "description": plot_outline.open_loops[0].get("description", "Follow the active open loop."),
                }
            )

        if continuation_anchor and continuation_anchor.open_loops and not any(c["choice_id"] == "choice_follow_open_loop" for c in choices):
            choices.append(
                {
                    "choice_id": "choice_follow_open_loop",
                    "label": "Follow the unresolved lead.",
                    "choice_type": "open_loop",
                    "risk_level": "variable",
                    "description": continuation_anchor.open_loops[0].get("description", "Follow the active open loop."),
                }
            )

        return choices

    def _branching_outcomes(
        self,
        *,
        choice_menu: List[Dict[str, Any]],
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        outcomes = []
        secret_ids = self._collect_secret_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        causal_ids = self._collect_causal_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)

        for choice in choice_menu:
            choice_id = choice["choice_id"]
            outcome_type = "state_shift"
            if choice["choice_type"] == "confront":
                outcome_type = "immediate_consequence"
            elif choice["choice_type"] == "withhold":
                outcome_type = "delayed_secret_pressure"
            elif choice["choice_type"] == "investigate":
                outcome_type = "evidence_gain"

            outcomes.append(
                {
                    "outcome_id": f"outcome_{choice_id}",
                    "choice_id": choice_id,
                    "outcome_type": outcome_type,
                    "description": f"{choice['label']} changes the next scene state.",
                    "affected_secret_ids": secret_ids,
                    "affected_causal_ids": causal_ids,
                    "locks_future_state": True,
                }
            )

        return outcomes

    def _state_deltas(
        self,
        *,
        branching_outcomes: List[Dict[str, Any]],
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        deltas = []

        relationship_ids = self._collect_relationship_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        secret_ids = self._collect_secret_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        causal_ids = self._collect_causal_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        world_details = self._collect_world_details(plot_outline=plot_outline, chapter=chapter, assembled_scenes=[], continuation_anchor=continuation_anchor)

        for outcome in branching_outcomes:
            deltas.append(
                {
                    "state_delta_id": f"delta_{outcome['outcome_id']}",
                    "choice_id": outcome["choice_id"],
                    "delta_type": outcome["outcome_type"],
                    "relationship_ids": relationship_ids,
                    "secret_ids": secret_ids,
                    "causal_ids": causal_ids,
                    "world_details": world_details,
                    "description": f"Apply {outcome['outcome_type']} after {outcome['choice_id']}.",
                }
            )

        return deltas

    def _quest_log_updates(
        self,
        *,
        player_objective: str,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        updates = [
            {
                "quest_update_id": "quest_main_objective",
                "quest_type": "main",
                "status": "active",
                "description": player_objective,
            }
        ]

        if plot_outline:
            for payoff in plot_outline.payoff_setups[:5]:
                updates.append(
                    {
                        "quest_update_id": f"quest_payoff_{payoff.get('payoff_id')}",
                        "quest_type": "payoff",
                        "status": "pending",
                        "description": payoff.get("description"),
                    }
                )

        if continuation_anchor:
            for loop in continuation_anchor.open_loops[:5]:
                updates.append(
                    {
                        "quest_update_id": f"quest_open_loop_{loop.get('loop_id')}",
                        "quest_type": "open_loop",
                        "status": loop.get("status", "open"),
                        "description": loop.get("description"),
                    }
                )

        return self._unique_dicts(updates, key="quest_update_id")

    def _inventory_hooks(
        self,
        *,
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        assembled_scenes: List[AssembledScene],
    ) -> List[Dict[str, Any]]:
        details = self._collect_world_details(plot_outline=plot_outline, chapter=chapter, assembled_scenes=assembled_scenes, continuation_anchor=None)
        hooks = []

        for detail in details:
            lowered = str(detail).lower()
            if any(marker in lowered for marker in ["badge", "key", "letter", "artifact", "proof", "map", "weapon"]):
                hooks.append(
                    {
                        "inventory_hook_id": f"inventory_{self._safe_id(detail)}",
                        "item_name": detail,
                        "item_type": "evidence_or_artifact",
                        "description": f"{detail} can become an inspectable or usable game object.",
                    }
                )

        return hooks

    def _relationship_state_hooks(
        self,
        *,
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "relationship_hook_id": f"relationship_hook_{relationship_id}",
                "relationship_id": relationship_id,
                "tracked_values": ["trust", "resentment", "betrayal_risk", "repair_potential"],
                "description": f"Choices can update relationship state for {relationship_id}.",
            }
            for relationship_id in self._collect_relationship_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        ]

    def _secret_state_hooks(
        self,
        *,
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "secret_hook_id": f"secret_hook_{secret_id}",
                "secret_id": secret_id,
                "tracked_values": ["known_by_player", "known_by_npc", "partial_evidence", "reveal_status"],
                "description": f"Choices can reveal, hide, or complicate {secret_id}.",
            }
            for secret_id in self._collect_secret_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        ]

    def _causal_state_hooks(
        self,
        *,
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "causal_hook_id": f"causal_hook_{causal_id}",
                "causal_id": causal_id,
                "tracked_values": ["setup", "choice", "consequence", "payoff_status"],
                "description": f"Choices must preserve cause/effect state for {causal_id}.",
            }
            for causal_id in self._collect_causal_ids(plot_outline=plot_outline, chapter=chapter, continuation_anchor=continuation_anchor)
        ]

    def _world_state_hooks(
        self,
        *,
        chapter: GeneratedChapter | None,
        plot_outline: PlotOutline | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[Dict[str, Any]]:
        details = self._collect_world_details(plot_outline=plot_outline, chapter=chapter, assembled_scenes=[], continuation_anchor=continuation_anchor)
        return [
            {
                "world_hook_id": f"world_hook_{self._safe_id(detail)}",
                "world_detail": detail,
                "tracked_values": ["available", "changed", "contradicted", "reinforced"],
                "description": f"Game state must keep world detail consistent: {detail}.",
            }
            for detail in details
        ]

    def _formatted_text(
        self,
        *,
        title: str,
        player_objective: str,
        scene_setup: Dict[str, Any],
        npc_dialogue_blocks: List[Dict[str, Any]],
        choice_menu: List[Dict[str, Any]],
        branching_outcomes: List[Dict[str, Any]],
        state_deltas: List[Dict[str, Any]],
        quest_log_updates: List[Dict[str, Any]],
    ) -> str:
        lines = [
            f"# {title}",
            "",
            "## Player Objective",
            player_objective,
            "",
            "## Scene Setup",
            scene_setup.get("setup_text", ""),
            "",
            "## NPC Dialogue",
        ]

        for block in npc_dialogue_blocks:
            lines.append(f"- {block.get('npc_id')}: {block.get('line')}")

        lines.extend(["", "## Choices"])
        for choice in choice_menu:
            lines.append(f"- [{choice.get('choice_id')}] {choice.get('label')} — {choice.get('description')}")

        lines.extend(["", "## Branching Outcomes"])
        for outcome in branching_outcomes:
            lines.append(f"- {outcome.get('outcome_id')}: {outcome.get('description')}")

        lines.extend(["", "## State Deltas"])
        for delta in state_deltas:
            lines.append(f"- {delta.get('state_delta_id')}: {delta.get('description')}")

        lines.extend(["", "## Quest Log Updates"])
        for update in quest_log_updates:
            lines.append(f"- {update.get('quest_update_id')}: {update.get('description')}")

        return "\n".join(lines).strip()

    def _export_payload(
        self,
        *,
        source_id: str,
        title: str,
        formatted_text: str,
        choice_menu: List[Dict[str, Any]],
        branching_outcomes: List[Dict[str, Any]],
        state_deltas: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "export_id": f"export_game_scene_{source_id}",
            "source_id": source_id,
            "target_format": "game_scene",
            "title": title,
            "text": formatted_text,
            "choice_count": len(choice_menu),
            "branching_outcome_count": len(branching_outcomes),
            "state_delta_count": len(state_deltas),
            "suggested_extension": ".md",
        }

    def _warnings(
        self,
        *,
        choice_menu: List[Dict[str, Any]],
        branching_outcomes: List[Dict[str, Any]],
        state_deltas: List[Dict[str, Any]],
        format_plan: FormatAdaptationPlan | None,
        series_package: SeriesSeasonFormatPackage | None,
    ) -> List[str]:
        warnings: List[str] = []

        if len(choice_menu) < 2:
            warnings.append("Interactive scene has fewer than two choices.")

        if not branching_outcomes:
            warnings.append("Interactive scene has no branching outcomes.")

        if not state_deltas:
            warnings.append("Interactive scene has no state deltas.")

        if format_plan and format_plan.target_format not in {"game_scene", "scene", "chapter"}:
            warnings.append(f"Format plan target is {format_plan.target_format}; applying game formatter carefully.")

        if series_package and not series_package.episode_cards:
            warnings.append("Series package has no episode cards; game scene loses episode context.")

        return self._unique(warnings)

    def _collect_character_ids(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        values: List[str] = []
        if plot_outline:
            values.extend(plot_outline.continuity_requirements.get("required_character_ids", []))
            values.extend([item.get("character_id") for item in plot_outline.character_arc_threads if item.get("character_id")])
        if chapter:
            values.extend(chapter.used_character_ids)
        for scene in assembled_scenes:
            values.extend(scene.used_character_ids)
        if continuation_anchor:
            values.extend(continuation_anchor.active_character_ids)
        return self._unique(values)

    def _collect_relationship_ids(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        values: List[str] = []
        if plot_outline:
            values.extend(plot_outline.continuity_requirements.get("required_relationship_ids", []))
            values.extend([item.get("relationship_id") for item in plot_outline.relationship_arc_threads if item.get("relationship_id")])
        if chapter:
            values.extend(chapter.used_relationship_ids)
        if continuation_anchor:
            values.extend(continuation_anchor.active_relationship_ids)
        return self._unique(values)

    def _collect_secret_ids(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        values: List[str] = []
        if plot_outline:
            values.extend(plot_outline.continuity_requirements.get("required_secret_ids", []))
            values.extend([item.get("secret_id") for item in plot_outline.secret_threads if item.get("secret_id")])
        if chapter:
            values.extend(chapter.used_secret_ids)
        if continuation_anchor:
            values.extend(continuation_anchor.active_secret_ids)
        return self._unique(values)

    def _collect_causal_ids(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        values: List[str] = []
        if plot_outline:
            values.extend(plot_outline.continuity_requirements.get("required_causal_ids", []))
            values.extend([item.get("causal_id") for item in plot_outline.causal_threads if item.get("causal_id")])
        if chapter:
            values.extend(chapter.used_causal_ids)
        if continuation_anchor:
            values.extend(continuation_anchor.active_causal_ids)
        return self._unique(values)

    def _collect_world_details(
        self,
        *,
        plot_outline: PlotOutline | None,
        chapter: GeneratedChapter | None,
        assembled_scenes: List[AssembledScene],
        continuation_anchor: LongFormContinuationAnchor | None,
    ) -> List[str]:
        values: List[str] = []
        if plot_outline:
            values.extend(plot_outline.continuity_requirements.get("required_world_details", []))
            values.extend([item.get("world_detail") for item in plot_outline.world_state_threads if item.get("world_detail")])
        if chapter:
            values.extend(chapter.used_world_details)
        for scene in assembled_scenes:
            values.extend(scene.used_world_details)
        if continuation_anchor:
            values.extend(continuation_anchor.active_world_details)
        return self._unique(values)

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
            if marker and marker not in seen:
                seen.add(marker)
                result.append(value)
        return result
