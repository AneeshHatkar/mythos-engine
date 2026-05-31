from backend.app.engines.simulation.relationship_graph_engine import RelationshipGraphEngine
from backend.app.schemas.simulation import SimulationState, SimulationWorldState


def char_kael():
    return {
        "character_id": "char_kael",
        "origin": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "belonging can be revoked after public failure"},
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
        "origin": {"social_class": "old_nobility", "family_name_status": "trusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "love becomes dangerous when witnessed"},
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
        "origin": {"social_class": "academy_sponsored", "family_name_status": "distrusted"},
        "psychology": {
            "psychology_profile": {"core_wound": "belonging can be revoked after public failure"},
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
        "culture": ["public names carry legal trust", "class status controls court access"],
        "factions": ["Oath Court", "Relic Guild"],
    }


def test_relationship_graph_builds_multidimensional_edges():
    engine = RelationshipGraphEngine()

    result = engine.build_relationship_graph(
        character_profiles=[char_kael(), char_seren(), char_vask()],
        world_context=sample_world(),
        user_intent={"genre": "dark academy romance with rivalry and betrayal"},
    )

    assert result["success"] is True
    assert result["relationship_count"] == 3
    assert result["simulation_ready"] is True
    assert result["graph_metrics"]["relationship_count"] == 3

    first = next(iter(result["relationship_states"].values()))

    assert "trust" in first
    assert "romantic_tension" in first
    assert "betrayal_risk" in first
    assert "metadata" in first
    assert first["metadata"]["relationship_family"]


def test_relationship_graph_initializes_simulation_state():
    engine = RelationshipGraphEngine()
    state = SimulationState(
        simulation_id="sim_rel_graph_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
    )

    result = engine.initialize_state_relationships(
        state=state,
        character_profiles=[char_kael(), char_seren()],
        world_context=sample_world(),
        user_intent={"genre": "romance rivalry"},
    )

    updated = result["updated_state"]

    assert result["success"] is True
    assert result["relationship_count"] == 1
    assert len(updated.relationship_states) == 1
    assert updated.metadata["relationship_graph_history"]
    assert result["added_relationship_ids"]


def test_relationship_graph_does_not_overwrite_existing_by_default():
    engine = RelationshipGraphEngine()
    state = SimulationState(
        simulation_id="sim_rel_graph_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
    )

    first = engine.initialize_state_relationships(
        state=state,
        character_profiles=[char_kael(), char_seren()],
        world_context=sample_world(),
        user_intent={"genre": "romance rivalry"},
    )
    second = engine.initialize_state_relationships(
        state=state,
        character_profiles=[char_kael(), char_seren()],
        world_context=sample_world(),
        user_intent={"genre": "romance rivalry"},
    )

    assert first["added_relationship_ids"]
    assert second["skipped_relationship_ids"]
    assert len(second["updated_state"].relationship_states) == 1


def test_relationship_delta_from_event_public_humiliation():
    engine = RelationshipGraphEngine()

    delta = engine.build_relationship_delta_from_event(
        simulation_id="sim_001",
        relationship_id="rel_char_kael_char_seren",
        character_a_id="char_kael",
        character_b_id="char_seren",
        event_type="public_humiliation",
        intensity=0.8,
        reason="Seren fails to defend Kael during public ranking humiliation.",
        source_event_id="evt_humiliation",
    )

    assert delta.relationship_id == "rel_char_kael_char_seren"
    assert delta.trust_delta < 0
    assert delta.resentment_delta > 0
    assert delta.rivalry_delta > 0
    assert delta.source_event_id == "evt_humiliation"


def test_relationship_delta_preview_applies_bounded_changes():
    engine = RelationshipGraphEngine()
    graph = engine.build_relationship_graph(
        character_profiles=[char_kael(), char_seren()],
        world_context=sample_world(),
        user_intent={"genre": "romance rivalry"},
    )

    rel_payload = next(iter(graph["relationship_states"].values()))
    from backend.app.schemas.simulation import SimulationRelationshipState

    rel_state = SimulationRelationshipState.model_validate(rel_payload)

    delta = engine.build_relationship_delta_from_event(
        simulation_id="sim_001",
        relationship_id=rel_state.relationship_id,
        character_a_id=rel_state.character_a_id,
        character_b_id=rel_state.character_b_id,
        event_type="private_confession",
        intensity=0.7,
        reason="truth disclosure with vulnerability",
    )

    preview = engine.apply_relationship_delta_preview(
        relationship_state=rel_state,
        delta=delta,
    )

    assert preview["success"] is True
    assert preview["preview_state"]["trust"] >= rel_state.trust
    assert preview["preview_state"]["romantic_tension"] >= rel_state.romantic_tension
    assert preview["recommended"] is True


def test_relationship_graph_balance_warns_for_empty_graph():
    engine = RelationshipGraphEngine()

    metrics = engine.score_graph_balance({})

    assert metrics["relationship_count"] == 0
    assert metrics["warnings"] == ["relationship graph is empty"]


def test_relationship_graph_balance_warns_for_dense_graph():
    engine = RelationshipGraphEngine()

    dense = {}
    for i in range(201):
        dense[f"rel_{i}"] = {
            "trust": 0.2,
            "rivalry": 0.1,
            "resentment": 0.1,
            "betrayal_risk": 0.1,
            "romantic_tension": 0.0,
            "repair_potential": 0.2,
            "power_imbalance": 0.1,
        }

    metrics = engine.score_graph_balance(dense)

    assert metrics["relationship_count"] == 201
    assert metrics["relationship_density_warning"] is True
    assert any("dense" in warning for warning in metrics["warnings"])


def test_relationship_graph_supports_user_intent_and_no_fixed_cast_size():
    engine = RelationshipGraphEngine()

    characters = []
    for i in range(12):
        base = char_kael() if i % 2 == 0 else char_seren()
        cloned = dict(base)
        cloned["character_id"] = f"char_{i}"
        cloned["origin"] = dict(base["origin"])
        cloned["origin"]["social_class"] = "old_nobility" if i % 3 == 0 else "academy_sponsored"
        characters.append(cloned)

    result = engine.build_relationship_graph(
        character_profiles=characters,
        world_context=sample_world(),
        user_intent={
            "target_format": "series",
            "user_wants": "large ensemble with romance, rivalry, and political pressure",
        },
    )

    assert result["success"] is True
    assert result["character_count"] == 12
    assert result["relationship_count"] == 66
    assert result["simulation_ready"] is True
