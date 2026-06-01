from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


class StoryIntentInterpreter:
    """Interprets natural-language user story requests into structured intent.

    This is intentionally deterministic for v0.1 so tests remain stable.
    Later, an LLM provider can be added behind the same contract without
    changing downstream Chunk 5 engines.
    """

    engine_name = "story_generation.story_intent_interpreter"

    FORMAT_KEYWORDS = {
        StoryFormat.novel: ["novel", "literary", "book prose", "prose"],
        StoryFormat.chapter: ["chapter"],
        StoryFormat.short_story: ["short story"],
        StoryFormat.scene: ["scene"],
        StoryFormat.movie: ["movie", "film", "cinematic"],
        StoryFormat.screenplay: ["screenplay", "script"],
        StoryFormat.series_episode: ["episode", "tv episode"],
        StoryFormat.season_outline: ["season", "season arc"],
        StoryFormat.multi_book_arc: ["multi-book", "multi book", "saga", "franchise", "series of books"],
        StoryFormat.comic_scene: ["comic", "manga", "graphic novel"],
        StoryFormat.game_scene: ["game", "interactive", "choice-based", "rpg"],
        StoryFormat.treatment: ["treatment"],
    }

    GENRE_KEYWORDS = {
        "dark_academy": ["dark academy", "academy", "school ranking", "elite school"],
        "fantasy": ["fantasy", "magic", "magical", "kingdom", "empire"],
        "romance": ["romance", "romantic", "love", "slow burn", "enemies to lovers"],
        "political": ["political", "court", "empire", "faction", "rebellion", "government"],
        "mystery": ["mystery", "secret", "clue", "investigation", "crime"],
        "thriller": ["thriller", "suspense", "chase", "conspiracy"],
        "tragedy": ["tragic", "tragedy", "heartbreak", "loss"],
        "comedy": ["comedy", "funny", "humor", "comic relief"],
        "action": ["action", "fight", "battle", "war", "duel"],
        "sci_fi": ["sci-fi", "science fiction", "space", "cyber", "ai"],
        "mythic": ["myth", "mythic", "god", "prophecy", "legend"],
        "horror": ["horror", "scary", "haunting", "monster"],
    }

    TONE_KEYWORDS = {
        "dark": ["dark", "grim", "bleak"],
        "tragic": ["tragic", "heartbreaking", "devastating"],
        "epic": ["epic", "grand", "massive"],
        "intimate": ["intimate", "quiet", "personal"],
        "cinematic": ["cinematic", "visual", "movie-like"],
        "literary": ["literary", "poetic", "beautiful prose"],
        "tense": ["tense", "pressure", "suspenseful"],
        "romantic": ["romantic", "slow burn", "yearning"],
        "funny": ["funny", "humorous", "comedic"],
        "mysterious": ["mysterious", "cryptic", "secretive"],
        "non_cringe": ["not cringe", "non cringe", "not cheesy", "not corny"],
    }

    POV_KEYWORDS = {
        "first_person": ["first person", "1st person"],
        "third_limited": ["third limited", "third-person limited", "close third"],
        "third_omniscient": ["omniscient", "third omniscient"],
        "screenplay_camera": ["camera", "screenplay", "script"],
    }

    LENGTH_KEYWORDS = {
        "short": ["short", "brief", "quick"],
        "medium": ["medium", "normal length"],
        "long": ["long", "detailed", "deep"],
        "very_long": ["very long", "huge", "massive", "thousands of pages", "saga"],
    }

    FORBIDDEN_PATTERNS = [
        r"not\s+([a-zA-Z0-9_\- ]+)",
        r"without\s+([a-zA-Z0-9_\- ]+)",
        r"avoid\s+([a-zA-Z0-9_\- ]+)",
        r"no\s+([a-zA-Z0-9_\- ]+)",
    ]

    def interpret(
        self,
        *,
        user_prompt: str,
        intent_id: str = "intent_latest",
        defaults: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        defaults = defaults or {}
        prompt = user_prompt.strip()
        lower = prompt.lower()

        desired_format = self._detect_format(lower, defaults.get("desired_format"))
        generation_mode = self._detect_generation_mode(lower, desired_format, defaults.get("generation_mode"))

        genres = self._detect_keywords(lower, self.GENRE_KEYWORDS)
        tone_tags = self._detect_keywords(lower, self.TONE_KEYWORDS)

        pov_preference = self._detect_single(lower, self.POV_KEYWORDS, defaults.get("pov_preference"))
        target_length = self._detect_single(lower, self.LENGTH_KEYWORDS, defaults.get("target_length"))

        preferred_character_count = self._detect_character_count(lower)
        required_character_ids = self._detect_required_character_ids(prompt)
        forbidden_elements = self._detect_forbidden_elements(lower)

        emotional_beats = self._detect_emotional_beats(lower)
        plot_beats = self._detect_plot_beats(lower)
        ending_preference = self._detect_ending_preference(lower)

        density = self._detect_density(lower)
        intensities = self._detect_intensities(lower)

        commercial_target = self._detect_commercial_target(lower)
        audience_type = self._detect_audience_type(lower)

        intent = StoryIntent(
            intent_id=intent_id,
            user_prompt=prompt,
            desired_format=desired_format,
            generation_mode=generation_mode,
            genres=genres or defaults.get("genres", []),
            tone_tags=tone_tags or defaults.get("tone_tags", []),
            pov_preference=pov_preference,
            target_length=target_length,
            required_character_ids=required_character_ids or defaults.get("required_character_ids", []),
            preferred_character_count=preferred_character_count or defaults.get("preferred_character_count"),
            forbidden_elements=forbidden_elements or defaults.get("forbidden_elements", []),
            required_emotional_beats=emotional_beats,
            required_plot_beats=plot_beats,
            ending_preference=ending_preference,
            dialogue_density=density["dialogue_density"],
            worldbuilding_density=density["worldbuilding_density"],
            romance_intensity=intensities["romance_intensity"],
            action_intensity=intensities["action_intensity"],
            tragedy_intensity=intensities["tragedy_intensity"],
            comedy_intensity=intensities["comedy_intensity"],
            commercial_target=commercial_target,
            audience_type=audience_type,
            metadata={
                "engine_name": self.engine_name,
                "deterministic": True,
                "source": "rule_based_interpretation",
                "detected_keywords": {
                    "genres": genres,
                    "tone_tags": tone_tags,
                    "emotional_beats": emotional_beats,
                    "plot_beats": plot_beats,
                },
            },
        )

        warnings = self._build_warnings(intent=intent, lower_prompt=lower)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_intent": intent,
            "story_intent_dict": intent.model_dump(mode="json"),
            "warnings": warnings,
        }

    def explain_intent(self, *, intent: StoryIntent) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "intent_id": intent.intent_id,
            "summary": {
                "format": intent.desired_format.value,
                "generation_mode": intent.generation_mode.value,
                "genres": intent.genres,
                "tone_tags": intent.tone_tags,
                "pov_preference": intent.pov_preference,
                "target_length": intent.target_length,
                "required_character_ids": intent.required_character_ids,
                "preferred_character_count": intent.preferred_character_count,
                "forbidden_elements": intent.forbidden_elements,
                "required_emotional_beats": intent.required_emotional_beats,
                "required_plot_beats": intent.required_plot_beats,
                "ending_preference": intent.ending_preference,
            },
            "why_it_matters": [
                "This structured intent will feed the generation mode controller.",
                "The generation contract resolver will merge this intent with Chunk 4 handoff payloads.",
                "Validators will use this intent to check whether the output followed the user request.",
            ],
        }

    def merge_intent_with_overrides(
        self,
        *,
        intent: StoryIntent,
        overrides: Dict[str, Any],
    ) -> Dict[str, Any]:
        data = intent.model_dump(mode="json")

        for key, value in overrides.items():
            if key in data and value is not None:
                data[key] = value

        merged = StoryIntent(**data)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_intent": merged,
            "story_intent_dict": merged.model_dump(mode="json"),
            "overrides_applied": sorted(overrides.keys()),
        }

    def _detect_format(self, lower: str, default: Optional[Any] = None) -> StoryFormat:
        # More specific formats must be checked before generic "scene".
        # Special case: "novel chapter" means novel format with chapter generation mode.
        if "novel chapter" in lower or "chapter of a novel" in lower:
            return StoryFormat.novel

        priority_order = [
            StoryFormat.screenplay,
            StoryFormat.game_scene,
            StoryFormat.series_episode,
            StoryFormat.season_outline,
            StoryFormat.multi_book_arc,
            StoryFormat.comic_scene,
            StoryFormat.treatment,
            StoryFormat.movie,
            StoryFormat.chapter,
            StoryFormat.short_story,
            StoryFormat.novel,
            StoryFormat.scene,
        ]

        for story_format in priority_order:
            keywords = self.FORMAT_KEYWORDS.get(story_format, [])
            if any(keyword in lower for keyword in keywords):
                return story_format

        if default:
            return StoryFormat(default)

        return StoryFormat.scene

    def _detect_generation_mode(
        self,
        lower: str,
        story_format: StoryFormat,
        default: Optional[Any] = None,
    ) -> GenerationMode:
        if "rewrite" in lower or "revise" in lower or "improve" in lower:
            return GenerationMode.rewrite_existing
        if "continue" in lower or "next chapter" in lower:
            return GenerationMode.continue_story
        if "compare" in lower or "multiple drafts" in lower or "versions" in lower:
            return GenerationMode.compare_drafts
        if "novel chapter" in lower or "chapter of a novel" in lower:
            return GenerationMode.chapter
        if story_format == StoryFormat.chapter:
            return GenerationMode.chapter
        if story_format == StoryFormat.screenplay:
            return GenerationMode.screenplay_scene
        if story_format == StoryFormat.movie:
            return GenerationMode.movie_scene
        if story_format == StoryFormat.series_episode:
            return GenerationMode.series_episode
        if story_format == StoryFormat.season_outline:
            return GenerationMode.season_outline
        if story_format == StoryFormat.multi_book_arc:
            return GenerationMode.multi_book_arc
        if story_format == StoryFormat.game_scene:
            return GenerationMode.interactive_game_scene
        if "dialogue" in lower:
            return GenerationMode.dialogue_only
        if default:
            return GenerationMode(default)
        return GenerationMode.full_scene

    def _detect_keywords(self, lower: str, mapping: Dict[str, List[str]]) -> List[str]:
        detected = []
        for label, keywords in mapping.items():
            if any(keyword in lower for keyword in keywords):
                detected.append(label)
        return detected

    def _detect_single(
        self,
        lower: str,
        mapping: Dict[str, List[str]],
        default: Optional[str] = None,
    ) -> Optional[str]:
        for label, keywords in mapping.items():
            if any(keyword in lower for keyword in keywords):
                return label
        return default

    def _detect_character_count(self, lower: str) -> Optional[int]:
        patterns = [
            r"(\d+)\s+(?:main\s+)?characters",
            r"(\d+)\s+(?:important\s+)?people",
            r"(\d+)\s+destined\s+people",
            r"cast\s+of\s+(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, lower)
            if match:
                return int(match.group(1))

        if "large cast" in lower or "ensemble" in lower:
            return 10

        return None

    def _detect_required_character_ids(self, prompt: str) -> List[str]:
        ids = re.findall(r"char_[a-zA-Z0-9_]+", prompt)
        return sorted(set(ids))

    def _detect_forbidden_elements(self, lower: str) -> List[str]:
        forbidden = []

        for pattern in self.FORBIDDEN_PATTERNS:
            for match in re.finditer(pattern, lower):
                phrase = match.group(1).strip(" .,!?:;")
                if 2 <= len(phrase) <= 60:
                    forbidden.append(phrase)

        cleaned = []
        for item in forbidden:
            if item not in cleaned and item not in {"it", "this", "that"}:
                cleaned.append(item)

        return cleaned[:12]

    def _detect_emotional_beats(self, lower: str) -> List[str]:
        beats = []
        mapping = {
            "betrayal": ["betrayal", "betray", "traitor"],
            "confession": ["confession", "confess"],
            "heartbreak": ["heartbreak", "breaks his heart", "breaks her heart"],
            "reconciliation": ["reconcile", "repair", "forgive"],
            "sacrifice": ["sacrifice"],
            "public_humiliation": ["humiliation", "public shame", "embarrassed publicly"],
            "yearning": ["yearning", "longing", "slow burn"],
            "rage": ["rage", "anger", "furious"],
            "grief": ["grief", "mourning", "loss"],
            "hope": ["hope", "hopeful"],
        }

        for beat, keywords in mapping.items():
            if any(keyword in lower for keyword in keywords):
                beats.append(beat)

        return beats

    def _detect_plot_beats(self, lower: str) -> List[str]:
        beats = []
        mapping = {
            "secret_reveal": ["reveal", "secret comes out", "truth comes out"],
            "trial": ["trial", "court", "hearing"],
            "duel": ["duel"],
            "war": ["war", "battle"],
            "escape": ["escape", "run away"],
            "investigation": ["investigation", "investigate", "clue"],
            "ranking_ceremony": ["ranking ceremony", "rank ceremony"],
            "twist": ["twist", "reversal"],
            "ending_hook": ["hook", "cliffhanger"],
            "political_betrayal": ["political betrayal", "faction betrayal"],
        }

        for beat, keywords in mapping.items():
            if any(keyword in lower for keyword in keywords):
                beats.append(beat)

        return beats

    def _detect_ending_preference(self, lower: str) -> Optional[str]:
        if "happy ending" in lower:
            return "happy"
        if "sad ending" in lower or "tragic ending" in lower:
            return "tragic"
        if "bittersweet" in lower:
            return "bittersweet"
        if "cliffhanger" in lower:
            return "cliffhanger"
        if "open ending" in lower:
            return "open"
        return None

    def _detect_density(self, lower: str) -> Dict[str, float]:
        dialogue_density = 0.5
        worldbuilding_density = 0.5

        if "dialogue heavy" in lower or "lots of dialogue" in lower:
            dialogue_density = 0.8
        if "less dialogue" in lower or "minimal dialogue" in lower:
            dialogue_density = 0.25

        if "rich worldbuilding" in lower or "lots of worldbuilding" in lower:
            worldbuilding_density = 0.85
        if "less worldbuilding" in lower or "minimal worldbuilding" in lower:
            worldbuilding_density = 0.25

        return {
            "dialogue_density": dialogue_density,
            "worldbuilding_density": worldbuilding_density,
        }

    def _detect_intensities(self, lower: str) -> Dict[str, float]:
        return {
            "romance_intensity": self._intensity_from_words(
                lower,
                strong=["romantic", "romance", "slow burn", "yearning", "enemies to lovers"],
                very_strong=["intense romance", "heavy romance"],
            ),
            "action_intensity": self._intensity_from_words(
                lower,
                strong=["action", "fight", "duel", "battle", "war"],
                very_strong=["heavy action", "combat focused"],
            ),
            "tragedy_intensity": self._intensity_from_words(
                lower,
                strong=["tragic", "heartbreak", "loss", "grief"],
                very_strong=["devastating", "very tragic"],
            ),
            "comedy_intensity": self._intensity_from_words(
                lower,
                strong=["funny", "comedy", "humor", "comic relief"],
                very_strong=["very funny", "comedy heavy"],
            ),
        }

    def _intensity_from_words(
        self,
        lower: str,
        *,
        strong: List[str],
        very_strong: List[str],
    ) -> float:
        if any(keyword in lower for keyword in very_strong):
            return 0.9
        if any(keyword in lower for keyword in strong):
            return 0.7
        return 0.0

    def _detect_commercial_target(self, lower: str) -> Optional[str]:
        if "bestseller" in lower or "commercial" in lower or "marketable" in lower:
            return "commercial_high_appeal"
        if "prestige" in lower or "award" in lower:
            return "prestige_literary"
        if "franchise" in lower or "series potential" in lower:
            return "franchise_potential"
        return None

    def _detect_audience_type(self, lower: str) -> Optional[str]:
        if "young adult" in lower or "ya" in lower:
            return "young_adult"
        if "adult" in lower:
            return "adult"
        if "middle grade" in lower:
            return "middle_grade"
        if "anime" in lower:
            return "anime_audience"
        if "web novel" in lower:
            return "web_novel_audience"
        return None

    def _build_warnings(self, *, intent: StoryIntent, lower_prompt: str) -> List[str]:
        warnings = []

        if intent.preferred_character_count and intent.preferred_character_count > 20:
            warnings.append(
                "Large cast detected; later engines should use scaling, ranking, and subplot capacity checks."
            )

        if "thousands of pages" in lower_prompt or "1000" in lower_prompt:
            warnings.append(
                "Long-form generation detected; generate through outlines, chapters, scenes, memory updates, and continuation anchors rather than one raw output."
            )

        if not intent.genres:
            warnings.append("No clear genre detected; later engines may need defaults or user clarification.")

        if not intent.tone_tags:
            warnings.append("No clear tone detected; later engines may use neutral balanced tone.")

        return warnings
