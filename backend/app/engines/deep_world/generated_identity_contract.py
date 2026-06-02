from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import (
    DetailDepthContract,
    GeneratedElementDepthReport,
    GeneratedNameProfile,
)


class GeneratedIdentityContractBuilder:
    def build_name_profile(
        self,
        *,
        source_id: str,
        generated_for_type: str,
        base_name: str,
        culture_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        culture_context = culture_context or {}

        culture = culture_context.get("culture", "Saltroot bell-road culture")
        region = culture_context.get("region", "Saltroot Forest")
        language_logic = culture_context.get(
            "language_logic",
            "compound names combine road-memory roots with witness-law suffixes",
        )

        unique_name = culture_context.get("unique_name") or self._make_unique_name(
            base_name=base_name,
            generated_for_type=generated_for_type,
        )

        profile = GeneratedNameProfile(
            name_profile_id=f"name_profile_{source_id}_{self._slug(unique_name)}",
            source_id=source_id,
            generated_for_type=generated_for_type,
            unique_name=unique_name,
            name_origin=(
                f"{unique_name} is derived from {culture}; the name reflects local history, "
                f"region pressure, and social memory rather than random sound."
            ),
            name_meaning=culture_context.get(
                "name_meaning",
                f"A name associated with {region}, inherited memory, and public identity.",
            ),
            name_language_logic=language_logic,
            cultural_context=culture,
            world_context=region,
            pronunciation_hint=culture_context.get("pronunciation_hint"),
            nickname_rules=culture_context.get("nickname_rules", [
                "nicknames shorten around trusted family or travel companions",
                "public nicknames may encode profession or oath status",
            ]),
            title_rules=culture_context.get("title_rules", [
                "formal titles attach after civic duty, exile, or oath witness status",
            ]),
            taboo_name_rules=culture_context.get("taboo_name_rules", [
                "names tied to betrayal may be replaced by function-only titles",
            ]),
            alias_rules=culture_context.get("alias_rules", [
                "aliases form when a person crosses borders, breaks oath, or hides family origin",
            ]),
            related_place_or_family=culture_context.get("related_place_or_family"),
            anti_genericity_signal=(
                "Name includes culture, language logic, social rules, and world context; "
                "not a template fantasy placeholder."
            ),
            detail_depth_score=float(culture_context.get("detail_depth_score", 0.88)),
            provenance={
                "generated_by_engine": "GeneratedIdentityContractBuilder",
                "origin_type": "culture_aware_name_profile",
                "source_id": source_id,
                "context_keys": sorted(culture_context.keys()),
            },
            compression_summary=(
                f"{unique_name}: {generated_for_type} name from {culture}; "
                f"meaning tied to {region}."
            ),
        )

        return {"generated_name_profile": profile}

    def build_detail_depth_contract(self, *, source_id: str) -> Dict[str, Any]:
        return {
            "detail_depth_contract": DetailDepthContract(
                detail_depth_contract_id=f"detail_depth_contract_{source_id}",
                source_id=source_id,
            )
        }

    def evaluate_generated_element(
        self,
        *,
        source_id: str,
        target_element_id: str,
        target_element_type: str,
        element_payload: Dict[str, Any],
        contract: DetailDepthContract | None = None,
    ) -> Dict[str, Any]:
        contract = contract or self.build_detail_depth_contract(source_id=source_id)["detail_depth_contract"]

        missing = [
            field for field in contract.required_identity_fields
            if not element_payload.get(field)
        ]

        shallow_warnings: List[str] = []
        for key in ["story_use", "character_effect", "plot_effect", "memory_effect", "cultural_context", "world_context"]:
            if len(str(element_payload.get(key, ""))) < 20:
                shallow_warnings.append(f"{key} is too shallow.")

        depth_score = max(0.0, 1.0 - (len(missing) * 0.06) - (len(shallow_warnings) * 0.12))
        passed = not missing and not shallow_warnings and depth_score >= contract.minimum_detail_depth_score

        report = GeneratedElementDepthReport(
            depth_report_id=f"depth_report_{source_id}_{target_element_id}",
            source_id=source_id,
            target_element_id=target_element_id,
            target_element_type=target_element_type,
            passed=passed,
            detail_depth_score=depth_score,
            naming_depth_score=0.9 if element_payload.get("unique_name") and element_payload.get("name_origin") else 0.2,
            lore_depth_score=0.85 if element_payload.get("lore_connection") or element_payload.get("historical_memory") else 0.35,
            story_usefulness_score=0.9 if element_payload.get("story_use") and element_payload.get("plot_effect") else 0.2,
            missing_fields=missing,
            shallow_output_warnings=shallow_warnings,
            repair_actions=self._repair_actions(missing_fields=missing, shallow_warnings=shallow_warnings),
        )

        return {"generated_element_depth_report": report}

    def validate_name_profile(self, *, profile: GeneratedNameProfile) -> Dict[str, Any]:
        blockers: List[str] = []
        if profile.detail_depth_score < 0.75:
            blockers.append("Name profile detail depth score is below threshold.")
        if not profile.name_origin or not profile.name_meaning or not profile.name_language_logic:
            blockers.append("Name profile lacks origin, meaning, or language logic.")
        if not profile.cultural_context or not profile.world_context:
            blockers.append("Name profile lacks cultural or world context.")

        return {
            "passed": not blockers,
            "blockers": blockers,
            "name_profile_id": profile.name_profile_id,
            "unique_name": profile.unique_name,
        }

    def summarize_name_profile(self, *, profile: GeneratedNameProfile) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "name_profile_id": profile.name_profile_id,
                "unique_name": profile.unique_name,
                "generated_for_type": profile.generated_for_type,
                "name_meaning": profile.name_meaning,
                "detail_depth_score": profile.detail_depth_score,
                "compression_summary": profile.compression_summary,
            },
        }

    def _make_unique_name(self, *, base_name: str, generated_for_type: str) -> str:
        cleaned = " ".join(part.capitalize() for part in base_name.replace("_", " ").split())
        if generated_for_type in {"person", "character", "people"}:
            return f"{cleaned} Veyrann"
        if generated_for_type in {"country", "political_unit"}:
            return f"The Bellmarch Concord of {cleaned}"
        if generated_for_type in {"flora", "plant"}:
            return f"{cleaned} Ashbloom"
        if generated_for_type in {"fauna", "creature", "species"}:
            return f"{cleaned} Fogwalker"
        return f"{cleaned} of the Witness Road"

    def _repair_actions(self, *, missing_fields: List[str], shallow_warnings: List[str]) -> List[str]:
        actions = []
        for field in missing_fields:
            actions.append(f"Add missing required identity/depth field: {field}")
        if shallow_warnings:
            actions.append("Expand shallow fields into story, character, plot, memory, culture, and lore explanations.")
        return actions

    def _slug(self, value: str) -> str:
        return "_".join(part for part in value.lower().replace("/", " ").replace("-", " ").split() if part)
