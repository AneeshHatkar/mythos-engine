from typing import Any, Dict, List, Optional


class GenreAdaptationMLHookEngine:
    """Builds genre, adaptation, and ML-learning hooks for downstream generation.

    This engine does not train the model yet. It creates the structured metadata
    Chunk 5+ will use to generate novels, films, series, scripts, episodes, and
    later learn from user-provided PDFs or story corpora in a safe/evaluated way.
    """

    engine_name = "simulation.genre_adaptation_ml_hook_engine"

    GENRE_TAGS = {
        "fantasy",
        "dark_fantasy",
        "science_fiction",
        "romance",
        "tragedy",
        "mystery",
        "thriller",
        "political_intrigue",
        "dark_academy",
        "coming_of_age",
        "mythic_epic",
        "comedy",
        "action",
        "drama",
        "horror",
        "supernatural",
        "historical",
        "slice_of_life",
        "adventure",
    }

    OUTPUT_FORMATS = {
        "novel",
        "chapter",
        "short_story",
        "movie",
        "screenplay",
        "series",
        "series_episode",
        "season_outline",
        "franchise_outline",
        "comic_scene",
        "game_scene",
        "treatment",
    }

    LEARNING_HOOK_TYPES = {
        "style_profile",
        "character_pattern",
        "worldbuilding_pattern",
        "plot_structure_pattern",
        "dialogue_pattern",
        "scene_pacing_pattern",
        "emotional_arc_pattern",
        "genre_convention",
        "anti_genericity_signal",
        "quality_metric",
        "evaluation_target",
        "pdf_corpus_ingestion",
        "reference_work_profile",
    }

    def create_genre_profile(
        self,
        *,
        profile_id: str,
        primary_genres: List[str],
        secondary_genres: List[str] | None = None,
        tone_tags: List[str] | None = None,
        taboo_or_avoid_tags: List[str] | None = None,
        intensity_targets: Dict[str, float] | None = None,
        convention_targets: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        primary = [genre if genre in self.GENRE_TAGS else "drama" for genre in primary_genres]
        secondary = [genre if genre in self.GENRE_TAGS else "drama" for genre in (secondary_genres or [])]

        return {
            "profile_id": profile_id,
            "primary_genres": self._unique(primary),
            "secondary_genres": self._unique(secondary),
            "tone_tags": tone_tags or [],
            "taboo_or_avoid_tags": taboo_or_avoid_tags or [],
            "intensity_targets": {
                key: self._bounded(value)
                for key, value in (intensity_targets or {}).items()
            },
            "convention_targets": convention_targets or {},
            "metadata": metadata or {},
        }

    def create_adaptation_profile(
        self,
        *,
        adaptation_id: str,
        output_format: str,
        target_length: Optional[str] = None,
        act_structure: Optional[str] = None,
        pov_mode: str = "third_person_limited",
        prose_density: float = 0.6,
        dialogue_density: float = 0.5,
        scene_count_target: Optional[int] = None,
        episode_count_target: Optional[int] = None,
        chapter_count_target: Optional[int] = None,
        visuality_target: float = 0.5,
        interiority_target: float = 0.5,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if output_format not in self.OUTPUT_FORMATS:
            output_format = "novel"

        return {
            "adaptation_id": adaptation_id,
            "output_format": output_format,
            "target_length": target_length,
            "act_structure": act_structure or self._default_structure(output_format),
            "pov_mode": pov_mode,
            "prose_density": self._bounded(prose_density),
            "dialogue_density": self._bounded(dialogue_density),
            "scene_count_target": scene_count_target,
            "episode_count_target": episode_count_target,
            "chapter_count_target": chapter_count_target,
            "visuality_target": self._bounded(visuality_target),
            "interiority_target": self._bounded(interiority_target),
            "format_constraints": self._format_constraints(output_format),
            "metadata": metadata or {},
        }

    def create_ml_learning_hook(
        self,
        *,
        hook_id: str,
        hook_type: str,
        source_type: str,
        source_id: str,
        learning_target: str,
        extracted_features: Dict[str, Any] | None = None,
        evaluation_metrics: Dict[str, float] | None = None,
        confidence: float = 0.5,
        requires_human_review: bool = False,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if hook_type not in self.LEARNING_HOOK_TYPES:
            hook_type = "quality_metric"

        return {
            "hook_id": hook_id,
            "hook_type": hook_type,
            "source_type": source_type,
            "source_id": source_id,
            "learning_target": learning_target,
            "extracted_features": extracted_features or {},
            "evaluation_metrics": {
                key: self._bounded(value)
                for key, value in (evaluation_metrics or {}).items()
            },
            "confidence": self._bounded(confidence),
            "requires_human_review": bool(requires_human_review),
            "metadata": metadata or {},
        }

    def build_generation_control_payload(
        self,
        *,
        payload_id: str,
        story_request: Dict[str, Any],
        genre_profile: Dict[str, Any],
        adaptation_profile: Dict[str, Any],
        handoff_package: Dict[str, Any] | None = None,
        learning_hooks: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        output_format = adaptation_profile.get("output_format", story_request.get("format", "novel"))

        payload = {
            "payload_id": payload_id,
            "payload_type": "generation_control",
            "story_request": story_request,
            "genre_profile": genre_profile,
            "adaptation_profile": adaptation_profile,
            "handoff_package_id": (handoff_package or {}).get("package_id"),
            "learning_hooks": learning_hooks or [],
            "generation_rules": self._generation_rules(
                story_request=story_request,
                genre_profile=genre_profile,
                adaptation_profile=adaptation_profile,
            ),
            "format_contract": self._format_contract(output_format, adaptation_profile),
            "quality_contract": self._quality_contract(genre_profile, adaptation_profile, learning_hooks or []),
            "anti_genericity_contract": self._anti_genericity_contract(story_request, genre_profile),
            "continuity_contract": {
                "must_preserve_causal_continuity": True,
                "must_preserve_character_memory": True,
                "must_preserve_relationship_state": True,
                "must_preserve_hidden_knowledge": True,
                "must_preserve_user_requested_characters": True,
                "can_use_project_created_characters": story_request.get("allow_project_created_characters", True),
                "allow_any_character_count": story_request.get("allow_any_character_count", True),
            },
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload": payload,
            "warnings": self._generation_control_warnings(payload),
        }

    def build_pdf_learning_hook_payload(
        self,
        *,
        corpus_id: str,
        document_ids: List[str],
        learning_goals: List[str],
        allowed_learning_scope: List[str] | None = None,
        excluded_learning_scope: List[str] | None = None,
        user_notes: str = "",
    ) -> Dict[str, Any]:
        """Creates future-ready hooks for learning from user-provided novels/PDFs.

        This does not copy or output the source text. It only defines what kinds
        of abstract features the system should learn later: pacing, character
        arcs, scene structure, worldbuilding density, dialogue dynamics, etc.
        """

        hooks = []
        for goal in learning_goals:
            hook = self.create_ml_learning_hook(
                hook_id=f"hook_{corpus_id}_{self._safe_id(goal)}",
                hook_type=self._hook_type_from_goal(goal),
                source_type="pdf_corpus",
                source_id=corpus_id,
                learning_target=goal,
                extracted_features={
                    "document_ids": document_ids,
                    "allowed_learning_scope": allowed_learning_scope or [
                        "abstract style features",
                        "story structure patterns",
                        "character arc patterns",
                        "worldbuilding density patterns",
                        "dialogue rhythm patterns",
                        "pacing and tension patterns",
                    ],
                    "excluded_learning_scope": excluded_learning_scope or [
                        "verbatim text reproduction",
                        "copyrighted passage memorization",
                        "direct character copying unless user owns/permits",
                    ],
                },
                evaluation_metrics={
                    "abstraction_safety": 0.9,
                    "feature_usefulness": 0.75,
                    "human_review_need": 0.45,
                },
                confidence=0.7,
                requires_human_review=True,
                metadata={"user_notes": user_notes},
            )
            hooks.append(hook)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "corpus_id": corpus_id,
            "document_ids": document_ids,
            "learning_hooks": hooks,
            "safety_contract": {
                "do_not_reproduce_source_verbatim": True,
                "learn_abstract_patterns_only": True,
                "track_source_document_ids": True,
                "require_human_review_for_style_transfer": True,
                "support_user_owned_or_permitted_references": True,
            },
        }

    def build_adaptation_plan(
        self,
        *,
        plan_id: str,
        story_request: Dict[str, Any],
        source_payload: Dict[str, Any],
        target_formats: List[str],
    ) -> Dict[str, Any]:
        adaptations = []
        for target_format in target_formats:
            profile = self.create_adaptation_profile(
                adaptation_id=f"{plan_id}_{target_format}",
                output_format=target_format,
                target_length=story_request.get("target_length"),
                pov_mode=story_request.get("pov_mode", "third_person_limited"),
                prose_density=story_request.get("prose_density", 0.6),
                dialogue_density=story_request.get("dialogue_density", 0.5),
                visuality_target=0.85 if target_format in {"movie", "screenplay", "comic_scene"} else 0.45,
                interiority_target=0.85 if target_format in {"novel", "chapter"} else 0.35,
            )
            adaptations.append(profile)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "plan_id": plan_id,
            "source_payload_id": source_payload.get("payload_id"),
            "target_formats": target_formats,
            "adaptation_profiles": adaptations,
            "adaptation_rules": {
                "preserve_core_causal_chain": True,
                "preserve_core_character_arcs": True,
                "allow_scene_compression": True,
                "allow_scene_expansion": True,
                "preserve_user_intent": True,
                "format_specific_rewrite_required": True,
            },
            "warnings": self._adaptation_plan_warnings(target_formats),
        }

    def register_generation_control_on_state(
        self,
        *,
        state: Any,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        payload_id = payload["payload_id"]
        state.metadata.setdefault("generation_control_payloads", {})[payload_id] = dict(payload)
        state.metadata.setdefault("generation_control_history", []).append(
            {
                "action": "register_generation_control",
                "payload_id": payload_id,
                "output_format": payload.get("adaptation_profile", {}).get("output_format"),
                "primary_genres": payload.get("genre_profile", {}).get("primary_genres", []),
                "hook_count": len(payload.get("learning_hooks", [])),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload_id": payload_id,
            "updated_state": state,
        }

    def build_generation_control_map(self, *, state: Any) -> Dict[str, Any]:
        records = state.metadata.get("generation_control_payloads", {})
        compact = {}

        for payload_id, payload in records.items():
            compact[payload_id] = {
                "payload_id": payload_id,
                "output_format": payload.get("adaptation_profile", {}).get("output_format"),
                "primary_genres": payload.get("genre_profile", {}).get("primary_genres", []),
                "tone_tags": payload.get("genre_profile", {}).get("tone_tags", []),
                "learning_hook_count": len(payload.get("learning_hooks", [])),
                "anti_genericity_required": payload.get("anti_genericity_contract", {}).get("must_avoid_generic_plot", True),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "payload_count": len(compact),
            "generation_control_records": compact,
            "warnings": [] if compact else ["no generation control payloads registered"],
        }

    def _generation_rules(
        self,
        *,
        story_request: Dict[str, Any],
        genre_profile: Dict[str, Any],
        adaptation_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "primary_genres": genre_profile.get("primary_genres", []),
            "secondary_genres": genre_profile.get("secondary_genres", []),
            "tone_tags": genre_profile.get("tone_tags", []),
            "avoid_tags": genre_profile.get("taboo_or_avoid_tags", []),
            "output_format": adaptation_profile.get("output_format"),
            "pov_mode": adaptation_profile.get("pov_mode"),
            "target_length": adaptation_profile.get("target_length"),
            "must_follow_user_wants": True,
            "must_not_force_fixed_character_count": True,
            "character_count_policy": "use as many or as few characters as the story needs",
            "character_source_policy": "mix user-supplied and project-created characters when useful",
            "requested_user_constraints": story_request.get("constraints", {}),
        }

    def _format_contract(self, output_format: str, adaptation_profile: Dict[str, Any]) -> Dict[str, Any]:
        base = {
            "output_format": output_format,
            "act_structure": adaptation_profile.get("act_structure"),
            "format_constraints": adaptation_profile.get("format_constraints", {}),
        }

        if output_format in {"movie", "screenplay"}:
            base.update(
                {
                    "must_be_visual": True,
                    "must_use_scene_beats": True,
                    "dialogue_should_be_performable": True,
                    "avoid_long_internal_monologue": True,
                }
            )
        elif output_format in {"novel", "chapter", "short_story"}:
            base.update(
                {
                    "must_include_interiority": True,
                    "must_use_prose_rhythm": True,
                    "dialogue_can_include_internal_subtext": True,
                    "worldbuilding_can_be_textural": True,
                }
            )
        elif output_format in {"series", "series_episode", "season_outline"}:
            base.update(
                {
                    "must_track_a_b_plots": True,
                    "must_support_episode_hooks": True,
                    "must_preserve_long_arc_memory": True,
                }
            )
        else:
            base.update({"must_preserve_requested_format": True})

        return base

    def _quality_contract(
        self,
        genre_profile: Dict[str, Any],
        adaptation_profile: Dict[str, Any],
        learning_hooks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            "character_specificity_target": 0.85,
            "causal_coherence_target": 0.90,
            "emotional_continuity_target": 0.85,
            "genre_adherence_target": 0.80,
            "format_adherence_target": 0.85,
            "anti_genericity_target": 0.85,
            "style_learning_hook_count": len([h for h in learning_hooks if h.get("hook_type") == "style_profile"]),
            "requires_eval_report": True,
        }

    def _anti_genericity_contract(self, story_request: Dict[str, Any], genre_profile: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "must_avoid_generic_plot": True,
            "must_use_specific_character_wounds": True,
            "must_use_specific_world_rules": True,
            "must_make_relationships_non_interchangeable": True,
            "must_include_causal_consequences": True,
            "must_respect_unique_user_wants": True,
            "requested_distinctive_elements": story_request.get("distinctive_elements", []),
            "genre_twist_targets": genre_profile.get("convention_targets", {}).get("twist_targets", []),
        }

    def _default_structure(self, output_format: str) -> str:
        return {
            "movie": "three_act_feature",
            "screenplay": "scene_sequence_feature",
            "novel": "chapter_arc_novel",
            "chapter": "scene_turn_chapter",
            "series": "season_long_arc",
            "series_episode": "teaser_a_plot_b_plot_resolution",
            "season_outline": "episode_by_episode_escalation",
            "franchise_outline": "multi_installment_arc",
            "short_story": "compressed_reversal_arc",
            "game_scene": "choice_consequence_scene",
            "comic_scene": "visual_panel_sequence",
            "treatment": "prose_screen_treatment",
        }.get(output_format, "general_story_structure")

    def _format_constraints(self, output_format: str) -> Dict[str, Any]:
        return {
            "novel": {"allow_interiority": True, "require_scene_prose": True},
            "chapter": {"allow_interiority": True, "require_chapter_turn": True},
            "movie": {"require_visual_beats": True, "compress_internal_monologue": True},
            "screenplay": {"require_scene_headings": True, "require_action_lines": True},
            "series_episode": {"require_episode_hook": True, "track_a_b_plots": True},
            "season_outline": {"require_episode_breakdown": True},
            "comic_scene": {"require_visual_panel_logic": True},
            "game_scene": {"require_choice_points": True},
        }.get(output_format, {"preserve_requested_format": True})

    def _hook_type_from_goal(self, goal: str) -> str:
        lower = goal.lower()
        if "style" in lower or "voice" in lower or "prose" in lower:
            return "style_profile"
        if "character" in lower:
            return "character_pattern"
        if "world" in lower:
            return "worldbuilding_pattern"
        if "plot" in lower or "structure" in lower:
            return "plot_structure_pattern"
        if "dialogue" in lower:
            return "dialogue_pattern"
        if "pacing" in lower or "tension" in lower:
            return "scene_pacing_pattern"
        if "emotion" in lower:
            return "emotional_arc_pattern"
        return "reference_work_profile"

    def _generation_control_warnings(self, payload: Dict[str, Any]) -> List[str]:
        warnings = []
        if not payload.get("genre_profile", {}).get("primary_genres"):
            warnings.append("generation control has no primary genre")
        if not payload.get("adaptation_profile", {}).get("output_format"):
            warnings.append("generation control has no output format")
        if payload.get("adaptation_profile", {}).get("output_format") == "screenplay":
            if payload.get("adaptation_profile", {}).get("interiority_target", 0.0) > 0.7:
                warnings.append("screenplay interiority target is high; convert interiority to visual behavior")
        return warnings

    def _adaptation_plan_warnings(self, target_formats: List[str]) -> List[str]:
        warnings = []
        if not target_formats:
            warnings.append("no target formats requested")
        unknown = [fmt for fmt in target_formats if fmt not in self.OUTPUT_FORMATS]
        if unknown:
            warnings.append(f"unknown target formats will use default profile: {unknown}")
        return warnings

    def _safe_id(self, text: str) -> str:
        cleaned = "".join(char.lower() if char.isalnum() else "_" for char in text)
        return cleaned.strip("_")[:80] or "goal"

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _unique(self, values: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for value in values:
            if value is None:
                continue
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result
