from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.app.schemas.foundation import EngineRunResult, new_id


class BaseEngine(ABC):
    """Base contract for every MythOS Engine module.

    Every future engine must return EngineRunResult so the system can audit,
    version, test, debug, and connect modules consistently.
    """

    engine_name: str = "base.engine"

    def build_result(
        self,
        *,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
        audit_id: Optional[str] = None,
        version_id: Optional[str] = None,
        generated_object_ids: Optional[List[str]] = None,
    ) -> EngineRunResult:
        return EngineRunResult(
            success=success,
            engine_name=self.engine_name,
            data=data or {},
            warnings=warnings or [],
            errors=errors or [],
            audit_id=audit_id,
            version_id=version_id,
            generated_object_ids=generated_object_ids or [],
        )

    def make_generated_id(self, prefix: str) -> str:
        return new_id(prefix)

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        """Run the engine and return a standard MythOS EngineRunResult."""
        raise NotImplementedError
