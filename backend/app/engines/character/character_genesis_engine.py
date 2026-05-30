from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.character import CharacterIdentity
from backend.app.schemas.foundation import EngineRunResult


class CharacterGenesisEngine(BaseEngine):
    """Generates early complete character seeds from world and role context.

    This engine does not yet build the final full character bible. Instead, it
    creates a coherent genesis seed that later engines expand into origin,
    family, psychology, trauma, emotion, memory, reputation, goals, morality,
    skills, growth, adaptability, destiny, and exportable character profiles.

    The goal is to generate characters as future interacting agents, not flat
    character cards.
    """

    engine_name = "character.genesis_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        population_context = payload.get("population_context", {})
        people_type = payload.get("people_type", {})
        world_grounding = payload.get("world_grounding", {})
        agent_state = payload.get("agent_state", {})
        character_mode = payload.get("character_mode", "major_character")
        requested_role = payload.get("role")
        seed_hint = payload.get("seed_hint", "")
        project_id = payload.get("project_id", "default_project")
        universe_id = payload.get("universe_id", "default_universe")
        world_id = payload.get("world_id") or self._infer_world_id(world_state)

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; genesis engine used general dark-fantasy defaults.")

        if not people_type:
            warnings.append("No people_type provided; genesis engine used adaptive survivor defaults.")

        if not population_context:
            warnings.append("No population_context provided; class/origin sampling used fallback defaults.")

        character_id = f"char_{uuid4().hex[:12]}"

        role = self._choose_role(
            requested_role=requested_role,
            character_mode=character_mode,
            people_type=people_type,
        )

        name = self._generate_name(
            world_state=world_state,
            people_type=people_type,
            role=role,
            seed_hint=seed_hint,
        )

        identity = CharacterIdentity(
            character_id=character_id,
            project_id=project_id,
            universe_id=universe_id,
            world_id=world_id,
            name=name,
            aliases=self._generate_aliases(people_type, role),
            role=role,
            importance_level=self._importance_for_mode(character_mode),
            character_depth_level=self._depth_for_mode(character_mode),
            culture=self._infer_culture(world_state),
            language=self._infer_language(world_state),
            faction=self._suggest_faction(world_state, people_type, role),
            occupation=self._suggest_occupation(people_type, role),
            public_status=self._suggest_public_status(people_type, role),
            private_truth=self._suggest_private_truth(people_type, role, seed_hint),
            legal_status=self._suggest_legal_status(world_grounding, people_type),
            canon_status="draft",
            tags=self._build_identity_tags(character_mode, people_type, role),
        )

        genesis_seed = self._build_genesis_seed(
            identity=identity,
            world_state=world_state,
            population_context=population_context,
            people_type=people_type,
            world_grounding=world_grounding,
            agent_state=agent_state,
            character_mode=character_mode,
            seed_hint=seed_hint,
        )

        relationship_hooks = self._build_relationship_hooks(genesis_seed, people_type, role)
        interaction_potential = self._build_interaction_potential(genesis_seed, people_type, role)
        next_engine_payload = self._build_next_engine_payload(genesis_seed, relationship_hooks)

        return self.build_result(
            success=True,
            data={
                "character_identity": identity.model_dump(),
                "genesis_seed": genesis_seed,
                "relationship_hooks": relationship_hooks,
                "interaction_potential": interaction_potential,
                "next_engine_payload": next_engine_payload,
                "genesis_summary": {
                    "character_id": character_id,
                    "name": name,
                    "role": role,
                    "character_mode": character_mode,
                    "people_type_id": people_type.get("people_type_id") or people_type.get("id"),
                    "world_grounded": bool(world_grounding),
                    "ready_for_origin_engine": True,
                    "ready_for_family_engine": True,
                    "ready_for_psychology_engine": True,
                    "ready_for_agent_simulation_later": bool(agent_state),
                },
                "training_notes": [
                    "Genesis seeds are not final character profiles; they are structured starting points.",
                    "Every generated character includes relationship hooks for future Chunk 4 interaction simulation.",
                    "The engine uses world grounding so characters stay tied to Chunk 2 systems.",
                    "Later Chunk 8 can train generation/ranking models using reviewed genesis-to-final-character pairs.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[character_id],
        )

    def _infer_world_id(self, world_state: Dict[str, Any]) -> str:
        identity = world_state.get("identity", {}) if isinstance(world_state, dict) else {}
        return identity.get("world_id") or identity.get("id") or "world_default"

    def _choose_role(self, *, requested_role: Any, character_mode: str, people_type: Dict[str, Any]) -> str:
        if requested_role:
            return str(requested_role)

        mode_map = {
            "protagonist": "protagonist",
            "villain": "villain",
            "antagonist": "antagonist",
            "love_interest": "love_interest",
            "rival": "rival",
            "mentor": "mentor",
            "side_character": "side_character",
            "ordinary_citizen": "ordinary_citizen",
            "civilization_simulation_agent": "civilization_agent",
            "game_companion": "game_companion",
            "adaptation_ready_character": "deuteragonist",
            "large_cast_generation": "side_character",
        }

        if character_mode in mode_map:
            return mode_map[character_mode]

        compatible_roles = people_type.get("compatible_roles", [])

        if compatible_roles:
            return compatible_roles[0]

        return "major_character"

    def _generate_name(
        self,
        *,
        world_state: Dict[str, Any],
        people_type: Dict[str, Any],
        role: str,
        seed_hint: str,
    ) -> str:
        hint = seed_hint.lower()
        type_id = people_type.get("people_type_id", "") or people_type.get("id", "")

        if "kael" in hint or "kingmaker" in type_id:
            return "Kael Veyran"

        if "mira" in hint or role == "love_interest":
            return "Mira Solen"

        if "villain" in role or "institutional" in type_id:
            return "Magister Oren Vaul"

        if "rival" in role or "failed_prodigy" in type_id:
            return "Sera Ash"

        if "ordinary" in role:
            return "Tovin Reed"

        if "limit_break" in type_id or "anomaly" in type_id:
            return "Ilyen Var"

        if "oath" in type_id:
            return "Liora Venn"

        return "Aren Vale"

    def _generate_aliases(self, people_type: Dict[str, Any], role: str) -> List[str]:
        type_name = people_type.get("name", "")

        aliases = []

        if type_name:
            aliases.append(type_name)

        if role == "villain":
            aliases.append("the lawful hand")

        if "limit" in str(people_type).lower():
            aliases.append("the exception")

        return aliases

    def _importance_for_mode(self, mode: str) -> int:
        if mode in {"protagonist", "villain", "love_interest", "rival", "adaptation_ready_character"}:
            return 5
        if mode in {"mentor", "major_character", "game_companion"}:
            return 4
        if mode in {"side_character", "civilization_simulation_agent"}:
            return 3
        return 2

    def _depth_for_mode(self, mode: str) -> int:
        if mode in {"ordinary_citizen"}:
            return 3
        return self._importance_for_mode(mode)

    def _infer_culture(self, world_state: Dict[str, Any]) -> str:
        text = str(world_state).lower()

        if "oath" in text:
            return "Oath-bound academy empire"

        if "border" in text:
            return "Border-fractured imperial culture"

        return "Velmoran imperial culture"

    def _infer_language(self, world_state: Dict[str, Any]) -> str:
        text = str(world_state).lower()

        if "academy" in text:
            return "formal academy register and local district speech"

        return "regional common speech"

    def _suggest_faction(self, world_state: Dict[str, Any], people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower() + " " + role.lower()

        if "institutional" in text or "villain" in text:
            return "Oath Court Administration"

        if "hidden_kingmaker" in text or "academy" in str(world_state).lower():
            return "Academy lower-rank network"

        if "ordinary" in text:
            return "local witness network"

        if "limit" in text or "anomaly" in text:
            return "unclassified anomaly registry"

        return "unaffiliated pressure group"

    def _suggest_occupation(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower() + " " + role.lower()

        if "academy" in text or role in {"protagonist", "rival", "love_interest"}:
            return "academy student"

        if "villain" in text or "institutional" in text:
            return "oath court official"

        if "ordinary" in text:
            return "market courier and witness"

        if "mentor" in role:
            return "disgraced instructor"

        return "world-system participant"

    def _suggest_public_status(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "hidden kingmaker" in text:
            return "quiet low-rank student"

        if "elite" in text:
            return "high-trust academy figure"

        if "failed prodigy" in text:
            return "publicly diminished former prodigy"

        if "institutional" in text:
            return "respected legal authority"

        if "ordinary" in text:
            return "unremarkable citizen"

        if "limit-break" in text or "anomaly" in text:
            return "misclassified student"

        return "draft public identity"

    def _suggest_private_truth(self, people_type: Dict[str, Any], role: str, seed_hint: str) -> str:
        text = str(people_type).lower() + " " + seed_hint.lower()

        if "hidden kingmaker" in text:
            return "sees how power moves before the powerful notice him"

        if "elite truth" in text:
            return "knows their privilege is built on edited records"

        if "failed prodigy" in text:
            return "is more afraid of pity than defeat"

        if "institutional" in text:
            return "believes order matters more than innocent exceptions"

        if "ordinary" in text:
            return "remembers a detail that powerful people erased"

        if "limit-break" in text or "anomaly" in text:
            return "can exceed a limit only by paying a destabilizing cost"

        return "contains a contradiction that later engines must deepen"

    def _suggest_legal_status(self, world_grounding: Dict[str, Any], people_type: Dict[str, Any]) -> str:
        tags = world_grounding.get("world_dependency_tags", [])
        text = str(people_type).lower()

        if "family_name_legal_trust" in tags and ("hidden" in text or "ordinary" in text):
            return "low-trust legal identity"

        if "institutional" in text:
            return "high-trust legal authority"

        if "limit" in text or "anomaly" in text:
            return "unclassified by current law"

        return "legally recognized"

    def _build_identity_tags(self, character_mode: str, people_type: Dict[str, Any], role: str) -> List[str]:
        tags = [character_mode, role]

        type_id = people_type.get("people_type_id") or people_type.get("id")

        if type_id:
            tags.append(type_id)

        if "limit" in str(people_type).lower():
            tags.append("adaptability_candidate")

        return sorted(set(tags))

    def _build_genesis_seed(
        self,
        *,
        identity: CharacterIdentity,
        world_state: Dict[str, Any],
        population_context: Dict[str, Any],
        people_type: Dict[str, Any],
        world_grounding: Dict[str, Any],
        agent_state: Dict[str, Any],
        character_mode: str,
        seed_hint: str,
    ) -> Dict[str, Any]:
        social_class = self._choose_social_class(population_context, people_type, identity.role)
        people_text = str(people_type).lower()

        skill_rarity = "rare" if identity.importance_level >= 4 else "common"

        if "limit" in people_text or "anomaly" in people_text:
            skill_rarity = "anomaly"

        return {
            "character_id": identity.character_id,
            "name": identity.name,
            "role": identity.role,
            "character_mode": character_mode,
            "people_type_id": people_type.get("people_type_id") or people_type.get("id"),
            "seed_hint": seed_hint,
            "social_class": social_class,
            "family_name_status": self._choose_family_name_status(social_class, people_type),
            "origin_direction": self._choose_origin_direction(social_class, people_type, world_grounding),
            "family_direction": self._choose_family_direction(social_class, people_type),
            "core_wound": self._choose_core_wound(people_type, agent_state),
            "core_desire": self._choose_core_desire(people_type, agent_state),
            "core_fear": self._choose_core_fear(people_type, agent_state),
            "defense_mechanism": self._choose_defense_mechanism(people_type),
            "surface_goal": self._choose_surface_goal(people_type, identity.role),
            "hidden_goal": self._choose_hidden_goal(people_type, identity.role),
            "true_need": self._choose_true_need(people_type),
            "primary_skill": self._choose_primary_skill(people_type, identity.role),
            "skill_domain": self._choose_skill_domain(people_type, identity.role),
            "skill_rank": "S" if skill_rarity in {"rare", "anomaly"} else "C",
            "skill_rarity": skill_rarity,
            "skill_cost": self._choose_skill_cost(skill_rarity, people_type),
            "limitation": self._choose_skill_limitation(people_type),
            "destiny_type": self._choose_destiny_type(people_type, identity.role),
            "adaptability_type": self._choose_adaptability_type(people_type, identity.role),
            "breakthrough_condition": self._choose_breakthrough_condition(people_type, identity.role),
            "adaptation_cost": self._choose_adaptation_cost(people_type),
            "adaptation_risk": self._choose_adaptation_risk(people_type),
            "post_break_consequence": self._choose_post_break_consequence(world_grounding, people_type),
            "world_dependency_tags": world_grounding.get("world_dependency_tags", []),
            "active_story_hooks": world_grounding.get("active_story_hooks", []),
        }

    def _choose_social_class(self, population_context: Dict[str, Any], people_type: Dict[str, Any], role: str) -> str:
        compatible = people_type.get("compatible_classes", [])

        if compatible:
            return compatible[0]

        groups = population_context.get("population_groups", [])

        if groups:
            return groups[0].get("social_class", "commoner")

        if role == "villain":
            return "imperial_elite"

        return "academy_sponsored"

    def _choose_family_name_status(self, social_class: str, people_type: Dict[str, Any]) -> str:
        if social_class in {"imperial_elite", "old_nobility"}:
            return "trusted"

        if social_class in {"erased", "underclass", "relic_miner"}:
            return "distrusted"

        if "hidden" in str(people_type).lower():
            return "distrusted"

        return "recognized"

    def _choose_origin_direction(self, social_class: str, people_type: Dict[str, Any], world_grounding: Dict[str, Any]) -> str:
        if social_class in {"erased", "relic_miner", "commoner"}:
            return "low-trust origin shaped by class barriers and institutional suspicion"

        if social_class in {"imperial_elite", "old_nobility"}:
            return "high-trust origin shaped by inherited privilege and public obligation"

        if world_grounding.get("world_dependency_tags"):
            return "origin must explain access to world systems: " + ", ".join(world_grounding["world_dependency_tags"][:3])

        return "origin should reveal why the character is near the main conflict"

    def _choose_family_direction(self, social_class: str, people_type: Dict[str, Any]) -> str:
        if social_class in {"imperial_elite", "old_nobility"}:
            return "family pressure should involve inheritance, reputation, and public duty"

        if social_class in {"erased", "relic_miner", "commoner"}:
            return "family pressure should involve debt, legal trust, survival, or erased records"

        return "family pressure should explain the character's emotional pattern"

    def _choose_core_wound(self, people_type: Dict[str, Any], agent_state: Dict[str, Any]) -> str:
        state_wound = agent_state.get("internal_state", {}).get("core_wound") if isinstance(agent_state, dict) else None

        if state_wound:
            return state_wound

        wounds = people_type.get("likely_wounds", [])

        if wounds:
            return wounds[0]

        return "being assigned a role before being known"

    def _choose_core_desire(self, people_type: Dict[str, Any], agent_state: Dict[str, Any]) -> str:
        state_desire = agent_state.get("internal_state", {}).get("core_desire") if isinstance(agent_state, dict) else None

        if state_desire:
            return state_desire

        goals = people_type.get("likely_goals", [])

        if goals:
            return goals[0]

        return "to be seen accurately"

    def _choose_core_fear(self, people_type: Dict[str, Any], agent_state: Dict[str, Any]) -> str:
        state_fear = agent_state.get("internal_state", {}).get("core_fear") if isinstance(agent_state, dict) else None

        if state_fear:
            return state_fear

        text = str(people_type).lower()

        if "villain" in text or "institutional" in text:
            return "the world becoming uncontrollable"

        if "love" in text:
            return "being chosen only as an emotional reward"

        if "ordinary" in text:
            return "telling the truth and still being ignored"

        return "being disposable"

    def _choose_defense_mechanism(self, people_type: Dict[str, Any]) -> str:
        text = str(people_type).lower()

        if "hidden" in text:
            return "cold restraint"

        if "elite" in text:
            return "controlled politeness"

        if "failed" in text:
            return "false arrogance"

        if "villain" in text or "institutional" in text:
            return "procedural certainty"

        if "ordinary" in text:
            return "practical avoidance"

        return "controlled distance"

    def _choose_surface_goal(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "villain" in text or role == "villain":
            return "preserve institutional order"

        if "love" in text:
            return "complete their own mission without becoming someone else's reward"

        if "ordinary" in text:
            return "survive without being noticed by power"

        goals = people_type.get("likely_goals", [])

        return goals[0] if goals else "survive the current conflict"

    def _choose_hidden_goal(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "hidden" in text:
            return "prove that invisible people can decide visible power"

        if "failed" in text:
            return "be respected without needing to be perfect again"

        if "institutional" in text:
            return "prove that order was worth the people it harmed"

        if "ordinary" in text:
            return "tell one truth that cannot be erased"

        return "be chosen without being used"

    def _choose_true_need(self, people_type: Dict[str, Any]) -> str:
        text = str(people_type).lower()

        if "institutional" in text:
            return "accept that order without mercy is cowardice"

        if "love" in text:
            return "be loved without losing selfhood"

        if "failed" in text:
            return "find worth outside achievement"

        return "be seen without performance"

    def _choose_primary_skill(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "hidden" in text:
            return "Pattern Reading"

        if "institutional" in text:
            return "Legal Weaponization"

        if "elite" in text:
            return "Institutional Navigation"

        if "failed" in text:
            return "Disciplined Technique"

        if "ordinary" in text:
            return "Witness Memory"

        if "limit" in text or "anomaly" in text:
            return "Pressure Adaptation"

        return "Social Survival"

    def _choose_skill_domain(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "hidden" in text or "ordinary" in text:
            return "observation"

        if "elite" in text or "institutional" in text:
            return "law"

        if "failed" in text:
            return "combat"

        if "limit" in text or "anomaly" in text:
            return "adaptability"

        return "social_manipulation"

    def _choose_skill_cost(self, skill_rarity: str, people_type: Dict[str, Any]) -> str | None:
        if skill_rarity not in {"rare", "anomaly"}:
            return None

        if "limit" in str(people_type).lower() or "anomaly" in str(people_type).lower():
            return "emotional and physical instability after exceeding limits"

        return "emotional exhaustion and social exposure"

    def _choose_skill_limitation(self, people_type: Dict[str, Any]) -> str | None:
        text = str(people_type).lower()

        if "hidden" in text:
            return "fails when personally attached"

        if "institutional" in text:
            return "cannot understand mercy outside procedure"

        if "limit" in text or "anomaly" in text:
            return "cannot repeat breakthroughs without worsening instability"

        return "weak when forced into public vulnerability"

    def _choose_destiny_type(self, people_type: Dict[str, Any], role: str) -> str | None:
        compatible = people_type.get("compatible_destinies", [])

        if compatible:
            return compatible[0]

        if role == "protagonist":
            return "world_catalyst"

        if role == "villain":
            return "false_savior"

        return None

    def _choose_adaptability_type(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "limit" in text or "anomaly" in text:
            return "limit_break_anomaly"

        if "survivor" in text or role in {"protagonist", "rival"}:
            return "earned_breakthrough"

        if role == "villain":
            return "corruption_boost"

        return "emotional_adaptability"

    def _choose_breakthrough_condition(self, people_type: Dict[str, Any], role: str) -> str:
        text = str(people_type).lower()

        if "ordinary" in text:
            return "someone powerful denies an obvious truth"

        if "institutional" in text:
            return "order fails publicly and cannot be defended by procedure"

        if "limit" in text or "anomaly" in text:
            return "someone weaker will die or be erased unless the character exceeds a limit"

        return "protects someone weaker at personal cost"

    def _choose_adaptation_cost(self, people_type: Dict[str, Any]) -> str:
        text = str(people_type).lower()

        if "hidden" in text:
            return "burns safe anonymity"

        if "elite" in text:
            return "risks inherited protection"

        if "institutional" in text:
            return "breaks public legitimacy"

        if "limit" in text or "anomaly" in text:
            return "destabilizes body, identity, or public classification"

        return "loses emotional safety"

    def _choose_adaptation_risk(self, people_type: Dict[str, Any]) -> str:
        text = str(people_type).lower()

        if "institutional" in text:
            return "becomes more authoritarian after failure"

        if "limit" in text or "anomaly" in text:
            return "repeated breakthroughs cause instability and exploitation"

        return "emotional crash after action"

    def _choose_post_break_consequence(self, world_grounding: Dict[str, Any], people_type: Dict[str, Any]) -> str:
        tags = world_grounding.get("world_dependency_tags", [])

        if "family_name_legal_trust" in tags:
            return "legal trust status changes or comes under investigation"

        if "academy_gatekeeping" in tags:
            return "academy authorities notice and classify the character"

        if "oath_religion" in tags:
            return "oath institutions interpret the breakthrough as religious evidence"

        if "limit" in str(people_type).lower():
            return "the world updates its rules around this character"

        return "social position changes after the breakthrough"

    def _build_relationship_hooks(
        self,
        genesis_seed: Dict[str, Any],
        people_type: Dict[str, Any],
        role: str,
    ) -> Dict[str, Any]:
        tendencies = people_type.get("relationship_tendencies", [])

        return {
            "trust_triggers": [
                "someone protects their private truth without using it",
                "someone accepts cost rather than demanding performance",
            ],
            "betrayal_triggers": [
                "being publicly abandoned",
                "being treated as a tool, symbol, or exception instead of a person",
            ],
            "romantic_response": (
                "slow trust and guarded tenderness"
                if role in {"love_interest", "protagonist", "rival"}
                else "relationship response depends on respect and consistency"
            ),
            "rivalry_response": "respects competence but resents effortless privilege",
            "loyalty_threshold": "loyal after repeated proof under social risk",
            "secret_pressure": "hides the part of themselves that would change public classification",
            "conflict_style": "quiet escalation until a moral threshold is crossed",
            "relationship_tendencies": tendencies,
            "limit_break_relationship_trigger": genesis_seed.get("breakthrough_condition"),
        }

    def _build_interaction_potential(
        self,
        genesis_seed: Dict[str, Any],
        people_type: Dict[str, Any],
        role: str,
    ) -> Dict[str, Any]:
        return {
            "best_pairings": [
                "elite truth-seeker",
                "failed prodigy rival",
                "ordinary witness",
                "institutional antagonist",
            ],
            "conflict_sources": [
                genesis_seed.get("family_name_status"),
                genesis_seed.get("social_class"),
                genesis_seed.get("core_wound"),
                genesis_seed.get("hidden_goal"),
            ],
            "scene_functions": [
                "reveal class pressure",
                "force hidden goal into public action",
                "trigger memory or shame response",
                "create choice between safety and truth",
            ],
            "franchise_potential_hooks": [
                "fan debate over moral choice",
                "ship tension through guarded trust",
                "symbolic breakthrough moment",
                "institutional enemy recognition",
            ],
            "chunk4_ready": True,
        }

    def _build_next_engine_payload(
        self,
        genesis_seed: Dict[str, Any],
        relationship_hooks: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "origin_engine_payload": {
                "character_seed": genesis_seed,
                "relationship_hooks": relationship_hooks,
            },
            "family_engine_payload": {
                "character_seed": genesis_seed,
                "family_direction": genesis_seed.get("family_direction"),
            },
            "psychology_engine_payload": {
                "character_seed": genesis_seed,
                "core_wound": genesis_seed.get("core_wound"),
                "core_desire": genesis_seed.get("core_desire"),
                "core_fear": genesis_seed.get("core_fear"),
            },
            "adaptability_engine_payload": {
                "character_seed": genesis_seed,
                "adaptability_type": genesis_seed.get("adaptability_type"),
                "breakthrough_condition": genesis_seed.get("breakthrough_condition"),
                "adaptation_cost": genesis_seed.get("adaptation_cost"),
                "adaptation_risk": genesis_seed.get("adaptation_risk"),
                "post_break_consequence": genesis_seed.get("post_break_consequence"),
            },
        }
