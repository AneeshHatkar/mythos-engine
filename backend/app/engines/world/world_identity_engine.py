from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import (
    WorldDNAProfile,
    WorldIdentity,
    WorldScaleGranularityProfile,
)


class WorldIdentityEngine(BaseEngine):
    """Generates the deep identity layer of a world.

    This engine creates the first layer of a World Bible:
    - world identity
    - emotional promise
    - hidden truth
    - central contradiction
    - world DNA
    - scale/granularity profile

    It is intentionally deterministic/rule-based for Chunk 2.

    Later, Chunk 8 can add trained models, ranking models, embeddings,
    dataset-based inspiration, and preference learning while keeping this same
    structured output contract.
    """

    engine_name = "world.identity_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        target_format = payload.get("target_format", "novel_series")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; generated identity will be generic."
            )

        world_name = self._derive_world_name(payload)

        identity = self._build_identity(
            world_name=world_name,
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        dna = self._build_world_dna(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        scale = self._build_scale_profile(
            target_format=target_format,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "identity": identity.model_dump(mode="json"),
                "world_dna": dna.model_dump(mode="json"),
                "scale_granularity": scale.model_dump(mode="json"),
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _derive_world_name(self, payload: Dict[str, Any]) -> str:
        explicit_name = payload.get("world_name") or payload.get("name")
        if explicit_name:
            return str(explicit_name)

        seed = str(payload.get("seed_premise", "")).lower()

        if "ashen" in seed or "oath" in seed:
            return "Velmora"

        if "empire" in seed and "academy" in seed:
            return "Aureth Vale"

        if "civilization" in seed and "players" in seed:
            return "The Manyborn Realms"

        if "relic" in seed:
            return "Eldrath"

        return "Mythraen"

    def _build_identity(
        self,
        *,
        world_name: str,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> WorldIdentity:
        seed = seed_premise.lower()

        is_academy = "dark_academy" in genre_tags or "academy" in seed
        is_political = "political_fantasy" in genre_tags or "empire" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed
        is_relic = "relic" in seed
        is_magic = "magic" in seed

        alternate_names = [f"The {world_name} Dominion"]
        mythic_names = ["The World Beneath the First Oath"]
        forbidden_names = ["The Promise-Broken Realm"]

        if is_academy:
            alternate_names.append(f"The Academy Empire of {world_name}")

        if is_political:
            mythic_names.append("The Crown That Teaches Obedience")

        if is_destiny:
            forbidden_names.append("The Land Where Too Many Fates Awaken")

        if is_relic:
            mythic_names.append("The Realm of Buried Crowns")

        public_identity_parts = []

        if is_academy:
            public_identity_parts.append(
                "a civilization where elite academies decide who is allowed to rise"
            )

        if is_political:
            public_identity_parts.append(
                "an empire ruled through bloodline legitimacy, institutional control, and inherited law"
            )

        if is_magic:
            public_identity_parts.append(
                "a world where power is regulated through approved magical inheritance"
            )

        if not public_identity_parts:
            public_identity_parts.append(
                "a layered civilization shaped by power, memory, hierarchy, and social pressure"
            )

        hidden_identity_parts = []

        if is_destiny:
            hidden_identity_parts.append(
                "a world destabilized by the awakening of rare destiny-bearing people"
            )

        if is_tragic:
            hidden_identity_parts.append(
                "a society already living inside the consequences of an old collapse"
            )

        if is_political:
            hidden_identity_parts.append(
                "a political machine built to hide the truth of its own founding"
            )

        if is_relic:
            hidden_identity_parts.append(
                "an economy and religion quietly dependent on artifacts whose origin is not what citizens are told"
            )

        if not hidden_identity_parts:
            hidden_identity_parts.append(
                "a world whose deepest rules are not the ones its citizens are taught"
            )

        emotional_promise = (
            "power, longing, betrayal, inheritance, and the cost of becoming exceptional"
        )

        if is_tragic:
            emotional_promise = (
                "beauty, ambition, betrayal, grief, and the slow collapse of everything "
                "people were taught to trust"
            )

        if desired_complexity in {"extreme", "god_level"}:
            emotional_promise += (
                "; every institution, artifact, law, and family name hides a possible story engine"
            )

        central_question = (
            "What kind of person can survive a world that rewards obedience but needs rebellion?"
        )

        if is_destiny:
            central_question = (
                "What happens when too many people are born with destinies large enough "
                "to break civilization?"
            )

        if is_academy and is_political:
            central_question = (
                "Can truth survive when education itself is controlled by the ruling class?"
            )

        if is_academy and is_political and is_destiny:
            central_question = (
                "Can a civilization survive when the people it forbids from learning are "
                "the same people destiny chooses to change history?"
            )

        return WorldIdentity(
            world_name=world_name,
            alternate_names=alternate_names,
            mythic_names=mythic_names,
            forbidden_names=forbidden_names,
            public_identity="; ".join(public_identity_parts) + ".",
            hidden_identity="; ".join(hidden_identity_parts) + ".",
            emotional_promise=emotional_promise,
            genre_promise=", ".join(genre_tags) if genre_tags else "high-depth speculative drama",
            reader_promise=(
                "A world where every law, institution, family name, artifact, secret, "
                "boundary, and historical lie can become story fuel."
            ),
            world_thesis=(
                "Power survives by turning history into rules, but exceptional people expose "
                "the lies those rules depend on."
            ),
            symbolic_core=(
                "The crown, the oath, the locked archive, the forbidden classroom, "
                "and the artifact nobody is allowed to name."
            ),
            central_world_question=central_question,
            world_wound=(
                "A founding betrayal was converted into official law and taught as virtue."
            ),
            world_desire="The world wants stability, hierarchy, obedience, and controlled greatness.",
            world_fear=(
                "The world fears uncontrolled talent, revealed history, unrankable people, "
                "and destinies born outside approved bloodlines."
            ),
            world_contradiction=(
                "The society claims destiny proves divine order, but punishes destined people "
                "when they are born outside approved institutions, families, or classes."
            ),
            world_myth=(
                "The first rulers claimed the gods gave them the right to educate, judge, "
                "rank, and name truth itself."
            ),
        )

    def _build_world_dna(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> WorldDNAProfile:
        seed = seed_premise.lower()

        dominant_conflict_type = "class_vs_destiny"

        if "war" in seed:
            dominant_conflict_type = "war_vs_identity"
        elif "mystery" in genre_tags:
            dominant_conflict_type = "truth_vs_control"
        elif "romance" in genre_tags:
            dominant_conflict_type = "desire_vs_status"

        dominant_social_structure = "noble_academy_hierarchy"

        if "civilization" in seed:
            dominant_social_structure = "multi_faction_civilization_pressure"
        elif "dystopian" in genre_tags:
            dominant_social_structure = "surveillance_state_hierarchy"

        dominant_power_source = "institutional_access_to_forbidden_knowledge"

        if "relic" in seed:
            dominant_power_source = "relic_mines_and_oath_artifacts"

        if "magic" in seed:
            dominant_power_source = "regulated_magic_and_bloodline_law"

        dominant_emotional_atmosphere = "beautiful_collapse"

        if "hopeful" in tone_tags:
            dominant_emotional_atmosphere = "wounded_but_ascending"
        elif "grim" in tone_tags:
            dominant_emotional_atmosphere = "elegant_despair"

        uniqueness_axes = {
            "academy_politics": 0.9 if "dark_academy" in genre_tags else 0.55,
            "class_pressure": 0.88,
            "historical_lie_density": 0.86,
            "destiny_pressure": 0.92 if "destiny" in seed or "destined" in seed else 0.65,
            "institutional_control": 0.9,
            "symbolic_artifact_potential": 0.84,
            "world_scale_complexity": 0.95
            if desired_complexity in {"extreme", "god_level"}
            else 0.75,
            "future_training_structure_quality": 0.9,
        }

        return WorldDNAProfile(
            dominant_conflict_type=dominant_conflict_type,
            dominant_social_structure=dominant_social_structure,
            dominant_power_source=dominant_power_source,
            dominant_emotional_atmosphere=dominant_emotional_atmosphere,
            dominant_aesthetic_pattern=(
                "ancient prestige decaying into ritualized institutional control"
            ),
            dominant_historical_wound=(
                "a founding betrayal disguised as sacred law"
            ),
            dominant_law_pattern=(
                "rights determined by birth, education, controlled legitimacy, and access to truth"
            ),
            dominant_belief_pattern=(
                "oath-bound destiny religion mixed with political obedience"
            ),
            rarity_profile=(
                "high-rarity world: academy politics + oath mythology + destiny destabilization "
                "+ institutional information control"
            ),
            similarity_warnings=[],
            uniqueness_axes=uniqueness_axes,
        )

    def _build_scale_profile(
        self,
        *,
        target_format: str,
        desired_complexity: str,
    ) -> WorldScaleGranularityProfile:
        format_key = target_format.lower()

        if "movie" in format_key:
            return WorldScaleGranularityProfile(
                target_format=target_format,
                scale_label="movie_scale",
                expected_story_length="one feature film or limited adaptation arc",
                recommended_region_count=2,
                recommended_faction_count=4,
                recommended_institution_count=3,
                recommended_artifact_count=3,
                history_depth="focused",
                location_density="medium",
            )

        if "seven" in format_key or "series" in format_key:
            return WorldScaleGranularityProfile(
                target_format=target_format,
                scale_label="epic_series_scale",
                expected_story_length="seven-novel saga or multi-season prestige series",
                recommended_region_count=8,
                recommended_faction_count=12,
                recommended_institution_count=10,
                recommended_artifact_count=15,
                history_depth="deep",
                location_density="high",
            )

        if "civilization" in format_key or "simulation" in format_key:
            return WorldScaleGranularityProfile(
                target_format=target_format,
                scale_label="civilization_simulation_scale",
                expected_story_length="large-scale emergent civilization simulation",
                recommended_region_count=20,
                recommended_faction_count=30,
                recommended_institution_count=25,
                recommended_artifact_count=40,
                history_depth="very_deep",
                location_density="very_high",
            )

        if desired_complexity in {"extreme", "god_level"}:
            return WorldScaleGranularityProfile(
                target_format=target_format,
                scale_label="god_level_expandable_world",
                expected_story_length="expandable franchise world with novels, films, games, and spin-offs",
                recommended_region_count=10,
                recommended_faction_count=16,
                recommended_institution_count=14,
                recommended_artifact_count=20,
                history_depth="deep",
                location_density="high",
            )

        return WorldScaleGranularityProfile(
            target_format=target_format,
            scale_label="large",
            expected_story_length="long-form novel or expandable franchise world",
            recommended_region_count=5,
            recommended_faction_count=8,
            recommended_institution_count=7,
            recommended_artifact_count=10,
            history_depth="medium_deep",
            location_density="medium_high",
        )
