from typing import Any, Dict, List, Optional


class CastSelectionEngine:
    """Selects and optimizes casts for stories, arcs, scenes, and simulations.

    MythOS is not limited to 20 normal people or 27 destined people. The user can
    provide any number of characters, the project can generate thousands more,
    and this engine can select the best ensemble mix for the requested story.
    """

    engine_name = "simulation.cast_selection_engine"

    CHARACTER_ROLE_TYPES = {
        "protagonist",
        "deuteragonist",
        "antagonist",
        "villain",
        "rival",
        "mentor",
        "love_interest",
        "friend",
        "foil",
        "traitor",
        "wildcard",
        "comic_relief",
        "faction_leader",
        "witness",
        "victim",
        "agent_of_change",
        "destined_person",
        "ordinary_person",
        "created_character",
        "user_supplied_character",
    }

    STORY_FUNCTIONS = {
        "drive_plot",
        "create_conflict",
        "hold_secret",
        "reveal_truth",
        "test_loyalty",
        "break_pattern",
        "repair_relationship",
        "raise_stakes",
        "represent_faction",
        "anchor_romance",
        "provide_contrast",
        "create_mystery",
        "cause_betrayal",
        "offer_wisdom",
        "force_choice",
        "carry_emotional_core",
    }

    def create_cast_candidate(
        self,
        *,
        character_id: str,
        display_name: Optional[str] = None,
        role_tags: List[str] | None = None,
        story_function_tags: List[str] | None = None,
        source_type: str = "created_character",
        user_requested: bool = False,
        destined_weight: float = 0.0,
        normal_person_weight: float = 0.0,
        faction_ids: List[str] | None = None,
        romance_tags: List[str] | None = None,
        conflict_tags: List[str] | None = None,
        mystery_tags: List[str] | None = None,
        backstory_depth: float = 0.5,
        agency_score: float = 0.5,
        emotional_pressure: float = 0.5,
        social_influence: float = 0.5,
        relationship_density: float = 0.5,
        uniqueness_score: float = 0.5,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        normalized_roles = [role if role in self.CHARACTER_ROLE_TYPES else "created_character" for role in (role_tags or [])]
        normalized_functions = [
            function if function in self.STORY_FUNCTIONS else "drive_plot"
            for function in (story_function_tags or [])
        ]

        return {
            "character_id": character_id,
            "display_name": display_name or character_id,
            "role_tags": self._unique(normalized_roles),
            "story_function_tags": self._unique(normalized_functions),
            "source_type": source_type,
            "user_requested": bool(user_requested),
            "destined_weight": self._bounded(destined_weight),
            "normal_person_weight": self._bounded(normal_person_weight),
            "faction_ids": faction_ids or [],
            "romance_tags": romance_tags or [],
            "conflict_tags": conflict_tags or [],
            "mystery_tags": mystery_tags or [],
            "backstory_depth": self._bounded(backstory_depth),
            "agency_score": self._bounded(agency_score),
            "emotional_pressure": self._bounded(emotional_pressure),
            "social_influence": self._bounded(social_influence),
            "relationship_density": self._bounded(relationship_density),
            "uniqueness_score": self._bounded(uniqueness_score),
            "metadata": metadata or {},
        }

    def build_candidate_from_state(
        self,
        *,
        state: Any,
        character_id: str,
    ) -> Dict[str, Any]:
        character = state.character_states.get(character_id)
        if not character:
            return self.create_cast_candidate(
                character_id=character_id,
                display_name=character_id,
                role_tags=["created_character"],
                story_function_tags=["drive_plot"],
                metadata={"missing_from_state": True},
            )

        metadata = character.metadata or {}
        role_tags = metadata.get("role_tags", metadata.get("archetype_tags", []))
        story_functions = metadata.get("story_function_tags", [])
        source_type = metadata.get("source_type", "created_character")

        relationship_density = self._relationship_density_for_character(state, character_id)
        emotional_pressure = self._emotional_pressure_for_character(state, character_id)
        social_influence = self._social_influence_for_character(state, character_id)
        agency_score = self._agency_score_for_character(metadata)

        return self.create_cast_candidate(
            character_id=character_id,
            display_name=metadata.get("display_name") or metadata.get("name") or character_id,
            role_tags=role_tags or ["created_character"],
            story_function_tags=story_functions or self._infer_story_functions(metadata),
            source_type=source_type,
            user_requested=bool(metadata.get("user_requested", False)),
            destined_weight=float(metadata.get("destined_weight", 0.0)),
            normal_person_weight=float(metadata.get("normal_person_weight", 0.0)),
            faction_ids=metadata.get("faction_ids", []) + metadata.get("affiliation_ids", []),
            romance_tags=metadata.get("romance_tags", []),
            conflict_tags=metadata.get("conflict_tags", []),
            mystery_tags=metadata.get("mystery_tags", []),
            backstory_depth=float(metadata.get("backstory_depth", 0.5)),
            agency_score=agency_score,
            emotional_pressure=emotional_pressure,
            social_influence=social_influence,
            relationship_density=relationship_density,
            uniqueness_score=float(metadata.get("uniqueness_score", 0.5)),
            metadata=metadata,
        )

    def score_candidate_for_story(
        self,
        *,
        candidate: Dict[str, Any],
        story_request: Dict[str, Any] | None = None,
        required_roles: List[str] | None = None,
        required_story_functions: List[str] | None = None,
        preferred_faction_ids: List[str] | None = None,
        preferred_tone_tags: List[str] | None = None,
    ) -> Dict[str, Any]:
        request = story_request or {}
        required_roles = required_roles or request.get("required_roles", [])
        required_story_functions = required_story_functions or request.get("required_story_functions", [])
        preferred_faction_ids = preferred_faction_ids or request.get("preferred_faction_ids", [])
        preferred_tone_tags = preferred_tone_tags or request.get("tone_tags", [])

        role_fit = self._overlap_score(candidate.get("role_tags", []), required_roles)
        function_fit = self._overlap_score(candidate.get("story_function_tags", []), required_story_functions)
        faction_fit = self._overlap_score(candidate.get("faction_ids", []), preferred_faction_ids)
        tone_fit = self._tone_fit(candidate, preferred_tone_tags)

        user_bonus = 0.20 if candidate.get("user_requested") else 0.0
        source_bonus = 0.08 if candidate.get("source_type") == "user_supplied_character" else 0.04
        depth = candidate.get("backstory_depth", 0.5)
        agency = candidate.get("agency_score", 0.5)
        emotional = candidate.get("emotional_pressure", 0.5)
        social = candidate.get("social_influence", 0.5)
        density = candidate.get("relationship_density", 0.5)
        uniqueness = candidate.get("uniqueness_score", 0.5)

        requested_mode = request.get("character_mode", "mixed")
        mode_fit = self._mode_fit(candidate, requested_mode)

        score = round(
            min(
                1.0,
                role_fit * 0.16
                + function_fit * 0.18
                + faction_fit * 0.06
                + tone_fit * 0.06
                + depth * 0.10
                + agency * 0.10
                + emotional * 0.10
                + social * 0.08
                + density * 0.08
                + uniqueness * 0.08
                + mode_fit * 0.08
                + user_bonus
                + source_bonus,
            ),
            3,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_id": candidate.get("character_id"),
            "candidate": candidate,
            "cast_fit_score": score,
            "score_components": {
                "role_fit": role_fit,
                "function_fit": function_fit,
                "faction_fit": faction_fit,
                "tone_fit": tone_fit,
                "mode_fit": mode_fit,
                "backstory_depth": depth,
                "agency_score": agency,
                "emotional_pressure": emotional,
                "social_influence": social,
                "relationship_density": density,
                "uniqueness_score": uniqueness,
                "user_bonus": user_bonus,
                "source_bonus": source_bonus,
            },
            "warnings": self._candidate_warnings(candidate, score),
        }

    def select_cast(
        self,
        *,
        state: Any,
        story_request: Dict[str, Any],
        candidate_ids: List[str] | None = None,
        candidate_pool: List[Dict[str, Any]] | None = None,
        target_cast_size: Optional[int] = None,
        min_cast_size: int = 1,
        max_cast_size: Optional[int] = None,
        allow_any_size: bool = True,
    ) -> Dict[str, Any]:
        candidates = candidate_pool or []
        if not candidates:
            ids = candidate_ids or list(state.character_states.keys())
            candidates = [self.build_candidate_from_state(state=state, character_id=cid) for cid in ids]

        scored = [
            self.score_candidate_for_story(
                candidate=candidate,
                story_request=story_request,
            )
            for candidate in candidates
        ]

        ranked = sorted(scored, key=lambda item: item["cast_fit_score"], reverse=True)

        target_size = self._target_cast_size(
            ranked=ranked,
            story_request=story_request,
            target_cast_size=target_cast_size,
            min_cast_size=min_cast_size,
            max_cast_size=max_cast_size,
            allow_any_size=allow_any_size,
        )

        selected = self._select_balanced_cast(
            ranked=ranked,
            target_size=target_size,
            story_request=story_request,
        )

        selected_ids = [item["character_id"] for item in selected]

        ensemble_report = self.evaluate_ensemble_balance(
            selected_candidates=[item["candidate"] for item in selected],
            story_request=story_request,
        )

        cast_record = {
            "cast_id": story_request.get("cast_id", "cast_selection_latest"),
            "story_request_id": story_request.get("story_request_id"),
            "selected_character_ids": selected_ids,
            "selected_count": len(selected_ids),
            "allow_any_size": allow_any_size,
            "target_cast_size": target_size,
            "selected_candidates": selected,
            "ensemble_report": ensemble_report,
            "rejected_top_candidates": [
                item for item in ranked if item["character_id"] not in set(selected_ids)
            ][:10],
        }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "cast_record": cast_record,
            "warnings": self._selection_warnings(cast_record, story_request),
            "chunk5_handoff": self._chunk5_handoff(cast_record, story_request),
        }

    def evaluate_ensemble_balance(
        self,
        *,
        selected_candidates: List[Dict[str, Any]],
        story_request: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        request = story_request or {}
        role_counts: Dict[str, int] = {}
        function_counts: Dict[str, int] = {}
        faction_counts: Dict[str, int] = {}

        for candidate in selected_candidates:
            for role in candidate.get("role_tags", []):
                role_counts[role] = role_counts.get(role, 0) + 1
            for function in candidate.get("story_function_tags", []):
                function_counts[function] = function_counts.get(function, 0) + 1
            for faction in candidate.get("faction_ids", []):
                faction_counts[faction] = faction_counts.get(faction, 0) + 1

        diversity_score = self._diversity_score(selected_candidates, role_counts, function_counts, faction_counts)
        role_coverage = self._required_coverage(role_counts, request.get("required_roles", []))
        function_coverage = self._required_coverage(function_counts, request.get("required_story_functions", []))
        destined_mix = self._average([c.get("destined_weight", 0.0) for c in selected_candidates])
        ordinary_mix = self._average([c.get("normal_person_weight", 0.0) for c in selected_candidates])
        user_supplied_count = sum(1 for c in selected_candidates if c.get("user_requested") or c.get("source_type") == "user_supplied_character")

        ensemble_score = round(
            min(
                1.0,
                diversity_score * 0.28
                + role_coverage * 0.20
                + function_coverage * 0.20
                + self._average([c.get("relationship_density", 0.5) for c in selected_candidates]) * 0.12
                + self._average([c.get("emotional_pressure", 0.5) for c in selected_candidates]) * 0.10
                + self._average([c.get("uniqueness_score", 0.5) for c in selected_candidates]) * 0.10,
            ),
            3,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "selected_count": len(selected_candidates),
            "role_counts": role_counts,
            "function_counts": function_counts,
            "faction_counts": faction_counts,
            "diversity_score": diversity_score,
            "role_coverage": role_coverage,
            "function_coverage": function_coverage,
            "destined_mix_score": destined_mix,
            "ordinary_mix_score": ordinary_mix,
            "user_supplied_count": user_supplied_count,
            "ensemble_score": ensemble_score,
            "warnings": self._ensemble_warnings(selected_candidates, role_counts, function_counts, request),
        }

    def optimize_cast_for_scene(
        self,
        *,
        state: Any,
        scene_request: Dict[str, Any],
        available_character_ids: List[str] | None = None,
    ) -> Dict[str, Any]:
        story_request = {
            "story_request_id": scene_request.get("scene_id"),
            "cast_id": f"cast_scene_{scene_request.get('scene_id', 'unknown')}",
            "required_roles": scene_request.get("required_roles", []),
            "required_story_functions": scene_request.get("required_story_functions", []),
            "preferred_faction_ids": scene_request.get("preferred_faction_ids", []),
            "tone_tags": scene_request.get("tone_tags", []),
            "character_mode": scene_request.get("character_mode", "mixed"),
            "format": scene_request.get("format", "scene"),
        }

        return self.select_cast(
            state=state,
            story_request=story_request,
            candidate_ids=available_character_ids,
            target_cast_size=scene_request.get("target_cast_size"),
            min_cast_size=scene_request.get("min_cast_size", 1),
            max_cast_size=scene_request.get("max_cast_size"),
            allow_any_size=scene_request.get("allow_any_size", True),
        )

    def register_cast_on_state(
        self,
        *,
        state: Any,
        cast_record: Dict[str, Any],
    ) -> Dict[str, Any]:
        cast_id = cast_record["cast_id"]
        state.metadata.setdefault("cast_registry", {})[cast_id] = dict(cast_record)
        state.metadata.setdefault("cast_selection_history", []).append(
            {
                "action": "register_cast",
                "cast_id": cast_id,
                "selected_count": cast_record.get("selected_count"),
                "selected_character_ids": cast_record.get("selected_character_ids", []),
                "ensemble_score": cast_record.get("ensemble_report", {}).get("ensemble_score"),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "cast_id": cast_id,
            "updated_state": state,
        }

    def build_cast_map(self, *, state: Any) -> Dict[str, Any]:
        registry = state.metadata.get("cast_registry", {})
        records = {}

        for cast_id, cast in registry.items():
            records[cast_id] = {
                "cast_id": cast_id,
                "story_request_id": cast.get("story_request_id"),
                "selected_character_ids": cast.get("selected_character_ids", []),
                "selected_count": cast.get("selected_count", 0),
                "ensemble_score": cast.get("ensemble_report", {}).get("ensemble_score", 0.0),
                "diversity_score": cast.get("ensemble_report", {}).get("diversity_score", 0.0),
                "role_coverage": cast.get("ensemble_report", {}).get("role_coverage", 0.0),
                "function_coverage": cast.get("ensemble_report", {}).get("function_coverage", 0.0),
            }

        ranked = sorted(records.values(), key=lambda item: item["ensemble_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "cast_count": len(records),
            "cast_records": records,
            "ranked_casts": ranked,
            "best_cast": ranked[0] if ranked else None,
            "warnings": self._cast_map_warnings(ranked),
        }

    def _select_balanced_cast(
        self,
        *,
        ranked: List[Dict[str, Any]],
        target_size: int,
        story_request: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        selected: List[Dict[str, Any]] = []
        selected_ids = set()

        required_roles = story_request.get("required_roles", [])
        required_functions = story_request.get("required_story_functions", [])

        # First: always protect explicitly user-requested characters when available.
        for item in ranked:
            candidate = item["candidate"]
            if candidate.get("user_requested") or candidate.get("source_type") == "user_supplied_character":
                selected.append(item)
                selected_ids.add(item["character_id"])
                if len(selected) >= target_size:
                    return selected

        # Second: cover required roles.
        for role in required_roles:
            if any(role in item["candidate"].get("role_tags", []) for item in selected):
                continue
            for item in ranked:
                if item["character_id"] in selected_ids:
                    continue
                if role in item["candidate"].get("role_tags", []):
                    selected.append(item)
                    selected_ids.add(item["character_id"])
                    break
            if len(selected) >= target_size:
                return selected

        # Third: cover story functions.
        for function in required_functions:
            if any(function in item["candidate"].get("story_function_tags", []) for item in selected):
                continue
            for item in ranked:
                if item["character_id"] in selected_ids:
                    continue
                if function in item["candidate"].get("story_function_tags", []):
                    selected.append(item)
                    selected_ids.add(item["character_id"])
                    break
            if len(selected) >= target_size:
                return selected

        # Fourth: fill with highest scoring candidates.
        for item in ranked:
            if item["character_id"] in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(item["character_id"])
            if len(selected) >= target_size:
                break

        return selected

    def _target_cast_size(
        self,
        *,
        ranked: List[Dict[str, Any]],
        story_request: Dict[str, Any],
        target_cast_size: Optional[int],
        min_cast_size: int,
        max_cast_size: Optional[int],
        allow_any_size: bool,
    ) -> int:
        if target_cast_size is not None:
            size = int(target_cast_size)
        else:
            format_name = story_request.get("format", "scene")
            if format_name in {"short_scene", "scene"}:
                size = min(5, len(ranked))
            elif format_name in {"movie", "feature_film"}:
                size = min(12, len(ranked))
            elif format_name in {"series", "season"}:
                size = min(18, len(ranked))
            elif format_name in {"novel", "book"}:
                size = min(16, len(ranked))
            elif format_name in {"epic", "saga", "multi_book", "franchise"}:
                size = min(30, len(ranked))
            else:
                size = min(10, len(ranked))

        size = max(min_cast_size, size)
        if max_cast_size is not None:
            size = min(size, int(max_cast_size))
        if not allow_any_size:
            size = max(min_cast_size, min(size, max_cast_size or size))

        return min(size, len(ranked))

    def _relationship_density_for_character(self, state: Any, character_id: str) -> float:
        if not state.relationship_states:
            return 0.0
        count = 0
        strength = 0.0
        for rel in state.relationship_states.values():
            if character_id in {rel.character_a_id, rel.character_b_id}:
                count += 1
                strength += rel.trust * 0.18 + rel.resentment * 0.16 + rel.rivalry * 0.16 + rel.affection * 0.14 + rel.betrayal_risk * 0.18 + rel.repair_potential * 0.18
        return round(min(1.0, count * 0.12 + strength * 0.25), 3)

    def _emotional_pressure_for_character(self, state: Any, character_id: str) -> float:
        records = [
            record
            for record in state.metadata.get("emotional_carryover_registry", {}).values()
            if record.get("character_id") == character_id and record.get("status") != "resolved"
        ]
        if not records:
            return 0.3
        return round(min(1.0, self._average([float(r.get("intensity", 0.0)) for r in records]) + len(records) * 0.05), 3)

    def _social_influence_for_character(self, state: Any, character_id: str) -> float:
        latest = state.metadata.get("social_graphs", {}).get("latest_social_graph")
        if latest:
            edges = [
                edge for edge in latest.get("edges", {}).values()
                if edge.get("source_id") == character_id or edge.get("target_id") == character_id
            ]
            return round(min(1.0, len(edges) * 0.08 + sum(float(edge.get("strength", 0.0)) for edge in edges) * 0.08), 3)

        character = state.character_states.get(character_id)
        if not character:
            return 0.3
        reputation = character.metadata.get("reputation_state", {})
        public = float(reputation.get("public", reputation.get("general", 0.3)) or 0.3)
        faction_bonus = min(0.3, len(character.metadata.get("faction_ids", [])) * 0.12)
        return round(min(1.0, public * 0.5 + faction_bonus + 0.25), 3)

    def _agency_score_for_character(self, metadata: Dict[str, Any]) -> float:
        if "agency_score" in metadata:
            return self._bounded(float(metadata["agency_score"]))
        if metadata.get("agency_constraints", {}).get("hard_limit_score"):
            return self._bounded(1.0 - float(metadata["agency_constraints"]["hard_limit_score"]))
        return 0.55

    def _infer_story_functions(self, metadata: Dict[str, Any]) -> List[str]:
        tags = set(metadata.get("role_tags", []) + metadata.get("archetype_tags", []))
        functions = []
        if tags.intersection({"antagonist", "villain", "rival"}):
            functions.extend(["create_conflict", "force_choice"])
        if tags.intersection({"love_interest"}):
            functions.append("anchor_romance")
        if tags.intersection({"mentor"}):
            functions.append("offer_wisdom")
        if tags.intersection({"traitor"}):
            functions.append("cause_betrayal")
        if tags.intersection({"destined_person"}):
            functions.extend(["drive_plot", "raise_stakes"])
        return functions or ["drive_plot"]

    def _overlap_score(self, values: List[str], required: List[str]) -> float:
        if not required:
            return 0.5
        if not values:
            return 0.0
        overlap = len(set(values).intersection(set(required)))
        return round(min(1.0, overlap / max(1, len(set(required)))), 3)

    def _tone_fit(self, candidate: Dict[str, Any], tone_tags: List[str]) -> float:
        if not tone_tags:
            return 0.5
        text = " ".join(
            candidate.get("role_tags", [])
            + candidate.get("story_function_tags", [])
            + candidate.get("romance_tags", [])
            + candidate.get("conflict_tags", [])
            + candidate.get("mystery_tags", [])
            + list(candidate.get("metadata", {}).get("tone_tags", []))
        ).lower()
        matches = sum(1 for tag in tone_tags if str(tag).lower() in text)
        return round(min(1.0, matches / max(1, len(tone_tags))), 3)

    def _mode_fit(self, candidate: Dict[str, Any], mode: str) -> float:
        mode = str(mode or "mixed").lower()
        if mode == "mixed":
            return 0.65
        if mode in {"destined", "destined_people"}:
            return candidate.get("destined_weight", 0.0)
        if mode in {"ordinary", "normal", "normal_people"}:
            return candidate.get("normal_person_weight", 0.0)
        if mode in {"user_supplied", "user_characters"}:
            return 1.0 if candidate.get("user_requested") or candidate.get("source_type") == "user_supplied_character" else 0.2
        if mode in {"created", "generated"}:
            return 1.0 if candidate.get("source_type") == "created_character" else 0.4
        return 0.5

    def _diversity_score(
        self,
        candidates: List[Dict[str, Any]],
        role_counts: Dict[str, int],
        function_counts: Dict[str, int],
        faction_counts: Dict[str, int],
    ) -> float:
        if not candidates:
            return 0.0
        role_diversity = min(1.0, len(role_counts) / max(1, len(candidates)))
        function_diversity = min(1.0, len(function_counts) / max(1, len(candidates)))
        faction_diversity = min(1.0, max(1, len(faction_counts)) / max(1, len(candidates)))
        source_diversity = min(1.0, len({c.get("source_type") for c in candidates}) / max(1, len(candidates)))
        return round(role_diversity * 0.35 + function_diversity * 0.35 + faction_diversity * 0.20 + source_diversity * 0.10, 3)

    def _required_coverage(self, counts: Dict[str, int], required: List[str]) -> float:
        if not required:
            return 0.6
        covered = sum(1 for item in required if counts.get(item, 0) > 0)
        return round(covered / max(1, len(set(required))), 3)

    def _candidate_warnings(self, candidate: Dict[str, Any], score: float) -> List[str]:
        warnings = []
        if score < 0.25:
            warnings.append(f"{candidate.get('character_id')} has low cast fit")
        if candidate.get("backstory_depth", 0.0) < 0.25:
            warnings.append(f"{candidate.get('character_id')} has shallow backstory")
        if not candidate.get("story_function_tags"):
            warnings.append(f"{candidate.get('character_id')} has no story function tags")
        return warnings

    def _ensemble_warnings(
        self,
        candidates: List[Dict[str, Any]],
        role_counts: Dict[str, int],
        function_counts: Dict[str, int],
        request: Dict[str, Any],
    ) -> List[str]:
        warnings = []
        if not candidates:
            warnings.append("selected cast is empty")
        if request.get("required_roles") and self._required_coverage(role_counts, request.get("required_roles", [])) < 1.0:
            warnings.append("not all required roles are covered")
        if request.get("required_story_functions") and self._required_coverage(function_counts, request.get("required_story_functions", [])) < 1.0:
            warnings.append("not all required story functions are covered")
        if len(candidates) > 25:
            warnings.append("large cast selected; use subgroups/scenes to avoid clutter")
        return warnings

    def _selection_warnings(self, cast_record: Dict[str, Any], story_request: Dict[str, Any]) -> List[str]:
        warnings = []
        warnings.extend(cast_record.get("ensemble_report", {}).get("warnings", []))
        if cast_record["selected_count"] == 0:
            warnings.append("no cast selected")
        if cast_record["selected_count"] < story_request.get("min_cast_size", 1):
            warnings.append("selected cast smaller than requested minimum")
        return self._unique(warnings)

    def _cast_map_warnings(self, ranked: List[Dict[str, Any]]) -> List[str]:
        if not ranked:
            return ["no casts registered"]
        if ranked[0].get("ensemble_score", 0.0) < 0.45:
            return ["best registered cast has weak ensemble score"]
        return []

    def _chunk5_handoff(self, cast_record: Dict[str, Any], story_request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "cast_id": cast_record.get("cast_id"),
            "selected_character_ids": cast_record.get("selected_character_ids", []),
            "selected_count": cast_record.get("selected_count", 0),
            "format": story_request.get("format"),
            "character_mode": story_request.get("character_mode", "mixed"),
            "scene_grouping_needed": cast_record.get("selected_count", 0) > 8,
            "ensemble_score": cast_record.get("ensemble_report", {}).get("ensemble_score"),
            "dominant_roles": cast_record.get("ensemble_report", {}).get("role_counts", {}),
            "dominant_functions": cast_record.get("ensemble_report", {}).get("function_counts", {}),
            "must_preserve_user_requested_characters": any(
                item["candidate"].get("user_requested") or item["candidate"].get("source_type") == "user_supplied_character"
                for item in cast_record.get("selected_candidates", [])
            ),
        }

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

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
