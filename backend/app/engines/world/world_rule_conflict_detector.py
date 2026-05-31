from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EngineResult:
    success: bool
    engine_name: str
    data: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)



class WorldRuleConflictDetector:
    """Detects contradictory world rules before simulation consumes them."""

    engine_name = "world.rule_conflict_detector"

    def run(self, payload: Dict[str, Any]) -> EngineResult:
        world = payload.get("world_profile") or payload.get("world") or payload
        conflicts = []
        warnings = []

        legal_text = self._joined(world.get("legal_constraints") or world.get("laws") or [])
        culture_text = self._joined(world.get("culture") or world.get("cultural_rules") or [])
        access_text = self._joined(world.get("academy_access") or world.get("access_rules") or [])
        geography_text = self._joined(world.get("geography") or world.get("locations") or [])
        travel_text = self._joined(world.get("travel_rules") or world.get("travel_constraints") or [])
        magic_text = self._joined(world.get("magic_rules") or world.get("power_laws") or [])
        economy_text = self._joined(world.get("economy") or world.get("resources") or [])

        if "cannot testify" in legal_text and "must testify" in legal_text and not self._has_exception_route(legal_text):
            conflicts.append("legal contradiction: a group both cannot testify and must testify without an exception route")

        if "erased" in legal_text and "sponsor" in legal_text and "sponsor" not in access_text:
            warnings.append("legal system references sponsor exceptions, but access rules do not define sponsor routes")

        if "instant travel" in travel_text and ("distant" in geography_text or "outer" in geography_text):
            conflicts.append("travel contradiction: instant travel conflicts with distance/geography constraints unless explained")

        if "requires cost" in magic_text and ("costless" in magic_text or "no cost" in magic_text):
            conflicts.append("power contradiction: power requires cost and is also described as costless")

        if "scarcity" in economy_text and "unlimited" in economy_text:
            conflicts.append("resource contradiction: economy claims scarcity and unlimited resources")

        consistency_score = max(0.0, 1.0 - 0.22 * len(conflicts) - 0.08 * len(warnings))

        return EngineResult(
            success=True,
            engine_name=self.engine_name,
            data={
                "world_id": world.get("world_id", "unknown_world"),
                "conflicts": conflicts,
                "warnings": warnings,
                "world_rule_consistency_score": round(consistency_score, 3),
                "simulation_safe": len(conflicts) == 0 and consistency_score >= 0.7,
                "checked_axes": [
                    "legal_constraints",
                    "culture",
                    "access_rules",
                    "geography_travel",
                    "power_laws",
                    "economy_resources",
                ],
            },
            warnings=warnings,
            errors=[],
        )

    def _joined(self, value: Any) -> str:
        if isinstance(value, list):
            return " ".join(str(item).lower() for item in value)
        if isinstance(value, dict):
            return " ".join(str(item).lower() for item in value.values())
        return str(value or "").lower()

    def _has_exception_route(self, text: str) -> bool:
        return any(token in text for token in ["unless", "except", "sponsor", "witness", "appeal", "permit"])
