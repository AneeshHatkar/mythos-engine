from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    CharacterVoiceInstruction,
    ConstraintSatisfactionReport,
    DialogueBeat,
    GenerationContract,
    SceneBeat,
    SceneBlueprint,
)


class ProseStyleEngine:
    """Builds a prose/style profile for drafting.

    This engine does not write the final scene yet. It creates a precise style
    plan so later drafting engines avoid generic prose and follow the requested
    format, tone, character voice, emotional pressure, and world detail density.
    """

    engine_name = "story_generation.prose_style_engine"

    STYLE_PRESETS = {
        "tense": {
            "sentence_rhythm": "controlled_escalation",
            "imagery_density": 0.55,
            "internality_level": 0.55,
            "sensory_detail_level": 0.65,
            "metaphor_level": 0.35,
        },
        "dark": {
            "sentence_rhythm": "heavy_with_sharp_breaks",
            "imagery_density": 0.70,
            "internality_level": 0.65,
            "sensory_detail_level": 0.70,
            "metaphor_level": 0.45,
        },
        "tragic": {
            "sentence_rhythm": "slow_pressure_then_break",
            "imagery_density": 0.65,
            "internality_level": 0.80,
            "sensory_detail_level": 0.60,
            "metaphor_level": 0.55,
        },
        "romantic": {
            "sentence_rhythm": "restrained_and_intimate",
            "imagery_density": 0.60,
            "internality_level": 0.75,
            "sensory_detail_level": 0.55,
            "metaphor_level": 0.45,
        },
        "cinematic": {
            "sentence_rhythm": "visual_cut_based",
            "imagery_density": 0.75,
            "internality_level": 0.25,
            "sensory_detail_level": 0.75,
            "metaphor_level": 0.25,
        },
        "literary": {
            "sentence_rhythm": "varied_literary",
            "imagery_density": 0.80,
            "internality_level": 0.75,
            "sensory_detail_level": 0.70,
            "metaphor_level": 0.65,
        },
    }

    FORMAT_RULES = {
        "scene": {
            "paragraph_style": "balanced_scene_blocks",
            "dialogue_format": "prose_dialogue",
            "internal_monologue_allowed": True,
            "camera_direction_allowed": False,
        },
        "novel": {
            "paragraph_style": "novelistic_varied",
            "dialogue_format": "prose_dialogue",
            "internal_monologue_allowed": True,
            "camera_direction_allowed": False,
        },
        "chapter": {
            "paragraph_style": "chapter_scene_sequence",
            "dialogue_format": "prose_dialogue",
            "internal_monologue_allowed": True,
            "camera_direction_allowed": False,
        },
        "screenplay": {
            "paragraph_style": "screenplay_action_lines",
            "dialogue_format": "screenplay_dialogue_blocks",
            "internal_monologue_allowed": False,
            "camera_direction_allowed": True,
        },
        "movie": {
            "paragraph_style": "cinematic_action_blocks",
            "dialogue_format": "screenplay_like_dialogue",
            "internal_monologue_allowed": False,
            "camera_direction_allowed": True,
        },
        "game_scene": {
            "paragraph_style": "interactive_scene_blocks",
            "dialogue_format": "choice_aware_dialogue",
            "internal_monologue_allowed": True,
            "camera_direction_allowed": False,
        },
        "multi_book_arc": {
            "paragraph_style": "outline_with_payoff_markers",
            "dialogue_format": "minimal_or_sample_dialogue",
            "internal_monologue_allowed": False,
            "camera_direction_allowed": False,
        },
    }

    GENERIC_PHRASES_TO_AVOID = [
        "heart skipped a beat",
        "little did they know",
        "a chill ran down",
        "for what felt like forever",
        "eyes widened",
        "time stood still",
        "everything changed",
        "in that moment",
        "without warning",
        "destiny awaited",
    ]

    def build_prose_style_profile(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        scene_beats: List[SceneBeat] | None = None,
        dialogue_beats: List[DialogueBeat] | None = None,
        voice_instructions: List[CharacterVoiceInstruction] | None = None,
        constraint_report: ConstraintSatisfactionReport | None = None,
        story_context: Dict[str, Any] | None = None,
        world_detail_pack: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        scene_beats = scene_beats or []
        dialogue_beats = dialogue_beats or []
        voice_instructions = voice_instructions or []
        story_context = story_context or {}
        world_detail_pack = world_detail_pack or {}

        tone_tags = contract.tone_contract.get("tone_tags", [])
        selected_format = contract.selected_format.value

        profile = {
            "prose_style_profile_id": f"prose_style_{blueprint.scene_id}",
            "scene_id": blueprint.scene_id,
            "selected_format": selected_format,
            "tone_tags": tone_tags,
            "genre_tags": contract.tone_contract.get("genres", []),
            "style_blend": self._style_blend(tone_tags=tone_tags),
            "format_rules": self._format_rules(selected_format=selected_format, contract=contract),
            "sentence_rhythm": self._sentence_rhythm(tone_tags=tone_tags, scene_beats=scene_beats),
            "imagery_density": self._density_value(tone_tags=tone_tags, key="imagery_density", default=0.55),
            "internality_level": self._internality_level(contract=contract, tone_tags=tone_tags),
            "dialogue_to_prose_balance": self._dialogue_balance(dialogue_beats=dialogue_beats, contract=contract),
            "sensory_detail_level": self._sensory_detail_level(tone_tags=tone_tags, world_detail_pack=world_detail_pack),
            "metaphor_level": self._density_value(tone_tags=tone_tags, key="metaphor_level", default=0.35),
            "world_detail_usage_rules": self._world_detail_usage_rules(world_detail_pack=world_detail_pack, blueprint=blueprint),
            "character_voice_usage_rules": self._character_voice_usage_rules(voice_instructions=voice_instructions),
            "emotional_rendering_rules": self._emotional_rendering_rules(story_context=story_context, blueprint=blueprint),
            "generic_phrase_bans": self._generic_phrase_bans(contract=contract),
            "revision_pressure": self._revision_pressure(constraint_report=constraint_report),
            "drafting_instructions": self._drafting_instructions(
                contract=contract,
                blueprint=blueprint,
                tone_tags=tone_tags,
                selected_format=selected_format,
            ),
        }

        profile["style_specificity_score"] = self._style_specificity_score(profile)
        profile["warnings"] = self._warnings(profile=profile, constraint_report=constraint_report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "prose_style_profile": profile,
            "handoff_to_next_engine": {
                "next_engine": "story_generation.commercial_appeal_engine",
                "payload_keys": [
                    "prose_style_profile",
                    "generation_contract",
                    "scene_blueprint",
                    "scene_beats",
                    "dialogue_beats",
                    "world_detail_pack",
                    "story_context",
                ],
            },
        }

    def validate_prose_style_profile(self, *, prose_style_profile: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if not prose_style_profile.get("prose_style_profile_id"):
            blockers.append("prose_style_profile_id missing")
        else:
            passed.append("prose_style_profile_id_present")

        if prose_style_profile.get("selected_format"):
            passed.append("selected_format_present")
        else:
            blockers.append("selected_format missing")

        if prose_style_profile.get("format_rules"):
            passed.append("format_rules_present")
        else:
            blockers.append("format rules missing")

        if prose_style_profile.get("drafting_instructions"):
            passed.append("drafting_instructions_present")
        else:
            blockers.append("drafting instructions missing")

        if prose_style_profile.get("generic_phrase_bans"):
            passed.append("generic_phrase_bans_present")
        else:
            warnings.append("generic phrase bans missing")

        if prose_style_profile.get("style_specificity_score", 0.0) >= 0.5:
            passed.append("style_specificity_usable")
        else:
            warnings.append("style specificity is weak")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "passed_checks": passed,
        }

    def build_style_prompt_payload(self, *, prose_style_profile: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "style_prompt_payload_id": f"style_prompt_{prose_style_profile.get('scene_id', 'unknown')}",
            "format": prose_style_profile.get("selected_format"),
            "tone": prose_style_profile.get("tone_tags", []),
            "rhythm": prose_style_profile.get("sentence_rhythm"),
            "dialogue_balance": prose_style_profile.get("dialogue_to_prose_balance"),
            "internality_level": prose_style_profile.get("internality_level"),
            "sensory_detail_level": prose_style_profile.get("sensory_detail_level"),
            "metaphor_level": prose_style_profile.get("metaphor_level"),
            "must_do": prose_style_profile.get("drafting_instructions", []),
            "must_avoid": prose_style_profile.get("generic_phrase_bans", []),
            "world_rules": prose_style_profile.get("world_detail_usage_rules", []),
            "voice_rules": prose_style_profile.get("character_voice_usage_rules", []),
            "emotion_rules": prose_style_profile.get("emotional_rendering_rules", []),
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "style_prompt_payload": payload,
        }

    def summarize_prose_style_profile(self, *, prose_style_profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "prose_style_profile_id": prose_style_profile.get("prose_style_profile_id"),
                "selected_format": prose_style_profile.get("selected_format"),
                "tone_count": len(prose_style_profile.get("tone_tags", [])),
                "style_specificity_score": prose_style_profile.get("style_specificity_score", 0.0),
                "generic_phrase_ban_count": len(prose_style_profile.get("generic_phrase_bans", [])),
                "world_rule_count": len(prose_style_profile.get("world_detail_usage_rules", [])),
                "voice_rule_count": len(prose_style_profile.get("character_voice_usage_rules", [])),
                "emotion_rule_count": len(prose_style_profile.get("emotional_rendering_rules", [])),
                "warning_count": len(prose_style_profile.get("warnings", [])),
            },
        }

    def _style_blend(self, *, tone_tags: List[str]) -> Dict[str, float]:
        if not tone_tags:
            return {"neutral_specific": 1.0}

        weight = round(1.0 / len(tone_tags), 3)
        return {str(tag): weight for tag in tone_tags}

    def _format_rules(self, *, selected_format: str, contract: GenerationContract) -> Dict[str, Any]:
        rules = dict(self.FORMAT_RULES.get(selected_format, self.FORMAT_RULES["scene"]))
        rules.update(contract.format_contract or {})
        return rules

    def _sentence_rhythm(self, *, tone_tags: List[str], scene_beats: List[SceneBeat]) -> str:
        if tone_tags:
            for tone in tone_tags:
                preset = self.STYLE_PRESETS.get(str(tone))
                if preset:
                    return preset["sentence_rhythm"]

        if scene_beats:
            max_tension = max([beat.tension_value for beat in scene_beats], default=0.0)
            if max_tension >= 0.8:
                return "escalating_shorter_near_climax"

        return "balanced_specific"

    def _density_value(self, *, tone_tags: List[str], key: str, default: float) -> float:
        values = []
        for tone in tone_tags:
            preset = self.STYLE_PRESETS.get(str(tone))
            if preset and key in preset:
                values.append(float(preset[key]))

        if not values:
            return default

        return round(sum(values) / len(values), 3)

    def _internality_level(self, *, contract: GenerationContract, tone_tags: List[str]) -> float:
        selected_format = contract.selected_format.value
        rules = self.FORMAT_RULES.get(selected_format, {})

        if rules.get("internal_monologue_allowed") is False:
            return 0.0

        return self._density_value(tone_tags=tone_tags, key="internality_level", default=0.55)

    def _dialogue_balance(self, *, dialogue_beats: List[DialogueBeat], contract: GenerationContract) -> Dict[str, Any]:
        selected_format = contract.selected_format.value
        base = {
            "dialogue_density": contract.tone_contract.get("dialogue_density", 0.5),
            "planned_dialogue_beat_count": len(dialogue_beats),
            "recommended_balance": "balanced",
        }

        if selected_format in {"screenplay", "movie"}:
            base["recommended_balance"] = "dialogue_and_action_lines"
            base["dialogue_density"] = max(base["dialogue_density"], 0.65)
        elif len(dialogue_beats) >= 5:
            base["recommended_balance"] = "dialogue_forward"
            base["dialogue_density"] = max(base["dialogue_density"], 0.60)
        elif selected_format in {"novel", "chapter"}:
            base["recommended_balance"] = "prose_with_dialogue"
        return base

    def _sensory_detail_level(self, *, tone_tags: List[str], world_detail_pack: Dict[str, Any]) -> float:
        base = self._density_value(tone_tags=tone_tags, key="sensory_detail_level", default=0.55)

        if world_detail_pack.get("sensory_detail_hints"):
            base += 0.10

        if world_detail_pack.get("specificity_score", 0.0) >= 0.7:
            base += 0.05

        return round(max(0.0, min(1.0, base)), 3)

    def _world_detail_usage_rules(
        self,
        *,
        world_detail_pack: Dict[str, Any],
        blueprint: SceneBlueprint,
    ) -> List[str]:
        rules = []

        for detail in blueprint.required_world_details[:5]:
            rules.append(f"Use world detail concretely: {detail}")

        for hint in world_detail_pack.get("sensory_detail_hints", [])[:3]:
            rules.append(f"Render sensory detail: {hint}")

        for anchor in world_detail_pack.get("law_and_rule_anchors", [])[:3]:
            detail = anchor.get("detail")
            if detail:
                rules.append(f"Make rule visible through action: {detail}")

        return self._unique(rules)

    def _character_voice_usage_rules(
        self,
        *,
        voice_instructions: List[CharacterVoiceInstruction],
    ) -> List[str]:
        rules = []

        for instruction in voice_instructions:
            rules.append(
                f"{instruction.character_id}: {instruction.vocabulary_style}, {instruction.rhythm}, "
                f"power behavior: {instruction.power_behavior}"
            )
            if instruction.silence_behavior:
                rules.append(f"{instruction.character_id} silence behavior: {instruction.silence_behavior}")
            if instruction.forbidden_phrases:
                rules.append(f"{instruction.character_id} must avoid: {', '.join(instruction.forbidden_phrases)}")

        return rules

    def _emotional_rendering_rules(
        self,
        *,
        story_context: Dict[str, Any],
        blueprint: SceneBlueprint,
    ) -> List[str]:
        rules = []

        if blueprint.emotional_turn:
            rules.append(f"Scene emotional turn: {blueprint.emotional_turn}")

        for item in story_context.get("emotional_pressure", [])[:5]:
            character_id = item.get("character_id")
            emotion = item.get("dominant_emotion")
            intensity = item.get("dominant_intensity")
            if character_id and emotion:
                rules.append(f"{character_id}: render {emotion} at intensity {intensity} through behavior, not labels.")

        if not rules:
            rules.append("Render emotion through choice, silence, body language, and subtext before naming it.")

        return rules

    def _generic_phrase_bans(self, *, contract: GenerationContract) -> List[str]:
        bans = list(self.GENERIC_PHRASES_TO_AVOID)

        originality = contract.originality_rules or {}
        forbidden = originality.get("forbidden_elements", [])
        if isinstance(forbidden, list):
            bans.extend([str(item) for item in forbidden])

        return self._unique(bans)

    def _revision_pressure(self, *, constraint_report: ConstraintSatisfactionReport | None) -> Dict[str, Any]:
        if constraint_report is None:
            return {
                "needs_repair_before_draft": False,
                "failed_constraints": [],
                "warnings": [],
            }

        return {
            "needs_repair_before_draft": not constraint_report.satisfied,
            "failed_constraints": constraint_report.failed_constraints,
            "warnings": constraint_report.warnings,
        }

    def _drafting_instructions(
        self,
        *,
        contract: GenerationContract,
        blueprint: SceneBlueprint,
        tone_tags: List[str],
        selected_format: str,
    ) -> List[str]:
        instructions = [
            f"Write in selected format: {selected_format}.",
            "Use concrete world details instead of generic fantasy/sci-fi filler.",
            "Keep character voice distinct for each speaker.",
            "Respect knowledge boundaries and do not leak hidden information.",
            "Every major beat must connect to cause, consequence, relationship, or emotion.",
        ]

        if tone_tags:
            instructions.append(f"Maintain tone: {', '.join(tone_tags)}.")

        if blueprint.ending_hook:
            instructions.append(f"Build toward ending hook: {blueprint.ending_hook}")

        if contract.provenance_required:
            instructions.append("Generated output must be traceable to contract, beats, and context.")

        return instructions

    def _style_specificity_score(self, profile: Dict[str, Any]) -> float:
        score = 0.0

        if profile.get("tone_tags"):
            score += 0.15
        if profile.get("format_rules"):
            score += 0.15
        if profile.get("world_detail_usage_rules"):
            score += 0.20
        if profile.get("character_voice_usage_rules"):
            score += 0.20
        if profile.get("emotional_rendering_rules"):
            score += 0.15
        if profile.get("generic_phrase_bans"):
            score += 0.10
        if profile.get("drafting_instructions"):
            score += 0.05

        return round(max(0.0, min(1.0, score)), 3)

    def _warnings(
        self,
        *,
        profile: Dict[str, Any],
        constraint_report: ConstraintSatisfactionReport | None,
    ) -> List[str]:
        warnings = []

        if profile.get("style_specificity_score", 0.0) < 0.5:
            warnings.append("Style specificity is low; drafting may become generic.")

        if not profile.get("world_detail_usage_rules"):
            warnings.append("No world detail usage rules found.")

        if not profile.get("character_voice_usage_rules"):
            warnings.append("No character voice usage rules found.")

        if constraint_report and not constraint_report.satisfied:
            warnings.append("Constraint report is not satisfied; drafting should wait for repair.")

        return warnings

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
