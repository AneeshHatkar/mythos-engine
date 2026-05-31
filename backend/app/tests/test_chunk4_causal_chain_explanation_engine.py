from backend.app.engines.simulation.causal_chain_explanation_engine import CausalChainExplanationEngine
from backend.app.engines.simulation.consequence_resolver import ConsequenceResolver
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_causal_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        character_states={
            "char_kael": SimulationCharacterState(character_id="char_kael"),
            "char_seren": SimulationCharacterState(character_id="char_seren"),
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.5,
            )
        },
        metadata={"consequence_queue": {}},
    )


def add_ready_consequence(state):
    state.metadata["consequence_queue"]["cons_relationship"] = {
        "consequence_id": "cons_relationship",
        "consequence_type": "relationship",
        "source_event_id": "evt_truth",
        "source_choice_id": "choice_truth",
        "summary": "Seren feels betrayed by public truth reveal.",
        "affected_entity_ids": ["char_kael", "char_seren"],
        "trigger_type": "immediate",
        "status": "ready",
        "severity": 0.8,
        "payload": {"action_type": "expose_secret"},
        "metadata": {},
    }


def test_causal_engine_creates_node_and_edge():
    engine = CausalChainExplanationEngine()

    node = engine.create_causal_node(
        node_id="node_choice_truth",
        node_type="choice",
        label="Truth choice",
        summary="Kael chooses to expose the truth.",
        entity_ids=["char_kael"],
        importance=0.8,
    )

    edge = engine.create_causal_edge(
        edge_id="edge_choice_causes_consequence",
        source_node_id="node_choice_truth",
        target_node_id="node_consequence",
        edge_type="causes",
        explanation="The reveal caused fallout.",
        strength=0.9,
    )

    assert node["node_type"] == "choice"
    assert node["importance"] == 0.8
    assert edge["edge_type"] == "causes"
    assert edge["strength"] == 0.9


def test_causal_engine_registers_graph_on_state():
    state = build_state()
    engine = CausalChainExplanationEngine()

    node = engine.create_causal_node(
        node_id="node_a",
        node_type="event",
        label="Event A",
        summary="A happened.",
    )

    result = engine.register_causal_graph_on_state(
        state=state,
        graph_id="graph_test",
        nodes=[node],
        edges=[],
    )

    assert result["success"] is True
    assert "graph_test" in state.metadata["causal_graphs"]
    assert "node_a" in state.metadata["causal_graphs"]["graph_test"]["nodes"]


def test_causal_engine_adds_node_and_edge():
    state = build_state()
    engine = CausalChainExplanationEngine()

    engine.register_causal_graph_on_state(state=state, graph_id="graph_test")

    node_a = engine.create_causal_node(
        node_id="node_a",
        node_type="event",
        label="Event A",
        summary="A happened.",
    )
    node_b = engine.create_causal_node(
        node_id="node_b",
        node_type="consequence",
        label="Consequence B",
        summary="B happened.",
    )
    engine.add_node_to_graph(state=state, graph_id="graph_test", node=node_a)
    engine.add_node_to_graph(state=state, graph_id="graph_test", node=node_b)

    edge = engine.create_causal_edge(
        edge_id="edge_a_b",
        source_node_id="node_a",
        target_node_id="node_b",
        edge_type="causes",
        explanation="A caused B.",
        strength=0.8,
    )

    result = engine.add_edge_to_graph(state=state, graph_id="graph_test", edge=edge)

    assert result["success"] is True
    assert "edge_a_b" in state.metadata["causal_graphs"]["graph_test"]["edges"]


def test_causal_engine_blocks_edge_with_missing_node():
    state = build_state()
    engine = CausalChainExplanationEngine()

    engine.register_causal_graph_on_state(state=state, graph_id="graph_test")

    edge = engine.create_causal_edge(
        edge_id="edge_missing",
        source_node_id="node_missing",
        target_node_id="node_other_missing",
        edge_type="causes",
        explanation="Invalid.",
    )

    result = engine.add_edge_to_graph(state=state, graph_id="graph_test", edge=edge)

    assert result["success"] is False
    assert len(result["blockers"]) == 2


