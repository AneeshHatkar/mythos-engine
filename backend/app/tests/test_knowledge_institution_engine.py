from backend.app.engines.world.knowledge_institution_engine import (
    KnowledgeInstitutionEngine,
)
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.world import InstitutionProfile, KnowledgeEducationProfile


def test_knowledge_institution_engine_returns_engine_result():
    engine = KnowledgeInstitutionEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A late imperial academy empire where forbidden books, sealed archives, "
                "relic research, and destiny classification control society."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "tone_tags": ["tragic"],
            "desired_complexity": "extreme",
        }
    )

    assert isinstance(result, EngineRunResult)
    assert result.success is True
    assert result.engine_name == "world.knowledge_institution_engine"
    assert "knowledge_education" in result.data
    assert "institutions" in result.data
    assert "training_notes" in result.data


def test_knowledge_institution_engine_generates_knowledge_controls():
    engine = KnowledgeInstitutionEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A dark academy empire where oath law, relic texts, and destiny files are censored."
            ),
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "god_level",
        }
    )

    knowledge = KnowledgeEducationProfile.model_validate(result.data["knowledge_education"])

    assert knowledge.literacy_rate_notes != ""
    assert len(knowledge.education_access_rules) >= 5
    assert len(knowledge.academy_entrance_rules) >= 5
    assert len(knowledge.forbidden_books) >= 7
    assert len(knowledge.public_archives) >= 5
    assert len(knowledge.secret_archives) >= 6
    assert len(knowledge.propaganda_systems) >= 5
    assert len(knowledge.censorship_methods) >= 6
    assert len(knowledge.information_punishments) >= 7

    assert "The Unlicensed Destiny Index" in knowledge.forbidden_books
    assert "The Relic Debt Ledger" in knowledge.secret_archives
    assert any("training-ineligible" in item for item in knowledge.information_punishments)


def test_knowledge_institution_engine_generates_institutions():
    engine = KnowledgeInstitutionEngine()

    result = engine.run(
        {
            "seed_premise": (
                "A relic academy empire where destiny classification, banks, temples, and border offices control opportunity."
            ),
            "genre_tags": ["dark_academy", "political_fantasy", "dystopian"],
            "desired_complexity": "god_level",
        }
    )

    institutions = [
        InstitutionProfile.model_validate(item)
        for item in result.data["institutions"]
    ]

    assert len(institutions) >= 10

    names = [institution.name for institution in institutions]

    assert "The Ashen Crown Academy" in names
    assert "The Silent Register" in names
    assert "The High Crown Court" in names
    assert "The Relic Appraisal and Recovery Board" in names
    assert "The Destiny Classification Board" in names
    assert "The Civic Observation Bureau" in names
    assert "The Institute of Corrected Futures" in names


def test_knowledge_institution_engine_institutions_have_depth():
    engine = KnowledgeInstitutionEngine()

    result = engine.run(
        {
            "seed_premise": "A political academy empire with sealed archives and court corruption.",
            "genre_tags": ["dark_academy", "political_fantasy"],
            "desired_complexity": "extreme",
        }
    )

    institutions = [
        InstitutionProfile.model_validate(item)
        for item in result.data["institutions"]
    ]

    for institution in institutions:
        assert institution.name != ""
        assert institution.institution_type != ""
        assert institution.public_purpose != ""
        assert institution.hidden_purpose != ""
        assert len(institution.entrance_rules) >= 3
        assert len(institution.rank_system) >= 3
        assert 0.0 <= institution.corruption_level <= 1.0
        assert len(institution.internal_factions) >= 3
        assert len(institution.story_uses) >= 3


def test_knowledge_institution_engine_warns_when_seed_missing():
    engine = KnowledgeInstitutionEngine()

    result = engine.run({})

    assert result.success is True
    assert len(result.warnings) == 1
    assert "seed_premise" in result.warnings[0]
