from backend.app.engines.story_generation.generation_contract_resolver import GenerationContractResolver
from backend.app.engines.story_generation.generation_mode_controller import GenerationModeController
from backend.app.schemas.story_generation import GenerationMode, StoryFormat, StoryIntent


def make_intent(**kwargs):
    data = {
        "intent_id": "intent_contract_test",
        "user_prompt": "Write a dark academy scene where Kael reveals evidence.",
        "desired_format": StoryFormat.scene,
        "generation_mode": GenerationMode.full_scene,
        "genres": ["dark_academy", "mystery"],
        "tone_tags": ["tense"],
        "required_character_ids": ["char_kael"],
        "required_plot_beats": ["secret_reveal"],
    }
    data.update(kwargs)
    return StoryIntent(**data)


def make_handoff():
    return {
        "simulation_id": "sim_001",
        "run_id": "run_001",
        "handoff_package_id": "handoff_001",
        "scene_payload_id": "scene_payload_001",
        "selected_character_ids": ["char_kael", "char_seren", "char_vask"],
        "linked_secret_ids": ["secret_rank_system"],
        "causal_node_ids": ["cause_trial_reveal"],
        "consequence_ids": ["cons_reputation_shift"],
        "relationship_ids": ["rel_kael_seren"],
        "world_context": {
            "world_rules": {
                "rule_oath_court_proof": "public evidence changes legal rank"
            }
        },
        "relationship_context": {
            "rel_kael_seren": {"trust": 0.3}
        },
        "quality_report_id": "quality_001",
        "anti_genericity_report_id": "anti_001",
    }


def test_contract_resolver_builds_contract_from_intent_and_handoff():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
        generation_control_payload={"generation_control_payload_id": "gen_control_001"},
    )

    contract = result["generation_contract"]

    assert result["success"] is True
    assert contract.generation_contract_id == "contract_intent_contract_test"
    assert contract.handoff_reference.simulation_id == "sim_001"
    assert contract.handoff_reference.handoff_package_id == "handoff_001"
    assert "char_kael" in contract.required_character_ids
    assert "char_seren" in contract.allowed_character_ids
    assert "secret_rank_system" in contract.required_secret_ids
    assert "cause_trial_reveal" in contract.required_causal_node_ids
    assert "cons_reputation_shift" in contract.required_consequence_ids
    assert "rel_kael_seren" in contract.required_relationship_ids


def test_contract_resolver_adds_format_contract_for_screenplay():
    intent = make_intent(
        desired_format=StoryFormat.screenplay,
        generation_mode=GenerationMode.screenplay_scene,
        user_prompt="Write this as a screenplay scene.",
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )

    contract = result["generation_contract"]

    assert contract.selected_format == StoryFormat.screenplay
    assert contract.format_contract["requires_scene_heading"] is True
    assert contract.format_contract["requires_dialogue_blocks"] is True
    assert contract.format_contract["minimize_internal_monologue"] is True


def test_contract_resolver_builds_originality_rules():
    intent = make_intent(
        forbidden_elements=["copying famous scenes", "secret spoilers"],
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )

    contract = result["generation_contract"]

    assert contract.originality_rules["no_raw_source_text"] is True
    assert contract.originality_rules["abstract_style_only"] is True
    assert "copying famous scenes" in contract.originality_rules["forbidden_elements"]


def test_contract_resolver_blocks_secret_reveal_for_mystery_without_required_reveal():
    intent = make_intent(
        required_plot_beats=[],
        genres=["mystery"],
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )

    contract = result["generation_contract"]

    assert "major_mystery_solution_until_planned_reveal" in contract.forbidden_secret_reveals


def test_contract_resolver_quality_thresholds_are_bounded():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
        overrides={
            "quality_thresholds": {
                "overall_score": 2.0,
                "voice_consistency": -1.0,
            }
        },
    )

    thresholds = result["generation_contract"].quality_thresholds

    assert thresholds["overall_score"] == 1.0
    assert thresholds["voice_consistency"] == 0.0


def test_contract_resolver_validates_contract():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    contract = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )["generation_contract"]

    validation = resolver.validate_contract(contract=contract)

    assert validation["success"] is True
    assert validation["valid"] is True
    assert "validation_required" in validation["passed_checks"]
    assert "provenance_required" in validation["passed_checks"]
    assert "quality_thresholds_present" in validation["passed_checks"]


def test_contract_resolver_explains_contract():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    contract = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )["generation_contract"]

    explanation = resolver.explain_contract(contract=contract)

    assert explanation["success"] is True
    assert explanation["explanation"]["selected_format"] == "scene"
    assert "char_kael" in explanation["explanation"]["character_rules"]["required"]
    assert len(explanation["why_it_matters"]) >= 2


def test_contract_resolver_supports_large_scale_warning():
    intent = make_intent(
        preferred_character_count=1000,
        desired_format=StoryFormat.multi_book_arc,
        generation_mode=GenerationMode.multi_book_arc,
    )
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )

    assert result["generation_contract"].selected_format == StoryFormat.multi_book_arc
    assert any("Huge entity pool" in warning for warning in result["warnings"])
    assert any("Long-form mode" in warning for warning in result["warnings"])


def test_contract_resolver_warns_when_no_simulation_id():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload={},
    )

    assert result["generation_contract"].handoff_reference.simulation_id == "sim_unknown"
    assert any("No simulation_id found" in warning for warning in result["warnings"])


def test_contract_resolver_outputs_dict_for_api_usage():
    intent = make_intent()
    mode = GenerationModeController().choose_mode(intent=intent)
    resolver = GenerationContractResolver()

    result = resolver.resolve_contract(
        intent=intent,
        mode_decision=mode,
        handoff_payload=make_handoff(),
    )

    data = result["generation_contract_dict"]

    assert data["story_intent_id"] == "intent_contract_test"
    assert data["selected_format"] == "scene"
    assert data["handoff_reference"]["simulation_id"] == "sim_001"
