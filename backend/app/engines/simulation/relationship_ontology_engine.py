from typing import Any, Dict, List, Tuple


class RelationshipOntologyEngine:
    """Classifies relationship dynamics into story-useful relationship families.

    This avoids generic labels and gives later simulation, plot, scene, genre,
    and prose engines a richer relationship contract.
    """

    engine_name = "simulation.relationship_ontology_engine"

    def classify_relationship(
        self,
        *,
        character_a: Dict[str, Any],
        character_b: Dict[str, Any],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        world = world_context or {}
        dna = story_dna or {}
        intent = user_intent or {}

        a = self._flatten(character_a)
        b = self._flatten(character_b)

        a_id = str(a.get("character_id") or character_a.get("character_id") or "character_a")
        b_id = str(b.get("character_id") or character_b.get("character_id") or "character_b")

        axes = self._score_axes(a, b, world, dna, intent)
        family = self._select_family(axes, world, intent)
        subtype = self._select_subtype(family, axes, world, dna, intent)

        rupture_triggers = self._rupture_triggers(family, axes)
        repair_conditions = self._repair_conditions(family, axes)
        event_fuel = self._event_fuel(family, subtype, axes)
        simulation_hooks = self._simulation_hooks(family, subtype, axes)

        result = {
            "success": True,
            "engine_name": self.engine_name,
            "relationship_id": self._relationship_id(a_id, b_id),
            "character_a_id": a_id,
            "character_b_id": b_id,
            "relationship_family": family,
            "relationship_subtype": subtype,
            "relationship_label": f"{family}:{subtype}",
            "ontology_axes": axes,
            "initial_state_recommendation": self._initial_state_recommendation(family, axes),
            "rupture_triggers": rupture_triggers,
            "repair_conditions": repair_conditions,
            "event_fuel": event_fuel,
            "simulation_hooks": simulation_hooks,
            "genre_uses": self._genre_uses(family, subtype, intent),
            "warnings": self._warnings(axes),
        }

        return result

    def classify_relationship_set(
        self,
        *,
        character_profiles: List[Dict[str, Any]],
        world_context: Dict[str, Any] | None = None,
        story_dna: Dict[str, Any] | None = None,
        user_intent: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        records = []

        for i, char_a in enumerate(character_profiles):
            for j, char_b in enumerate(character_profiles):
                if j <= i:
                    continue
                records.append(
                    self.classify_relationship(
                        character_a=char_a,
                        character_b=char_b,
                        world_context=world_context,
                        story_dna=story_dna,
                        user_intent=user_intent,
                    )
                )

        family_counts: Dict[str, int] = {}
        for record in records:
            family = record["relationship_family"]
            family_counts[family] = family_counts.get(family, 0) + 1

        return {
            "success": True,
            "engine_name": self.engine_name,
            "character_count": len(character_profiles),
            "relationship_count": len(records),
            "family_counts": family_counts,
            "relationship_ontology_records": records,
            "ensemble_relationship_ready": bool(records),
            "warnings": self._set_warnings(records),
        }

    def _score_axes(
        self,
        a: Dict[str, Any],
        b: Dict[str, Any],
        world: Dict[str, Any],
        dna: Dict[str, Any],
        intent: Dict[str, Any],
    ) -> Dict[str, Any]:
        class_gap = self._binary_diff(a.get("social_class"), b.get("social_class"))
        family_status_gap = self._binary_diff(a.get("family_name_status"), b.get("family_name_status"))
        wound_mirror = self._semantic_overlap(a.get("core_wound"), b.get("core_wound"))
        goal_collision = self._goal_collision(a, b)
        morality_gap = self._binary_diff(a.get("dominant_moral_value"), b.get("dominant_moral_value"))
        voice_contrast = self._binary_diff(a.get("voice_family"), b.get("voice_family"))
        power_contrast = self._binary_diff(a.get("skill_family"), b.get("skill_family"))
        status_pressure = self._status_pressure(a, b, world)
        secrecy_pressure = self._secrecy_pressure(world, dna, intent)
        romance_requested = self._contains_any(intent, ["romance", "slow burn", "slow-burn", "love interest"])
        rivalry_requested = self._contains_any(intent, ["rivalry", "rivals", "enemy", "enemies"])
        betrayal_requested = self._contains_any(intent, ["betrayal", "traitor", "backstab"])
        political_pressure = self._contains_any(world, ["court", "faction", "nobility", "institution", "academy", "guild"])

        chemistry_score = round(min(1.0, 0.18 + class_gap * 0.18 + wound_mirror * 0.18 + voice_contrast * 0.16 + status_pressure * 0.18 + romance_requested * 0.2), 3)
        conflict_score = round(min(1.0, 0.2 + goal_collision * 0.25 + class_gap * 0.15 + morality_gap * 0.15 + rivalry_requested * 0.18 + political_pressure * 0.12), 3)
        trust_risk = round(min(1.0, 0.15 + secrecy_pressure * 0.25 + family_status_gap * 0.15 + betrayal_requested * 0.25 + political_pressure * 0.12), 3)
        repair_potential = round(min(1.0, 0.25 + wound_mirror * 0.25 + chemistry_score * 0.25 + self._shared_need(a, b) * 0.2), 3)
        power_imbalance = round(min(1.0, class_gap * 0.35 + family_status_gap * 0.2 + political_pressure * 0.2 + power_contrast * 0.15), 3)

        return {
            "class_gap": class_gap,
            "family_status_gap": family_status_gap,
            "wound_mirror": wound_mirror,
            "goal_collision": goal_collision,
            "morality_gap": morality_gap,
            "voice_contrast": voice_contrast,
            "power_contrast": power_contrast,
            "status_pressure": status_pressure,
            "secrecy_pressure": secrecy_pressure,
            "political_pressure": political_pressure,
            "romance_requested": bool(romance_requested),
            "rivalry_requested": bool(rivalry_requested),
            "betrayal_requested": bool(betrayal_requested),
            "chemistry_score": chemistry_score,
            "conflict_score": conflict_score,
            "trust_risk": trust_risk,
            "repair_potential": repair_potential,
            "power_imbalance": power_imbalance,
        }

    def _select_family(self, axes: Dict[str, Any], world: Dict[str, Any], intent: Dict[str, Any]) -> str:
        if axes["betrayal_requested"] and axes["trust_risk"] >= 0.45:
            return "loyalty_under_betrayal_pressure"

        if axes["romance_requested"] and axes["status_pressure"] >= 0.45:
            return "romance_blocked_by_public_status"

        if axes["romance_requested"] and axes["chemistry_score"] >= 0.55 and axes["conflict_score"] >= 0.45:
            return "rivalry_with_romantic_subtext"

        if axes["rivalry_requested"] or (axes["conflict_score"] >= 0.55 and axes["chemistry_score"] >= 0.4):
            return "rivalry_with_hidden_respect"

        if axes["political_pressure"] >= 1 and axes["trust_risk"] >= 0.4:
            return "political_alliance_with_private_distrust"

        if axes["power_imbalance"] >= 0.55 and axes["repair_potential"] >= 0.45:
            return "mentor_bond_corrupted_by_legacy"

        if axes["wound_mirror"] >= 0.45:
            return "mirror_wound_bond"

        return "emergent_story_bond"

    def _select_subtype(
        self,
        family: str,
        axes: Dict[str, Any],
        world: Dict[str, Any],
        dna: Dict[str, Any],
        intent: Dict[str, Any],
    ) -> str:
        if family == "romance_blocked_by_public_status":
            if axes["secrecy_pressure"] >= 0.5:
                return "slow_burn_under_visibility_threat"
            return "status_gap_slow_burn"

        if family == "rivalry_with_romantic_subtext":
            return "respect_becomes_dangerous_intimacy"

        if family == "rivalry_with_hidden_respect":
            if axes["goal_collision"] >= 0.5:
                return "same_goal_opposite_method"
            return "respect_hidden_inside_competition"

        if family == "loyalty_under_betrayal_pressure":
            return "trust_tested_by_secret_leverage"

        if family == "political_alliance_with_private_distrust":
            return "public_alignment_private_threat"

        if family == "mentor_bond_corrupted_by_legacy":
            return "guidance_contaminated_by_old_failure"

        if family == "mirror_wound_bond":
            return "same_wound_different_mask"

        return "undefined_but_expandable"

    def _initial_state_recommendation(self, family: str, axes: Dict[str, Any]) -> Dict[str, float]:
        state = {
            "trust": 0.25,
            "affection": 0.15,
            "respect": 0.25,
            "fear": 0.05,
            "envy": 0.05,
            "loyalty": 0.05,
            "debt": 0.0,
            "resentment": 0.1,
            "romantic_tension": 0.0,
            "rivalry": 0.1,
            "dependency": 0.0,
            "power_imbalance": axes["power_imbalance"],
            "knowledge_asymmetry": axes["trust_risk"],
            "repair_potential": axes["repair_potential"],
            "betrayal_risk": axes["trust_risk"],
        }

        if family in {"romance_blocked_by_public_status", "rivalry_with_romantic_subtext"}:
            state["romantic_tension"] = max(0.25, axes["chemistry_score"] * 0.6)
            state["resentment"] = max(state["resentment"], 0.2)
            state["respect"] = max(state["respect"], 0.35)

        if "rivalry" in family:
            state["rivalry"] = max(0.45, axes["conflict_score"])
            state["respect"] = max(state["respect"], 0.45)

        if "political" in family:
            state["trust"] = min(state["trust"], 0.18)
            state["power_imbalance"] = max(state["power_imbalance"], 0.45)

        if "betrayal" in family:
            state["betrayal_risk"] = max(state["betrayal_risk"], 0.55)
            state["knowledge_asymmetry"] = max(state["knowledge_asymmetry"], 0.45)

        return {key: round(float(value), 3) for key, value in state.items()}

    def _rupture_triggers(self, family: str, axes: Dict[str, Any]) -> List[str]:
        triggers = ["public humiliation", "withheld truth", "broken promise"]

        if "romance" in family:
            triggers.extend(["public status exposure", "misread sacrifice", "forced alliance with rival"])
        if "rivalry" in family:
            triggers.extend(["victory stolen", "respect denied publicly", "same goal forced into competition"])
        if "betrayal" in family:
            triggers.extend(["secret leverage revealed", "blackmail pressure", "protective lie exposed"])
        if "political" in family:
            triggers.extend(["public vote reversal", "faction order", "legal testimony conflict"])

        return list(dict.fromkeys(triggers))

    def _repair_conditions(self, family: str, axes: Dict[str, Any]) -> List[str]:
        conditions = ["truth disclosure with cost", "visible consequence", "choice that protects the other without reward"]

        if "romance" in family:
            conditions.extend(["private vulnerability", "public defense despite status cost"])
        if "rivalry" in family:
            conditions.extend(["earned respect under pressure", "shared danger forces cooperation"])
        if "betrayal" in family:
            conditions.extend(["confession before exposure", "debt repayment", "proof of changed priority"])
        if "political" in family:
            conditions.extend(["risking faction position", "protecting testimony instead of reputation"])

        return list(dict.fromkeys(conditions))

    def _event_fuel(self, family: str, subtype: str, axes: Dict[str, Any]) -> List[str]:
        events = ["private_confession", "public_humiliation", "promise_made"]

        if "romance" in family:
            events.extend(["romantic_boundary_crossing", "social_duel", "rescue"])
        if "rivalry" in family:
            events.extend(["ranking_challenge", "social_duel", "forced_teamwork"])
        if "betrayal" in family:
            events.extend(["blackmail_attempt", "promise_broken", "secret_discovery"])
        if "political" in family:
            events.extend(["trial", "faction_order", "negotiation_offer"])

        return list(dict.fromkeys(events))

    def _simulation_hooks(self, family: str, subtype: str, axes: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "relationship_arc_seed": family,
            "initial_delta_sensitivity": {
                "trust": 0.8 if axes["trust_risk"] >= 0.5 else 0.45,
                "romantic_tension": 0.8 if "romance" in family else 0.25,
                "rivalry": 0.75 if "rivalry" in family else 0.25,
                "respect": 0.65 if axes["conflict_score"] >= 0.45 else 0.35,
            },
            "must_track": [
                "trust",
                "respect",
                "betrayal_risk",
                "knowledge_asymmetry",
                "repair_potential",
            ],
            "recommended_validators": [
                "relationship_jump_limit",
                "no_romance_without_pressure",
                "no_betrayal_without_trigger",
                "repair_requires_cost",
            ],
        }

    def _genre_uses(self, family: str, subtype: str, intent: Dict[str, Any]) -> List[str]:
        uses = []
        text = self._joined(intent)

        if "romance" in text or "romance" in family:
            uses.append("slow_burn_romance_arc")
        if "mystery" in text or "secret" in subtype:
            uses.append("secret_as_relationship_pressure")
        if "political" in text or "political" in family:
            uses.append("faction_relationship_pressure")
        if "dark" in text or "academy" in text:
            uses.append("status_and_reputation_pressure")

        if not uses:
            uses.append("general_story_simulation_arc")

        return list(dict.fromkeys(uses))

    def _warnings(self, axes: Dict[str, Any]) -> List[str]:
        warnings = []
        if axes["chemistry_score"] < 0.25 and axes["conflict_score"] < 0.25:
            warnings.append("relationship has low chemistry and low conflict; may need stronger contrast or shared pressure")
        if axes["romance_requested"] and axes["chemistry_score"] < 0.35:
            warnings.append("romance requested but chemistry score is weak; add contrast, vulnerability, or pressure")
        if axes["trust_risk"] > 0.75 and axes["repair_potential"] < 0.35:
            warnings.append("high betrayal risk with low repair potential; relationship may rupture permanently")
        return warnings

    def _set_warnings(self, records: List[Dict[str, Any]]) -> List[str]:
        warnings = []
        if not records:
            warnings.append("no relationships classified")
            return warnings

        generic_count = sum(1 for item in records if item["relationship_family"] == "emergent_story_bond")
        if generic_count / max(1, len(records)) > 0.6:
            warnings.append("too many generic relationship families; ensemble may need stronger contrast/pressure")

        return warnings

    def _binary_diff(self, a: Any, b: Any) -> float:
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
        return min(1.0, len(a_words & b_words) / max(1, min(len(a_words), len(b_words))))

    def _goal_collision(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        a_goal = str(a.get("surface_goal") or a.get("hidden_goal") or "").lower()
        b_goal = str(b.get("surface_goal") or b.get("hidden_goal") or "").lower()

        if not a_goal or not b_goal:
            return 0.0

        collision_terms = ["ranking", "truth", "power", "inheritance", "survive", "protect", "court", "academy"]
        shared = sum(1 for term in collision_terms if term in a_goal and term in b_goal)

        return min(1.0, shared * 0.35)

    def _status_pressure(self, a: Dict[str, Any], b: Dict[str, Any], world: Dict[str, Any]) -> float:
        class_gap = self._binary_diff(a.get("social_class"), b.get("social_class"))
        family_gap = self._binary_diff(a.get("family_name_status"), b.get("family_name_status"))
        world_text = self._joined(world)
        world_pressure = 1.0 if any(token in world_text for token in ["class", "status", "nobility", "rank", "public names"]) else 0.0
        return min(1.0, class_gap * 0.35 + family_gap * 0.25 + world_pressure * 0.4)

    def _secrecy_pressure(self, world: Dict[str, Any], dna: Dict[str, Any], intent: Dict[str, Any]) -> float:
        text = " ".join([self._joined(world), self._joined(dna), self._joined(intent)])
        count = sum(1 for token in ["secret", "truth", "lie", "witness", "court", "hidden", "betrayal"] if token in text)
        return min(1.0, count * 0.18)

    def _shared_need(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        a_need = str(a.get("true_need") or "").lower()
        b_need = str(b.get("true_need") or "").lower()
        if not a_need or not b_need:
            return 0.0
        return self._semantic_overlap(a_need, b_need)

    def _contains_any(self, value: Any, tokens: List[str]) -> int:
        text = self._joined(value)
        return 1 if any(token in text for token in tokens) else 0

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

    def _relationship_id(self, a_id: str, b_id: str) -> str:
        ordered = sorted([a_id, b_id])
        return "rel_" + "_".join(ordered)
