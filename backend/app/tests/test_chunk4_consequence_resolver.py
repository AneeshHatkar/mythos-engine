from backend.app.engines.simulation.consequence_resolver import ConsequenceResolver
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_consequence_resolver_001",
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


def add_consequence(state, consequence_id, consequence_type, affected=None, payload=None, severity=0.7, status="ready"):
    state.metadata.setdefault("consequence_queue", {})[consequence_id] = {
        "consequence_id": consequence_id,
        "consequence_type": consequence_type,
        "source_event_id": "evt_truth",
        "source_choice_id": "choice_truth",
        "summary": f"{consequence_type} consequence summary.",
        "affected_entity_ids": affected or ["char_kael", "char_seren"],
        "trigger_type": "immediate",
        "status": status,
        "severity": severity,
        "payload": payload or {},
        "metadata": {},
    }


def test_consequence_resolver_builds_relationship_delta_batch():
    state = build_state()
    add_consequence(
        state,
        "cons_relationship",
        "relationship",
        payload={"action_type": "expose_secret"},
    )
    resolver = ConsequenceResolver()

    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_relationship",
    )

    assert batch.source_engine == resolver.engine_name
    assert len(batch.relationship_deltas) == 1
    delta = batch.relationship_deltas[0]
    assert delta.relationship_id == "rel_char_kael_char_seren"
    assert delta.trust_delta < 0
    assert delta.resentment_delta > 0
    assert "source_consequence_id=cons_relationship" in batch.warnings
    assert "chunk5_scene_type=relationship_fallout_scene" in batch.warnings


def test_consequence_resolver_builds_reputation_delta_batch():
    state = build_state()
    add_consequence(
        state,
        "cons_reputation",
        "reputation",
        affected=["char_kael"],
        payload={"action_type": "expose_secret"},
    )
    resolver = ConsequenceResolver()

    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_reputation",
    )

    assert len(batch.reputation_deltas) == 1
    delta = batch.reputation_deltas[0]
    assert delta.character_id == "char_kael"
    assert delta.reputation_score_delta < 0
    assert delta.trust_score_delta < 0


def test_consequence_resolver_builds_knowledge_delta_batch():
    state = build_state()
    add_consequence(
        state,
        "cons_knowledge",
        "knowledge",
        affected=["char_kael"],
        payload={
            "action_type": "expose_secret",
            "secret_ids": ["secret_rank_system_edited"],
            "evidence_ids": ["evidence_cracked_badge"],
            "rumor_ids": ["rumor_rank_edit"],
        },
    )
    resolver = ConsequenceResolver()

    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_knowledge",
    )

    assert len(batch.knowledge_deltas) == 1
    delta = batch.knowledge_deltas[0]
    assert delta.knowledge_holder_id == "char_kael"
    assert "secret_rank_system_edited" in delta.suspected_secret_ids_added
    assert "evidence_cracked_badge" in delta.evidence_ids_seen
    assert "rumor_rank_edit" in delta.rumor_ids_heard
    assert delta.no_magic_knowledge_checked is True


def test_consequence_resolver_builds_resource_delta_batch():
    state = build_state()
    add_consequence(
        state,
        "cons_resource",
        "resource",
        affected=["char_kael"],
        payload={
            "resource_id": "resource_archive_access",
            "amount_delta": -0.4,
            "resource_type": "archive_access",
        },
    )
    resolver = ConsequenceResolver()

    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_resource",
    )

    assert len(batch.resource_deltas) == 1
    delta = batch.resource_deltas[0]
    assert delta.resource_id == "resource_archive_access"
    assert delta.quantity_delta == -0.4


def test_consequence_resolver_builds_faction_delta_batch():
    state = build_state()
    add_consequence(
        state,
        "cons_faction",
        "faction",
        affected=["faction_oath_court"],
        severity=0.8,
    )
    resolver = ConsequenceResolver()

    batch = resolver.build_delta_batch_from_consequence(
        state=state,
        consequence_id="cons_faction",
    )

    assert len(batch.faction_deltas) == 1
    delta = batch.faction_deltas[0]
    assert delta.faction_id == "faction_oath_court"
    assert delta.legitimacy_delta < 0
    assert delta.hostility_delta > 0


def test_consequence_resolver_resolves_ready_consequence():
    state = build_state()
    add_consequence(state, "cons_relationship", "relationship")
    resolver = ConsequenceResolver()

    result = resolver.resolve_ready_consequence(
        state=state,
        consequence_id="cons_relationship",
    )

    assert result["success"] is True
    assert result["updated_consequence"]["status"] == "triggered"
    assert result["updated_consequence"]["metadata"]["resolver_engine"] == resolver.engine_name
    assert result["delta_batch"].relationship_deltas
    assert state.metadata["consequence_resolution_history"]


def test_consequence_resolver_blocks_non_ready_consequence():
    state = build_state()
    add_consequence(state, "cons_queued", "relationship", status="queued")
    resolver = ConsequenceResolver()

    result = resolver.resolve_ready_consequence(
        state=state,
        consequence_id="cons_queued",
    )

    assert result["success"] is False
    assert "not ready" in result["errors"][0]


def test_consequence_resolver_resolves_all_ready_consequences():
    state = build_state()
    add_consequence(state, "cons_relationship", "relationship")
    add_consequence(state, "cons_reputation", "reputation", affected=["char_kael"])
    add_consequence(state, "cons_queued", "knowledge", affected=["char_kael"], status="queued")
    resolver = ConsequenceResolver()

    result = resolver.resolve_all_ready_consequences(state=state)

    assert result["success"] is True
    assert result["ready_count"] == 2
    assert result["resolved_count"] == 2
    assert state.metadata["consequence_queue"]["cons_relationship"]["status"] == "triggered"
    assert state.metadata["consequence_queue"]["cons_reputation"]["status"] == "triggered"


def test_consequence_resolver_builds_chunk5_handoff():
    resolver = ConsequenceResolver()

    handoff = resolver.build_chunk5_handoff_from_consequence(
        {
            "consequence_type": "branch",
            "severity": 0.9,
            "summary": "Branch consequence.",
            "affected_entity_ids": ["char_kael"],
            "source_choice_id": "choice_truth",
            "source_event_id": "evt_truth",
            "payload": {"requires_branch_review": True},
        }
    )

    assert handoff["scene_type"] == "branch_point_scene"
    assert handoff["priority"] == "high"
    assert handoff["plot_branch_required"] is True
    assert handoff["must_show_causal_link"] is True
