import pytest
from pydantic import ValidationError

from backend.app.schemas.character import (
    AdaptabilityProfile,
    CharacterAgentState,
    CharacterBibleExport,
    CharacterDatasetMetadata,
    CharacterIdentity,
    CharacterScoreProfile,
    CharacterSnapshotMetadata,
    CompleteCharacterProfile,
    DestinyProfile,
    EmotionVector,
    FamilyMember,
    FamilyProfile,
    GoalRecord,
    GrowthTrack,
    MemoryRecord,
    MoralProfile,
    OriginProfile,
    PeopleTypeProfile,
    PopulationGroup,
    ProphecyLink,
    PsychologyProfile,
    ReputationProfile,
    SkillProfile,
    TraumaRecord,
)


def test_character_identity_schema_validates_required_fields():
    identity = CharacterIdentity(
        character_id="char_kael",
        project_id="proj_ashen",
        universe_id="uni_main",
        world_id="world_velmora",
        name="Kael Veyran",
        role="hidden kingmaker",
        importance_level=4,
        character_depth_level=4,
        culture="Lower Ash",
        public_status="low-ranked scholarship student",
        private_truth="sees political and emotional patterns before others do",
    )

    assert identity.character_id == "char_kael"
    assert identity.name == "Kael Veyran"
    assert identity.importance_level == 4
    assert identity.character_depth_level == 4


def test_population_group_schema_tracks_distribution_constraints():
    group = PopulationGroup(
        group_id="pop_lower_ash_students",
        world_id="world_velmora",
        group_name="Lower Ash scholarship students",
        social_class="commoner",
        occupation_roles=["student", "runner", "archive aide"],
        estimated_count=120,
        percentage_of_population=4.5,
        education_access=0.25,
        wealth_access=0.1,
        legal_trust_level=0.2,
        destiny_density=0.04,
    )

    assert group.estimated_count == 120
    assert group.percentage_of_population == 4.5
    assert group.education_access == 0.25


def test_people_type_profile_contains_pressure_behavior():
    people_type = PeopleTypeProfile(
        people_type_id="people.hidden_kingmaker",
        name="Hidden Kingmaker",
        category="strategic_support",
        description="A low-visibility person whose choices determine who rises.",
        rarity="rare",
        compatible_roles=["protagonist", "mentor", "catalyst"],
        pressure_responses=["observes before acting", "protects through indirect moves"],
        likely_wounds=["unseen worth"],
        likely_goals=["be chosen without performing value"],
    )

    assert "observes before acting" in people_type.pressure_responses
    assert people_type.rarity == "rare"


def test_origin_profile_tracks_world_grounding():
    origin = OriginProfile(
        origin_id="origin_kael",
        character_id="char_kael",
        birth_status="orphan",
        social_class="commoner",
        origin_location="Lower Ash District",
        family_name_trust=0.1,
        wealth_rank=0.05,
        education_access=0.25,
        forbidden_access=["royal magic curriculum"],
        class_wound="believes visibility leads to humiliation",
        mobility_score=0.35,
        world_constraint_notes=["commoners cannot legally study royal magic"],
    )

    assert origin.family_name_trust == 0.1
    assert "royal magic curriculum" in origin.forbidden_access


def test_family_profile_supports_family_graph_and_secrets():
    family = FamilyProfile(
        family_id="fam_veyran",
        character_id="char_kael",
        family_name="Veyran",
        family_status="erased",
        family_reputation="legally unreliable",
        family_debt=["archive debt"],
        family_secrets=["records were deliberately sealed"],
        parents=[FamilyMember(name="Unknown mother", relation="mother", status="missing")],
        family_artifact_links=["cracked rank badge"],
    )

    assert family.family_status == "erased"
    assert family.parents[0].relation == "mother"
    assert "records were deliberately sealed" in family.family_secrets


