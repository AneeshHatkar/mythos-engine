from backend.app.schemas.world import (
    ArtifactProfile,
    ClassTier,
    CausalityLink,
    LocationProfile,
    TrainingReadinessMetadata,
    WorldBible,
    WorldCreate,
    WorldDNAProfile,
    WorldIdentity,
    WorldRule,
    WorldRuleSet,
)


def test_world_create_schema_accepts_deep_world_request():
    world = WorldCreate(
        universe_id="uni_test",
        name="Velmora",
        seed_premise="A late imperial collapse world ruled by noble academies.",
        target_format="seven_novel_series",
        genre_tags=["dark_academy", "political_fantasy"],
        tone_tags=["epic", "tragic", "intelligent"],
        desired_complexity="extreme",
    )

    assert world.universe_id == "uni_test"
    assert world.name == "Velmora"
    assert "dark_academy" in world.genre_tags
    assert world.desired_complexity == "extreme"


def test_world_identity_schema_captures_deep_identity():
    identity = WorldIdentity(
        world_name="Velmora",
        alternate_names=["The Ashen Empire"],
        mythic_names=["The Land Beneath the Oath Bell"],
        forbidden_names=["The Promise-Breaking Realm"],
        public_identity="An empire of noble academies and ancient law.",
        hidden_identity="A civilization cursed by broken divine oaths.",
        emotional_promise="Power, betrayal, longing, and collapse.",
        central_world_question="Can a world built on inherited lies survive the truth?",
        world_wound="The first royal oath was broken and erased from history.",
    )

    assert identity.world_name == "Velmora"
    assert identity.hidden_identity.startswith("A civilization")
    assert "Oath Bell" in identity.mythic_names[0]


def test_world_rule_set_supports_multiple_rule_categories():
    destiny_rule = WorldRule(
        rule_name="Destined Awakening Pressure",
        rule_category="destiny",
        description="Too many destined people awakening at once destabilizes civilization.",
        cost_or_limit="Each awakening increases social and political pressure.",
        story_uses=["collapse clock", "character rivalry", "prophecy panic"],
    )

    rule_set = WorldRuleSet(destiny_rules=[destiny_rule])

    assert len(rule_set.destiny_rules) == 1
    assert rule_set.destiny_rules[0].rule_name == "Destined Awakening Pressure"


def test_world_bible_contains_all_major_world_systems():
    bible = WorldBible(
        world_id="world_test",
        universe_id="uni_test",
        identity=WorldIdentity(world_name="Velmora"),
    )

    bible.geography.locations.append(
        LocationProfile(
            name="The Ashen Crown Academy",
            location_type="academy",
            danger_level=0.7,
            symbolic_meaning="A place where birth decides truth.",
        )
    )

    bible.society.class_tiers.append(
        ClassTier(
            name="S-Class Noble Bloodlines",
            rank=1,
            privileges=["Royal magic access", "Academy inheritance"],
            restrictions=["Bound by oath-law"],
        )
    )

    bible.artifacts.append(
        ArtifactProfile(
            name="The Oath Bell",
            artifact_type="religious_political_artifact",
            symbolism="Every broken promise becomes history's debt.",
            plot_potential=["trial scene", "betrayal reveal", "religious conflict"],
        )
    )

    bible.causality_graph.links.append(
        CausalityLink(
            cause="Relic scarcity",
            effect="Academy tuition rises",
            affected_systems=["economy", "education", "class"],
        )
    )

    assert bible.identity is not None
    assert bible.identity.world_name == "Velmora"
    assert len(bible.geography.locations) == 1
    assert len(bible.society.class_tiers) == 1
    assert len(bible.artifacts) == 1
    assert len(bible.causality_graph.links) == 1


def test_world_dna_and_training_metadata_prepare_future_learning():
    dna = WorldDNAProfile(
        dominant_conflict_type="class_vs_destiny",
        dominant_social_structure="noble_academy_empire",
        dominant_power_source="oath_magic_and_relic_mines",
        dominant_emotional_atmosphere="beautiful_collapse",
        uniqueness_axes={
            "academy_politics": 0.9,
            "oath_religion": 0.85,
            "destiny_pressure": 0.95,
        },
    )

    metadata = TrainingReadinessMetadata(
        generation_method="rule_based_v0",
        dataset_tags=["dark_academy", "political_fantasy", "world_bible"],
        consistency_score=0.88,
        originality_score=0.91,
        story_potential_score=0.94,
        training_eligible=False,
        do_not_train=True,
    )

    assert dna.uniqueness_axes["destiny_pressure"] == 0.95
    assert metadata.do_not_train is True
    assert metadata.training_eligible is False
