from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.schemas.simulation import (
    SimulationCharacterState,
    SimulationKnowledgeState,
    SimulationRelationshipState,
    SimulationState,
    SimulationWorldState,
)


def build_state():
    return SimulationState(
        simulation_id="sim_antigeneric_001",
        world_state=SimulationWorldState(
            world_id="world_velmora",
            metadata={
                "world_rules": {"oath_court": "truth has legal and magical cost"},
                "locations": ["location_court"],
                "factions": ["faction_oath_court"],
                "culture": {"law": "public proof can rewrite status"},
            },
        ),
        character_states={
            "char_kael": SimulationCharacterState(
                character_id="char_kael",
                current_location_id="location_court",
                metadata={
                    "display_name": "Kael",
                    "role_tags": ["protagonist"],
                    "story_function_tags": ["drive_plot", "reveal_truth"],
                    "source_type": "user_supplied_character",
                    "user_requested": True,
                    "backstory": "Kael was exiled after a false court ranking.",
                    "goals": {"main": "prove rank corruption without losing his last ally"},
                    "psychology": {"core_wound": "belonging can be revoked by public institutions"},
                    "voice_profile": {"style": "guarded, precise, angry when cornered"},
                    "backstory_depth": 0.9,
                    "agency_score": 0.8,
                    "uniqueness_score": 0.85,
                },
            ),
            "char_seren": SimulationCharacterState(
                character_id="char_seren",
                current_location_id="location_court",
                metadata={
                    "display_name": "Seren",
                    "role_tags": ["love_interest", "traitor"],
                    "story_function_tags": ["anchor_romance", "cause_betrayal", "test_loyalty"],
                    "backstory": "Seren serves the oath court that protects her younger brother.",
                    "goals": {"main": "protect the source while hiding her role"},
                    "psychology": {"core_wound": "love becomes dangerous when duty watches"},
                    "voice_profile": {"style": "controlled, restrained, formal under stress"},
                    "backstory_depth": 0.85,
                    "agency_score": 0.7,
                    "uniqueness_score": 0.8,
                },
            ),
            "char_vask": SimulationCharacterState(
                character_id="char_vask",
                current_location_id="location_court",
                metadata={
                    "display_name": "Vask",
                    "role_tags": ["antagonist"],
                    "story_function_tags": ["create_conflict", "force_choice"],
                    "backstory": "Vask weaponizes public proof rituals.",
                    "goals": {"main": "keep the oath court's ranking system untouched"},
                    "voice_profile": {"style": "polite institutional threat"},
                    "backstory_depth": 0.75,
                    "agency_score": 0.75,
                    "uniqueness_score": 0.7,
                },
            ),
        },
        knowledge_states={
            "char_kael": SimulationKnowledgeState(
                entity_id="char_kael",
                known_secret_ids=["secret_rank_system_edited"],
                evidence_seen_ids=["evidence_cracked_badge"],
            )
        },
        relationship_states={
            "rel_char_kael_char_seren": SimulationRelationshipState(
                relationship_id="rel_char_kael_char_seren",
                character_a_id="char_kael",
                character_b_id="char_seren",
                trust=0.28,
                affection=0.5,
                resentment=0.55,
                betrayal_risk=0.65,
                repair_potential=0.7,
                romantic_tension=0.5,
                power_imbalance=0.3,
                knowledge_asymmetry=0.6,
            )
        },
        metadata={
            "secret_registry": {"secret_rank_system_edited": {"secret_id": "secret_rank_system_edited"}},
            "evidence_registry": {"evidence_cracked_badge": {"evidence_id": "evidence_cracked_badge"}},
        },
    )


