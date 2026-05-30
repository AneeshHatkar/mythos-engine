import math
import re
from collections import Counter
from typing import Any, Dict, List, Tuple

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.services.world_run_store import world_run_store


class EmbeddingOriginalityEngine(BaseEngine):
    """Deterministic embedding-style originality and similarity scorer.

    This is not full ML embedding/vector DB yet.

    It is a Chunk 2-safe, dependency-light semantic similarity layer that:
    - vectorizes world text using weighted token features
    - compares a candidate world against stored world-generation runs
    - detects near-duplicates
    - scores originality risk
    - recommends whether a world should enter a training dataset

    Later Chunk 8 can replace this with real embedding models, vector DBs,
    RAG retrieval, clustering, and learned originality scoring.
    """

    engine_name = "world.embedding_originality_engine"

    STOPWORDS = {
        "the", "and", "or", "of", "to", "in", "a", "an", "is", "are", "was", "were",
        "with", "for", "by", "on", "as", "that", "this", "it", "be", "from", "into",
        "their", "its", "not", "can", "will", "world", "system", "systems", "people",
        "where", "through", "between", "later", "future", "engine", "engines",
        "generated", "generation", "data", "metadata", "summary", "score", "scores",
    }

    HIGH_SIGNAL_TERMS = {
        "academy": 2.0,
        "oath": 2.2,
        "relic": 2.1,
        "archive": 2.1,
        "destiny": 2.1,
        "class": 1.8,
        "noble": 1.7,
        "commoner": 1.7,
        "law": 1.7,
        "court": 1.7,
        "border": 1.6,
        "market": 1.5,
        "prophecy": 1.9,
        "artifact": 1.8,
        "memory": 1.8,
        "erased": 2.0,
        "debt": 1.8,
        "ritual": 1.7,
        "faction": 1.7,
        "surveillance": 2.0,
        "civilization": 1.8,
        "collapse": 1.8,
        "romance": 1.8,
        "inheritance": 1.8,
        "forbidden": 1.9,
        "sponsor": 1.7,
        "religion": 1.6,
        "war": 1.5,
        "healing": 1.5,
        "magic": 1.6,
        "technology": 1.5,
        "species": 1.5,
    }

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        candidate_label = payload.get("candidate_label", "candidate_world")
        compare_against_saved_runs = payload.get("compare_against_saved_runs", True)
        top_k = int(payload.get("top_k", 5))
        minimum_similarity_to_report = float(payload.get("minimum_similarity_to_report", 0.05))

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; originality score will be conservative.")

        candidate_vector = self._vectorize(world_state)
        candidate_text = self._flatten_text(world_state)

        saved_comparisons: List[Dict[str, Any]] = []

        if compare_against_saved_runs:
            saved_comparisons = self._compare_against_saved_runs(
                candidate_vector=candidate_vector,
                candidate_text=candidate_text,
                top_k=top_k,
                minimum_similarity_to_report=minimum_similarity_to_report,
            )

        originality_report = self._build_originality_report(
            candidate_label=candidate_label,
            candidate_vector=candidate_vector,
            candidate_text=candidate_text,
            saved_comparisons=saved_comparisons,
        )

        return self.build_result(
            success=True,
            data={
                "embedding_originality_report": originality_report,
                "training_notes": [
                    "This is deterministic embedding-style scoring, not full ML embeddings.",
                    "It provides a safe Chunk 2 originality layer using stored world runs.",
                    "Later Chunk 8 should replace or augment this with real embedding models and vector DB search.",
                    "High similarity should block automatic training promotion until human review.",
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

    def _tokens(self, text: str) -> List[str]:
        raw_tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())

        return [
            token
            for token in raw_tokens
            if token not in self.STOPWORDS and len(token) >= 3
        ]

    def _bigrams(self, tokens: List[str]) -> List[str]:
        return [
            f"{tokens[idx]}__{tokens[idx + 1]}"
            for idx in range(len(tokens) - 1)
        ]

    def _vectorize(self, obj: Any) -> Dict[str, float]:
        text = self._flatten_text(obj)
        tokens = self._tokens(text)
        bigrams = self._bigrams(tokens)

        counts = Counter(tokens)

        # Add lower-weight bigram features to capture phrase-level overlap.
        for bigram in bigrams:
            counts[bigram] += 0.5

        vector: Dict[str, float] = {}

        for token, count in counts.items():
            base_token = token.split("__")[0]
            weight = self.HIGH_SIGNAL_TERMS.get(base_token, 1.0)

            if "__" in token:
                weight *= 1.15

            vector[token] = float(count) * weight

        return vector

    def _cosine_similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0

        shared = set(a) & set(b)

        dot = sum(a[key] * b[key] for key in shared)
        norm_a = math.sqrt(sum(value * value for value in a.values()))
        norm_b = math.sqrt(sum(value * value for value in b.values()))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def _jaccard_similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        keys_a = set(a)
        keys_b = set(b)

        if not keys_a and not keys_b:
            return 1.0

        if not keys_a or not keys_b:
            return 0.0

        return len(keys_a & keys_b) / len(keys_a | keys_b)

    def _hybrid_similarity(self, a: Dict[str, float], b: Dict[str, float]) -> float:
        cosine = self._cosine_similarity(a, b)
        jaccard = self._jaccard_similarity(a, b)

        return round((cosine * 0.72) + (jaccard * 0.28), 3)

    def _compare_against_saved_runs(
        self,
        *,
        candidate_vector: Dict[str, float],
        candidate_text: str,
        top_k: int,
        minimum_similarity_to_report: float,
    ) -> List[Dict[str, Any]]:
        saved_runs = world_run_store.list_runs(limit=100)
        comparisons: List[Dict[str, Any]] = []

        for saved in saved_runs:
            run_id = saved["run_id"]
            full_run = world_run_store.get_run(run_id)

            if not full_run:
                continue

            saved_world = full_run.get("world_state", {})
            saved_vector = self._vectorize(saved_world)
            similarity = self._hybrid_similarity(candidate_vector, saved_vector)

            if similarity < minimum_similarity_to_report:
                continue

            comparisons.append(
                {
                    "run_id": run_id,
                    "world_name": full_run.get("world_name"),
                    "template_id": full_run.get("template_id"),
                    "quality_tier": full_run.get("quality_tier"),
                    "training_eligible": full_run.get("training_eligible"),
                    "similarity": similarity,
                    "overlap_tier": self._overlap_tier(similarity),
                    "shared_high_signal_terms": self._shared_high_signal_terms(
                        candidate_text,
                        self._flatten_text(saved_world),
                    ),
                    "created_at": full_run.get("created_at"),
                }
            )

        comparisons.sort(key=lambda item: item["similarity"], reverse=True)

        return comparisons[:top_k]

    def _shared_high_signal_terms(self, a_text: str, b_text: str) -> List[str]:
        a_lower = a_text.lower()
        b_lower = b_text.lower()

        return sorted(
            term
            for term in self.HIGH_SIGNAL_TERMS
            if term in a_lower and term in b_lower
        )

    def _overlap_tier(self, similarity: float) -> str:
        if similarity >= 0.82:
            return "near_duplicate"
        if similarity >= 0.65:
            return "high_overlap"
        if similarity >= 0.42:
            return "medium_overlap"
        return "low_overlap"

    def _build_originality_report(
        self,
        *,
        candidate_label: str,
        candidate_vector: Dict[str, float],
        candidate_text: str,
        saved_comparisons: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        nearest_similarity = (
            saved_comparisons[0]["similarity"]
            if saved_comparisons
            else 0.0
        )

        unique_signal_terms = [
            term
            for term in self.HIGH_SIGNAL_TERMS
            if term in candidate_text.lower()
        ]

        detail_density = min(1.0, len(candidate_text.split()) / 1500)
        motif_diversity = min(1.0, len(unique_signal_terms) / 12)

        duplicate_penalty = 0.0

        if nearest_similarity >= 0.82:
            duplicate_penalty = 0.55
        elif nearest_similarity >= 0.65:
            duplicate_penalty = 0.35
        elif nearest_similarity >= 0.42:
            duplicate_penalty = 0.18

        originality_score = max(
            0.0,
            min(
                1.0,
                0.25
                + (detail_density * 0.25)
                + (motif_diversity * 0.35)
                + 0.15
                - duplicate_penalty,
            ),
        )

        duplicate_risk = self._overlap_tier(nearest_similarity)

        training_recommendation = "training_candidate_after_review"

        if duplicate_risk in {"near_duplicate", "high_overlap"}:
            training_recommendation = "block_training_until_deduplicated"
        elif originality_score < 0.65:
            training_recommendation = "revise_before_training"
        elif not saved_comparisons:
            training_recommendation = "needs_more_comparison_data"

        return {
            "candidate_label": candidate_label,
            "originality_score": round(originality_score, 3),
            "nearest_similarity": nearest_similarity,
            "duplicate_risk": duplicate_risk,
            "detail_density": round(detail_density, 3),
            "motif_diversity": round(motif_diversity, 3),
            "unique_signal_terms": unique_signal_terms,
            "nearest_saved_worlds": saved_comparisons,
            "training_recommendation": training_recommendation,
            "notes": [
                "Similarity is computed with deterministic weighted token vectors.",
                "This is not a replacement for real embeddings but gives Chunk 2 a useful deduplication layer.",
                "Near-duplicate or high-overlap worlds should not enter training data automatically.",
            ],
        }
