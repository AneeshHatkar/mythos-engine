from typing import Any, Dict, List


class CharacterContrastMatrixService:
    """Compares characters so ensembles do not become interchangeable."""

    CONTRAST_AXES = [
        "core_wound",
        "surface_goal",
        "hidden_goal",
        "dominant_moral_value",
        "social_class",
        "skill_family",
        "voice_family",
        "agency_capacity",
        "relationship_readiness_family",
        "public_mask",
        "private_truth",
        "symbolic_role",
    ]

    def build_contrast_matrix(self, *, character_profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        records = []

        for i, a in enumerate(character_profiles):
            for j, b in enumerate(character_profiles):
                if j <= i:
                    continue
                records.append(self.compare_characters(a, b))

        average_contrast = round(sum(r["contrast_score"] for r in records) / len(records), 3) if records else 0.0
        redundancy_warnings = [r for r in records if r["redundancy_warning"]]

        return {
            "success": True,
            "character_count": len(character_profiles),
            "pair_count": len(records),
            "average_contrast_score": average_contrast,
            "redundancy_warning_count": len(redundancy_warnings),
            "contrast_records": records,
            "ensemble_ready": bool(records) and average_contrast >= 0.35 and len(redundancy_warnings) == 0,
        }

    def compare_characters(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        flat_a = self._flatten(a)
        flat_b = self._flatten(b)

        a_id = str(flat_a.get("character_id") or a.get("character_id") or "char_a")
        b_id = str(flat_b.get("character_id") or b.get("character_id") or "char_b")

        axis_results = {}
        differences = 0
        mirrors = 0

        for axis in self.CONTRAST_AXES:
            va = flat_a.get(axis)
            vb = flat_b.get(axis)
            same = bool(va and vb and str(va).lower() == str(vb).lower())
            both_present = va is not None and vb is not None
            different = both_present and not same

            axis_results[axis] = {
                "a": va,
                "b": vb,
                "same": same,
                "different": different,
                "both_present": both_present,
            }

            if different:
                differences += 1
            if same:
                mirrors += 1

        present_axes = sum(1 for item in axis_results.values() if item["both_present"]) or 1
        contrast_score = round(differences / present_axes, 3)
        mirror_score = round(mirrors / present_axes, 3)

        foil_score = round((contrast_score * 0.65) + (mirror_score * 0.20), 3)
        chemistry_score = round(min(1.0, contrast_score * 0.45 + mirror_score * 0.35 + 0.2), 3)
        conflict_score = round(min(1.0, contrast_score * 0.70 + self._goal_conflict_bonus(flat_a, flat_b)), 3)

        redundancy_warning = contrast_score < 0.25 and mirror_score > 0.45

        return {
            "character_a_id": a_id,
            "character_b_id": b_id,
            "contrast_score": contrast_score,
            "mirror_score": mirror_score,
            "foil_score": foil_score,
            "chemistry_score": chemistry_score,
            "conflict_score": conflict_score,
            "redundancy_warning": redundancy_warning,
            "contrast_axes": axis_results,
            "story_uses": self._story_uses(contrast_score, mirror_score, conflict_score),
        }

    def _goal_conflict_bonus(self, a: Dict[str, Any], b: Dict[str, Any]) -> float:
        a_goal = str(a.get("surface_goal") or a.get("hidden_goal") or "").lower()
        b_goal = str(b.get("surface_goal") or b.get("hidden_goal") or "").lower()
        if not a_goal or not b_goal:
            return 0.0
        if any(token in a_goal and token in b_goal for token in ["ranking", "truth", "power", "survive"]):
            return 0.1
        return 0.0

    def _story_uses(self, contrast: float, mirror: float, conflict: float) -> List[str]:
        uses = []
        if contrast >= 0.55:
            uses.append("foil dynamic")
        if mirror >= 0.35:
            uses.append("mirror wound reveal")
        if conflict >= 0.55:
            uses.append("relationship conflict engine fuel")
        if not uses:
            uses.append("requires more differentiation")
        return uses

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