def test_psychology_profile_requires_behavior_rule():
    psychology = PsychologyProfile(
        psychology_id="psy_kael",
        character_id="char_kael",
        core_wound="performance-based love",
        core_desire="to be chosen without proving usefulness",
        core_fear="being ordinary and disposable",
        core_lie="love is only given to useful people",
        core_truth="he has worth outside utility",
        defense_mechanism="cold restraint",
        betrayal_response="withdraws and waits for a decisive moment",
        behavior_rules=["When publicly humiliated, he becomes silent and strategically observant."],
    )

    assert psychology.core_wound == "performance-based love"
    assert len(psychology.behavior_rules) == 1

    with pytest.raises(ValidationError):
        PsychologyProfile(
            psychology_id="psy_bad",
            character_id="char_bad",
            core_wound="wound",
            core_desire="desire",
            core_fear="fear",
            core_lie="lie",
            core_truth="truth",
            defense_mechanism="mask",
            behavior_rules=[],
        )


def test_trauma_emotion_memory_reputation_goal_schemas():
    trauma = TraumaRecord(
        trauma_id="trauma_public_rank",
        character_id="char_kael",
        trauma_source="public ranking humiliation",
        trauma_intensity=0.8,
        trigger_events=["ranking ceremony"],
        avoidance_behavior="avoids public accusation",
        coping_behavior="studies the system quietly",
        healing_condition="being defended without being useful first",
    )

    emotion = EmotionVector(shame=0.7, anger=0.4, hope=0.2)

    memory = MemoryRecord(
        memory_id="mem_badge",
        character_id="char_kael",
        content="He remembers the cracked rank badge being thrown at his feet.",
        emotional_weight=0.9,
        trigger_terms=["badge", "ranking", "laughter"],
        behavioral_influence=["avoids public ceremonies"],
    )

    reputation = ReputationProfile(
        reputation_id="rep_kael",
        character_id="char_kael",
        public_reputation="quiet low-rank student",
        private_truth="strategic observer",
        faction_reputations={"academy_elites": "harmless", "lower_ash": "reliable"},
        rumors=["failed rank exam"],
        witness_paths=["ranking ceremony witnesses"],
    )

    goal = GoalRecord(
        goal_id="goal_truth",
        character_id="char_kael",
        goal_type="hidden_goal",
        description="Find proof that the ranking system is edited.",
        priority=0.9,
        urgency=0.7,
        failure_consequence="continues believing the lie about his worth",
    )

    assert trauma.trauma_intensity == 0.8
    assert emotion.shame == 0.7
    assert memory.emotional_weight == 0.9
    assert reputation.faction_reputations["academy_elites"] == "harmless"
    assert goal.priority == 0.9


def test_moral_skill_growth_and_adaptability_schemas():
    morality = MoralProfile(
        moral_profile_id="moral_kael",
        character_id="char_kael",
        compassion=0.75,
        justice=0.8,
        ambition=0.65,
        revenge=0.35,
        forbidden_lines=["will not betray someone powerless for status"],
    )

    skill = SkillProfile(
        skill_id="skill_pattern",
        character_id="char_kael",
        domain="observation",
        name="Pattern Reading",
        rank="S",
        rarity="rare",
        mastery=0.84,
        cost="emotional exhaustion",
        limitation="struggles when personally attached",
        counter="chaotic false signals",
    )

    growth = GrowthTrack(
        growth_id="growth_voice",
        character_id="char_kael",
        domain="public courage",
        current_level=0.2,
        target_level=0.8,
        milestones=["speaks in a small hearing", "accuses an elite publicly"],
        breakthrough_conditions=["someone defends him first"],
    )

    adaptability = AdaptabilityProfile(
        adaptability_id="adapt_kael",
        character_id="char_kael",
        adaptability_score=0.82,
        limit_break_potential=0.76,
        pressure_thresholds={"public_injustice": 0.7},
        breakthrough_conditions=["witnesses an innocent lower-ranked student punished"],
        adaptation_domains=["emotional", "social", "skill"],
        cost_of_adaptation=["burns his safe anonymity"],
        risk_of_instability=0.45,
        post_break_change=["can speak publicly once but suffers emotional crash"],
        limit_break_types=["relationship_triggered_break", "earned_breakthrough"],
    )

    assert morality.justice == 0.8
    assert skill.rank == "S"
    assert growth.current_level == 0.2
    assert adaptability.limit_break_potential == 0.76

    with pytest.raises(ValidationError):
        SkillProfile(
            skill_id="skill_bad",
            character_id="char_bad",
            domain="magic",
            name="Bad Rank",
            rank="Z",
        )

    with pytest.raises(ValidationError):
        AdaptabilityProfile(
            adaptability_id="adapt_bad",
            character_id="char_bad",
            adaptability_score=0.5,
            breakthrough_conditions=[],
        )


