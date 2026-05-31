from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class EngineResult:
    success: bool
    engine_name: str
    data: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

from backend.app.schemas.global_refs import CanonStatus, EntityRef, EntityType


class WorldLocationAccessEngine:
    """Builds simulation-ready location, travel, and access constraints."""

    engine_name = "world.location_access_engine"

    def run(self, payload: Dict[str, Any]) -> EngineResult:
        world = payload.get("world_profile") or payload.get("world") or payload
        project_id = payload.get("project_id", "default_project")
        universe_id = payload.get("universe_id", "default_universe")

        raw_locations = (
            world.get("locations")
            or world.get("geography")
            or ["capital district", "outer district", "restricted court district"]
        )

        locations = self._list(raw_locations)
        location_refs = [
            EntityRef(
                entity_type=EntityType.LOCATION,
                entity_id=self._slug("location", location),
                display_name=str(location),
                project_id=project_id,
                universe_id=universe_id,
                canon_status=CanonStatus.DRAFT,
            ).model_dump()
            for location in locations
        ]

        access_rules = []
        witness_rules = []
        travel_edges = []

        for location in locations:
            lowered = str(location).lower()
            rule = {
                "location_id": self._slug("location", location),
                "location_name": str(location),
                "allowed_classes": ["academy_sponsored", "old_nobility"],
                "restricted_classes": [],
                "requires_sponsor": False,
                "controlled_by_faction": None,
                "event_allowed_types": ["conversation", "rumor_spread", "negotiation"],
            }

            if "court" in lowered or "capital" in lowered:
                rule["requires_sponsor"] = True
                rule["restricted_classes"] = ["erased", "distrusted"]
                rule["event_allowed_types"].extend(["trial", "public_humiliation", "social_duel"])

            if "outer" in lowered:
                rule["allowed_classes"].append("erased")
                rule["event_allowed_types"].extend(["secret_discovery", "blackmail_attempt", "physical_duel"])

            if "academy" in lowered:
                rule["event_allowed_types"].extend(["rivalry", "ranking_challenge", "promise_made"])

            access_rules.append(rule)

            witness_rules.append(
                {
                    "location_id": rule["location_id"],
                    "witness_possible": True,
                    "witness_limitations": [
                        "characters must be present, authorized, hidden, or connected by rumor/evidence path"
                    ],
                }
            )

        for idx, location in enumerate(locations):
            if idx + 1 < len(locations):
                travel_edges.append(
                    {
                        "from_location_id": self._slug("location", location),
                        "to_location_id": self._slug("location", locations[idx + 1]),
                        "travel_cost": "medium",
                        "requires_permission": False,
                        "rumor_transmission_possible": True,
                    }
                )

        return EngineResult(
            success=True,
            engine_name=self.engine_name,
            data={
                "world_id": world.get("world_id", "unknown_world"),
                "location_refs": location_refs,
                "travel_edges": travel_edges,
                "access_rules": access_rules,
                "witness_possible_rules": witness_rules,
                "simulation_ready": bool(location_refs and access_rules),
            },
            warnings=[],
            errors=[],
        )

    def _list(self, value: Any) -> List[Any]:
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            return list(value.values())
        return [value]

    def _slug(self, prefix: str, value: Any) -> str:
        raw = str(value).lower().strip()
        safe = "".join(ch if ch.isalnum() else "_" for ch in raw).strip("_")
        safe = "_".join(part for part in safe.split("_") if part)
        return f"{prefix}_{safe[:48] or 'unknown'}"
