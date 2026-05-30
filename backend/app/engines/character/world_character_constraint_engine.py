from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldCharacterConstraintEngine(BaseEngine):
    """Maps Chunk 2 world constraints onto Chunk 3 character concepts.

    This engine prevents characters from becoming generic or logically detached
    from their world.

    It checks whether a character's class, origin, education, power access,
    faction position, destiny, rare skills, and adaptability exceptions fit the
    world rules.
    """

    engine_name = "character.world_character_constraint_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        character_seed = payload.get("character_seed", {})
        population_context = payload.get("population_context", {})
        people_type = payload.get("people_type", {})

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; constraint mapper used general defaults.")

        if not character_seed:
            warnings.append("No character_seed provided; constraint mapper evaluated an empty draft concept.")

        constraints = self._extract_world_constraints(world_state)
        checks = self._run_constraint_checks(
            constraints=constraints,
            character_seed=character_seed,
            population_context=population_context,
            people_type=people_type,
        )

        risk_summary = self._build_risk_summary(checks)
        repair_plan = self._build_repair_plan(checks, character_seed)
        grounding_profile = self._build_grounding_profile(
            constraints=constraints,
            checks=checks,
            character_seed=character_seed,
            people_type=people_type,
        )

        return self.build_result(
            success=True,
            data={
                "world_constraints": constraints,
                "constraint_checks": checks,
                "constraint_risk_summary": risk_summary,
                "repair_plan": repair_plan,
                "grounding_profile": grounding_profile,
                "training_notes": [
                    "World-to-character mapping keeps character outputs grounded in Chunk 2 systems.",
                    "Constraint failures are not always errors; they can become story hooks if explained.",
                    "Adaptability and limit-break exceptions must include condition, cost, risk, and consequence.",
                    "Later ML/RAG systems should learn this mapping from curated world-character pairs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _extract_world_constraints(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        world_text = str(world_state).lower()

        laws = world_state.get("law", {}) or world_state.get("rules", {})
        society = world_state.get("society", {})
        economy = world_state.get("economy", {})
        institutions = world_state.get("institutions", {}) or world_state.get("knowledge_education", {})
        belief = world_state.get("belief", {})
        culture = world_state.get("culture", {})
        technology = world_state.get("technology_magic_science", {})
        civilization_pressure = world_state.get("civilization_pressure", {})

        constraints = {
            "commoner_royal_magic_restricted": self._contains_any(
                world_text,
                ["commoners cannot legally study royal magic", "commoner", "royal magic", "forbidden magic"],
            ),
            "family_name_affects_legal_trust": self._contains_any(
                world_text,
                ["family names determine legal trust", "family name", "legal trust"],
            ),
            "noble_academy_gatekeeping": self._contains_any(
                world_text,
                ["noble academies", "academy", "elite institutions", "access to power"],
            ),
            "relic_economy_pressure": self._contains_any(
                world_text,
                ["relic", "relic-mining", "mining cities", "artifact economy"],
            ),
            "oath_religion_pressure": self._contains_any(
                world_text,
                ["oath-gods", "oath gods", "oath bell", "oath law", "ritual oath"],
            ),
            "underground_market_exists": self._contains_any(
                world_text,
                ["underground market", "black market", "illegal tutor", "false-name"],
            ),
            "border_ruins_exist": self._contains_any(
                world_text,
                ["border ruins", "ruins", "borderfolk", "frontier"],
            ),
            "destiny_pressure_high": self._contains_any(
                world_text,
                ["destiny-bearing", "destined people", "destiny pressure", "appearing too fast"],
            ),
            "law_summary": laws,
            "society_summary": society,
            "economy_summary": economy,
            "institution_summary": institutions,
            "belief_summary": belief,
            "culture_summary": culture,
            "technology_magic_summary": technology,
            "civilization_pressure_summary": civilization_pressure,
        }

        return constraints

    def _contains_any(self, text: str, terms: List[str]) -> bool:
        return any(term in text for term in terms)

    def _run_constraint_checks(
        self,
        *,
        constraints: Dict[str, Any],
        character_seed: Dict[str, Any],
        population_context: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        checks: List[Dict[str, Any]] = []

        social_class = self._field(character_seed, "social_class")
        desired_power = self._field(character_seed, "desired_power") or self._field(character_seed, "power")
        education_goal = self._field(character_seed, "education_goal") or self._field(character_seed, "institution_goal")
        family_name_status = self._field(character_seed, "family_name_status")
        skill_rarity = self._field(character_seed, "skill_rarity")
        destiny_type = self._field(character_seed, "destiny_type")
        adaptability_type = self._field(character_seed, "adaptability_type")
        role = self._field(character_seed, "role")
        origin_location = self._field(character_seed, "origin_location")

        checks.append(
            self._check_commoner_magic_access(
                constraints=constraints,
                social_class=social_class,
                desired_power=desired_power,
                education_goal=education_goal,
                character_seed=character_seed,
            )
        )

        checks.append(
            self._check_family_name_trust(
                constraints=constraints,
                family_name_status=family_name_status,
                social_class=social_class,
            )
        )

        checks.append(
            self._check_academy_access(
                constraints=constraints,
                social_class=social_class,
                education_goal=education_goal,
                people_type=people_type,
                character_seed=character_seed,
            )
        )

        checks.append(
            self._check_relic_economy_grounding(
                constraints=constraints,
                social_class=social_class,
                origin_location=origin_location,
                character_seed=character_seed,
            )
        )

        checks.append(
            self._check_oath_culture_grounding(
                constraints=constraints,
                character_seed=character_seed,
                role=role,
            )
        )

        checks.append(
            self._check_destiny_density(
                constraints=constraints,
                destiny_type=destiny_type,
                role=role,
                people_type=people_type,
            )
        )

        checks.append(
            self._check_rare_skill_cost(
                skill_rarity=skill_rarity,
                character_seed=character_seed,
            )
        )

        checks.append(
            self._check_adaptability_exception(
                adaptability_type=adaptability_type,
                character_seed=character_seed,
                people_type=people_type,
            )
        )

        checks.append(
            self._check_population_fit(
                social_class=social_class,
                population_context=population_context,
            )
        )

        return checks

    def _field(self, data: Dict[str, Any], key: str) -> Any:
        if key in data:
            return data[key]

        origin = data.get("origin", {})
        if isinstance(origin, dict) and key in origin:
            return origin[key]

        identity = data.get("identity", {})
        if isinstance(identity, dict) and key in identity:
            return identity[key]

        return None

    def _base_check(
        self,
        *,
        check_id: str,
        label: str,
        status: str,
        severity: str,
        explanation: str,
        required_fix: str | None = None,
        story_hook: str | None = None,
    ) -> Dict[str, Any]:
        return {
            "check_id": check_id,
            "label": label,
            "status": status,
            "severity": severity,
            "explanation": explanation,
            "required_fix": required_fix,
            "story_hook": story_hook,
        }

    def _check_commoner_magic_access(
        self,
        *,
        constraints: Dict[str, Any],
        social_class: Any,
        desired_power: Any,
        education_goal: Any,
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        text = f"{desired_power} {education_goal}".lower()
        is_commoner = str(social_class).lower() in {"commoner", "relic_miner", "underclass", "erased", "borderfolk"}
        wants_royal_magic = "royal magic" in text or "forbidden magic" in text

        if constraints["commoner_royal_magic_restricted"] and is_commoner and wants_royal_magic:
            explanation = character_seed.get("access_explanation") or character_seed.get("rule_exception_reason")

            if explanation:
                return self._base_check(
                    check_id="commoner_magic_access",
                    label="Commoner royal magic access",
                    status="explained_exception",
                    severity="medium",
                    explanation="Character violates normal magic access law but includes an explanation.",
                    story_hook="Forbidden education can become a legal, class, and institutional conflict.",
                )

            return self._base_check(
                check_id="commoner_magic_access",
                label="Commoner royal magic access",
                status="violation",
                severity="high",
                explanation="Commoner/low-trust character seeks restricted royal magic without explanation.",
                required_fix="Add sponsor, illegal tutor, forged name, hidden lineage, scholarship loophole, or underground access.",
                story_hook="The violation can become a major academy/legal conflict.",
            )

        return self._base_check(
            check_id="commoner_magic_access",
            label="Commoner royal magic access",
            status="pass",
            severity="none",
            explanation="No unexplained restricted magic access detected.",
        )

    def _check_family_name_trust(
        self,
        *,
        constraints: Dict[str, Any],
        family_name_status: Any,
        social_class: Any,
    ) -> Dict[str, Any]:
        if not constraints["family_name_affects_legal_trust"]:
            return self._base_check(
                check_id="family_name_trust",
                label="Family-name legal trust",
                status="not_applicable",
                severity="none",
                explanation="World does not indicate family-name legal trust constraints.",
            )

        if not family_name_status:
            return self._base_check(
                check_id="family_name_trust",
                label="Family-name legal trust",
                status="needs_detail",
                severity="medium",
                explanation="World uses family names for legal trust, but character lacks family-name status.",
                required_fix="Add trusted, distrusted, erased, forged, noble, or unknown family-name status.",
            )

        if str(family_name_status).lower() in {"erased", "forged", "unknown", "distrusted"}:
            return self._base_check(
                check_id="family_name_trust",
                label="Family-name legal trust",
                status="story_risk",
                severity="medium",
                explanation="Character has low-trust family-name status in a legal trust world.",
                story_hook="This creates barriers in courts, academy admissions, contracts, and witness credibility.",
            )

        return self._base_check(
            check_id="family_name_trust",
            label="Family-name legal trust",
            status="pass",
            severity="none",
            explanation="Family-name status is compatible with world trust system.",
        )

    def _check_academy_access(
        self,
        *,
        constraints: Dict[str, Any],
        social_class: Any,
        education_goal: Any,
        people_type: Dict[str, Any],
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not constraints["noble_academy_gatekeeping"]:
            return self._base_check(
                check_id="academy_access",
                label="Academy access",
                status="not_applicable",
                severity="none",
                explanation="World does not indicate academy gatekeeping.",
            )

        wants_academy = "academy" in str(education_goal).lower() or "student" in str(character_seed).lower()
        low_access_class = str(social_class).lower() in {"commoner", "relic_miner", "underclass", "erased", "borderfolk"}

        if wants_academy and low_access_class:
            has_path = any(
                key in character_seed
                for key in ["sponsor", "scholarship", "forged_identity", "illegal_tutor", "patron"]
            )

            if has_path:
                return self._base_check(
                    check_id="academy_access",
                    label="Academy access",
                    status="explained_exception",
                    severity="medium",
                    explanation="Low-access character has a route into academy systems.",
                    story_hook="The access path creates dependency, debt, blackmail, or exposure risk.",
                )

            return self._base_check(
                check_id="academy_access",
                label="Academy access",
                status="violation",
                severity="high",
                explanation="Low-access character is tied to academy access without sponsor, scholarship, forged identity, or loophole.",
                required_fix="Add a concrete access route such as sponsor, scholarship, forged identity, patron, illegal tutor, and the cost attached to it.",
            )

        return self._base_check(
            check_id="academy_access",
            label="Academy access",
            status="pass",
            severity="none",
            explanation="Academy access is plausible for this character concept.",
        )

    def _check_relic_economy_grounding(
        self,
        *,
        constraints: Dict[str, Any],
        social_class: Any,
        origin_location: Any,
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not constraints["relic_economy_pressure"]:
            return self._base_check(
                check_id="relic_economy_grounding",
                label="Relic economy grounding",
                status="not_applicable",
                severity="none",
                explanation="World does not indicate relic economy pressure.",
            )

        text = str(character_seed).lower()
        is_mining_class = str(social_class).lower() in {"relic_miner", "laborer", "commoner"}
        mentions_relic = "relic" in text or "mine" in text or "mining" in str(origin_location).lower()

        if is_mining_class and not mentions_relic:
            return self._base_check(
                check_id="relic_economy_grounding",
                label="Relic economy grounding",
                status="needs_detail",
                severity="low",
                explanation="Low-resource character in relic economy world lacks relation to relic labor/debt/injury/trade.",
                required_fix="Add relic debt, mining injury, family labor history, refinery work, or anti-relic politics.",
            )

        return self._base_check(
            check_id="relic_economy_grounding",
            label="Relic economy grounding",
            status="pass",
            severity="none",
            explanation="Character has enough relation or no required relation to relic economy.",
        )

    def _check_oath_culture_grounding(
        self,
        *,
        constraints: Dict[str, Any],
        character_seed: Dict[str, Any],
        role: Any,
    ) -> Dict[str, Any]:
        if not constraints["oath_religion_pressure"]:
            return self._base_check(
                check_id="oath_culture_grounding",
                label="Oath culture grounding",
                status="not_applicable",
                severity="none",
                explanation="World does not indicate oath religion pressure.",
            )

        text = str(character_seed).lower()

        if any(term in text for term in ["oath", "bell", "ritual", "god", "vow"]):
            return self._base_check(
                check_id="oath_culture_grounding",
                label="Oath culture grounding",
                status="pass",
                severity="none",
                explanation="Character is grounded in oath/religion/cultural pressure.",
            )

        if str(role).lower() in {"protagonist", "villain", "mentor", "love_interest"}:
            return self._base_check(
                check_id="oath_culture_grounding",
                label="Oath culture grounding",
                status="needs_detail",
                severity="low",
                explanation="Major character in oath-pressure world lacks relation to oaths, ritual, belief, or rejection.",
                required_fix="Add oath belief, oath refusal, ritual guilt, family vow, broken promise, or anti-faith stance.",
            )

        return self._base_check(
            check_id="oath_culture_grounding",
            label="Oath culture grounding",
            status="pass",
            severity="none",
            explanation="Minor/non-central character can be lightly grounded in oath culture for now.",
        )

    def _check_destiny_density(
        self,
        *,
        constraints: Dict[str, Any],
        destiny_type: Any,
        role: Any,
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not destiny_type:
            return self._base_check(
                check_id="destiny_density",
                label="Destiny density",
                status="pass",
                severity="none",
                explanation="Character is not marked with explicit destiny.",
            )

        is_major = str(role).lower() in {"protagonist", "deuteragonist", "villain", "antagonist", "love_interest", "rival"}

        if constraints["destiny_pressure_high"] and is_major:
            return self._base_check(
                check_id="destiny_density",
                label="Destiny density",
                status="story_pressure",
                severity="medium",
                explanation="Major character has destiny in a world already pressured by too many destiny-bearing people.",
                story_hook="Destiny should create social pressure, competition, classification, or institutional control.",
            )

        if not is_major:
            return self._base_check(
                check_id="destiny_density",
                label="Destiny density",
                status="needs_detail",
                severity="low",
                explanation="Non-major character with destiny needs clear reason or role.",
                required_fix="Clarify whether destiny is false, minor, local, inherited, or misunderstood.",
            )

        return self._base_check(
            check_id="destiny_density",
            label="Destiny density",
            status="pass",
            severity="none",
            explanation="Destiny assignment is plausible.",
        )

    def _check_rare_skill_cost(
        self,
        *,
        skill_rarity: Any,
        character_seed: Dict[str, Any],
    ) -> Dict[str, Any]:
        rare_values = {"rare", "elite", "legendary", "mythic", "anomaly", "S", "SS", "SSS", "Mythic", "Anomaly"}

        if str(skill_rarity) not in rare_values:
            return self._base_check(
                check_id="rare_skill_cost",
                label="Rare skill cost",
                status="pass",
                severity="none",
                explanation="No rare skill requiring special cost detected.",
            )

        has_cost = any(
            key in character_seed
            for key in ["skill_cost", "limitation", "counter", "training_needed", "social_consequence"]
        )

        if has_cost:
            return self._base_check(
                check_id="rare_skill_cost",
                label="Rare skill cost",
                status="pass",
                severity="none",
                explanation="Rare skill includes cost, limit, counter, training, or social consequence.",
            )

        return self._base_check(
            check_id="rare_skill_cost",
            label="Rare skill cost",
            status="violation",
            severity="high",
            explanation="Rare or high-rank skill has no cost, limitation, counter, training need, or social consequence.",
            required_fix="Add cost, limit, counter, training requirement, and social consequence.",
        )

    def _check_adaptability_exception(
        self,
        *,
        adaptability_type: Any,
        character_seed: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        people_type_text = str(people_type).lower()
        has_limit_break = bool(adaptability_type) or "limit-break" in people_type_text or "limit_break" in people_type_text

        if not has_limit_break:
            return self._base_check(
                check_id="adaptability_exception",
                label="Adaptability / limit-break exception",
                status="pass",
                severity="none",
                explanation="No limit-break exception requested.",
            )

        required = ["breakthrough_condition", "adaptation_cost", "adaptation_risk", "post_break_consequence"]
        missing = [key for key in required if key not in character_seed]

        if missing:
            return self._base_check(
                check_id="adaptability_exception",
                label="Adaptability / limit-break exception",
                status="violation",
                severity="high",
                explanation=f"Limit-break concept is missing required fields: {', '.join(missing)}.",
                required_fix="Add condition, cost, risk, and consequence before allowing limit-break behavior.",
            )

        return self._base_check(
            check_id="adaptability_exception",
            label="Adaptability / limit-break exception",
            status="pass",
            severity="none",
            explanation="Limit-break concept includes condition, cost, risk, and consequence.",
            story_hook="This character can become a controlled exception without breaking world logic.",
        )

    def _check_population_fit(
        self,
        *,
        social_class: Any,
        population_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        groups = population_context.get("population_groups", [])

        if not groups:
            return self._base_check(
                check_id="population_fit",
                label="Population fit",
                status="not_checked",
                severity="low",
                explanation="No population groups supplied for distribution fit.",
            )

        class_matches = [
            group for group in groups
            if str(group.get("social_class")).lower() == str(social_class).lower()
        ]

        if class_matches:
            return self._base_check(
                check_id="population_fit",
                label="Population fit",
                status="pass",
                severity="none",
                explanation="Character social class exists in the modeled population distribution.",
            )

        return self._base_check(
            check_id="population_fit",
            label="Population fit",
            status="needs_detail",
            severity="medium",
            explanation="Character social class does not appear in supplied population groups.",
            required_fix="Add matching population group or explain why this character is an imported/outlier class.",
        )

    def _build_risk_summary(self, checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        violation_count = sum(1 for check in checks if check["status"] == "violation")
        needs_detail_count = sum(1 for check in checks if check["status"] == "needs_detail")
        story_risk_count = sum(1 for check in checks if check["status"] in {"story_risk", "story_pressure"})
        explained_exception_count = sum(1 for check in checks if check["status"] == "explained_exception")

        high_severity_count = sum(1 for check in checks if check["severity"] == "high")
        medium_severity_count = sum(1 for check in checks if check["severity"] == "medium")

        grounding_score = max(
            0.0,
            1.0
            - (violation_count * 0.18)
            - (needs_detail_count * 0.08)
            - (high_severity_count * 0.12)
            - (medium_severity_count * 0.05),
        )

        return {
            "total_checks": len(checks),
            "violation_count": violation_count,
            "needs_detail_count": needs_detail_count,
            "story_risk_count": story_risk_count,
            "explained_exception_count": explained_exception_count,
            "high_severity_count": high_severity_count,
            "medium_severity_count": medium_severity_count,
            "world_grounding_score": round(grounding_score, 3),
            "grounding_tier": self._grounding_tier(grounding_score),
        }

    def _grounding_tier(self, score: float) -> str:
        if score >= 0.85:
            return "strongly_grounded"
        if score >= 0.65:
            return "usable_with_minor_repairs"
        if score >= 0.4:
            return "needs_revision"
        return "world_logic_failure"

    def _build_repair_plan(
        self,
        checks: List[Dict[str, Any]],
        character_seed: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        repairs = []

        for check in checks:
            if check.get("required_fix"):
                repairs.append(
                    {
                        "check_id": check["check_id"],
                        "priority": check["severity"],
                        "repair": check["required_fix"],
                        "story_hook": check.get("story_hook"),
                    }
                )

        if not repairs:
            repairs.append(
                {
                    "check_id": "none",
                    "priority": "none",
                    "repair": "No required repairs. Character concept is compatible enough for next engine.",
                    "story_hook": None,
                }
            )

        return repairs

    def _build_grounding_profile(
        self,
        *,
        constraints: Dict[str, Any],
        checks: List[Dict[str, Any]],
        character_seed: Dict[str, Any],
        people_type: Dict[str, Any],
    ) -> Dict[str, Any]:
        active_story_hooks = [
            check["story_hook"]
            for check in checks
            if check.get("story_hook")
        ]

        world_dependency_tags = []

        if constraints["commoner_royal_magic_restricted"]:
            world_dependency_tags.append("magic_access_law")

        if constraints["family_name_affects_legal_trust"]:
            world_dependency_tags.append("family_name_legal_trust")

        if constraints["noble_academy_gatekeeping"]:
            world_dependency_tags.append("academy_gatekeeping")

        if constraints["relic_economy_pressure"]:
            world_dependency_tags.append("relic_economy")

        if constraints["oath_religion_pressure"]:
            world_dependency_tags.append("oath_religion")

        if constraints["destiny_pressure_high"]:
            world_dependency_tags.append("destiny_pressure")

        return {
            "character_name": character_seed.get("name"),
            "role": character_seed.get("role"),
            "people_type_id": people_type.get("people_type_id"),
            "world_dependency_tags": world_dependency_tags,
            "active_story_hooks": active_story_hooks,
            "can_advance_to_genesis": not any(
                check["status"] == "violation"
                for check in checks
            ),
            "requires_human_review": any(
                check["status"] in {"violation", "needs_detail"}
                for check in checks
            ),
        }
