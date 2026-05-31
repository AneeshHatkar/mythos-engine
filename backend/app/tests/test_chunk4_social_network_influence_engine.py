from backend.app.engines.simulation.social_network_influence_engine import SocialNetworkInfluenceEngine
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_social_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "rumor_edges": [
                    {
                        "from_location_id": "location_court",
                        "to_location_id": "location_archive",
                        "bidirectional": True,
                        "strength": 0.65,
                    }
                ]
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "faction_ids": ["faction_students"],
                    "faction_influence": 0.45,
                    "reputation_state": {"public": 0.25},
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "faction_ids": ["faction_oath_court"],
                    "faction_influence": 0.7,
                    "reputation_state": {"public": 0.35},
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_archive",
                metadata={
                    "faction_ids": ["faction_oath_court"],
                    "faction_influence": 0.65,
                    "reputation_state": {"public": 0.15},
                },
            ),
            "char_mira": SimulationCharacterState(
                character_id="char_mira",
                current_location_id="location_rooftop",
                metadata={},
            ),
        },
        relationship_states={
            "rel_kael_seren": SimulationRelationshipState(
                relationship_id="rel_kael_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.58,
                respect=0.62,
                affection=0.25,
                loyalty=0.18,
                rivalry=0.2,
                resentment=0.1,
                fear=0.05,
                power_imbalance=0.25,
                knowledge_asymmetry=0.3,
            ),
            "rel_seren_vask": SimulationRelationshipState(
                relationship_id="rel_seren_vask",
                character_a_id="char_seren",
                character_b_id="char_vask",
                trust=0.25,
                respect=0.4,
                affection=0.0,
                loyalty=0.1,
                rivalry=0.5,
                resentment=0.45,
                fear=0.25,
                power_imbalance=0.5,
                knowledge_asymmetry=0.5,
            ),
        },
        metadata={
            "obligation_registry": {
                "obl_seren_kael": {
                    "obligation_id": "obl_seren_kael",
                    "promiser_id": "char_seren",
                    "promisee_id": "char_kael",
                    "status": "active",
                    "pressure_score": 0.7,
                }
            },
            "leverage_registry": {
                "lev_vask_seren": {
                    "leverage_id": "lev_vask_seren",
                    "holder_id": "char_vask",
                    "target_id": "char_seren",
                    "status": "active",
                    "pressure_level": 0.8,
                }
            },
            "bargain_registry": {
                "bar_court": {
                    "bargain_id": "bar_court",
                    "linked_faction_ids": ["faction_oath_court"],
                }
            },
        },
    )


def test_social_engine_builds_social_graph():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()

    result = engine.build_social_graph(state=state)

    graph = result["social_graph"]

    assert result["success"] is True
    assert "char_kael" in graph["nodes"]
    assert "faction_oath_court" in graph["nodes"]
    assert "location_court" in graph["nodes"]
    assert "rel_kael_seren" in graph["edges"]
    assert any(edge["edge_type"] == "leverage" for edge in graph["edges"].values())
    assert any(edge["edge_type"] == "obligation" for edge in graph["edges"].values())


def test_social_engine_calculates_character_influence():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()
    graph = engine.build_social_graph(state=state)["social_graph"]

    report = engine.calculate_character_influence(
        state=state,
        character_id="char_seren",
        graph=graph,
    )

    assert report["success"] is True
    assert report["character_id"] == "char_seren"
    assert report["influence_score"] > 0.1
    assert report["centrality"] > 0
    assert report["connected_edge_count"] > 0


def test_social_engine_calculates_influence_path():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()
    graph = engine.build_social_graph(state=state)["social_graph"]

    report = engine.calculate_influence_path(
        state=state,
        source_id="char_kael",
        target_id="char_vask",
        graph=graph,
        max_depth=4,
    )

    assert report["success"] is True
    assert report["path_count"] >= 1
    assert report["best_path"]["path"][0] == "char_kael"
    assert report["best_path"]["path"][-1] == "char_vask"
    assert report["can_influence"] in {True, False}


def test_social_engine_evaluates_rumor_reach():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()

    report = engine.evaluate_rumor_reach(
        state=state,
        origin_id="char_kael",
        rumor_id="rumor_rank_edit",
        max_depth=3,
    )

    assert report["success"] is True
    assert report["origin_id"] == "char_kael"
    assert report["reachable_count"] >= 1
    assert "reachable_characters" in report
    assert "reach_score" in report


def test_social_engine_detects_coalitions():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()
    graph = engine.build_social_graph(state=state)["social_graph"]

    report = engine.detect_coalitions(state=state, graph=graph)

    assert report["success"] is True
    assert report["coalition_count"] >= 1
    assert "coalitions" in report
    assert all("coalition_type" in coalition for coalition in report["coalitions"])


def test_social_engine_detects_isolated_characters():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()
    graph = engine.build_social_graph(state=state)["social_graph"]

    report = engine.detect_isolated_characters(
        state=state,
        graph=graph,
        isolation_threshold=0.18,
    )

    assert report["success"] is True
    assert "isolated_characters" in report
    assert "isolated_count" in report


def test_social_engine_builds_social_influence_map():
    state = build_state()
    engine = SocialNetworkInfluenceEngine()

    result = engine.build_social_influence_map(state=state)

    assert result["success"] is True
    assert "ranked_characters" in result
    assert len(result["ranked_characters"]) == 4
    assert "character_influence" in result
    assert "coalitions" in result
    assert "chunk5_handoff" in result
    assert "social_center_character_id" in result["chunk5_handoff"]
