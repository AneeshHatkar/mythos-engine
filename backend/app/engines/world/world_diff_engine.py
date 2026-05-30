from typing import Any, Dict, List, Set

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldDiffEngine(BaseEngine):
    """Compares two world states for similarity, uniqueness, and quality.

    This engine helps MythOS avoid generating thousands of repetitive worlds.

    It compares:
    - shared motifs
    - unique motifs
    - system overlap
    - generic overlap risk
    - quality scores
    - training-readiness signals
    - story potential differences
    - merge/revision opportunities

    Later this can support:
    - world recommendation
    - dataset deduplication
    - originality benchmarks
    - world variant selection
    - franchise planning
    """

    engine_name = "world.diff_engine"

    IMPORTANT_MOTIFS = [
        "academy",
        "oath",
        "relic",
        "archive",
        "destiny",
        "class",
        "noble",
        "commoner",
        "law",
        "court",
        "border",
        "market",
        "prophecy",
        "artifact",
        "memory",
        "erased",
        "debt",
        "ritual",
        "faction",
        "surveillance",
        "civilization",
        "collapse",
        "romance",
        "inheritance",
        "forbidden",
        "sponsor",
        "kingdom",
        "empire",
        "religion",
        "war",
        "healing",
        "magic",
        "technology",
        "species",
    ]

    SYSTEM_KEYS = [
        "identity",
        "rules",
        "chronology",
        "geography",
        "demographics",
        "society",
        "power_structure",
        "military_security",
        "economy",
        "law",
        "belief",
        "culture",
        "knowledge_education",
        "institutions",
        "technology_magic_science",
        "species_creatures",
        "artifacts",
        "aesthetic_texture",
        "civilization_pressure",
        "causality_graph",
        "quality_summary",
        "dataset_metadata",
    ]

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_a = payload.get("world_a", {})
        world_b = payload.get("world_b", {})
        label_a = payload.get("label_a", "world_a")
        label_b = payload.get("label_b", "world_b")

        warnings: List[str] = []

        if not world_a:
            warnings.append("world_a is empty or missing.")

        if not world_b:
            warnings.append("world_b is empty or missing.")

        comparison = self._compare_worlds(
            world_a=world_a,
            world_b=world_b,
            label_a=label_a,
            label_b=label_b,
        )

        return self.build_result(
            success=True,
            data={
                "comparison": comparison,
                "training_notes": [
                    "World diff can support future dataset deduplication.",
                    "High similarity with low unique motif counts should block training promotion.",
                    "Comparison scores are deterministic Chunk 2 heuristics and can later be replaced by embeddings.",
                    "Future Chunk 8 can add vector similarity, clustering, and learned originality scoring.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[],
        )

    def _flatten_text(self, obj: Any) -> str:
        if obj is None:
            return ""
        if isinstance(obj, str):
            return obj
        if isinstance(obj, (int, float, bool)):
            return str(obj)
        if isinstance(obj, list):
            return " ".join(self._flatten_text(item) for item in obj)
        if isinstance(obj, dict):
            return " ".join(
                str(key) + " " + self._flatten_text(value)
                for key, value in obj.items()
            )
        return str(obj)

    def _tokenize(self, text: str) -> Set[str]:
        cleaned = ""
        for ch in text.lower():
            if ch.isalnum() or ch in {"_", "-"}:
                cleaned += ch
            else:
                cleaned += " "

        stopwords = {
            "the",
            "and",
            "or",
            "of",
            "to",
            "in",
            "a",
            "an",
            "is",
            "are",
            "with",
            "for",
            "by",
            "on",
            "as",
            "that",
            "this",
            "it",
            "be",
            "from",
            "into",
            "their",
            "its",
            "not",
            "can",
            "will",
            "world",
            "system",
        }

        return {
            token
            for token in cleaned.split()
            if len(token) >= 4 and token not in stopwords
        }

    def _detect_motifs(self, text: str) -> Set[str]:
        lower = text.lower()
        return {motif for motif in self.IMPORTANT_MOTIFS if motif in lower}

    def _system_coverage(self, world: Dict[str, Any]) -> Set[str]:
        return {
            key
            for key in self.SYSTEM_KEYS
            if world.get(key) not in (None, {}, [], "")
        }

    def _get_quality_summary(self, world: Dict[str, Any]) -> Dict[str, float]:
        quality = world.get("quality_summary", {})

        if "dataset_metadata" in world:
            metadata_quality = world.get("dataset_metadata", {}).get("quality_snapshot", {})
            if metadata_quality:
                quality = {**metadata_quality, **quality}

        return {
            "consistency_score": float(quality.get("consistency_score", 0.0) or 0.0),
            "originality_score": float(quality.get("originality_score", 0.0) or 0.0),
            "story_potential_score": float(quality.get("story_potential_score", 0.0) or 0.0),
            "training_readiness_score": float(quality.get("training_readiness_score", 0.0) or 0.0),
            "genericness_risk_score": float(quality.get("genericness_risk_score", 1.0) or 1.0),
        }

    def _compare_worlds(
        self,
        *,
        world_a: Dict[str, Any],
        world_b: Dict[str, Any],
        label_a: str,
        label_b: str,
    ) -> Dict[str, Any]:
        text_a = self._flatten_text(world_a)
        text_b = self._flatten_text(world_b)

        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)

        motifs_a = self._detect_motifs(text_a)
        motifs_b = self._detect_motifs(text_b)

        systems_a = self._system_coverage(world_a)
        systems_b = self._system_coverage(world_b)

        token_similarity = self._jaccard(tokens_a, tokens_b)
        motif_similarity = self._jaccard(motifs_a, motifs_b)
        system_similarity = self._jaccard(systems_a, systems_b)

        overall_similarity = round(
            (token_similarity * 0.45)
            + (motif_similarity * 0.35)
            + (system_similarity * 0.20),
            3,
        )

        overlap_risk = self._overlap_risk(overall_similarity, motif_similarity)

        quality_a = self._get_quality_summary(world_a)
        quality_b = self._get_quality_summary(world_b)

        winner = self._choose_stronger_world(
            label_a=label_a,
            label_b=label_b,
            quality_a=quality_a,
            quality_b=quality_b,
            unique_motifs_a=motifs_a - motifs_b,
            unique_motifs_b=motifs_b - motifs_a,
        )

        return {
            "labels": {
                "world_a": label_a,
                "world_b": label_b,
            },
            "similarity": {
                "overall_similarity": overall_similarity,
                "token_similarity": round(token_similarity, 3),
                "motif_similarity": round(motif_similarity, 3),
                "system_similarity": round(system_similarity, 3),
                "overlap_risk": overlap_risk,
            },
            "motif_diff": {
                "shared_motifs": sorted(motifs_a & motifs_b),
                "unique_to_a": sorted(motifs_a - motifs_b),
                "unique_to_b": sorted(motifs_b - motifs_a),
                "motif_count_a": len(motifs_a),
                "motif_count_b": len(motifs_b),
            },
            "system_diff": {
                "shared_systems": sorted(systems_a & systems_b),
                "missing_from_a": sorted(systems_b - systems_a),
                "missing_from_b": sorted(systems_a - systems_b),
                "system_count_a": len(systems_a),
                "system_count_b": len(systems_b),
            },
            "quality_diff": {
                "world_a": quality_a,
                "world_b": quality_b,
                "score_deltas_a_minus_b": self._quality_deltas(quality_a, quality_b),
                "stronger_world": winner,
            },
            "recommendations": self._build_recommendations(
                label_a=label_a,
                label_b=label_b,
                overall_similarity=overall_similarity,
                overlap_risk=overlap_risk,
                motifs_a=motifs_a,
                motifs_b=motifs_b,
                systems_a=systems_a,
                systems_b=systems_b,
                quality_a=quality_a,
                quality_b=quality_b,
                stronger_world=winner,
            ),
        }

    def _jaccard(self, a: Set[str], b: Set[str]) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def _overlap_risk(self, overall_similarity: float, motif_similarity: float) -> str:
        if overall_similarity >= 0.72 or motif_similarity >= 0.82:
            return "high"
        if overall_similarity >= 0.45 or motif_similarity >= 0.55:
            return "medium"
        return "low"

    def _quality_deltas(
        self,
        quality_a: Dict[str, float],
        quality_b: Dict[str, float],
    ) -> Dict[str, float]:
        keys = sorted(set(quality_a) | set(quality_b))
        return {
            key: round(quality_a.get(key, 0.0) - quality_b.get(key, 0.0), 3)
            for key in keys
        }

    def _average_quality(self, quality: Dict[str, float]) -> float:
        return (
            quality.get("consistency_score", 0.0)
            + quality.get("originality_score", 0.0)
            + quality.get("story_potential_score", 0.0)
            + quality.get("training_readiness_score", 0.0)
            + (1.0 - quality.get("genericness_risk_score", 1.0))
        ) / 5

    def _choose_stronger_world(
        self,
        *,
        label_a: str,
        label_b: str,
        quality_a: Dict[str, float],
        quality_b: Dict[str, float],
        unique_motifs_a: Set[str],
        unique_motifs_b: Set[str],
    ) -> Dict[str, Any]:
        average_a = self._average_quality(quality_a) + min(0.08, len(unique_motifs_a) * 0.01)
        average_b = self._average_quality(quality_b) + min(0.08, len(unique_motifs_b) * 0.01)

        if abs(average_a - average_b) <= 0.025:
            winner = "tie"
        elif average_a > average_b:
            winner = label_a
        else:
            winner = label_b

        return {
            "winner": winner,
            "world_a_strength_score": round(average_a, 3),
            "world_b_strength_score": round(average_b, 3),
            "reason": (
                "Strength score combines consistency, originality, story potential, training readiness, low genericness risk, and unique motif bonus."
            ),
        }

    def _build_recommendations(
        self,
        *,
        label_a: str,
        label_b: str,
        overall_similarity: float,
        overlap_risk: str,
        motifs_a: Set[str],
        motifs_b: Set[str],
        systems_a: Set[str],
        systems_b: Set[str],
        quality_a: Dict[str, float],
        quality_b: Dict[str, float],
        stronger_world: Dict[str, Any],
    ) -> List[str]:
        recommendations = []

        if overlap_risk == "high":
            recommendations.append(
                "High overlap risk: do not keep both worlds in the same training dataset without stronger differentiation."
            )
        elif overlap_risk == "medium":
            recommendations.append(
                "Medium overlap risk: preserve both only if their unique motifs and story engines are strengthened."
            )
        else:
            recommendations.append(
                "Low overlap risk: worlds are sufficiently distinct for separate evaluation."
            )

        if not motifs_a - motifs_b:
            recommendations.append(f"{label_a} needs more unique motifs.")
        if not motifs_b - motifs_a:
            recommendations.append(f"{label_b} needs more unique motifs.")

        if len(systems_a) < len(systems_b):
            recommendations.append(f"{label_a} has weaker system coverage; add missing systems before comparison.")
        elif len(systems_b) < len(systems_a):
            recommendations.append(f"{label_b} has weaker system coverage; add missing systems before comparison.")

        if quality_a.get("originality_score", 0.0) < quality_b.get("originality_score", 0.0):
            recommendations.append(f"{label_a} should borrow no content, but should study why {label_b} has stronger originality signals.")
        elif quality_b.get("originality_score", 0.0) < quality_a.get("originality_score", 0.0):
            recommendations.append(f"{label_b} should borrow no content, but should study why {label_a} has stronger originality signals.")

        if stronger_world["winner"] != "tie":
            recommendations.append(
                f"Prefer {stronger_world['winner']} as the stronger candidate for world-bible expansion."
            )
        else:
            recommendations.append(
                "Both worlds are close in strength; use template, audience, or franchise goals to choose."
            )

        if overall_similarity >= 0.65:
            recommendations.append(
                "Add different geography, resource logic, belief system, visual palette, or institutional contradictions to reduce similarity."
            )

        return recommendations