def test_destiny_prophecy_dataset_snapshot_and_export_schemas():
    destiny = DestinyProfile(
        destiny_id="dest_kael",
        character_id="char_kael",
        destiny_type="hidden_kingmaker",
        destiny_score=0.94,
        visibility="hidden",
        trigger="witnessing public injustice without anyone intervening",
        burden="must choose who receives power",
        cost="loses safety when he acts openly",
        failure_condition="choosing personal safety over truth three times",
        fulfillment_path="exposes ranking fraud without becoming ruler",
    )

    prophecy = ProphecyLink(
        prophecy_link_id="prop_link_kael",
        character_id="char_kael",
        prophecy_id="prop_oath_bell",
        prophecy_text="The bell will answer the one who refuses the crown.",
        role_in_prophecy="misread kingmaker",
        interpretation_variants=["future king", "crown destroyer", "witness"],
        truth_status="partial",
    )

    metadata = CharacterDatasetMetadata(
        metadata_id="meta_kael",
        character_id="char_kael",
        training_eligible=True,
        human_review_required=True,
        do_not_train=False,
        source_mode="human_approved_synthetic",
        quality_tier="strong",
        duplicate_risk="low_overlap",
        character_type_tags=["hidden_kingmaker"],
        adaptability_tags=["earned_breakthrough"],
    )

    snapshot = CharacterSnapshotMetadata(
        snapshot_id="charsnap_kael_v1",
        character_id="char_kael",
        snapshot_type="character_v1",
        snapshot_label="Initial deep profile",
        change_summary="Generated complete profile.",
    )

    export = CharacterBibleExport(
        export_id="charbible_kael",
        character_id="char_kael",
        export_title="Kael Veyran Character Bible",
        character_bible_markdown="# Kael Veyran",
        character_bible_json={"name": "Kael Veyran"},
        export_readiness_score=0.88,
    )

    assert destiny.destiny_score == 0.94
    assert prophecy.truth_status == "partial"
    assert metadata.training_eligible is True
    assert metadata.do_not_train is False
    assert snapshot.rollback_ready is True
    assert export.export_readiness_score == 0.88


def test_complete_character_profile_completion_ratio():
    identity = CharacterIdentity(
        character_id="char_kael",
        project_id="proj_ashen",
        universe_id="uni_main",
        name="Kael Veyran",
        role="hidden kingmaker",
    )

    psychology = PsychologyProfile(
        psychology_id="psy_kael",
        character_id="char_kael",
        core_wound="performance-based love",
        core_desire="to be chosen freely",
        core_fear="being disposable",
        core_lie="usefulness is love",
        core_truth="worth exists before performance",
        defense_mechanism="cold restraint",
        behavior_rules=["Under shame pressure, he becomes observant and silent."],
    )

    adaptability = AdaptabilityProfile(
        adaptability_id="adapt_kael",
        character_id="char_kael",
        adaptability_score=0.8,
        limit_break_potential=0.7,
        breakthrough_conditions=["protects someone weaker"],
        adaptation_domains=["emotional"],
        cost_of_adaptation=["public exposure"],
    )

    agent_state = CharacterAgentState(
        agent_state_id="agent_kael",
        character_id="char_kael",
        internal_state={"core_wound": "performance-based love"},
        emotional_state={"dominant": "restrained shame"},
        adaptability_state={"limit_break_ready": False},
        simulation_readiness=0.75,
    )

    profile = CompleteCharacterProfile(
        identity=identity,
        psychology=psychology,
        adaptability=adaptability,
        goals=[
            GoalRecord(
                goal_id="goal_truth",
                character_id="char_kael",
                goal_type="hidden_goal",
                description="Find proof of rank fraud.",
            )
        ],
        skills=[
            SkillProfile(
                skill_id="skill_pattern",
                character_id="char_kael",
                domain="observation",
                name="Pattern Reading",
                rank="S",
                limitation="fails under attachment",
            )
        ],
        agent_state=agent_state,
    )

    assert profile.identity.name == "Kael Veyran"
    assert profile.completion_ratio() > 0.2
    assert profile.adaptability.limit_break_potential == 0.7
