from backend.app.engines.world.economy_law_engine import EconomyLawEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import EconomyProfile, LawSystem


def test_economy_law_engine_returns_engine_result():
    engine = EconomyLawEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where relic mines fund elite institutions, "
                "oath law controls inheritance, and destiny-bearing people become economic assets."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.economy_law_engine"
    assert "economy" in result.data
    assert "law" in result.data
    assert "training_notes" in result.data


def test_economy_law_engine_generates_resource_economy():
    engine = EconomyLawEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where legal credibility, healing, education, "
                "and destiny sponsorship are scarce resources."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    economy = EconomyProfile.model_validate(result.data["economy"])

    assert economy.currency_system != ""
    assert len(economy.main_resources) >= 6
    assert len(economy.trade_routes) >= 5
    assert economy.taxation_system != ""
    assert economy.debt_system != ""
    assert economy.labor_system != ""
    assert len(economy.black_markets) >= 6
    assert economy.wealth_concentration != ""
    assert economy.academy_or_institution_funding != ""
    assert len(economy.collapse_triggers) >= 6

    resource_names = [resource.name for resource in economy.main_resources]
    assert "Relic Ore and Memory-Stone" in resource_names
    assert "Destiny Sponsorship Rights" in resource_names
    assert "Legal Credibility" in resource_names


def test_economy_law_engine_generates_law_and_rights():
    engine = EconomyLawEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A magic academy empire with relic ownership law, oath courts, "
                "destiny classification, and forbidden knowledge."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "extreme",
        }
    )

    law = LawSystem.model_validate(result.data["law"])

    assert law.legal_summary != ""
    assert len(law.legal_classes) >= 6
    assert len(law.rights_by_birth) >= 6
    assert len(law.forbidden_acts) >= 9
    assert len(law.punishments) >= 8
    assert len(law.courts) >= 6
    assert len(law.law_enforcement_groups) >= 5
    assert len(law.legal_loopholes) >= 5
    assert law.corruption_level >= 0.7

    assert "Destiny Classification Review Chamber" in law.courts
    assert any("royal-class magic" in act for act in law.forbidden_acts)
    assert any("relic" in act.lower() for act in law.forbidden_acts)


def test_economy_law_engine_links_law_to_class_and_power():
    engine = EconomyLawEngine()

    result = engine.run(
        {
            "seed_premise": "A political fantasy empire where law protects founder bloodlines.",
            "genre_tags": ["political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    law = LawSystem.model_validate(result.data["law"])

    founder_rights = law.rights_by_birth["Founder-protected citizens"]

    assert "presumed credible in court" in founder_rights
    assert any("sponsor" in loophole.lower() for loophole in law.legal_loopholes)
    assert any("identity" in loophole.lower() for loophole in law.legal_loopholes)


def test_economy_law_engine_warns_when_seed_missing():
    engine = EconomyLawEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]
