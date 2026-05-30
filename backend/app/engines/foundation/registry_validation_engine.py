from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class RegistryValidationEngine(BaseEngine):
    """Validates registry type payloads before or after insertion.

    This is a small foundation engine used to prove the engine contract.
    Later, bigger engines will follow the same structure:
    WorldBuilderEngine, CharacterGenesisEngine, PlotPlannerEngine, etc.
    """

    engine_name = "foundation.registry_validation"

    REQUIRED_FIELDS = ["type_id", "category", "name", "description"]

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        warnings: List[str] = []
        errors: List[str] = []

        for field in self.REQUIRED_FIELDS:
            if not payload.get(field):
                errors.append(f"Missing required registry field: {field}")

        type_id = payload.get("type_id", "")
        if type_id and "." not in type_id:
            warnings.append(
                "Registry type_id should usually use dotted namespace format, "
                "for example destiny.kingmaker.hidden."
            )

        tags = payload.get("tags", [])
        if tags is not None and not isinstance(tags, list):
            errors.append("Registry tags must be a list of strings.")

        compatible_with = payload.get("compatible_with", [])
        if compatible_with is not None and not isinstance(compatible_with, list):
            errors.append("compatible_with must be a list.")

        conflicts_with = payload.get("conflicts_with", [])
        if conflicts_with is not None and not isinstance(conflicts_with, list):
            errors.append("conflicts_with must be a list.")

        success = len(errors) == 0

        return self.build_result(
            success=success,
            data={
                "validated_type_id": type_id,
                "category": payload.get("category"),
                "is_valid": success,
                "field_count": len(payload),
            },
            warnings=warnings,
            errors=errors,
            generated_object_ids=[],
        )
