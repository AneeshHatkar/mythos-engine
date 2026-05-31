from typing import Any, Dict, List

from backend.app.schemas.canon import CanonLock, CanonValidationResult


class CanonLockService:
    """Enforces canon locks before engines mutate canon-sensitive state."""

    def __init__(self) -> None:
        self._locks: List[CanonLock] = []

    def add_lock(self, lock: CanonLock | Dict[str, Any]) -> Dict[str, Any]:
        record = lock if isinstance(lock, CanonLock) else CanonLock.model_validate(lock)
        self._locks.append(record)

        return {
            "success": True,
            "lock_id": record.lock_id,
            "lock_type": record.lock_type,
            "target_entity_id": record.target_ref.entity_id,
        }

    def list_locks(self, *, target_entity_id: str | None = None) -> List[Dict[str, Any]]:
        locks = self._locks
        if target_entity_id:
            locks = [lock for lock in locks if lock.target_ref.entity_id == target_entity_id]
        return [lock.model_dump() for lock in locks]

    def validate_change(
        self,
        *,
        target_entity_id: str,
        proposed_value: Dict[str, Any],
        branch_id: str = "main",
        allow_retcon: bool = False,
    ) -> Dict[str, Any]:
        violations = []
        warnings = []
        blocked_by = []

        for lock in self._locks:
            if lock.target_ref.entity_id != target_entity_id:
                continue
            if lock.branch_id != branch_id:
                continue

            locked_value = lock.locked_value or {}
            for key, locked in locked_value.items():
                if key in proposed_value and proposed_value[key] != locked:
                    if allow_retcon and lock.can_override_with_retcon:
                        warnings.append(f"retcon override used for {key}")
                    else:
                        violations.append(f"{key} is locked as {locked}; proposed {proposed_value[key]}")
                        blocked_by.append(lock.lock_id)

        result = CanonValidationResult(
            valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            blocked_by_lock_ids=blocked_by,
            retcon_required=bool(violations),
            alternate_branch_recommended=bool(violations),
        )

        return result.model_dump()
