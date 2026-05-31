from typing import Any, Dict, List

from backend.app.schemas.story_dna import StoryDNASeed


class StoryDNASeedService:
    """Builds theme, symbol, and moral-spine seeds for deep story intelligence."""

    def build_story_dna(
        self,
        *,
        project_id: str = "default_project",
        universe_id: str = "default_universe",
        world_profile: Dict[str, Any] | None = None,
        character_profiles: List[Dict[str, Any]] | None = None,
        genre_tags: List[str] | None = None,
    ) -> Dict[str, Any]:
        world = world_profile or {}
        characters = character_profiles or []
        genres = genre_tags or world.get("genre_tags") or ["academy", "political_intrigue", "romance"]

        world_text = self._joined(world)
        core_wounds = self._extract_character_wounds(characters)

        core_question = self._infer_core_question(world_text, genres)
        central_wound = core_wounds[0] if core_wounds else "belonging can be revoked by systems of power"
        moral_argument = self._infer_moral_argument(world_text, central_wound)

        seed = StoryDNASeed(
            project_id=project_id,
            universe_id=universe_id,
            core_question=core_question,
            central_wound=central_wound,
            moral_argument=moral_argument,
            recurring_symbol_set=self._infer_symbols(world_text, genres),
            image_system=self._infer_image_system(world_text, genres),
            emotional_promise=self._infer_emotional_promise(genres),
            philosophical_pressure=self._infer_philosophical_pressure(world_text),
            tragic_flaw_pattern="characters mistake public recognition for inner worth",
            redemption_path="truth, vulnerability, and chosen loyalty become stronger than institutional permission",
            corruption_path="characters trade truth for safety, status, and controlled belonging",
            meaning_of_power="power reveals what a person is willing to protect, distort, or sacrifice",
            meaning_of_love="love is proven when truth is protected without being weaponized",
            meaning_of_loss="loss becomes meaningful only when it changes what characters refuse to become",
            theme_tags=list(dict.fromkeys([*genres, "identity", "power", "truth", "belonging"])),
        )

        return {
            "success": True,
            "story_dna": seed.model_dump(),
            "chunk4_usage": [
                "event thematic pressure",
                "choice moral cost",
                "symbolic echo tracking",
                "relationship rupture/repair meaning",
                "scene seed emotional spine",
            ],
        }

    def _extract_character_wounds(self, characters: List[Dict[str, Any]]) -> List[str]:
        wounds = []
        for profile in characters:
            flat = self._flatten(profile)
            wound = flat.get("core_wound") or flat.get("central_wound")
            if wound:
                wounds.append(str(wound))
        return wounds

    def _infer_core_question(self, world_text: str, genres: List[str]) -> str:
        if "name" in world_text or "testify" in world_text or "court" in world_text:
            return "Can a person remain real when institutions control whose truth is recognized?"
        if "debt" in world_text:
            return "Can freedom exist when every choice is purchased by obligation?"
        if "romance" in genres:
            return "Can intimacy survive when survival rewards secrecy?"
        return "What does a person become when the world rewards the false self?"

    def _infer_moral_argument(self, world_text: str, central_wound: str) -> str:
        if "institution" in world_text or "court" in world_text or "academy" in world_text:
            return "A person is not made worthy by institutional permission."
        if "power" in world_text:
            return "Power without truth becomes another form of erasure."
        return f"The wound is false: {central_wound}"

    def _infer_symbols(self, world_text: str, genres: List[str]) -> List[str]:
        symbols = ["names", "mirrors", "contracts", "erased ink"]
        if "relic" in world_text:
            symbols.append("relic fragments")
        if "court" in world_text:
            symbols.append("oath marks")
        if "romance" in genres:
            symbols.append("unspoken vows")
        return list(dict.fromkeys(symbols))

    def _infer_image_system(self, world_text: str, genres: List[str]) -> List[str]:
        images = ["public rooms vs hidden corridors", "clean uniforms over old scars", "light on official documents"]
        if "memory" in world_text:
            images.append("memories stored like contraband")
        if "academy" in genres:
            images.append("ranking boards casting shadows")
        return images

    def _infer_emotional_promise(self, genres: List[str]) -> str:
        if "romance" in genres:
            return "The story will make withheld truth feel more intimate than confession."
        if "tragedy" in genres:
            return "The story will make every avoided truth return with interest."
        return "The story will make every victory feel earned by emotional cost."

    def _infer_philosophical_pressure(self, world_text: str) -> str:
        if "law" in world_text or "court" in world_text:
            return "law can preserve order while destroying truth"
        if "academy" in world_text:
            return "ranking systems turn private wounds into public currency"
        return "systems reward masks until characters mistake them for identity"

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
