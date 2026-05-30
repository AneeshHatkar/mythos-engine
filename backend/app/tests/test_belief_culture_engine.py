from backend.app.engines.world.belief_culture_engine import BeliefCultureEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import BeliefSystem, CultureProfile


def test_belief_culture_engine_returns_engine_result():
    engine = BeliefCultureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where oath law, relics, prophecy, "
                "and destiny-bearing people shape public culture."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.belief_culture_engine"
    assert "belief" in result.data
    assert "culture" in result.data
    assert "training_notes" in result.data


def test_belief_culture_engine_generates_belief_system():
    engine = BeliefCultureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where oath religion, destiny prophecy, and hidden gods shape law."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    belief = BeliefSystem.model_validate(result.data["belief"])

    assert belief.belief_summary != ""
    assert len(belief.gods_or_forces) >= 5
    assert len(belief.dead_or_forgotten_gods) >= 3
    assert len(belief.holy_texts) >= 4
    assert len(belief.rituals) >= 5
    assert len(belief.taboos) >= 5
    assert belief.afterlife_beliefs != ""
    assert len(belief.heresies) >= 4
    assert belief.prophecy_system != ""
    assert belief.destiny_philosophy != ""
    assert belief.free_will_philosophy != ""

    assert any("Many-Fated" in force for force in belief.gods_or_forces)
    assert any("Broken" in heresy or "broken" in heresy.lower() for heresy in belief.heresies)


def test_belief_culture_engine_generates_culture_profile():
    engine = BeliefCultureEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A dark academy empire where family names, oath law, relic mines, and destiny shape culture."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "god_level",
        }
    )

    culture = CultureProfile.model_validate(result.data["culture"])

    assert culture.culture_summary != ""
    assert len(culture.naming_rules) >= 5
    assert culture.family_name_logic != ""
    assert len(culture.honorifics) >= 6
    assert len(culture.class_speech_differences) >= 5
    assert len(culture.slang_and_insults) >= 5
    assert len(culture.greetings) >= 5
    assert len(culture.food_culture) >= 5
    assert len(culture.clothing_culture) >= 5
    assert len(culture.marriage_customs) >= 5
    assert len(culture.funeral_customs) >= 5
    assert len(culture.festivals) >= 5
    assert len(culture.taboo_gestures) >= 5

    assert any("Founder" in rule or "founder" in rule.lower() for rule in culture.naming_rules)
    assert any("academy" in item.lower() for item in culture.class_speech_differences)


def test_belief_culture_engine_adds_destiny_specific_culture():
    engine = BeliefCultureEngine()

    result = engine.run(
        {
            "seed_premise": "A world where 27 destined people awaken under oath religion.",
            "genre_tags": ["political_fantasy"],
            "desired_complexity": "extreme",
        }
    )

    belief = BeliefSystem.model_validate(result.data["belief"])
    culture = CultureProfile.model_validate(result.data["culture"])

    assert any("Many-Fated" in force for force in belief.gods_or_forces)
    assert "destiny" in belief.destiny_philosophy.lower()
    assert any("destined" in rule.lower() for rule in culture.naming_rules)
    assert any("Starless" in festival for festival in culture.festivals)


def test_belief_culture_engine_warns_when_seed_missing():
    engine = BeliefCultureEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]
