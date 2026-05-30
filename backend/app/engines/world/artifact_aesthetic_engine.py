from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import ArtifactProfile, AestheticTextureProfile


class ArtifactAestheticEngine(BaseEngine):
    """Generates artifacts, symbolic objects, and sensory/aesthetic texture.

    This layer makes the world memorable, filmable, and emotionally distinct.

    It defines:
    - legendary artifacts
    - political objects
    - religious objects
    - forbidden books
    - heirlooms, contracts, maps, keys, seals, crowns, exam scrolls
    - ownership history
    - legal/religious/emotional status
    - visual palette
    - architecture
    - soundscape
    - smellscape
    - clothing silhouettes
    - elite vs poor aesthetics
    - cinematic identity

    Later chunks use this for plot objects, character inheritance, mystery clues,
    visual adaptation, scene design, branding, game objects, and world-bible export.
    """

    engine_name = "world.artifact_aesthetic_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        seed_premise = payload.get("seed_premise", "")
        genre_tags = payload.get("genre_tags", [])
        tone_tags = payload.get("tone_tags", [])
        desired_complexity = payload.get("desired_complexity", "high")

        warnings: List[str] = []

        if not seed_premise:
            warnings.append(
                "No seed_premise provided; artifacts and aesthetics will use broad default structures."
            )

        artifacts = self._build_artifacts(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        aesthetic_texture = self._build_aesthetic_texture(
            seed_premise=seed_premise,
            genre_tags=genre_tags,
            tone_tags=tone_tags,
            desired_complexity=desired_complexity,
        )

        return self.build_result(
            success=True,
            data={
                "artifacts": [artifact.model_dump(mode="json") for artifact in artifacts],
                "aesthetic_texture": aesthetic_texture.model_dump(mode="json"),
                "training_notes": [
                    "Artifacts are structured for future plot, mystery, inheritance, and adaptation systems.",
                    "Aesthetic fields are structured for visual generation, world-bible export, frontend display, and adaptation reports.",
                    "Symbolic objects should later be checked against history, religion, law, economy, and character arcs.",
                    "This layer helps prevent generic worlds by giving each world sensory specificity and memorable objects.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _build_artifacts(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> List[ArtifactProfile]:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_empire = "empire" in seed or "political_fantasy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_destiny = "destiny" in seed or "destined" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed

        artifacts: List[ArtifactProfile] = [
            ArtifactProfile(
                name="The Ashen Crown Shard",
                artifact_type="political_religious_relic",
                origin=(
                    "Said to be a broken piece of the first imperial crown, preserved after the founding ceremony. "
                    "Hidden records suggest it broke before the lawful ceremony began."
                ),
                ownership_history=[
                    "first ruling house",
                    "temple oath vault",
                    "academy ceremonial hall",
                    "missing during the Silent Revision",
                ],
                symbolism="A symbol of legitimacy that secretly proves legitimacy was fractured from the start.",
                legal_status="state-protected artifact; unauthorized possession is treason",
                religious_status="holy object publicly; contested witness privately",
                emotional_status="a beautiful object that makes powerful families afraid",
                power_or_function="reacts to false succession claims and corrupted oath records",
                plot_potential=[
                    "succession proof",
                    "public ceremony collapse",
                    "lineage reveal",
                    "artifact theft",
                    "religious scandal",
                ],
            ),
            ArtifactProfile(
                name="The Oath Bell",
                artifact_type="sacred_legal_object",
                origin=(
                    "Forged before written law, supposedly to hear vows clearly enough for gods and courts to recognize them."
                ),
                ownership_history=[
                    "old witness priests",
                    "founding courts",
                    "Temple of First Witness",
                    "sealed during periods of unrest",
                ],
                symbolism="The promise that law is sacred, and the fear that sacred law can hear lies.",
                legal_status="required for highest oath ceremonies",
                religious_status="central sacred instrument",
                emotional_status="comforting to the obedient, terrifying to the guilty",
                power_or_function="rings differently near broken promises, erased names, or false witnesses",
                plot_potential=[
                    "wedding vow scene",
                    "trial by oath",
                    "betrayal reveal",
                    "public confession",
                    "forbidden ritual",
                ],
            ),
            ArtifactProfile(
                name="The Forbidden Exam Scroll",
                artifact_type="forbidden_book_exam_object",
                origin=(
                    "A surviving copy of an early academy exam written before commoner scholars were erased from history."
                ),
                ownership_history=[
                    "first commoner teaching hall",
                    "unknown student rebel",
                    "low-market book broker",
                    "hidden study circle",
                ],
                symbolism="Proof that merit once meant something different.",
                legal_status="illegal educational object; possession can cause expulsion or imprisonment",
                religious_status="not sacred officially; treated like a relic by illegal tutors",
                emotional_status="hopeful, dangerous, humiliating to elites",
                power_or_function="contains questions that expose the modern curriculum's political edits",
                plot_potential=[
                    "secret study group",
                    "exam scandal",
                    "teacher sacrifice",
                    "commoner genius reveal",
                    "archive mystery",
                ],
            ),
            ArtifactProfile(
                name="The Witness Map",
                artifact_type="map_memory_object",
                origin=(
                    "An old map marking the locations of families who witnessed the First Oath before their names were removed."
                ),
                ownership_history=[
                    "border oath-family",
                    "smuggler courier",
                    "Silent Register copyist",
                    "unknown heir",
                ],
                symbolism="Geography as testimony.",
                legal_status="unrecognized by courts but dangerous if authenticated",
                religious_status="heretical witness-object",
                emotional_status="grief carried as geography",
                power_or_function="reveals places official maps intentionally omit",
                plot_potential=[
                    "journey arc",
                    "lost province reveal",
                    "family restoration",
                    "border alliance",
                    "treasure-map inversion",
                ],
            ),
            ArtifactProfile(
                name="The Ledger Knife",
                artifact_type="contract_weapon",
                origin=(
                    "A ceremonial blade used by old bankers to cut debt ribbons when a family became legally dependent."
                ),
                ownership_history=[
                    "Crown Bank of Ledgers",
                    "debt houses",
                    "private auction",
                    "black-market collector",
                ],
                symbolism="Debt disguised as refinement.",
                legal_status="legal in ceremonies, illegal as weapon evidence",
                religious_status="ritually neutral but socially feared",
                emotional_status="cold, elegant, humiliating",
                power_or_function="marks contracts so deeply that later forgery becomes difficult",
                plot_potential=[
                    "debt trap",
                    "contract assassination",
                    "family ruin",
                    "blackmail evidence",
                    "marriage negotiation threat",
                ],
            ),
            ArtifactProfile(
                name="The Archive Gloves",
                artifact_type="institutional_tool",
                origin=(
                    "Ink-dark gloves worn by archivists to prevent skin oils and unauthorized identity traces from touching records."
                ),
                ownership_history=[
                    "Silent Register apprentices",
                    "revision officers",
                    "archive thieves",
                    "trial evidence lockers",
                ],
                symbolism="Touching truth without being touched by it.",
                legal_status="restricted institutional tool",
                religious_status="used in oath-record handling",
                emotional_status="clinical, eerie, intimate",
                power_or_function="prevents certain records from recognizing the handler",
                plot_potential=[
                    "archive heist",
                    "identity concealment",
                    "evidence tampering",
                    "forbidden record retrieval",
                ],
            ),
        ]

        if is_relic:
            artifacts.extend(
                [
                    ArtifactProfile(
                        name="The Memory-Stone Core",
                        artifact_type="strategic_relic",
                        origin=(
                            "Recovered from the deepest legal layer of the Relic Ridge Mines after a collapse officially described as accidental."
                        ),
                        ownership_history=[
                            "unknown pre-imperial culture",
                            "mine-worker survivors",
                            "Relic Appraisal Board",
                            "academy research vault",
                        ],
                        symbolism="The buried past refusing to remain resource.",
                        legal_status="state-classified research object",
                        religious_status="suspected sleeping witness",
                        emotional_status="haunting, valuable, accusatory",
                        power_or_function="records emotional impressions from historical violence and reacts to repeated lies",
                        plot_potential=[
                            "relic debt reveal",
                            "mine revolt",
                            "artifact trial",
                            "memory vision",
                            "economic collapse clue",
                        ],
                    )
                ]
            )

        if is_destiny:
            artifacts.extend(
                [
                    ArtifactProfile(
                        name="The Unclaimed Fate Seal",
                        artifact_type="destiny_classification_object",
                        origin=(
                            "Used by classification boards to mark people whose destiny cannot be safely assigned to one institution."
                        ),
                        ownership_history=[
                            "Destiny Classification Board",
                            "sealed testing hall",
                            "stolen by a misranked student",
                        ],
                        symbolism="The world's attempt to stamp ownership onto the uncontrollable.",
                        legal_status="restricted state object",
                        religious_status="controversial prophecy instrument",
                        emotional_status="terrifying to families, insulting to the gifted",
                        power_or_function="records classification decisions and exposes altered destiny files",
                        plot_potential=[
                            "false ranking reveal",
                            "kidnapping evidence",
                            "rival destiny conflict",
                            "classification trial",
                        ],
                    )
                ]
            )

        if is_academy:
            artifacts.append(
                ArtifactProfile(
                    name="The Sponsor Candle",
                    artifact_type="academy_ritual_object",
                    origin=(
                        "A ceremonial candle exchanged between sponsor and student at the beginning of elite study."
                    ),
                    ownership_history=[
                        "academy ceremony halls",
                        "noble sponsors",
                        "students who owe more than tuition",
                    ],
                    symbolism="Opportunity that burns only because someone owns the flame.",
                    legal_status="recognized proof of sponsorship",
                    religious_status="minor oath object",
                    emotional_status="beautiful, hopeful, possessive",
                    power_or_function="binds student reputation to sponsor reputation",
                    plot_potential=[
                        "student debt",
                        "mentor betrayal",
                        "sponsorship romance tension",
                        "public rejection scene",
                    ],
                )
            )

        if is_tragic:
            artifacts.append(
                ArtifactProfile(
                    name="The Chair of Unread Names",
                    artifact_type="funerary_memory_object",
                    origin=(
                        "A plain empty chair placed at funerals for people whose names cannot be legally spoken."
                    ),
                    ownership_history=[
                        "erased families",
                        "mourning clergy",
                        "low-market memorial circles",
                    ],
                    symbolism="The grief law refuses to recognize.",
                    legal_status="tolerated in private, suspicious in public",
                    religious_status="folk-sacred object",
                    emotional_status="quiet devastation",
                    power_or_function="none officially; socially powerful because everyone knows what it means",
                    plot_potential=[
                        "funeral scene",
                        "erased person reveal",
                        "family grief",
                        "rebellion symbol",
                    ],
                )
            )

        if desired_complexity in {"extreme", "god_level"}:
            artifacts.append(
                ArtifactProfile(
                    name="The Corrected Future Lens",
                    artifact_type="experimental_research_object",
                    origin=(
                        "Built by the Institute of Corrected Futures to model possible rebellions, marriages, scandals, and institutional collapses."
                    ),
                    ownership_history=[
                        "future analysts",
                        "academy risk office",
                        "unknown sabotage attempt",
                    ],
                    symbolism="The arrogance of trying to calculate human becoming.",
                    legal_status="classified research device",
                    religious_status="suspected anti-prophecy heresy",
                    emotional_status="cold, seductive, horrifying",
                    power_or_function="simulates social outcomes but becomes unreliable near unclassified destiny pressure",
                    plot_potential=[
                        "prediction horror",
                        "AI/ML mirror for later MythOS systems",
                        "villain planning",
                        "future-choice conflict",
                    ],
                )
            )

        return artifacts

    def _build_aesthetic_texture(
        self,
        *,
        seed_premise: str,
        genre_tags: List[str],
        tone_tags: List[str],
        desired_complexity: str,
    ) -> AestheticTextureProfile:
        seed = seed_premise.lower()

        is_academy = "academy" in seed or "dark_academy" in genre_tags
        is_relic = "relic" in seed
        is_oath = "oath" in seed
        is_tragic = "tragic" in tone_tags or "collapse" in seed

        visual_palette = [
            "ash white",
            "oxidized gold",
            "ink black",
            "deep burgundy",
            "fog gray",
            "candle amber",
            "old parchment",
        ]

        if is_relic:
            visual_palette.extend(["mineral green", "memory-stone blue"])

        if is_tragic:
            visual_palette.append("funeral silver")

        architecture_style = (
            "Monumental academic-imperial architecture: high arches, sealed courtyards, bell towers, library bridges, "
            "stone lecture halls, carved family names, and hidden service corridors beneath ceremonial spaces."
        )

        if is_oath:
            architecture_style += (
                " Oath spaces are circular and echo-heavy so vows feel physically witnessed."
            )

        soundscape = [
            "distant bells before exams and trials",
            "quills scratching in archive rooms",
            "boots on polished stone corridors",
            "market whispers under canal bridges",
            "carriage wheels slowing at class checkpoints",
            "wind through border ruins",
        ]

        if is_relic:
            soundscape.append("low mineral humming near relic vaults")

        smellscape = [
            "ink, candle wax, and cold stone in academies",
            "wet paper and metal in archives",
            "coal smoke and mineral dust near relic roads",
            "spiced street food and damp cloth in low markets",
            "winter air mixed with old perfume during court ceremonies",
        ]

        food_textures = [
            "thin ceremonial wafers served before oath rituals",
            "dense miner bread with salt crust",
            "sharp pickled vegetables from border roads",
            "silken noble desserts arranged by family color",
            "portable low-market wraps meant to be eaten while moving",
        ]

        clothing_silhouettes = [
            "long academy coats with subtle rank piping",
            "high-collared noble formalwear",
            "ink-dark archivist gloves and sleeves",
            "layered border cloaks with hidden document pockets",
            "mine scarves wrapped close to the mouth",
            "student uniforms designed to reveal sponsorship status",
        ]

        symbolic_colors = [
            "oath white for legitimacy",
            "ink black for records and controlled truth",
            "crown gold for inherited authority",
            "burgundy for debt and family obligation",
            "fog gray for erased history",
            "lantern amber for illegal knowledge",
        ]

        if is_relic:
            symbolic_colors.append("memory-stone blue for relic witness and hidden debt")

        elite_visual_style = (
            "Controlled beauty: clean lines, expensive restraint, polished shoes, white fabric, gold pins, quiet gloves, "
            "old jewelry, and clothing that suggests nobody has ever had to run."
        )

        poor_visual_style = (
            "Practical resilience: repaired hems, hidden pockets, weathered boots, layered cloth, market dye, miner scarves, "
            "borrowed uniforms, and objects modified for survival."
        )

        cinematic_identity = (
            "A prestige dark-academy political fantasy world where every room looks beautiful enough to trust and structured enough to trap you. "
            "The visual language should contrast ceremony with rot, silence with pressure, and elegance with exploitation."
        )

        if desired_complexity in {"extreme", "god_level"}:
            cinematic_identity += (
                " Adaptation design should track class visually: who has light, who has space, who has silence, who has paperwork, and who has to move through hidden routes."
            )

        return AestheticTextureProfile(
            visual_palette=visual_palette,
            architecture_style=architecture_style,
            soundscape=soundscape,
            smellscape=smellscape,
            food_textures=food_textures,
            clothing_silhouettes=clothing_silhouettes,
            symbolic_colors=symbolic_colors,
            elite_visual_style=elite_visual_style,
            poor_visual_style=poor_visual_style,
            cinematic_identity=cinematic_identity,
        )
