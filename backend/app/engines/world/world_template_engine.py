from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldTemplateEngine(BaseEngine):
    """Provides reusable world templates/presets for controlled generation.

    This engine makes MythOS controllable and product-like.

    Instead of relying only on raw prompts, users can start from structured
    world modes such as:
    - dark academy empire
    - civilization simulation
    - dystopian megacity
    - romance kingdom
    - mythic religious world
    - movie-scale world
    - seven-novel saga world

    Later, the World Orchestrator will use these templates to configure
    all world engines consistently.
    """

    engine_name = "world.template_engine"

    TEMPLATE_CATALOG: Dict[str, Dict[str, Any]] = {
        "dark_academy_empire": {
            "template_id": "dark_academy_empire",
            "name": "Dark Academy Empire",
            "description": (
                "A prestige political fantasy world where elite academies, noble bloodlines, "
                "forbidden knowledge, class hierarchy, and institutional secrets control society."
            ),
            "recommended_genre_tags": ["dark_academy", "political_fantasy", "mystery_intrigue"],
            "recommended_tone_tags": ["elegant", "tragic", "tense", "intellectual"],
            "recommended_complexity": "god_level",
            "target_formats": ["novel_series", "streaming_series", "game_lore_bible"],
            "core_conflicts": [
                "merit versus birth",
                "knowledge versus control",
                "romance versus reputation",
                "truth versus institution",
                "destiny versus classification",
            ],
            "required_systems": [
                "academy hierarchy",
                "class law",
                "forbidden archives",
                "ritualized exams",
                "elite families",
                "black-market knowledge",
                "public reputation economy",
            ],
            "default_seed_additions": [
                "Noble academies control access to power.",
                "Family names determine legal trust.",
                "Forbidden texts preserve erased truths.",
                "Students are ranked publicly and owned quietly by sponsors.",
            ],
            "quality_focus": [
                "institutional hypocrisy",
                "class-specific consequences",
                "non-generic rituals",
                "visual identity",
                "mystery hooks",
            ],
        },
        "civilization_simulation": {
            "template_id": "civilization_simulation",
            "name": "Civilization Simulation World",
            "description": (
                "A large-scale world designed around population systems, resources, pressure, geography, "
                "institutions, wars, collapse dynamics, and long-term evolution."
            ),
            "recommended_genre_tags": ["civilization_simulation", "political_fantasy", "systems_fiction"],
            "recommended_tone_tags": ["strategic", "expansive", "historical", "systemic"],
            "recommended_complexity": "god_level",
            "target_formats": ["strategy_game", "simulation_game", "world_bible", "novel_series"],
            "core_conflicts": [
                "resource scarcity versus expansion",
                "law versus survival",
                "centralization versus frontier autonomy",
                "innovation versus tradition",
                "collapse versus reform",
            ],
            "required_systems": [
                "resource loops",
                "migration",
                "law enforcement",
                "infrastructure decay",
                "war readiness",
                "faction growth",
                "causality graph",
            ],
            "default_seed_additions": [
                "Civilization pressure rises across food, law, war, belief, and economy.",
                "Regions evolve differently based on resources and institutions.",
                "No crisis stays isolated; every failure has system-level consequences.",
            ],
            "quality_focus": [
                "causal links",
                "pressure modeling",
                "non-static institutions",
                "resource realism",
                "evolution over time",
            ],
        },
        "dystopian_megacity": {
            "template_id": "dystopian_megacity",
            "name": "Dystopian Megacity",
            "description": (
                "A controlled urban world where surveillance, permits, class zones, propaganda, "
                "data systems, underground networks, and social scoring shape daily life."
            ),
            "recommended_genre_tags": ["dystopian_institutional", "mystery_intrigue", "urban_political"],
            "recommended_tone_tags": ["cold", "paranoid", "sleek", "claustrophobic"],
            "recommended_complexity": "extreme",
            "target_formats": ["film", "streaming_series", "game_lore_bible"],
            "core_conflicts": [
                "safety versus freedom",
                "identity versus classification",
                "privacy versus survival",
                "order versus humanity",
                "truth versus official data",
            ],
            "required_systems": [
                "surveillance bureau",
                "movement permits",
                "black-market identity",
                "urban zones",
                "propaganda systems",
                "data corruption",
                "resistance cells",
            ],
            "default_seed_additions": [
                "Every citizen leaves a record.",
                "Movement is legal only when classified correctly.",
                "Underground networks trade identity, silence, and access.",
            ],
            "quality_focus": [
                "surveillance logic",
                "urban geography",
                "ethical pressure",
                "information control",
                "non-generic resistance",
            ],
        },
        "romance_kingdom": {
            "template_id": "romance_kingdom",
            "name": "Romance Kingdom",
            "description": (
                "A relationship-driven political world where marriage law, inheritance, family honor, "
                "courtship rituals, class boundaries, and public reputation create emotional stakes."
            ),
            "recommended_genre_tags": ["romance_pressure", "political_fantasy", "court_intrigue"],
            "recommended_tone_tags": ["romantic", "elegant", "yearning", "dramatic"],
            "recommended_complexity": "extreme",
            "target_formats": ["novel_series", "streaming_series", "film"],
            "core_conflicts": [
                "love versus family duty",
                "public reputation versus private truth",
                "inheritance versus desire",
                "class law versus emotional equality",
                "marriage alliance versus agency",
            ],
            "required_systems": [
                "marriage customs",
                "inheritance law",
                "court reputation",
                "family alliances",
                "class speech",
                "public shame",
                "ritualized intimacy",
            ],
            "default_seed_additions": [
                "Marriage is both emotional and legal warfare.",
                "Public gestures can alter family futures.",
                "Romance creates political consequences.",
            ],
            "quality_focus": [
                "romance obstacles",
                "status-coded intimacy",
                "emotional consequences",
                "family politics",
                "non-generic court rituals",
            ],
        },
        "mythic_religious_world": {
            "template_id": "mythic_religious_world",
            "name": "Mythic Religious World",
            "description": (
                "A world organized around gods, broken vows, sacred law, dead divinities, prophecy, "
                "heresy, ritual, pilgrimage, and spiritual-political authority."
            ),
            "recommended_genre_tags": ["mythic_fantasy", "political_fantasy", "spiritual_mystery"],
            "recommended_tone_tags": ["sacred", "tragic", "awe-filled", "ancient"],
            "recommended_complexity": "god_level",
            "target_formats": ["novel_series", "film", "world_bible"],
            "core_conflicts": [
                "faith versus truth",
                "prophecy versus free will",
                "heresy versus institution",
                "ritual versus justice",
                "dead gods versus living power",
            ],
            "required_systems": [
                "gods and forces",
                "dead gods",
                "holy texts",
                "heresies",
                "ritual law",
                "sacred geography",
                "afterlife beliefs",
            ],
            "default_seed_additions": [
                "The dominant religion protects a version of history that may be false.",
                "Dead gods remain socially and politically dangerous.",
                "Rituals can reveal contradictions in law.",
            ],
            "quality_focus": [
                "belief consequences",
                "ritual specificity",
                "prophecy ambiguity",
                "spiritual politics",
                "mythic symbolism",
            ],
        },
        "movie_scale_world": {
            "template_id": "movie_scale_world",
            "name": "Movie-Scale World",
            "description": (
                "A focused, visually strong world designed for a tight story with clear locations, "
                "memorable symbols, fast stakes, cinematic identity, and adaptation-ready conflict."
            ),
            "recommended_genre_tags": ["cinematic_world", "mystery_intrigue", "political_fantasy"],
            "recommended_tone_tags": ["visual", "sharp", "high-stakes", "iconic"],
            "recommended_complexity": "high",
            "target_formats": ["film", "limited_series", "pitch_deck"],
            "core_conflicts": [
                "truth versus public lie",
                "one artifact versus one institution",
                "one relationship versus one law",
                "one location hiding one world-scale secret",
            ],
            "required_systems": [
                "limited but memorable locations",
                "strong visual palette",
                "clear antagonist pressure",
                "artifact or secret",
                "high-stakes deadline",
                "cinematic texture",
            ],
            "default_seed_additions": [
                "The world should be understandable quickly but imply deeper history.",
                "Every location should be visually memorable.",
                "The main conflict should be legible in one sentence.",
            ],
            "quality_focus": [
                "clarity",
                "visual identity",
                "tight causality",
                "adaptation potential",
                "high signal-to-noise",
            ],
        },
        "seven_novel_saga": {
            "template_id": "seven_novel_saga",
            "name": "Seven-Novel Saga World",
            "description": (
                "A deep long-form world designed for multi-book escalation, character growth, "
                "faction shifts, secrets, historical wounds, romance arcs, and civilization-scale change."
            ),
            "recommended_genre_tags": ["dark_academy", "political_fantasy", "civilization_simulation", "mystery_intrigue"],
            "recommended_tone_tags": ["epic", "tragic", "slow-burn", "layered"],
            "recommended_complexity": "god_level",
            "target_formats": ["seven_novel_series", "streaming_series", "game_lore_bible"],
            "core_conflicts": [
                "youth versus institution",
                "truth versus inherited order",
                "destiny versus agency",
                "love versus historical pressure",
                "civilization collapse versus reform",
            ],
            "required_systems": [
                "long chronology",
                "multi-layer factions",
                "romance obstacles",
                "artifact mysteries",
                "world pressure",
                "causality graph",
                "sequel expansion zones",
                "training metadata",
            ],
            "default_seed_additions": [
                "The world must support many major characters across many years.",
                "Early school conflicts should connect to late civilization conflicts.",
                "Every book should reveal a deeper layer of the same world logic.",
            ],
            "quality_focus": [
                "long-term escalation",
                "multi-book secrets",
                "character-world feedback",
                "civilization evolution",
                "franchise potential",
            ],
        },
    }

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        template_id = payload.get("template_id")
        seed_premise = payload.get("seed_premise", "")
        user_overrides = payload.get("overrides", {})

        warnings: List[str] = []

        if template_id is None:
            return self.build_result(
                success=True,
                data={
                    "available_templates": self.list_templates(),
                    "template_count": len(self.TEMPLATE_CATALOG),
                    "usage": {
                        "template_id": "dark_academy_empire",
                        "seed_premise": "Optional project-specific premise",
                        "overrides": {
                            "recommended_complexity": "god_level",
                            "target_formats": ["seven_novel_series"],
                        },
                    },
                },
                warnings=["No template_id provided; returned template catalog instead."],
                errors=[],
                generated_object_ids=[],
            )

        if template_id not in self.TEMPLATE_CATALOG:
            return self.build_result(
                success=False,
                data={
                    "available_templates": self.list_templates(),
                },
                warnings=[],
                errors=[f"Unknown template_id: {template_id}"],
                generated_object_ids=[],
            )

        template = dict(self.TEMPLATE_CATALOG[template_id])

        if user_overrides:
            template = self._apply_overrides(template, user_overrides)

        orchestrator_payload = self._build_orchestrator_payload(
            template=template,
            seed_premise=seed_premise,
        )

        return self.build_result(
            success=True,
            data={
                "template": template,
                "orchestrator_payload": orchestrator_payload,
                "training_notes": [
                    "Templates are configuration presets, not generated story content.",
                    "World Orchestrator can use orchestrator_payload to run all world engines consistently.",
                    "Templates improve controllability and benchmark repeatability.",
                    "Future ML systems can use template_id as a conditioning label.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def list_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "template_id": template["template_id"],
                "name": template["name"],
                "description": template["description"],
                "recommended_complexity": template["recommended_complexity"],
                "target_formats": template["target_formats"],
                "recommended_genre_tags": template["recommended_genre_tags"],
            }
            for template in self.TEMPLATE_CATALOG.values()
        ]

    def _apply_overrides(
        self,
        template: Dict[str, Any],
        user_overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        allowed_override_keys = {
            "recommended_genre_tags",
            "recommended_tone_tags",
            "recommended_complexity",
            "target_formats",
            "core_conflicts",
            "required_systems",
            "default_seed_additions",
            "quality_focus",
        }

        for key, value in user_overrides.items():
            if key in allowed_override_keys:
                template[key] = value

        template["user_overrides_applied"] = sorted(
            key for key in user_overrides if key in allowed_override_keys
        )

        ignored = sorted(
            key for key in user_overrides if key not in allowed_override_keys
        )

        if ignored:
            template["ignored_override_keys"] = ignored

        return template

    def _build_orchestrator_payload(
        self,
        *,
        template: Dict[str, Any],
        seed_premise: str,
    ) -> Dict[str, Any]:
        seed_parts = []

        if seed_premise:
            seed_parts.append(seed_premise)

        seed_parts.extend(template["default_seed_additions"])

        expanded_seed = " ".join(seed_parts)

        return {
            "template_id": template["template_id"],
            "template_name": template["name"],
            "seed_premise": expanded_seed,
            "genre_tags": template["recommended_genre_tags"],
            "tone_tags": template["recommended_tone_tags"],
            "desired_complexity": template["recommended_complexity"],
            "target_formats": template["target_formats"],
            "core_conflicts": template["core_conflicts"],
            "required_systems": template["required_systems"],
            "quality_focus": template["quality_focus"],
            "generation_mode": "template_guided_world_orchestration",
        }