def create_run_state():
    state = build_state()
    orchestrator = InteractionSimulationOrchestrator()
    orchestrator.run_interaction_simulation(
        state=state,
        run_id="run_antigeneric",
        story_request={
            "story_request_id": "story_antigeneric",
            "cast_id": "cast_antigeneric",
            "scene_id": "scene_trial",
            "plot_arc_id": "arc_trial",
            "format": "novel",
            "primary_genres": ["dark_academy", "romance"],
            "tone_tags": ["tense", "mythic", "courtly"],
            "distinctive_elements": [
                "oath court ranking ritual",
                "cracked badge evidence",
                "romance where public truth harms the person loved",
            ],
            "constraints": {"must_preserve": "Seren cannot simply confess without cost"},
            "allow_any_character_count": True,
            "allow_project_created_characters": True,
            "required_roles": ["protagonist", "love_interest", "antagonist"],
            "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
            "scene_goal": "Kael reveals the cracked badge during the oath court ranking appeal.",
            "plot_goal": "Build a truth reveal where proof saves Kael but damages Seren.",
            "conflicts": [
                {
                    "conflict_id": "conflict_truth",
                    "conflict_type": "truth",
                    "title": "Proof that Saves Kael Breaks Seren",
                    "participant_ids": ["char_kael", "char_seren"],
                    "core_issue": "Kael needs public proof, but that proof exposes Seren's protected source.",
                    "opposing_goals": {
                        "char_kael": "use the cracked badge to overturn the false ranking",
                        "char_seren": "keep the source hidden to protect her brother",
                    },
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"],
                    "intensity": 0.85,
                    "stakes_score": 0.9,
                    "tension_score": 0.85,
                    "moral_complexity": 0.9,
                }
            ],
        },
        event_specs=[
            {
                "event_id": "evt_trial",
                "event_type": "trial",
                "event_name": "Kael places the cracked badge before the oath court.",
                "actor_ids": ["char_kael"],
                "target_ids": ["char_seren"],
                "witness_ids": ["char_vask"],
                "location_id": "location_court",
                "visibility": "public",
                "intensity": 0.85,
                "linked_secret_ids": ["secret_rank_system_edited"],
                "linked_evidence_ids": ["evidence_cracked_badge"],
            }
        ],
        target_cast_size=3,
    )
    return state


def test_anti_genericity_validator_checks_run():
    state = create_run_state()
    validator = SimulationAntiGenericityValidator()

    result = validator.validate_simulation_run(state=state, run_id="run_antigeneric")
    report = result["anti_genericity_report"]

    assert result["success"] is True
    assert report["run_id"] == "run_antigeneric"
    assert report["anti_genericity_score"] > 0.55
    assert report["label"] in {"acceptable", "specific", "highly_specific", "generic_risk"}
    assert "character_specificity" in report["checks"]
    assert "relationship_specificity" in report["checks"]
    assert "handoff_specificity" in report["checks"]
    assert "anti_genericity_run_antigeneric" in state.metadata["simulation_anti_genericity_reports"]


def test_anti_genericity_validator_detects_generic_user_request():
    validator = SimulationAntiGenericityValidator()

    report = validator.check_user_specificity(
        story_request={
            "scene_goal": "The chosen one must save the world from ancient evil.",
            "plot_goal": "Destiny awaits.",
            "primary_genres": ["fantasy"],
        }
    )

    assert report["score"] < 0.6
    assert "chosen one" in report["generic_phrase_hits"]
    assert "save the world" in report["generic_phrase_hits"]


def test_anti_genericity_validator_scores_specific_characters():
    state = build_state()
    validator = SimulationAntiGenericityValidator()

    report = validator.check_character_specificity(
        state=state,
        character_ids=["char_kael", "char_seren"],
    )

    assert report["score"] > 0.6
    assert report["character_reports"]["char_kael"]["has_backstory"] is True
    assert report["character_reports"]["char_seren"]["has_story_function"] is True


def test_anti_genericity_validator_scores_relationships():
    state = build_state()
    validator = SimulationAntiGenericityValidator()

    report = validator.check_relationship_specificity(
        state=state,
        character_ids=["char_kael", "char_seren"],
    )

    assert report["score"] > 0.5
    assert report["relationship_count"] == 1
    assert "rel_char_kael_char_seren" in report["relationship_reports"]


def test_anti_genericity_validator_builds_map():
    state = create_run_state()
    validator = SimulationAntiGenericityValidator()

    validator.validate_simulation_run(state=state, run_id="run_antigeneric")
    result = validator.build_anti_genericity_map(state=state)

    assert result["success"] is True
    assert result["report_count"] == 1
    assert result["best_report"]["report_id"] == "anti_genericity_run_antigeneric"
    assert "anti_genericity_run_antigeneric" in result["anti_genericity_reports"]