def test_causal_engine_builds_graph_from_consequence_batch():
    state = build_state()
    add_ready_consequence(state)

    resolver = ConsequenceResolver()
    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_relationship",
    )

    engine = CausalChainExplanationEngine()
    result = engine.build_graph_from_consequence_batch(
        state=state,
        graph_id="graph_cons_relationship",
        consequence_id="cons_relationship",
        delta_batch=batch,
    )

    graph = state.metadata["causal_graphs"]["graph_cons_relationship"]

    assert result["success"] is True
    assert result["node_count"] >= 3
    assert result["edge_count"] >= 2
    assert "node_consequence_cons_relationship" in graph["nodes"]
    assert any(node["node_type"] == "delta" for node in graph["nodes"].values())


def test_causal_engine_builds_graph_from_choice_report():
    state = build_state()
    engine = CausalChainExplanationEngine()

    choice_report = {
        "choice_id": "choice_truth",
        "actor_id": "char_kael",
        "target_id": "char_seren",
        "action_type": "expose_secret",
        "summary": "Kael exposes the truth.",
        "feasibility_score": 0.72,
        "risk_profile": {"overall_risk": 0.7},
        "agency_report": {
            "score_components": {
                "goal_fit": 0.8,
                "relationship_fit": 0.55,
                "coercion_pressure": 0.4,
            }
        },
        "blockers": [],
    }

    result = engine.build_graph_from_choice_report(
        state=state,
        graph_id="graph_choice_truth",
        choice_report=choice_report,
    )

    graph = state.metadata["causal_graphs"]["graph_choice_truth"]

    assert result["success"] is True
    assert "node_choice_choice_truth" in graph["nodes"]
    assert any(edge["edge_type"] in {"enables", "pressures", "motivates"} for edge in graph["edges"].values())


def test_causal_engine_explains_why():
    state = build_state()
    engine = CausalChainExplanationEngine()

    node_a = engine.create_causal_node(
        node_id="node_choice",
        node_type="choice",
        label="Truth reveal choice",
        summary="Kael revealed the truth.",
        importance=0.8,
    )
    node_b = engine.create_causal_node(
        node_id="node_consequence",
        node_type="consequence",
        label="Relationship fallout",
        summary="Seren felt betrayed.",
        importance=0.7,
    )
    edge = engine.create_causal_edge(
        edge_id="edge_choice_consequence",
        source_node_id="node_choice",
        target_node_id="node_consequence",
        edge_type="causes",
        explanation="The public reveal damaged trust.",
        strength=0.85,
    )

    engine.register_causal_graph_on_state(
        state=state,
        graph_id="graph_why",
        nodes=[node_a, node_b],
        edges=[edge],
    )

    result = engine.explain_why(
        state=state,
        graph_id="graph_why",
        target_node_id="node_consequence",
    )

    assert result["success"] is True
    assert result["ranked_causes"][0]["node_id"] == "node_choice"
    assert "happened mainly because" in result["why_explanation"]
    assert result["confidence"] > 0.5


def test_causal_engine_audits_graph():
    state = build_state()
    engine = CausalChainExplanationEngine()

    node_a = engine.create_causal_node(
        node_id="node_a",
        node_type="event",
        label="A",
        summary="A.",
    )
    node_b = engine.create_causal_node(
        node_id="node_b",
        node_type="event",
        label="B",
        summary="B.",
    )
    edge = engine.create_causal_edge(
        edge_id="edge_a_b",
        source_node_id="node_a",
        target_node_id="node_b",
        edge_type="causes",
        explanation="A caused B.",
        strength=0.8,
    )

    engine.register_causal_graph_on_state(
        state=state,
        graph_id="graph_audit",
        nodes=[node_a, node_b],
        edges=[edge],
    )

    audit = engine.audit_causal_graph(state=state, graph_id="graph_audit")

    assert audit["success"] is True
    assert audit["node_count"] == 2
    assert audit["edge_count"] == 1
    assert audit["graph_quality_score"] > 0.5


def test_causal_engine_builds_graph_map():
    state = build_state()
    engine = CausalChainExplanationEngine()

    node = engine.create_causal_node(
        node_id="node_a",
        node_type="event",
        label="A",
        summary="A.",
    )
    engine.register_causal_graph_on_state(
        state=state,
        graph_id="graph_one",
        nodes=[node],
        edges=[],
    )

    result = engine.build_causal_graph_map(state=state)

    assert result["success"] is True
    assert result["graph_count"] == 1
    assert "graph_one" in result["causal_graph_records"]
    assert "average_graph_quality" in result
