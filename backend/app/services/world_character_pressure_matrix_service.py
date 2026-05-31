from typing import Any, Dict, List

from backend.app.schemas.story_dna import WorldCharacterPressureRecord


class WorldCharacterPressureMatrixService:
    """Maps how the world pressures each character differently."""

    def build_pressure_matrix(
        self,
        *,
        world_profile: Dict[str, Any],
        character_profiles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        world_id = str(world_profile.get("world_id") or "unknown_world")
        records = []

        for profile in character_profiles:
            records.append(self.build_pressure_record(world_profile=world_profile, character_profile=profile))

        average_pressure = round(sum(r["pressure_score"] for r in records) / len(records), 3) if records else 0.0

        return {
            "success": True,
            "world_id": world_id,
            "character_count": len(character_profiles),
            "average_pressure_score": average_pressure,
            "pressure_records": records,
            "simulation_ready": bool(records) and average_pressure >= 0.25,
        }

    def build_pressure_record(self, *, world_profile: Dict[str, Any], character_profile: Dict[str, Any]) -> Dict[str, Any]:
        flat = self._flatten(character_profile)
        character_id = str(flat.get("character_id") or character_profile.get("character_id") or "unknown_character")
        world_id = str(world_profile.get("world_id") or "unknown_world")

        world_text = self._joined(world_profile)
        social_class = str(flat.get("social_class") or "").lower()
        family_status = str(flat.get("family_name_status") or "").lower()
        goal = str(flat.get("surface_goal") or flat.get("hidden_goal") or "").lower()
        skill = str(flat.get("skill_family") or flat.get("primary_skill") or "").lower()

        law_pressure = []
        class_pressure = []
        economic_pressure = []
        faction_pressure = []
        culture_pressure = []
        romance_pressure = []
        power_pressure = []

        if "testify" in world_text or "court" in world_text:
            law_pressure.append("legal recognition depends on institutional permission")
        if "distrusted" in family_status or "erased" in family_status:
            law_pressure.append("family-name status weakens public credibility")
            class_pressure.append("status access requires sponsor, exception, or debt route")
        if "academy" in world_text and ("ranking" in goal or "survive" in goal):
            class_pressure.append("academy ranking turns private worth into public status")
        if "debt" in world_text or "resource" in world_text or "relic labor" in world_text:
            economic_pressure.append("resource access can force bargains or delayed obedience")
        if "oath court" in world_text:
            faction_pressure.append("Oath Court can control testimony, legitimacy, and punishment")
        if "relic guild" in world_text:
            faction_pressure.append("Relic Guild can control power access and technical dependency")
        if "public names" in world_text or "culture" in world_text:
            culture_pressure.append("culture turns names and reputation into survival tools")
        if "romance" in world_text or "public status" in world_text:
            romance_pressure.append("public status can block intimacy or make affection dangerous")
        if "requires cost" in world_text or "cost" in world_text:
            power_pressure.append("power use must create cost, counterplay, or consequence")
        if skill:
            power_pressure.append(f"{skill} must obey world power laws and social consequences")

        categories = [
            law_pressure,
            class_pressure,
            economic_pressure,
            faction_pressure,
            culture_pressure,
            romance_pressure,
            power_pressure,
        ]
        pressure_score = round(min(1.0, sum(1 for category in categories if category) / len(categories)), 3)

        event_fuel = []
        if law_pressure:
            event_fuel.extend(["trial pressure", "public testimony conflict"])
        if class_pressure:
            event_fuel.extend(["public humiliation", "restricted access scene"])
        if economic_pressure:
            event_fuel.extend(["debt bargain", "resource leverage"])
        if faction_pressure:
            event_fuel.extend(["faction order", "political blackmail"])
        if romance_pressure:
            event_fuel.extend(["romance blocked by public status"])
        if power_pressure:
            event_fuel.extend(["power use with cost", "skill consequence scene"])

        record = WorldCharacterPressureRecord(
            character_id=character_id,
            world_id=world_id,
            law_pressure=law_pressure,
            class_pressure=class_pressure,
            economic_pressure=economic_pressure,
            faction_pressure=faction_pressure,
            religious_or_cultural_pressure=culture_pressure,
            romance_pressure=romance_pressure,
            power_pressure=power_pressure,
            pressure_score=pressure_score,
            simulation_event_fuel=list(dict.fromkeys(event_fuel)),
        )

        return record.model_dump()

    def _joined(self, value: Any) -> str:
        if isinstance(value, dict):
            return " ".join(self._joined(v) for v in value.values()).lower()
        if isinstance(value, list):
            return " ".join(self._joined(v) for v in value).lower()
        return str(value or "").lower()

    def _flatten(self, value: Any) -> Dict[str, Any]:
        flat: Dict[str, Any] = {}

        def walk(item: Any) -> None:
            if isinstance(item, dict):
                for key, val in item.items():
                    if key not in flat and not isinstance(val, (dict, list)):
                        flat[key] = val
                    walk(val)
            elif isinstance(item, list):
                for val in item:
                    walk(val)

        walk(value)
        return flat
