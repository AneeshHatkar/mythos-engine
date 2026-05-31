from backend.app.engines.simulation.opposite_nature_chemistry_engine import OppositeNatureChemistryEngine


def char_kael():
    return {
        "character_id": "char_kael",
        "origin": {
            "social_class": "academy_sponsored",
            "family_name_status": "distrusted",
            "origin_summary": "Scholarship student from a family whose records were erased by the court.",
            "family_pressure": "family name cannot testify without sponsor",
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes belonging can be revoked after public failure",
                "public_mask": "controlled precision",
                "private_truth": "terrified of being unreal",
            },
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "cognitive_inference"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
        "destiny": {"destiny_status": "hidden_destined"},
        "symbolic_role": "erased truth seeker",
    }


def char_seren():
    return {
        "character_id": "char_seren",
        "origin": {
            "social_class": "old_nobility",
            "family_name_status": "trusted",
            "origin_summary": "Noble court witness raised to protect family testimony.",
            "family_pressure": "family position depends on oath court loyalty",
        },
        "psychology": {
            "psychology_profile": {
                "core_wound": "believes love becomes dangerous when witnessed",
                "public_mask": "obedient noble composure",
                "private_truth": "wants truth more than safety",
            },
            "goal_profile": {
                "surface_goal": "protect family position",
                "hidden_goal": "free herself from inherited loyalty",
                "true_need": "truth without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "oath_magic"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "ceremonial_restraint_voice"}},
        "destiny": {"destiny_status": "false_destined"},
        "symbolic_role": "witness with divided loyalty",
    }


def char_flat():
    return {
        "character_id": "char_flat",
        "origin": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "believes belonging can be revoked after public failure"},
            "goal_profile": {
                "surface_goal": "survive academy ranking",
                "hidden_goal": "prove the ranking system is edited",
                "true_need": "belonging without permission",
            },
        },
        "power": {"skill_ontology": {"skill_family": "cognitive_inference"}},
        "dialogue": {"dialogue_voice_profile": {"voice_family": "controlled_subtext_voice"}},
        "symbolic_role": "erased truth seeker",
    }


def sample_world():
    return {
        "world_id": "world_velmora",
        "social_classes": ["academy_sponsored", "old_nobility"],
        "legal_constraints": ["distrusted family names require sponsor to testify"],
        "culture": ["public names carry legal trust", "class status controls court access"],
        "factions": ["Oath Court", "Relic Guild"],
        "economy": ["debt contracts", "relic labor"],
    }


def sample_story_dna():
    return {
        "core_question": "Can truth survive when institutions control whose testimony matters?",
        "moral_argument": "A person is not made worthy by institutional permission.",
        "recurring_symbol_set": ["names", "mirrors", "contracts"],
    }


def test_opposite_nature_engine_scores_high_chemistry_pair():
    engine = OppositeNatureChemistryEngine()

    result = engine.compare_characters(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={
            "target_format": "series",
            "genre": "dark academy romance political intrigue",
            "must_have": ["slow burn romance", "betrayal", "court trial"],
        },
    )

    assert result["success"] is True
    assert result["pair_id"] == "pair_char_kael_char_seren"
    assert result["contrast_score"] > 0.5
    assert result["chemistry_score"] > 0.25
    assert result["conflict_score"] > 0.25
    assert result["romance_potential"] > 0.25
    assert result["relationship_potential_label"] in {
        "high_heat_rivalry_romance",
        "dangerous_bond_with_betrayal_pressure",
        "high_conflict_high_chemistry",
        "romance_viable",
        "moderate_story_charge",
    }
    assert result["scene_fuel"]


def test_opposite_nature_engine_detects_lower_charge_similar_pair():
    engine = OppositeNatureChemistryEngine()

    result = engine.compare_characters(
        character_a=char_kael(),
        character_b=char_flat(),
        world_context=sample_world(),
        user_intent={},
    )

    assert result["success"] is True
    assert result["contrast_score"] < 0.6
    assert result["mirror_score"] >= 0.3
    assert result["relationship_potential_label"] in {
        "moderate_story_charge",
        "low_story_charge",
        "rivalry_viable",
    }


def test_opposite_nature_engine_outputs_repair_and_rupture_conditions():
    engine = OppositeNatureChemistryEngine()

    result = engine.compare_characters(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={"must_have": ["betrayal", "blackmail"]},
    )

    assert result["rupture_triggers"]
    assert result["repair_conditions"]
    assert "truth with cost" in result["repair_conditions"]
    assert result["betrayal_risk"] > 0.2


def test_opposite_nature_engine_scores_cast_selection_utility():
    engine = OppositeNatureChemistryEngine()

    result = engine.compare_characters(
        character_a=char_kael(),
        character_b=char_seren(),
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={"genre": "romance rivalry betrayal"},
    )

    utility = result["cast_selection_utility"]

    assert "utility_score" in utility
    assert "selection_reason" in utility
    assert isinstance(utility["recommended_for_main_cast"], bool)
    assert isinstance(utility["recommended_for_side_cast"], bool)
    assert isinstance(utility["recommended_for_background"], bool)


def test_opposite_nature_engine_compares_character_pool():
    engine = OppositeNatureChemistryEngine()

    result = engine.compare_character_pool(
        character_profiles=[char_kael(), char_seren(), char_flat()],
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={"target_format": "novel series", "genre": "dark academy romance"},
    )

    assert result["success"] is True
    assert result["character_count"] == 3
    assert result["pair_count"] == 3
    assert len(result["top_chemistry_pairs"]) == 3
    assert len(result["top_conflict_pairs"]) == 3
    assert result["pool_summary"]["average_chemistry"] >= 0.0
    assert "high_utility_pair_count" in result["pool_summary"]


def test_opposite_nature_engine_supports_large_pool_selection_signals():
    engine = OppositeNatureChemistryEngine()

    characters = []
    for i in range(15):
        base = char_kael() if i % 2 == 0 else char_seren()
        clone = dict(base)
        clone["character_id"] = f"char_{i}"
        clone["origin"] = dict(base["origin"])
        clone["origin"]["social_class"] = "old_nobility" if i % 3 == 0 else "academy_sponsored"
        characters.append(clone)

    result = engine.compare_character_pool(
        character_profiles=characters,
        world_context=sample_world(),
        story_dna=sample_story_dna(),
        user_intent={
            "target_format": "streaming series",
            "user_wants": "select strongest ensemble from a large generated character pool",
            "genre": "romance rivalry political betrayal",
        },
    )

    assert result["success"] is True
    assert result["character_count"] == 15
    assert result["pair_count"] == 105
    assert result["top_cast_selection_pairs"]
    assert result["pool_summary"]["average_cast_utility"] >= 0.0
