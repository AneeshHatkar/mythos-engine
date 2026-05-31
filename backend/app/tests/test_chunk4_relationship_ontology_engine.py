from backend.app.engines.simulation.relationship_ontology_engine import RelationshipOntologyEngine


def char_kael():
    return {
        "character_id": "char_kael",
        "identity": {"name": "Kael"},
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
            },
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "cognitive_inference"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
    }


def char_seren():
    return {
        "character_id": "char_seren",
        "identity": {"name": "Seren"},
        "origin": {
            "social_class": "old_nobility",
            "family_name_status": "trusted",
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes love becomes dangerous when witnessed",
            },
            "goal_profile": {
                "surface_goal": "protect family position",
                "hidden_goal": "free herself from inherited loyalty",
                "true_need": "truth without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "oath_magic"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "ceremonial_restraint_voice"}},
    }


def char_vask():
    return {
        "character_id": "char_vask",
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
            },
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "protect truth",
                "true_need": "belonging without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "cognitive_inference"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
    }


def sample_world():
    return {
        "world_id": "world_velmora",
        "social_classes": ["erased", "academy_sponsored", "old_nobility"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "factions": ["Oath Court", "Relic Guild"],
        "culture": ["public names carry legal trust", "class status controls court access"],
        "institutions": ["Academy", "Court"],
    }


def sample_story_dna():
    return {
        "core_question": "Can a person remain real when institutions control whose truth is recognized?",
        "moral_argument": "A person is not made worthy by institutional permission.",
        "recurring_symbol_set": ["names", "mirrors", "contracts"],
    }


def test_relationship_ontology_classifies_romance_blocked_by_status():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={
            "genre": "dark academy fantasy romance",
            "relationship_preference": "slow burn romance with rivalry and public status pressure",
        },
    )

    assert result["success"] is True
    assert result["relationship_id"] == "rel_char_kael_char_seren"
    assert result["relationship_family"] in {
        "romance_blocked_by_public_status",
        "rivalry_with_romantic_subtext",
    }
    assert result["initial_state_recommendation"]["romantic_tension"] > 0
    assert "romantic_boundary_crossing" in result["event_fuel"]
    assert "no_romance_without_pressure" in result["simulation_hooks"]["recommended_validators"]


def test_relationship_ontology_classifies_rivalry_with_hidden_respect():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        user_intent={
            "relationship_preference": "rivalry and enemies to allies",
        },
    )

    assert result["success"] is True
    assert result["relationship_family"] in {
        "rivalry_with_hidden_respect",
        "rivalry_with_romantic_subtext",
        "romance_blocked_by_public_status",
    }
    assert result["initial_state_recommendation"]["respect"] >= 0.35
    assert result["initial_state_recommendation"]["rivalry"] >= 0.1
    assert "social_duel" in result["event_fuel"]


def test_relationship_ontology_classifies_betrayal_pressure():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={
            "must_have": ["betrayal", "blackmail", "secret leverage"],
        },
    )

    assert result["success"] is True
    assert result["relationship_family"] == "loyalty_under_betrayal_pressure"
    assert result["initial_state_recommendation"]["betrayal_risk"] >= 0.55
    assert "blackmail_attempt" in result["event_fuel"]
    assert "trust_tested_by_secret_leverage" in result["relationship_subtype"]


def test_relationship_ontology_detects_mirror_wound_bond():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_vask(),
        world_context={},
        story_dna={},
        user_intent={},
    )

    assert result["success"] is True
    assert result["relationship_family"] in {
        "mirror_wound_bond",
        "emergent_story_bond",
        "rivalry_with_hidden_respect",
    }
    assert result["ontology_axes"]["wound_mirror"] > 0
    assert result["initial_state_recommendation"]["repair_potential"] >= 0.25


def test_relationship_ontology_set_classifies_all_pairs():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship_set(
        character_profiles=[char_kael(), char_seren(), char_vask()],
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={"genre": "dark academy romance with betrayal and rivalry"},
    )

    assert result["success"] is True
    assert result["character_count"] == 3
    assert result["relationship_count"] == 3
    assert result["family_counts"]
    assert result["ensemble_relationship_ready"] is True


def test_relationship_ontology_outputs_simulation_hooks_and_repair_conditions():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={"genre": "political intrigue romance"},
    )

    assert result["simulation_hooks"]["relationship_arc_seed"]
    assert "trust" in result["simulation_hooks"]["must_track"]
    assert result["rupture_triggers"]
    assert result["repair_conditions"]
    assert "truth disclosure with cost" in result["repair_conditions"]


def test_relationship_ontology_respects_user_intent_without_hardcoding_story():
    engine = RelationshipOntologyEngine()

    result = engine.classify_relationship(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        user_intent={
            "user_wants": "I want slow burn romance, rivalry, court politics, and betrayal pressure.",
            "must_avoid": ["instant romance", "cheap chosen one trope"],
        },
    )

    assert result["success"] is True
    assert result["ontology_axes"]["romance_requested"] is True
    assert result["relationship_family"] in {
        "romance_blocked_by_public_status",
        "rivalry_with_romantic_subtext",
        "loyalty_under_betrayal_pressure",
    }
    assert "slow_burn_romance_arc" in result["genre_uses"]
