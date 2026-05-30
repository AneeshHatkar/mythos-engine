from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class CharacterRegistrySeedEngine(BaseEngine):
    """Provides controlled registry vocabulary for Chunk 3.

    This seed pack gives the Character Intelligence Layer reusable categories
    for generation, scoring, validation, dataset metadata, originality checks,
    and future ML/RAG labeling.

    It is not a random list of tropes. It is a controlled vocabulary that helps
    keep generated characters consistent, testable, searchable, and trainable.
    """

    engine_name = "character.registry_seed_engine"

    PEOPLE_TYPES: List[Dict[str, Any]] = [
        {
            "id": "people.hidden_kingmaker",
            "name": "Hidden Kingmaker",
            "category": "strategic_support",
            "rarity": "rare",
            "description": "A low-visibility person whose choices decide who rises.",
            "pressure_responses": ["observe first", "act indirectly", "protect through strategy"],
            "anti_cliche_rule": "Must have a cost for being unseen, not just effortless cleverness.",
        },
        {
            "id": "people.failed_prodigy",
            "name": "Failed Prodigy",
            "category": "fallen_potential",
            "rarity": "uncommon",
            "description": "Someone once marked exceptional who now lives under public disappointment.",
            "pressure_responses": ["overtrain", "self-sabotage", "resent effortless talent"],
            "anti_cliche_rule": "Failure must change behavior, not just add aesthetic sadness.",
        },
        {
            "id": "people.false_saint",
            "name": "False Saint",
            "category": "moral_mask",
            "rarity": "rare",
            "description": "A publicly holy or admirable figure hiding self-serving motives.",
            "pressure_responses": ["perform virtue", "weaponize forgiveness", "hide cruelty as duty"],
            "anti_cliche_rule": "Must believe at least part of their own lie.",
        },
        {
            "id": "people.institutional_villain",
            "name": "Institutional Villain",
            "category": "systemic_antagonist",
            "rarity": "uncommon",
            "description": "A villain whose power comes from rules, offices, courts, schools, or bureaucracy.",
            "pressure_responses": ["cite procedure", "punish through systems", "erase evidence"],
            "anti_cliche_rule": "Must have an ideology stronger than personal cruelty.",
        },
        {
            "id": "people.adaptive_survivor",
            "name": "Adaptive Survivor",
            "category": "survival_adaptation",
            "rarity": "common",
            "description": "Someone who survives by changing faster than the system can categorize them.",
            "pressure_responses": ["change identity", "learn quickly", "abandon pride to survive"],
            "anti_cliche_rule": "Adaptation must leave scars and tradeoffs.",
        },
        {
            "id": "people.limit_break_anomaly",
            "name": "Limit-Break Anomaly",
            "category": "rule_exception",
            "rarity": "mythic",
            "description": "A person capable of exceeding limits under specific pressure and cost.",
            "pressure_responses": ["surge under extreme stakes", "destabilize after breakthrough"],
            "anti_cliche_rule": "Must have condition, cost, risk, and post-break consequence.",
        },
        {
            "id": "people.ordinary_witness",
            "name": "Ordinary Witness",
            "category": "grounded_observer",
            "rarity": "common",
            "description": "A non-special person whose perspective reveals how the world affects normal lives.",
            "pressure_responses": ["notice inconsistencies", "fear institutions", "protect small truths"],
            "anti_cliche_rule": "Ordinary must not mean irrelevant.",
        },
    ]

    CHARACTER_ROLES = [
        "protagonist",
        "deuteragonist",
        "antagonist",
        "villain",
        "rival",
        "mentor",
        "love_interest",
        "side_character",
        "ordinary_citizen",
        "civilization_agent",
        "game_companion",
        "symbolic_character",
        "catalyst",
        "foil",
        "witness",
    ]

    BIRTH_STATUSES = [
        "noble_birth",
        "common_birth",
        "orphaned",
        "adopted",
        "illegitimate",
        "erased_family_record",
        "refugee_birth",
        "borderborn",
        "institution_raised",
        "unknown_origin",
        "ritual_birth",
        "prophecy_marked_birth",
    ]

    SOCIAL_CLASSES = [
        "imperial_elite",
        "old_nobility",
        "new_money",
        "academy_sponsored",
        "merchant_class",
        "professional_class",
        "artisan_class",
        "commoner",
        "laborer",
        "relic_miner",
        "borderfolk",
        "underclass",
        "erased",
        "illegal_person",
    ]

    PSYCHOLOGICAL_WOUNDS = [
        "performance_based_love",
        "abandonment",
        "public_humiliation",
        "betrayal_by_guardian",
        "inherited_shame",
        "survivor_guilt",
        "class_disposability",
        "religious_guilt",
        "memory_erasure",
        "failed_destiny",
        "unwanted_power",
        "being_used_as_symbol",
    ]

    DEFENSE_MECHANISMS = [
        "cold_restraint",
        "humor_deflection",
        "perfectionism",
        "obedience_mask",
        "aggression",
        "intellectualization",
        "social_charm",
        "isolation",
        "false_arrogance",
        "self_sabotage",
        "caretaking",
        "control_seeking",
    ]

    TRAUMA_TRIGGERS = [
        "public_ranking",
        "authority_dismissal",
        "family_name_insult",
        "oath_bell_sound",
        "closed_archive_door",
        "ritual_ceremony",
        "crowd_laughter",
        "legal_document",
        "loss_of_voice",
        "abandonment_signal",
        "bloodline_accusation",
        "failed_exam",
    ]

    GOAL_TYPES = [
        "surface_goal",
        "hidden_goal",
        "emotional_goal",
        "survival_goal",
        "social_goal",
        "moral_goal",
        "romantic_goal",
        "revenge_goal",
        "belonging_goal",
        "freedom_goal",
        "truth_goal",
        "power_goal",
        "redemption_goal",
        "false_goal",
        "true_need",
    ]

    MORAL_AXES = [
        "compassion",
        "justice",
        "loyalty",
        "honesty",
        "mercy",
        "ambition",
        "revenge",
        "cruelty",
        "self_sacrifice",
        "manipulation_tolerance",
        "violence_tolerance",
        "corruption_risk",
        "redemption_potential",
    ]

    SKILL_DOMAINS = [
        "combat",
        "strategy",
        "emotional_intelligence",
        "observation",
        "memory",
        "social_manipulation",
        "leadership",
        "magic",
        "technology",
        "survival",
        "artistry",
        "politics",
        "medicine",
        "law",
        "ritual_knowledge",
        "investigation",
        "teaching",
        "craft",
        "stealth",
        "endurance",
    ]

    SKILL_RARITIES = [
        "common",
        "uncommon",
        "rare",
        "elite",
        "legendary",
        "mythic",
        "anomaly",
    ]

    SKILL_RANKS = [
        "F",
        "E",
        "D",
        "C",
        "B",
        "A",
        "S",
        "SS",
        "SSS",
        "Mythic",
        "Anomaly",
    ]

    GROWTH_ARCS = [
        "coward_to_witness",
        "tool_to_person",
        "obedient_to_free",
        "vengeful_to_just",
        "proud_to_humble",
        "isolated_to_bonded",
        "failed_prodigy_to_teacher",
        "chosen_one_to_refuser",
        "victim_to_boundary_setter",
        "hero_to_corrupted",
        "villain_to_redeemed",
        "ordinary_to_essential",
    ]

    ADAPTABILITY_TYPES = [
        "emotional_adaptability",
        "mental_adaptability",
        "social_adaptability",
        "moral_adaptability",
        "skill_adaptability",
        "power_adaptability",
        "destiny_adaptability",
        "trauma_adaptability",
        "leadership_adaptability",
        "survival_adaptability",
    ]

    LIMIT_BREAK_TYPES = [
        "earned_breakthrough",
        "desperation_surge",
        "destiny_activation",
        "forbidden_method",
        "trauma_override",
        "relationship_triggered_break",
        "moral_line_crossing",
        "self_sacrifice_evolution",
        "training_plateau_break",
        "world_anomaly_exception",
        "corruption_boost",
        "healing_breakthrough",
    ]

    DESTINY_TYPES = [
        "hidden_kingmaker",
        "chosen_heir",
        "failed_chosen_one",
        "oath_breaker",
        "crown_refuser",
        "prophecy_witness",
        "world_catalyst",
        "sacrifice_candidate",
        "false_savior",
        "destiny_thief",
        "legacy_carrier",
        "anomaly_bearer",
    ]

    PROPHECY_ROLES = [
        "subject",
        "witness",
        "misread_savior",
        "false_villain",
        "key_betrayer",
        "crown_refuser",
        "bell_answerer",
        "archive_opener",
        "bloodline_decoy",
        "final_interpreter",
    ]

    LEGACY_TYPES = [
        "inherited_debt",
        "inherited_guilt",
        "inherited_privilege",
        "bloodline_myth",
        "broken_oath",
        "family_curse",
        "hidden_lineage",
        "erased_record",
        "ancestral_promise",
        "legacy_artifact",
    ]

    MIRROR_TYPES = [
        "same_wound_opposite_choice",
        "same_goal_different_morality",
        "villain_reflection",
        "romantic_mirror",
        "mentor_future_self",
        "rival_shadow_self",
        "failed_version_of_protagonist",
        "healed_version_of_protagonist",
        "ordinary_version_of_legend",
        "corrupted_version_of_hero",
    ]

    DATASET_TAGS = [
        "human_approved_synthetic",
        "needs_review",
        "training_candidate",
        "do_not_train",
        "high_attachment",
        "high_originality",
        "near_duplicate_risk",
        "cliche_risk",
        "sensitive_content_review",
        "world_grounded",
        "simulation_ready",
        "adaptability_ready",
    ]

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        include_descriptions = payload.get("include_descriptions", True)

        registry = {
            "people_types": self.PEOPLE_TYPES if include_descriptions else [item["id"] for item in self.PEOPLE_TYPES],
            "character_roles": self.CHARACTER_ROLES,
            "birth_statuses": self.BIRTH_STATUSES,
            "social_classes": self.SOCIAL_CLASSES,
            "psychological_wounds": self.PSYCHOLOGICAL_WOUNDS,
            "defense_mechanisms": self.DEFENSE_MECHANISMS,
            "trauma_triggers": self.TRAUMA_TRIGGERS,
            "goal_types": self.GOAL_TYPES,
            "moral_axes": self.MORAL_AXES,
            "skill_domains": self.SKILL_DOMAINS,
            "skill_rarities": self.SKILL_RARITIES,
            "skill_ranks": self.SKILL_RANKS,
            "growth_arcs": self.GROWTH_ARCS,
            "adaptability_types": self.ADAPTABILITY_TYPES,
            "limit_break_types": self.LIMIT_BREAK_TYPES,
            "destiny_types": self.DESTINY_TYPES,
            "prophecy_roles": self.PROPHECY_ROLES,
            "legacy_types": self.LEGACY_TYPES,
            "mirror_types": self.MIRROR_TYPES,
            "dataset_tags": self.DATASET_TAGS,
        }

        return self.build_result(
            success=True,
            data={
                "registry": registry,
                "registry_summary": self._summary(registry),
                "training_notes": [
                    "This registry creates stable labels for future Chunk 8 training.",
                    "Labels are intentionally explicit so generated characters can be searched, scored, and deduplicated.",
                    "Adaptability and limit-break terms are included now because adaptive characters are core to Chunk 3.",
                    "These are seed vocabularies, not final model-learned taxonomies.",
                ],
            },
            warnings=[],
            errors=[],
            generated_object_ids=[],
        )

    def _summary(self, registry: Dict[str, Any]) -> Dict[str, int]:
        return {
            key: len(value)
            for key, value in registry.items()
        }

    def lookup(self, category: str, value: str) -> bool:
        """Simple membership check for tests and future validators."""

        category_map = {
            "character_roles": self.CHARACTER_ROLES,
            "birth_statuses": self.BIRTH_STATUSES,
            "social_classes": self.SOCIAL_CLASSES,
            "psychological_wounds": self.PSYCHOLOGICAL_WOUNDS,
            "defense_mechanisms": self.DEFENSE_MECHANISMS,
            "trauma_triggers": self.TRAUMA_TRIGGERS,
            "goal_types": self.GOAL_TYPES,
            "moral_axes": self.MORAL_AXES,
            "skill_domains": self.SKILL_DOMAINS,
            "skill_rarities": self.SKILL_RARITIES,
            "skill_ranks": self.SKILL_RANKS,
            "growth_arcs": self.GROWTH_ARCS,
            "adaptability_types": self.ADAPTABILITY_TYPES,
            "limit_break_types": self.LIMIT_BREAK_TYPES,
            "destiny_types": self.DESTINY_TYPES,
            "prophecy_roles": self.PROPHECY_ROLES,
            "legacy_types": self.LEGACY_TYPES,
            "mirror_types": self.MIRROR_TYPES,
            "dataset_tags": self.DATASET_TAGS,
        }

        if category == "people_types":
            return any(item["id"] == value or item["name"] == value for item in self.PEOPLE_TYPES)

        return value in category_map.get(category, [])
