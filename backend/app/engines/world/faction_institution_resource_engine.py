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


class FactionInstitutionResourceEngine:
    """Builds political, institutional, and resource constraints for simulation."""

    engine_name = "world.faction_institution_resource_engine"

    def run(self, payload: Dict[str, Any]) -> EngineResult:
        world = payload.get("world_profile") or payload.get("world") or payload
        project_id = payload.get("project_id", "default_project")
        universe_id = payload.get("universe_id", "default_universe")

        factions = self._list(world.get("factions") or ["Oath Court", "Relic Guild"])
        institutions = self._list(world.get("institutions") or ["Academy", "Court"])
        resources = self._list(world.get("resources") or world.get("economy") or ["relic labor", "sponsor seats"])

        faction_refs = [
            EntityRef(
                entity_type=EntityType.FACTION,
                entity_id=self._slug("faction", faction),
                display_name=str(faction),
                project_id=project_id,
                universe_id=universe_id,
                canon_status=CanonStatus.DRAFT,
            ).model_dump()
            for faction in factions
        ]

        institution_refs = [
            EntityRef(
                entity_type=EntityType.INSTITUTION,
                entity_id=self._slug("institution", institution),
                display_name=str(institution),
                project_id=project_id,
                universe_id=universe_id,
                canon_status=CanonStatus.DRAFT,
            ).model_dump()
            for institution in institutions
        ]

        resource_refs = [
            EntityRef(
                entity_type=EntityType.RESOURCE,
                entity_id=self._slug("resource", resource),
                display_name=str(resource),
                project_id=project_id,
                universe_id=universe_id,
                canon_status=CanonStatus.DRAFT,
            ).model_dump()
            for resource in resources
        ]

        faction_power_sources = []
        for faction in factions:
            text = str(faction).lower()
            faction_power_sources.append(
                {
                    "faction_id": self._slug("faction", faction),
                    "power_sources": self._infer_power_sources(text),
                    "enforcement_rules": self._infer_enforcement_rules(text),
                    "pressure_points": ["reputation", "access", "resources", "legal standing"],
                }
            )

        resource_dependencies = [
            {
                "resource_id": self._slug("resource", resource),
                "scarcity_level": "medium",
                "controlled_by": faction_refs[0]["entity_id"] if faction_refs else None,
                "simulation_pressure": "resource access can block choices, bargains, travel, or institutional protection",
            }
            for resource in resources
        ]

        return EngineResult(
            success=True,
            engine_name=self.engine_name,
            data={
                "world_id": world.get("world_id", "unknown_world"),
                "faction_refs": faction_refs,
                "institution_refs": institution_refs,
                "resource_refs": resource_refs,
                "faction_power_sources": faction_power_sources,
                "resource_dependencies": resource_dependencies,
                "institutional_authority": [
                    {
                        "institution_id": item["entity_id"],
                        "authority_scope": ["law", "status", "access", "public legitimacy"],
                    }
                    for item in institution_refs
                ],
                "simulation_ready": bool(faction_refs and institution_refs and resource_refs),
            },
            warnings=[],
            errors=[],
        )

    def _infer_power_sources(self, text: str) -> List[str]:
        sources = []
        if "court" in text or "oath" in text:
            sources.extend(["law", "legitimacy", "public testimony"])
        if "guild" in text or "relic" in text:
            sources.extend(["resources", "technical knowledge", "labor control"])
        if not sources:
            sources.extend(["reputation", "information", "alliances"])
        return sources

    def _infer_enforcement_rules(self, text: str) -> List[str]:
        if "court" in text or "oath" in text:
            return ["can punish oath-breaking", "can validate testimony", "can restrict legal access"]
        if "guild" in text or "relic" in text:
            return ["can restrict relic access", "can impose debt terms", "can control apprenticeship routes"]
        return ["can amplify rumors", "can withdraw support", "can enforce social pressure"]

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
