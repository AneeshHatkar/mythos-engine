from typing import Any, Dict, List


class OppositeNatureChemistryEngine:
    """Scores character chemistry through contrast, mirror wounds, pressure, and story use.

    This engine helps MythOS choose relationships/casts that feel emotionally charged
    instead of random. It is also useful later for cast selection and ensemble optimization.
    """

    engine_name = "simulation.opposite_nature_chemistry_engine"

    AXES = [
        "core_wound",
        "surface_goal",
        "hidden_goal",
        "true_need",
        "dominant_moral_value",
        "social_class",
        "family_name_status",
        "skill_family",
        "voice_family",
        "relationship_readiness_family",
        "destiny_status",
        "public_mask",
        "private_truth",
        "symbolic_role",
    ]

    def compare_characters(
        self,
        *,
        character_a: Dict[str, Any],
        character_b: Dict[str, Any],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        a = self._flatten(character_a)
        b = self._flatten(character_b)
        world = world_context or {}
        dna = story_dna or {}
        intent = user_intent or {}

        a_id = str(a.get("character_id") or character_a.get("character_id") or "character_a")
        b_id = str(b.get("character_id") or character_b.get("character_id") or "character_b")

        axis_report = self._axis_report(a, b)
        contrast_score = self._contrast_score(axis_report)
        mirror_score = self._mirror_score(a, b)
        pressure_score = self._pressure_score(a, b, world, dna, intent)
        goal_collision_score = self._goal_collision_score(a, b)
        status_gap_score = self._status_gap_score(a, b, world)
        voice_chemistry_score = self._voice_chemistry_score(a, b)
        power_interaction_score = self._power_interaction_score(a, b)
        backstory_interlock_score = self._backstory_interlock_score(a, b, world)

        chemistry_score = round(
            min(
                1.0,
                0.18 * contrast_score
                + 0.16 * mirror_score
                + 0.18 * pressure_score
                + 0.12 * voice_chemistry_score
                + 0.12 * power_interaction_score
                + 0.14 * backstory_interlock_score
                + 0.10 * self._intent_bonus(intent, ["romance", "chemistry", "slow burn", "love interest"]),
            ),
            3,
        )

        conflict_score = round(
            min(
                1.0,
                0.22 * contrast_score
                + 0.22 * goal_collision_score
                + 0.18 * status_gap_score
                + 0.16 * pressure_score
                + 0.12 * self._intent_bonus(intent, ["rivalry", "enemies", "political", "conflict"])
                + 0.10 * power_interaction_score,
            ),
            3,
        )

        romance_potential = round(
            min(
                1.0,
                0.28 * chemistry_score
                + 0.18 * pressure_score
                + 0.16 * mirror_score
                + 0.14 * voice_chemistry_score
                + 0.14 * self._intent_bonus(intent, ["romance", "slow burn", "love interest"])
                + 0.10 * status_gap_score,
            ),
            3,
        )

        rivalry_potential = round(
            min(
                1.0,
                0.30 * conflict_score
                + 0.18 * goal_collision_score
                + 0.18 * contrast_score
                + 0.14 * status_gap_score
                + 0.12 * power_interaction_score
                + 0.08 * self._intent_bonus(intent, ["rivalry", "rivals", "enemy"]),
            ),
            3,
        )

        betrayal_risk = round(
            min(
                1.0,
                0.22 * pressure_score
                + 0.20 * status_gap_score
                + 0.18 * goal_collision_score
                + 0.18 * self._secrecy_score(world, dna, intent)
                + 0.12 * self._intent_bonus(intent, ["betrayal", "blackmail", "secret"])
                + 0.10 * (1.0 - mirror_score),
            ),
            3,
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "pair_id": self._pair_id(a_id, b_id),
            "character_a_id": a_id,
            "character_b_id": b_id,
            "axis_report": axis_report,
            "contrast_score": contrast_score,
            "mirror_score": mirror_score,
            "pressure_score": pressure_score,
            "goal_collision_score": goal_collision_score,
            "status_gap_score": status_gap_score,
            "voice_chemistry_score": voice_chemistry_score,
            "power_interaction_score": power_interaction_score,
            "backstory_interlock_score": backstory_interlock_score,
            "chemistry_score": chemistry_score,
            "conflict_score": conflict_score,
            "romance_potential": romance_potential,
            "rivalry_potential": rivalry_potential,
            "betrayal_risk": betrayal_risk,
            "relationship_potential_label": self._potential_label(
                chemistry_score=chemistry_score,
                conflict_score=conflict_score,
                romance_potential=romance_potential,
                rivalry_potential=rivalry_potential,
                betrayal_risk=betrayal_risk,
            ),
            "rupture_triggers": self._rupture_triggers(
                conflict_score=conflict_score,
                betrayal_risk=betrayal_risk,
                status_gap_score=status_gap_score,
                goal_collision_score=goal_collision_score,
            ),
            "repair_conditions": self._repair_conditions(
                mirror_score=mirror_score,
                chemistry_score=chemistry_score,
                betrayal_risk=betrayal_risk,
            ),
            "scene_fuel": self._scene_fuel(
                chemistry_score=chemistry_score,
                conflict_score=conflict_score,
                romance_potential=romance_potential,
                rivalry_potential=rivalry_potential,
                betrayal_risk=betrayal_risk,
            ),
            "cast_selection_utility": self._cast_selection_utility(
                chemistry_score=chemistry_score,
                conflict_score=conflict_score,
                pressure_score=pressure_score,
                backstory_interlock_score=backstory_interlock_score,
            ),
            "warnings": self._warnings(
                chemistry_score=chemistry_score,
                conflict_score=conflict_score,
                romance_potential=romance_potential,
                rivalry_potential=rivalry_potential,
            ),
        }

    def compare_character_pool(
        self,
        *,
        character_profiles: List[Dict[str, Any]],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        pair_reports = []

        for i, a in enumerate(character_profiles):
            for j, b in enumerate(character_profiles):
                if j <= i:
                    continue
                pair_reports.append(
                    self.compare_characters(
                        character_a=a,
                        character_b=b,
                        world_context=world_context or {},
                        story_dna=story_dna or {},
                        user_intent=user_intent or {},
                    )
                )

        sorted_by_chemistry = sorted(pair_reports, key=lambda item: item["chemistry_score"], reverse=True)
        sorted_by_conflict = sorted(pair_reports, key=lambda item: item["conflict_score"], reverse=True)
        sorted_by_cast_utility = sorted(pair_reports, key=lambda item: item["cast_selection_utility"]["utility_score"], reverse=True)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_count": len(character_profiles),
            "pair_count": len(pair_reports),
            "pair_reports": pair_reports,
            "top_chemistry_pairs": sorted_by_chemistry[:10],
            "top_conflict_pairs": sorted_by_conflict[:10],
            "top_cast_selection_pairs": sorted_by_cast_utility[:10],
            "pool_summary": self._pool_summary(pair_reports),
            "warnings": self._pool_warnings(pair_reports),
        }

    def _axis_report(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        report = {}

        for axis in self.AXES:
            va = a.get(axis)
            vb = b.get(axis)
            both_present = va is not None and vb is not None
            same = both_present and str(va).lower() == str(vb).lower()
            different = both_present and not same
            report[axis] = {
                "a": va,
                "b": vb,
                "both_present": both_present,
                "same": same,
                "different": different,
                "semantic_overlap": self._semantic_overlap(va, vb),
            }

        return report

    def _contrast_score(self, axis_report: Dict[str, Any]) -> float:
        present = [item for item in axis_report.values() if item["both_present"]]
        if not present:
            return 0.0
        return round(sum(1 for item in present if item["different"]) / len(present), 3)

    def _mirror_score(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        wound = self._semantic_overlap(a.get("core_wound"), b.get("core_wound"))
        need = self._semantic_overlap(a.get("true_need"), b.get("true_need"))
        private_truth = self._semantic_overlap(a.get("private_truth"), b.get("private_truth"))
        symbolic = self._semantic_overlap(a.get("symbolic_role"), b.get("symbolic_role"))
        return round(min(1.0, wound * 0.35 + need * 0.30 + private_truth * 0.20 + symbolic * 0.15), 3)

    def _pressure_score(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
        world: Dict[str, Any],
        dna: Dict[str, Any],
        intent: Dict[str, Any],
    ) -> float:
        text = " ".join([self._joined(world), self._joined(dna), self._joined(intent)])
        terms = ["class", "status", "court", "academy", "faction", "secret", "trial", "rank", "nobility", "debt", "power"]
        world_pressure = min(1.0, sum(1 for term in terms if term in text) * 0.10)
        status_gap = self._status_gap_score(a, b, world)
        secrecy = self._secrecy_score(world, dna, intent)
        return round(min(1.0, world_pressure * 0.4 + status_gap * 0.35 + secrecy * 0.25), 3)

    def _goal_collision_score(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        a_text = f"{a.get('surface_goal', '')} {a.get('hidden_goal', '')}".lower()
        b_text = f"{b.get('surface_goal', '')} {b.get('hidden_goal', '')}".lower()
        if not a_text.strip() or not b_text.strip():
            return 0.0

        collision_terms = ["ranking", "truth", "power", "survive", "protect", "family", "court", "academy", "inheritance", "freedom"]
        shared = sum(1 for term in collision_terms if term in a_text and term in b_text)
        opposed = 0
        if "protect" in a_text and "expose" in b_text:
            opposed += 1
        if "protect" in b_text and "expose" in a_text:
            opposed += 1
        if "family" in a_text and "truth" in b_text:
            opposed += 1
        if "family" in b_text and "truth" in a_text:
            opposed += 1

        return round(min(1.0, shared * 0.18 + opposed * 0.22), 3)

    def _status_gap_score(self, a: Dict[str, Any], b: Dict[str, Any], world: Dict[str, Any]) -> float:
        social_gap = self._different(a.get("social_class"), b.get("social_class"))
        family_gap = self._different(a.get("family_name_status"), b.get("family_name_status"))
        world_text = self._joined(world)
        world_status = 1.0 if any(term in world_text for term in ["class", "status", "nobility", "rank", "public names"]) else 0.0
        return round(min(1.0, social_gap * 0.38 + family_gap * 0.28 + world_status * 0.34), 3)

    def _voice_chemistry_score(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        voice_gap = self._different(a.get("voice_family"), b.get("voice_family"))
        mask_gap = self._different(a.get("public_mask"), b.get("public_mask"))
        private_overlap = self._semantic_overlap(a.get("private_truth"), b.get("private_truth"))
        return round(min(1.0, voice_gap * 0.45 + mask_gap * 0.25 + private_overlap * 0.30), 3)

    def _power_interaction_score(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        skill_gap = self._different(a.get("skill_family"), b.get("skill_family"))
        destiny_gap = self._different(a.get("destiny_status"), b.get("destiny_status"))
        role_gap = self._different(a.get("symbolic_role"), b.get("symbolic_role"))
        return round(min(1.0, skill_gap * 0.45 + destiny_gap * 0.25 + role_gap * 0.30), 3)

    def _backstory_interlock_score(self, a: Dict[str, Any], b: Dict[str, Any], world: Dict[str, Any]) -> float:
        a_text = self._joined({
            "origin": a.get("origin_summary"),
            "family": a.get("family_pressure"),
            "wound": a.get("core_wound"),
            "memory": a.get("formative_memory_ids"),
        })
        b_text = self._joined({
            "origin": b.get("origin_summary"),
            "family": b.get("family_pressure"),
            "wound": b.get("core_wound"),
            "memory": b.get("formative_memory_ids"),
        })
        world_text = self._joined(world)

        overlap = self._semantic_overlap(a_text, b_text)
        shared_world_terms = sum(1 for term in ["academy", "court", "family", "rank", "debt", "secret", "relic"] if term in a_text and term in b_text and term in world_text)

        return round(min(1.0, overlap * 0.5 + shared_world_terms * 0.12), 3)

    def _secrecy_score(self, world: Dict[str, Any], dna: Dict[str, Any], intent: Dict[str, Any]) -> float:
        text = " ".join([self._joined(world), self._joined(dna), self._joined(intent)])
        return round(min(1.0, sum(1 for term in ["secret", "truth", "lie", "witness", "hidden", "betrayal", "blackmail"] if term in text) * 0.16), 3)

    def _potential_label(
        self,
        *,
        chemistry_score: float,
        conflict_score: float,
        romance_potential: float,
        rivalry_potential: float,
        betrayal_risk: float,
    ) -> str:
        if romance_potential >= 0.55 and rivalry_potential >= 0.45:
            return "high_heat_rivalry_romance"
        if betrayal_risk >= 0.55 and chemistry_score >= 0.35:
            return "dangerous_bond_with_betrayal_pressure"
        if conflict_score >= 0.55 and chemistry_score >= 0.35:
            return "high_conflict_high_chemistry"
        if romance_potential >= 0.5:
            return "romance_viable"
        if rivalry_potential >= 0.5:
            return "rivalry_viable"
        if chemistry_score < 0.25 and conflict_score < 0.25:
            return "low_story_charge"
        return "moderate_story_charge"

    def _rupture_triggers(
        self,
        *,
        conflict_score: float,
        betrayal_risk: float,
        status_gap_score: float,
        goal_collision_score: float,
    ) -> List[str]:
        triggers = []
        if betrayal_risk >= 0.35:
            triggers.extend(["secret exposure", "blackmail pressure", "protective lie discovered"])
        if status_gap_score >= 0.35:
            triggers.extend(["public status humiliation", "class boundary enforcement"])
        if goal_collision_score >= 0.35:
            triggers.extend(["same goal forced into opposition", "victory taken by the other"])
        if conflict_score >= 0.45:
            triggers.extend(["social duel", "public disagreement", "forced choice"])
        return list(dict.fromkeys(triggers or ["minor misunderstanding"]))

    def _repair_conditions(
        self,
        *,
        mirror_score: float,
        chemistry_score: float,
        betrayal_risk: float,
    ) -> List[str]:
        conditions = ["truth with cost"]
        if mirror_score >= 0.25:
            conditions.append("recognition of shared wound")
        if chemistry_score >= 0.35:
            conditions.append("private vulnerability")
        if betrayal_risk >= 0.35:
            conditions.extend(["accountability before exposure", "costly proof of changed priority"])
        conditions.append("choice that protects the other without public reward")
        return list(dict.fromkeys(conditions))

    def _scene_fuel(
        self,
        *,
        chemistry_score: float,
        conflict_score: float,
        romance_potential: float,
        rivalry_potential: float,
        betrayal_risk: float,
    ) -> List[str]:
        fuel = []
        if chemistry_score >= 0.35:
            fuel.append("charged private conversation")
        if conflict_score >= 0.35:
            fuel.append("public clash")
        if romance_potential >= 0.35:
            fuel.append("slow-burn boundary scene")
        if rivalry_potential >= 0.35:
            fuel.append("competition scene")
        if betrayal_risk >= 0.35:
            fuel.append("secret leverage scene")
        return fuel or ["low-pressure connective scene"]

    def _cast_selection_utility(
        self,
        *,
        chemistry_score: float,
        conflict_score: float,
        pressure_score: float,
        backstory_interlock_score: float,
    ) -> Dict[str, Any]:
        utility = round(min(1.0, chemistry_score * 0.28 + conflict_score * 0.28 + pressure_score * 0.24 + backstory_interlock_score * 0.20), 3)
        return {
            "utility_score": utility,
            "recommended_for_main_cast": utility >= 0.55,
            "recommended_for_side_cast": 0.35 <= utility < 0.55,
            "recommended_for_background": utility < 0.35,
            "selection_reason": self._selection_reason(utility),
        }

    def _selection_reason(self, utility: float) -> str:
        if utility >= 0.70:
            return "strong relationship engine fuel for main cast"
        if utility >= 0.55:
            return "useful main-cast relationship pressure"
        if utility >= 0.35:
            return "good side-cast or subplot utility"
        return "low immediate relationship utility unless user wants this character"

    def _warnings(
        self,
        *,
        chemistry_score: float,
        conflict_score: float,
        romance_potential: float,
        rivalry_potential: float,
    ) -> List[str]:
        warnings = []
        if chemistry_score < 0.25 and conflict_score < 0.25:
            warnings.append("pair has low chemistry and low conflict")
        if romance_potential > 0.5 and chemistry_score < 0.35:
            warnings.append("romance potential depends more on premise than actual chemistry")
        if rivalry_potential > 0.5 and conflict_score < 0.35:
            warnings.append("rivalry potential needs stronger goal collision or pressure")
        return warnings

    def _pool_summary(self, pair_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not pair_reports:
            return {
                "average_chemistry": 0.0,
                "average_conflict": 0.0,
                "average_cast_utility": 0.0,
                "high_utility_pair_count": 0,
            }

        return {
            "average_chemistry": self._avg(pair_reports, "chemistry_score"),
            "average_conflict": self._avg(pair_reports, "conflict_score"),
            "average_romance_potential": self._avg(pair_reports, "romance_potential"),
            "average_rivalry_potential": self._avg(pair_reports, "rivalry_potential"),
            "average_betrayal_risk": self._avg(pair_reports, "betrayal_risk"),
            "average_cast_utility": round(
                sum(item["cast_selection_utility"]["utility_score"] for item in pair_reports) / len(pair_reports),
                3,
            ),
            "high_utility_pair_count": sum(1 for item in pair_reports if item["cast_selection_utility"]["utility_score"] >= 0.55),
        }

    def _pool_warnings(self, pair_reports: List[Dict[str, Any]]) -> List[str]:
        if not pair_reports:
            return ["empty character pool"]

        summary = self._pool_summary(pair_reports)
        warnings = []
        if summary["average_cast_utility"] < 0.25:
            warnings.append("character pool has weak relationship utility for the current story intent")
        if summary["high_utility_pair_count"] == 0:
            warnings.append("no high-utility chemistry/conflict pairs found")
        return warnings

    def _avg(self, records: List[Dict[str, Any]], field: str) -> float:
        return round(sum(float(item.get(field, 0.0) or 0.0) for item in records) / len(records), 3)

    def _intent_bonus(self, intent: Dict[str, Any], tokens: List[str]) -> float:
        text = self._joined(intent)
        return 1.0 if any(token in text for token in tokens) else 0.0

    def _different(self, a: Any, b: Any) -> float:
        if a is None or b is None:
            return 0.0
        return 0.0 if str(a).lower() == str(b).lower() else 1.0

    def _semantic_overlap(self, a: Any, b: Any) -> float:
        if not a or not b:
            return 0.0
        a_words = {word for word in str(a).lower().replace("_", " ").split() if len(word) > 3}
        b_words = {word for word in str(b).lower().replace("_", " ").split() if len(word) > 3}
        if not a_words or not b_words:
            return 0.0
        return round(min(1.0, len(a_words & b_words) / max(1, min(len(a_words), len(b_words)))), 3)

    def _joined(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._joined(v) for v in value.values()).lower()
        if isinstance(value, list):
            return " ".join(self._joined(v) for v in value).lower()
        return str(value or "").lower()

    def _flatten(self, value: Any) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}

        def walk(item: Any) -> None:
            if isinstance(item, dict):
                for key, val in item.items():
                    if key not in flat and not isinstance(val, (dict, list)):
                        flat[key] = val
                    walk(val)
            elif isinstance(item, list):
                for val in item:
                    walk(val)

        walk(value)
        return flat

    def _pair_id(self, a_id: str, b_id: str) -> str:
        return "pair_" + "_".join(sorted([a_id, b_id]))
