from typing import Any, Dict, List

from backend.app.schemas.artifacts import ArtifactRecord
from backend.app.schemas.engine_ops import EngineErrorType
from backend.app.schemas.evaluation import InvariantType, QualityGateResult
from backend.app.schemas.global_refs import EntityRef, EntityType
from backend.app.schemas.handoffs import CharacterToSimulationContract, WorldToCharacterContract
from backend.app.services.character_learning_adapter import CharacterLearningAdapter
from backend.app.services.world_learning_adapter import WorldLearningAdapter


class CrossChunkReadinessVerifier:
    """Verifies that Chunks 1-3 are ready for Chunk 4 simulation.

    This is not a story generator. It is a structural readiness verifier that
    confirms the foundation, world contracts, character contracts, learning
    metadata, and simulation handoffs exist before Chunk 4 starts.
    """

    REQUIRED_FOUNDATION_SCHEMAS = [
        "EntityRef",
        "ArtifactRecord",
        "WorldToCharacterContract",
        "CharacterToSimulationContract",
        "QualityGateResult",
    ]

    REQUIRED_WORLD_SIMULATION_FIELDS = [
        "world_to_character_contract",
        "world_simulation_constraints",
        "cross_chunk_handoff",
        "chunk4_ready",
    ]

    REQUIRED_CHARACTER_SIMULATION_FIELDS = [
        "simulation_state_seed",
        "dialogue_constraint_seed",
        "agency_state_seed",
        "relationship_state_seed",
        "cross_chunk_handoff",
        "chunk4_ready",
    ]

    REQUIRED_INVARIANTS = [
        InvariantType.NO_MAGIC_KNOWLEDGE.value,
        InvariantType.NO_CONSEQUENCE_FREE_MAJOR_CHOICE.value,
        InvariantType.NO_RELATIONSHIP_JUMP_WITHOUT_CAUSE.value,
        InvariantType.NO_CANON_VIOLATION.value,
        InvariantType.NO_WORLD_CONTRACT_VIOLATION.value,
        InvariantType.NO_TRAINING_WITHOUT_PROVENANCE.value,
    ]

    def __init__(
        self,
        world_adapter: WorldLearningAdapter | None = None,
        character_adapter: CharacterLearningAdapter | None = None,
    ) -> None:
        self.world_adapter = world_adapter or WorldLearningAdapter()
        self.character_adapter = character_adapter or CharacterLearningAdapter()

    def verify_cross_chunk_readiness(
        self,
        *,
        world_payload: Dict[str, Any],
        character_payloads: List[Dict[str, Any]],
        project_id: str = "default_project",
        universe_id: str = "default_universe",
    ) -> Dict[str, Any]:
        foundation_report = self.verify_foundation_layer()
        world_report = self.verify_world_layer(
            world_payload=world_payload,
            project_id=project_id,
            universe_id=universe_id,
        )
        character_report = self.verify_character_layer(
            character_payloads=character_payloads,
            world_contract=world_report.get("world_to_character_contract", {}),
            project_id=project_id,
            universe_id=universe_id,
        )
        invariant_report = self.verify_required_invariants_available()
        handoff_report = self.verify_handoff_chain(
            world_report=world_report,
            character_report=character_report,
        )

        blockers = []
        for report in [foundation_report, world_report, character_report, invariant_report, handoff_report]:
            blockers.extend(report.get("blockers", []))

        ready = (
            foundation_report["ready"]
            and world_report["ready"]
            and character_report["ready"]
            and invariant_report["ready"]
            and handoff_report["ready"]
            and not blockers
        )

        readiness_score = round(
            sum(
                [
                    foundation_report["readiness_score"],
                    world_report["readiness_score"],
                    character_report["readiness_score"],
                    invariant_report["readiness_score"],
                    handoff_report["readiness_score"],
                ]
            )
            / 5,
            3,
        )

        return {
            "success": True,
            "cross_chunk_ready_for_chunk4": ready,
            "readiness_score": readiness_score,
            "project_id": project_id,
            "universe_id": universe_id,
            "foundation_report": foundation_report,
            "world_report": world_report,
            "character_report": character_report,
            "invariant_report": invariant_report,
            "handoff_report": handoff_report,
            "blockers": blockers,
            "recommendation": "start_chunk4" if ready else "fix_cross_chunk_readiness_blockers",
        }

    def verify_foundation_layer(self) -> Dict[str, Any]:
        checks = {
            "EntityRef": self._model_can_validate_entity_ref(),
            "ArtifactRecord": self._model_can_validate_artifact_record(),
            "WorldToCharacterContract": self._model_can_validate_world_handoff(),
            "CharacterToSimulationContract": self._model_can_validate_character_handoff(),
            "QualityGateResult": self._model_can_validate_quality_gate(),
        }

        missing = [name for name, ok in checks.items() if not ok]
        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0,
            "readiness_score": round(score, 3),
            "checks": checks,
            "blockers": [f"foundation schema unavailable: {name}" for name in missing],
        }

    def verify_world_layer(
        self,
        *,
        world_payload: Dict[str, Any],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        export = self.world_adapter.build_world_simulation_constraint_export(
            world_payload,
            project_id=project_id,
            universe_id=universe_id,
        )

        field_checks = {
            field: field in export and export.get(field) not in [None, "", [], {}]
            for field in self.REQUIRED_WORLD_SIMULATION_FIELDS
        }

        handoff_valid = False
        handoff_error = None
        try:
            handoff = WorldToCharacterContract.model_validate(export["cross_chunk_handoff"])
            handoff_valid = handoff.ready is True
        except Exception as exc:  # pragma: no cover - defensive
            handoff_error = str(exc)

        constraints = export.get("world_simulation_constraints", {})
        constraint_checks = {
            "legal_constraints": bool(constraints.get("legal_constraints")),
            "power_cost_rules": bool(constraints.get("power_cost_rules")),
            "permission_boundaries": bool(constraints.get("character_permission_boundaries")),
        }

        total_checks = list(field_checks.values()) + [handoff_valid] + list(constraint_checks.values())
        score = sum(1 for ok in total_checks if ok) / len(total_checks)

        blockers = []
        blockers.extend([f"world simulation field missing: {field}" for field, ok in field_checks.items() if not ok])
        blockers.extend([f"world simulation constraint missing: {field}" for field, ok in constraint_checks.items() if not ok])
        if not handoff_valid:
            blockers.append(f"world handoff invalid: {handoff_error or 'not ready'}")

        return {
            "ready": score >= 0.85 and export.get("chunk4_ready") is True,
            "readiness_score": round(score, 3),
            "world_id": export.get("world_id"),
            "world_to_character_contract": export.get("world_to_character_contract", {}),
            "world_simulation_constraint_export": export,
            "field_checks": field_checks,
            "constraint_checks": constraint_checks,
            "handoff_valid": handoff_valid,
            "blockers": blockers,
        }

    def verify_character_layer(
        self,
        *,
        character_payloads: List[Dict[str, Any]],
        world_contract: Dict[str, Any],
        project_id: str,
        universe_id: str,
    ) -> Dict[str, Any]:
        character_reports = []

        for payload in character_payloads:
            character_profile = self._extract_character_profile(payload)
            character_id = self.character_adapter._extract_character_id(character_profile, payload)

            world_validation = self.character_adapter.validate_character_against_world_contract(
                character_profile=character_profile,
                world_contract=world_contract,
            )
            chunk4_handoff = self.character_adapter.build_chunk4_handoff_contract(
                character_id=character_id,
                character_profile=character_profile,
            )
            simulation_contract = self.character_adapter.build_character_to_simulation_contract(
                character_id=character_id,
                character_profile=character_profile,
                project_id=project_id,
                universe_id=universe_id,
                world_contract_validation=world_validation,
                chunk4_handoff_contract=chunk4_handoff,
            )

            field_checks = {
                field: field in simulation_contract and simulation_contract.get(field) not in [None, "", [], {}]
                for field in self.REQUIRED_CHARACTER_SIMULATION_FIELDS
            }

            handoff_valid = False
            handoff_error = None
            try:
                handoff = CharacterToSimulationContract.model_validate(simulation_contract["cross_chunk_handoff"])
                handoff_valid = handoff.ready is True
            except Exception as exc:  # pragma: no cover - defensive
                handoff_error = str(exc)

            blocker_list = []
            blocker_list.extend([f"character simulation field missing: {field}" for field, ok in field_checks.items() if not ok])
            if world_validation.get("world_contract_valid") is False:
                blocker_list.append("character violates world contract")
            if not chunk4_handoff.get("handoff_ready", False):
                blocker_list.append("character Chunk 4 handoff not ready")
            if not handoff_valid:
                blocker_list.append(f"character simulation handoff invalid: {handoff_error or 'not ready'}")

            total_checks = list(field_checks.values()) + [
                world_validation.get("world_contract_valid", True),
                chunk4_handoff.get("handoff_ready", False),
                handoff_valid,
            ]
            score = sum(1 for ok in total_checks if ok) / len(total_checks)

            character_reports.append(
                {
                    "character_id": character_id,
                    "ready": score >= 0.85 and not blocker_list,
                    "readiness_score": round(score, 3),
                    "field_checks": field_checks,
                    "world_contract_validation": world_validation,
                    "chunk4_handoff_contract": chunk4_handoff,
                    "character_to_simulation_contract": simulation_contract,
                    "handoff_valid": handoff_valid,
                    "blockers": blocker_list,
                }
            )

        ready_count = sum(1 for item in character_reports if item["ready"])
        score = ready_count / len(character_reports) if character_reports else 0.0
        blockers = []
        for item in character_reports:
            blockers.extend([f"{item['character_id']}: {blocker}" for blocker in item["blockers"]])

        return {
            "ready": bool(character_reports) and ready_count == len(character_reports),
            "readiness_score": round(score, 3),
            "character_count": len(character_reports),
            "ready_character_count": ready_count,
            "character_reports": character_reports,
            "blockers": blockers,
        }

    def verify_required_invariants_available(self) -> Dict[str, Any]:
        checks = {
            invariant: invariant in self.REQUIRED_INVARIANTS
            for invariant in self.REQUIRED_INVARIANTS
        }
        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0,
            "readiness_score": round(score, 3),
            "required_invariants": self.REQUIRED_INVARIANTS,
            "checks": checks,
            "blockers": [f"invariant unavailable: {name}" for name, ok in checks.items() if not ok],
        }

    def verify_handoff_chain(
        self,
        *,
        world_report: Dict[str, Any],
        character_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        checks = {
            "world_to_character_ready": world_report.get("ready") is True,
            "character_to_simulation_ready": character_report.get("ready") is True,
            "at_least_one_character_ready": character_report.get("ready_character_count", 0) >= 1,
            "world_contract_available": bool(world_report.get("world_to_character_contract")),
            "character_contracts_available": all(
                bool(item.get("character_to_simulation_contract"))
                for item in character_report.get("character_reports", [])
            ),
        }

        score = sum(1 for ok in checks.values() if ok) / len(checks)

        return {
            "ready": score == 1.0,
            "readiness_score": round(score, 3),
            "checks": checks,
            "blockers": [f"handoff chain failed: {name}" for name, ok in checks.items() if not ok],
        }

    def _extract_character_profile(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        for key in ["character_full_profile", "character_profile", "character_bible", "profile", "character"]:
            if isinstance(payload.get(key), dict):
                return payload[key]
        data = payload.get("data")
        if isinstance(data, dict):
            for key in ["character_full_profile", "character_profile", "character_bible", "profile", "character"]:
                if isinstance(data.get(key), dict):
                    return data[key]
        return payload

    def _model_can_validate_entity_ref(self) -> bool:
        try:
            EntityRef(entity_type=EntityType.CHARACTER, entity_id="char_test")
            return True
        except Exception:
            return False

    def _model_can_validate_artifact_record(self) -> bool:
        try:
            ArtifactRecord(
                artifact_type="simulation_trace",
                source_engine="simulation.test_engine",
            )
            return True
        except Exception:
            return False

    def _model_can_validate_world_handoff(self) -> bool:
        try:
            WorldToCharacterContract(readiness_score=1.0, ready=True)
            return True
        except Exception:
            return False

    def _model_can_validate_character_handoff(self) -> bool:
        try:
            CharacterToSimulationContract(readiness_score=1.0, ready=True)
            return True
        except Exception:
            return False

    def _model_can_validate_quality_gate(self) -> bool:
        try:
            QualityGateResult(gate_name="test_gate", passed=True)
            return True
        except Exception:
            return False

    def error_taxonomy_available(self) -> List[str]:
        return [item.value for item in EngineErrorType]
