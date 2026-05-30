from typing import Any, Dict, List, Tuple

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldQualityEngine(BaseEngine):
    """Checks world consistency, originality, and story potential.

    This is the first world evaluation engine.

    It does not generate new world content. It evaluates world content so
    MythOS can become a research-grade system instead of a generic generator.

    It produces:
    - consistency score
    - originality score
    - story potential score
    - franchise potential score
    - genericness risk
    - training readiness score
    - detected strengths
    - detected weaknesses
    - missing systems
    - contradiction risks
    - suggested improvements

    Later chunks will use this for:
    - World Orchestrator validation
    - World Diff / Comparison
    - Quality Benchmark Pack
    - Dataset tagging
    - training eligibility
    - ML evaluation dashboards
    """

    engine_name = "world.quality_engine"

    REQUIRED_WORLD_SYSTEMS = [
        "identity",
        "world_dna",
        "scale_granularity",
        "rules",
        "boundary_constraints",
        "contradiction_intent",
        "chronology",
        "memory_archive",
        "geography",
        "environment",
        "infrastructure",
        "demographics",
        "society",
        "power_structure",
        "military_security",
        "economy",
        "law",
        "belief",
        "culture",
        "knowledge_education",
        "institutions",
        "technology_magic_science",
        "species_creatures",
        "artifacts",
        "aesthetic_texture",
        "civilization_pressure",
        "causality_graph",
    ]

    HIGH_VALUE_TERMS = [
        "oath",
        "archive",
        "relic",
        "destiny",
        "academy",
        "law",
        "class",
        "memory",
        "founding",
        "betrayal",
        "border",
        "debt",
        "forbidden",
        "witness",
        "classification",
        "erased",
        "sponsor",
        "ritual",
        "prophecy",
        "inheritance",
    ]

    GENERIC_RISK_TERMS = [
        "kingdom",
        "evil empire",
        "chosen one",
        "dark lord",
        "magic school",
        "ancient prophecy",
        "lost artifact",
        "great war",
        "good versus evil",
    ]

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", payload)
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not world_state:
            warnings.append(
                "No world_state provided; quality engine will evaluate an empty world state."
            )

        missing_systems = self._find_missing_systems(world_state)
        consistency = self._score_consistency(world_state, missing_systems)
        originality = self._score_originality(world_state)
        story_potential = self._score_story_potential(world_state)
        franchise_potential = self._score_franchise_potential(world_state)
        genericness_risk = self._score_genericness_risk(world_state)
        training_readiness = self._score_training_readiness(
            consistency_score=consistency["score"],
            originality_score=originality["score"],
            story_potential_score=story_potential["score"],
            missing_system_count=len(missing_systems),
            desired_complexity=desired_complexity,
        )

        contradiction_risks = self._detect_contradiction_risks(world_state)
        improvement_plan = self._build_improvement_plan(
            missing_systems=missing_systems,
            consistency_score=consistency["score"],
            originality_score=originality["score"],
            story_potential_score=story_potential["score"],
            genericness_risk=genericness_risk["score"],
            contradiction_risks=contradiction_risks,
        )

        data = {
            "quality_summary": {
                "consistency_score": consistency["score"],
                "originality_score": originality["score"],
                "story_potential_score": story_potential["score"],
                "franchise_potential_score": franchise_potential["score"],
                "genericness_risk_score": genericness_risk["score"],
                "training_readiness_score": training_readiness["score"],
                "quality_tier": self._quality_tier(
                    consistency["score"],
                    originality["score"],
                    story_potential["score"],
                    training_readiness["score"],
                ),
                "training_eligible": training_readiness["score"] >= 0.78
                and consistency["score"] >= 0.7
                and genericness_risk["score"] <= 0.45
                and len(missing_systems) <= 3,
            },
            "consistency_report": consistency,
            "originality_report": originality,
            "story_potential_report": story_potential,
            "franchise_potential_report": franchise_potential,
            "genericness_report": genericness_risk,
            "training_readiness_report": training_readiness,
            "missing_systems": missing_systems,
            "contradiction_risks": contradiction_risks,
            "improvement_plan": improvement_plan,
            "training_notes": [
                "Quality scores are deterministic heuristics for Chunk 2 and can later be replaced or augmented by ML evaluators.",
                "Training eligibility should require high consistency, originality, story potential, and low genericness risk.",
                "This engine should run after the World Orchestrator before saving curated training examples.",
                "Outputs are structured for future benchmark dashboards and world comparison systems.",
            ],
        }

        return self.build_result(
            success=True,
            data=data,
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _flatten_text(self, obj: Any) -> str:
        if obj is None:
            return ""

        if isinstance(obj, str):
            return obj

        if isinstance(obj, (int, float, bool)):
            return str(obj)

        if isinstance(obj, list):
            return " ".join(self._flatten_text(item) for item in obj)

        if isinstance(obj, dict):
            return " ".join(
                [str(key) + " " + self._flatten_text(value) for key, value in obj.items()]
            )

        return str(obj)

    def _find_missing_systems(self, world_state: Dict[str, Any]) -> List[str]:
        missing = []

        for system_name in self.REQUIRED_WORLD_SYSTEMS:
            value = world_state.get(system_name)
            if value is None or value == {} or value == [] or value == "":
                missing.append(system_name)

        return missing

    def _score_consistency(
        self,
        world_state: Dict[str, Any],
        missing_systems: List[str],
    ) -> Dict[str, Any]:
        total_systems = len(self.REQUIRED_WORLD_SYSTEMS)
        coverage_score = max(0.0, 1.0 - (len(missing_systems) / total_systems))

        text = self._flatten_text(world_state).lower()

        cross_system_signals = {
            "law_links": any(term in text for term in ["law", "court", "legal", "trial"]),
            "economy_links": any(term in text for term in ["debt", "tax", "resource", "funding"]),
            "belief_links": any(term in text for term in ["oath", "god", "ritual", "prophecy"]),
            "history_links": any(term in text for term in ["founding", "history", "erased", "archive"]),
            "class_links": any(term in text for term in ["class", "noble", "commoner", "rank"]),
            "geography_links": any(term in text for term in ["border", "capital", "market", "road"]),
        }

        link_score = sum(1 for value in cross_system_signals.values() if value) / len(
            cross_system_signals
        )

        contradiction_penalty = 0.0

        if "instant communication" in text and "message delay" in text:
            contradiction_penalty += 0.12

        if "unlimited healing" in text and "injury consequence" in text:
            contradiction_penalty += 0.12

        if "no magic" in text and "royal magic" in text:
            contradiction_penalty += 0.12

        score = max(0.0, min(1.0, (coverage_score * 0.55) + (link_score * 0.45) - contradiction_penalty))

        strengths = []

        if coverage_score >= 0.8:
            strengths.append("World has broad system coverage.")

        if link_score >= 0.8:
            strengths.append("World systems appear interconnected across law, economy, belief, history, class, and geography.")

        if contradiction_penalty == 0:
            strengths.append("No major obvious contradiction patterns detected by heuristic check.")

        weaknesses = []

        if missing_systems:
            weaknesses.append(f"Missing or empty systems: {', '.join(missing_systems[:8])}")

        if link_score < 0.6:
            weaknesses.append("World systems may be too isolated; add more causal links across law, economy, belief, class, history, and geography.")

        if contradiction_penalty > 0:
            weaknesses.append("Potential hard contradictions detected in communication, healing, or magic rules.")

        return {
            "score": round(score, 3),
            "coverage_score": round(coverage_score, 3),
            "cross_system_link_score": round(link_score, 3),
            "contradiction_penalty": round(contradiction_penalty, 3),
            "cross_system_signals": cross_system_signals,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

    def _score_originality(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        text = self._flatten_text(world_state).lower()
        word_count = max(1, len(text.split()))

        high_value_hits = {
            term: text.count(term)
            for term in self.HIGH_VALUE_TERMS
            if term in text
        }

        high_value_score = min(1.0, len(high_value_hits) / 12)

        repeated_generic_hits = {
            term: text.count(term)
            for term in self.GENERIC_RISK_TERMS
            if term in text
        }

        generic_penalty = min(0.35, sum(repeated_generic_hits.values()) * 0.04)

        specificity_score = min(1.0, word_count / 1200)

        named_object_bonus = 0.0
        for marker in ["the ", "academy", "register", "ledger", "bell", "crown", "archive"]:
            if marker in text:
                named_object_bonus += 0.025

        named_object_bonus = min(0.15, named_object_bonus)

        score = max(
            0.0,
            min(
                1.0,
                (high_value_score * 0.45)
                + (specificity_score * 0.25)
                + (named_object_bonus)
                + 0.25
                - generic_penalty,
            ),
        )

        strengths = []

        if high_value_score >= 0.7:
            strengths.append("World has strong recurring identity motifs.")

        if named_object_bonus >= 0.1:
            strengths.append("World contains memorable named systems/objects.")

        if specificity_score >= 0.7:
            strengths.append("World has enough detail density to avoid feeling thin.")

        weaknesses = []

        if high_value_score < 0.5:
            weaknesses.append("Add stronger unique motifs and recurring symbolic systems.")

        if repeated_generic_hits:
            weaknesses.append(
                "Generic trope risk detected: "
                + ", ".join(f"{term}={count}" for term, count in repeated_generic_hits.items())
            )

        return {
            "score": round(score, 3),
            "high_value_motif_score": round(high_value_score, 3),
            "specificity_score": round(specificity_score, 3),
            "generic_penalty": round(generic_penalty, 3),
            "high_value_hits": high_value_hits,
            "generic_hits": repeated_generic_hits,
            "strengths": strengths,
            "weaknesses": weaknesses,
        }

    def _score_story_potential(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        text = self._flatten_text(world_state).lower()

        story_engines = {
            "class_conflict": any(term in text for term in ["class", "commoner", "noble", "rank"]),
            "forbidden_knowledge": any(term in text for term in ["forbidden", "secret archive", "sealed", "censored"]),
            "political_intrigue": any(term in text for term in ["court", "faction", "succession", "kingmaker"]),
            "romance_obstacles": any(term in text for term in ["marriage", "sponsor", "reputation", "class"]),
            "mystery_engine": any(term in text for term in ["erased", "archive", "map", "hidden history"]),
            "war_or_rebellion": any(term in text for term in ["border", "army", "rebellion", "war"]),
            "spiritual_conflict": any(term in text for term in ["oath", "god", "heresy", "prophecy"]),
            "artifact_plot": any(term in text for term in ["artifact", "relic", "crown", "bell", "seal"]),
            "character_pressure": any(term in text for term in ["debt", "shame", "inheritance", "destiny"]),
            "system_collapse": any(term in text for term in ["collapse", "breaking point", "crisis", "pressure"]),
        }

        active_count = sum(1 for active in story_engines.values() if active)
        engine_score = active_count / len(story_engines)

        plot_hook_count = (
            text.count("story_uses")
            + text.count("plot_potential")
            + text.count("story_hooks")
            + text.count("system_breaking_points")
            + text.count("conflict")
            + text.count("crisis")
            + text.count("reveal")
            + text.count("pressure")
        )
        plot_hook_score = min(1.0, plot_hook_count / 18)

        score = min(1.0, (engine_score * 0.7) + (plot_hook_score * 0.3))

        strongest_story_engines = [
            name for name, active in story_engines.items() if active
        ]

        weaknesses = []

        if not story_engines["romance_obstacles"]:
            weaknesses.append("Romance/social intimacy pressure may be underdeveloped.")

        if not story_engines["mystery_engine"]:
            weaknesses.append("Mystery/investigation engine may be underdeveloped.")

        if not story_engines["war_or_rebellion"]:
            weaknesses.append("War/rebellion pressure may be underdeveloped.")

        if plot_hook_score < 0.4:
            weaknesses.append("Add more explicit plot hooks, story uses, or character-facing conflicts.")

        return {
            "score": round(score, 3),
            "engine_score": round(engine_score, 3),
            "plot_hook_score": round(plot_hook_score, 3),
            "story_engines": story_engines,
            "strongest_story_engines": strongest_story_engines,
            "weaknesses": weaknesses,
        }

    def _score_franchise_potential(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        text = self._flatten_text(world_state).lower()

        franchise_axes = {
            "multiple_regions": any(term in text for term in ["border", "capital", "market", "province", "region"]),
            "multiple_factions": any(term in text for term in ["faction", "house", "network", "board", "bloc"]),
            "artifact_system": any(term in text for term in ["artifact", "relic", "crown", "bell", "seal"]),
            "character_class_variety": any(term in text for term in ["noble", "commoner", "student", "miner", "archivist"]),
            "sequel_mysteries": any(term in text for term in ["unknown", "erased", "hidden", "lost", "forbidden"]),
            "adaptation_visuals": any(term in text for term in ["visual", "palette", "architecture", "cinematic", "soundscape"]),
            "system_evolution": any(term in text for term in ["causality", "pressure", "future", "collapse", "breaking"]),
        }

        score = sum(1 for value in franchise_axes.values() if value) / len(franchise_axes)

        return {
            "score": round(score, 3),
            "franchise_axes": franchise_axes,
            "notes": [
                "High franchise potential requires regions, factions, artifacts, character variety, mysteries, visual identity, and world evolution.",
            ],
        }

    def _score_genericness_risk(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        text = self._flatten_text(world_state).lower()

        generic_hits = {
            term: text.count(term)
            for term in self.GENERIC_RISK_TERMS
            if term in text
        }

        high_value_hit_count = sum(
            1 for term in self.HIGH_VALUE_TERMS if term in text
        )

        generic_hit_total = sum(generic_hits.values())

        raw_risk = min(1.0, generic_hit_total * 0.08)

        if high_value_hit_count >= 10:
            raw_risk = max(0.0, raw_risk - 0.25)

        if high_value_hit_count >= 15:
            raw_risk = max(0.0, raw_risk - 0.15)

        risk_tier = "low"
        if raw_risk >= 0.65:
            risk_tier = "high"
        elif raw_risk >= 0.35:
            risk_tier = "medium"

        return {
            "score": round(raw_risk, 3),
            "risk_tier": risk_tier,
            "generic_hits": generic_hits,
            "unique_motif_count": high_value_hit_count,
            "notes": [
                "Genericness risk is reduced when the world has recurring, specific, interconnected motifs.",
            ],
        }

    def _score_training_readiness(
        self,
        *,
        consistency_score: float,
        originality_score: float,
        story_potential_score: float,
        missing_system_count: int,
        desired_complexity: str,
    ) -> Dict[str, Any]:
        missing_penalty = min(0.35, missing_system_count * 0.025)

        complexity_bonus = 0.03 if desired_complexity in {"extreme", "god_level"} else 0.0

        score = max(
            0.0,
            min(
                1.0,
                (consistency_score * 0.35)
                + (originality_score * 0.3)
                + (story_potential_score * 0.3)
                + complexity_bonus
                - missing_penalty,
            ),
        )

        blockers = []

        if consistency_score < 0.7:
            blockers.append("Consistency score below training-ready threshold.")

        if originality_score < 0.65:
            blockers.append("Originality score below training-ready threshold.")

        if story_potential_score < 0.65:
            blockers.append("Story potential score below training-ready threshold.")

        if missing_system_count > 3:
            blockers.append("Too many missing systems for high-quality training data.")

        return {
            "score": round(score, 3),
            "missing_system_penalty": round(missing_penalty, 3),
            "complexity_bonus": round(complexity_bonus, 3),
            "blockers": blockers,
            "recommended_label": "training_candidate" if score >= 0.78 and not blockers else "needs_revision",
        }

    def _detect_contradiction_risks(self, world_state: Dict[str, Any]) -> List[str]:
        text = self._flatten_text(world_state).lower()

        risks = []

        if "instant communication" in text and ("secret" in text or "hidden" in text):
            risks.append(
                "Instant communication may weaken secrecy unless surveillance, encryption, class access, or distance limits are defined."
            )

        if "unlimited healing" in text:
            risks.append(
                "Unlimited healing may weaken injury, sacrifice, danger, and medical inequality unless strong costs exist."
            )

        if "no magic" in text and ("magic" in text or "oath-magic" in text):
            risks.append(
                "Magic presence appears ambiguous; clarify whether magic is literal, ritual, cultural, or illegal."
            )

        if "destiny" in text and "agency" not in text and "free will" not in text:
            risks.append(
                "Destiny systems should define agency/free-will rules so characters do not feel predetermined."
            )

        if "class" in text and "mobility" not in text:
            risks.append(
                "Class systems should define mobility paths, loopholes, and exceptions."
            )

        if "relic" in text and "cost" not in text and "debt" not in text:
            risks.append(
                "Relic systems should define costs, debt, limits, or corruption risks."
            )

        return risks

    def _build_improvement_plan(
        self,
        *,
        missing_systems: List[str],
        consistency_score: float,
        originality_score: float,
        story_potential_score: float,
        genericness_risk: float,
        contradiction_risks: List[str],
    ) -> List[str]:
        plan = []

        if missing_systems:
            plan.append(
                "Complete missing systems before orchestrator-level world generation: "
                + ", ".join(missing_systems[:8])
            )

        if consistency_score < 0.75:
            plan.append(
                "Add stronger causal links between law, economy, education, belief, geography, and class."
            )

        if originality_score < 0.7:
            plan.append(
                "Add more world-specific names, symbols, rituals, institutional contradictions, and unique resource logic."
            )

        if story_potential_score < 0.7:
            plan.append(
                "Add clearer plot engines: romance obstacles, mystery clues, rebellion triggers, villain leverage, and character pressure."
            )

        if genericness_risk > 0.45:
            plan.append(
                "Reduce generic trope dependence by replacing broad fantasy labels with concrete systems and consequences."
            )

        if contradiction_risks:
            plan.append(
                "Resolve contradiction risks before marking the world as training-eligible."
            )

        if not plan:
            plan.append(
                "World is strong enough for orchestrator integration and benchmark evaluation."
            )

        return plan

    def _quality_tier(
        self,
        consistency_score: float,
        originality_score: float,
        story_potential_score: float,
        training_readiness_score: float,
    ) -> str:
        average = (
            consistency_score
            + originality_score
            + story_potential_score
            + training_readiness_score
        ) / 4

        if average >= 0.88:
            return "excellent"
        if average >= 0.75:
            return "strong"
        if average >= 0.6:
            return "developing"
        return "weak"
