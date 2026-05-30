from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class DatasetMetadataEngine(BaseEngine):
    """Creates dataset tags and training-readiness metadata for world outputs.

    This engine does not train models.

    It prepares world outputs for future AI/ML work by producing:
    - dataset tags
    - genre tags
    - structure tags
    - complexity tags
    - risk tags
    - training eligibility flags
    - do-not-train flags
    - provenance fields
    - human review requirements
    - benchmark labels
    - future model-use notes

    This prevents MythOS from blindly learning from every generated output.
    """

    engine_name = "world.dataset_metadata_engine"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", payload)
        quality_summary = payload.get("quality_summary") or world_state.get("quality_summary", {})
        desired_complexity = payload.get("desired_complexity", "high")
        source_mode = payload.get("source_mode", "synthetic_engine_generated")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not world_state:
            warnings.append(
                "No world_state provided; metadata will be conservative and not training eligible."
            )

        metadata = self._build_metadata(
            world_state=world_state,
            quality_summary=quality_summary,
            desired_complexity=desired_complexity,
            source_mode=source_mode,
            user_rating=user_rating,
        )

        return self.build_result(
            success=True,
            data={
                "dataset_metadata": metadata,
                "training_notes": [
                    "This engine prepares generated worlds for future dataset curation.",
                    "It does not train, fine-tune, update weights, or modify the generator.",
                    "Training eligibility requires quality scores, provenance, human review, and low-risk flags.",
                    "Future Chunk 8 can use these fields for dataset versioning, model registry, and benchmark dashboards.",
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

    def _build_metadata(
        self,
        *,
        world_state: Dict[str, Any],
        quality_summary: Dict[str, Any],
        desired_complexity: str,
        source_mode: str,
        user_rating: Any,
    ) -> Dict[str, Any]:
        text = self._flatten_text(world_state).lower()

        genre_tags = self._detect_genre_tags(text)
        structure_tags = self._detect_structure_tags(world_state, text)
        complexity_tags = self._detect_complexity_tags(world_state, text, desired_complexity)
        content_tags = self._detect_content_tags(text)
        risk_tags = self._detect_risk_tags(text, quality_summary)
        benchmark_labels = self._build_benchmark_labels(
            genre_tags=genre_tags,
            structure_tags=structure_tags,
            complexity_tags=complexity_tags,
            content_tags=content_tags,
        )

        consistency_score = float(quality_summary.get("consistency_score", 0.0) or 0.0)
        originality_score = float(quality_summary.get("originality_score", 0.0) or 0.0)
        story_potential_score = float(quality_summary.get("story_potential_score", 0.0) or 0.0)
        training_readiness_score = float(quality_summary.get("training_readiness_score", 0.0) or 0.0)
        genericness_risk_score = float(quality_summary.get("genericness_risk_score", 1.0) or 1.0)

        human_review_required = self._requires_human_review(
            risk_tags=risk_tags,
            consistency_score=consistency_score,
            originality_score=originality_score,
            training_readiness_score=training_readiness_score,
            user_rating=user_rating,
        )

        training_eligible = (
            not human_review_required
            and training_readiness_score >= 0.78
            and consistency_score >= 0.72
            and originality_score >= 0.68
            and story_potential_score >= 0.7
            and genericness_risk_score <= 0.45
            and "do_not_train" not in risk_tags
            and source_mode in {"synthetic_engine_generated", "human_approved_synthetic"}
        )

        do_not_train = (
            "do_not_train" in risk_tags
            or "unclear_provenance" in risk_tags
            or "low_quality" in risk_tags
            or "needs_major_revision" in risk_tags
        )

        recommended_dataset_split = "holdout_review"

        if training_eligible and user_rating is not None and user_rating >= 8:
            recommended_dataset_split = "train_candidate"
        elif training_eligible:
            recommended_dataset_split = "validation_candidate"
        elif human_review_required:
            recommended_dataset_split = "human_review_queue"

        metadata = {
            "metadata_version": "world-dataset-metadata-v0.1",
            "source_mode": source_mode,
            "generation_method": "deterministic_chunk2_engine_pipeline",
            "model_version": "none_yet_rule_based",
            "future_model_use": "eligible_for_future_ranking_or_generation_training_only_after_review",
            "dataset_tags": sorted(
                set(genre_tags + structure_tags + complexity_tags + content_tags)
            ),
            "genre_tags": genre_tags,
            "structure_tags": structure_tags,
            "complexity_tags": complexity_tags,
            "content_tags": content_tags,
            "risk_tags": risk_tags,
            "benchmark_labels": benchmark_labels,
            "quality_snapshot": {
                "consistency_score": consistency_score,
                "originality_score": originality_score,
                "story_potential_score": story_potential_score,
                "training_readiness_score": training_readiness_score,
                "genericness_risk_score": genericness_risk_score,
            },
            "human_review_required": human_review_required,
            "training_eligible": training_eligible,
            "do_not_train": do_not_train,
            "recommended_dataset_split": recommended_dataset_split,
            "user_rating": user_rating,
            "curation_notes": self._build_curation_notes(
                training_eligible=training_eligible,
                human_review_required=human_review_required,
                do_not_train=do_not_train,
                risk_tags=risk_tags,
                genre_tags=genre_tags,
                structure_tags=structure_tags,
            ),
            "audit_recommendations": [
                "Store original input prompt with generated world snapshot.",
                "Store quality report before any training decision.",
                "Store human approval before train_candidate promotion.",
                "Store source/provenance and model version when ML generation begins.",
            ],
        }

        return metadata

    def _detect_genre_tags(self, text: str) -> List[str]:
        tags = []

        checks = {
            "dark_academy": ["academy", "exam", "student", "sponsor", "forbidden book"],
            "political_fantasy": ["court", "noble", "empire", "succession", "house"],
            "mythic_fantasy": ["oath", "god", "ritual", "prophecy", "sacred"],
            "civilization_simulation": ["civilization", "resource", "collapse", "causality", "pressure"],
            "dystopian_institutional": ["surveillance", "classification", "permit", "censorship"],
            "mystery_intrigue": ["archive", "erased", "hidden", "secret", "witness"],
            "romance_pressure": ["marriage", "reputation", "forbidden romance", "class"],
        }

        for tag, terms in checks.items():
            if any(term in text for term in terms):
                tags.append(tag)

        return tags

    def _detect_structure_tags(self, world_state: Dict[str, Any], text: str) -> List[str]:
        tags = []

        if "causality_graph" in world_state:
            tags.append("causal_graph_available")

        if "quality_summary" in world_state or "quality_tier" in text:
            tags.append("quality_scored")

        if "artifacts" in world_state:
            tags.append("artifact_system_available")

        if "institutions" in world_state:
            tags.append("institution_system_available")

        if "factions" in text or "power_structure" in world_state:
            tags.append("faction_ready")

        if "training_notes" in text:
            tags.append("training_notes_present")

        if "world_state" in world_state:
            tags.append("nested_world_state_payload")

        return tags

    def _detect_complexity_tags(
        self,
        world_state: Dict[str, Any],
        text: str,
        desired_complexity: str,
    ) -> List[str]:
        tags = [f"desired_complexity_{desired_complexity}"]

        word_count = len(text.split())

        if word_count >= 5000:
            tags.append("very_high_detail_density")
        elif word_count >= 2000:
            tags.append("high_detail_density")
        elif word_count >= 800:
            tags.append("medium_detail_density")
        else:
            tags.append("low_detail_density")

        system_count = sum(
            1
            for value in world_state.values()
            if value not in (None, {}, [], "")
        )

        if system_count >= 20:
            tags.append("large_world_system_coverage")
        elif system_count >= 10:
            tags.append("medium_world_system_coverage")
        else:
            tags.append("low_world_system_coverage")

        if "causality" in text and "pressure" in text and "training" in text:
            tags.append("research_grade_structure_candidate")

        return tags

    def _detect_content_tags(self, text: str) -> List[str]:
        tags = []

        content_checks = {
            "has_class_system": ["class", "rank", "noble", "commoner"],
            "has_legal_system": ["law", "court", "legal", "trial"],
            "has_economy_system": ["debt", "tax", "resource", "funding"],
            "has_belief_system": ["god", "oath", "ritual", "heresy", "prophecy"],
            "has_knowledge_control": ["archive", "censorship", "forbidden", "education"],
            "has_symbolic_objects": ["artifact", "relic", "crown", "bell", "seal"],
            "has_world_pressure": ["collapse", "pressure", "crisis", "breaking point"],
            "has_future_ml_hooks": ["training", "metadata", "benchmark", "model"],
        }

        for tag, terms in content_checks.items():
            if any(term in text for term in terms):
                tags.append(tag)

        return tags

    def _detect_risk_tags(
        self,
        text: str,
        quality_summary: Dict[str, Any],
    ) -> List[str]:
        tags = []

        consistency_score = float(quality_summary.get("consistency_score", 0.0) or 0.0)
        originality_score = float(quality_summary.get("originality_score", 0.0) or 0.0)
        training_readiness_score = float(quality_summary.get("training_readiness_score", 0.0) or 0.0)
        genericness_risk_score = float(quality_summary.get("genericness_risk_score", 1.0) or 1.0)

        if consistency_score < 0.55:
            tags.append("low_consistency")

        if originality_score < 0.55:
            tags.append("low_originality")

        if training_readiness_score < 0.55:
            tags.append("low_training_readiness")

        if genericness_risk_score > 0.65:
            tags.append("high_genericness_risk")

        if consistency_score < 0.45 or training_readiness_score < 0.45:
            tags.append("low_quality")

        if "copyrighted" in text or "fanfiction" in text or "directly based on" in text:
            tags.append("unclear_provenance")
            tags.append("do_not_train")

        if "generate from harry potter" in text or "like game of thrones exactly" in text:
            tags.append("unsafe_similarity_prompt")
            tags.append("do_not_train")

        if (
            len(text.split()) < 200
            and (
                consistency_score < 0.72
                or originality_score < 0.68
                or training_readiness_score < 0.78
            )
        ):
            tags.append("needs_major_revision")

        return tags

    def _requires_human_review(
        self,
        *,
        risk_tags: List[str],
        consistency_score: float,
        originality_score: float,
        training_readiness_score: float,
        user_rating: Any,
    ) -> bool:
        if "do_not_train" in risk_tags:
            return True

        if "unclear_provenance" in risk_tags:
            return True

        if consistency_score < 0.72:
            return True

        if originality_score < 0.68:
            return True

        if training_readiness_score < 0.78:
            return True

        if user_rating is None:
            return True

        if user_rating < 8:
            return True

        return False

    def _build_benchmark_labels(
        self,
        *,
        genre_tags: List[str],
        structure_tags: List[str],
        complexity_tags: List[str],
        content_tags: List[str],
    ) -> List[str]:
        labels = []

        if "dark_academy" in genre_tags and "political_fantasy" in genre_tags:
            labels.append("benchmark_dark_academy_political_empire")

        if "civilization_simulation" in genre_tags:
            labels.append("benchmark_civilization_pressure_world")

        if "mystery_intrigue" in genre_tags and "has_knowledge_control" in content_tags:
            labels.append("benchmark_archive_mystery_world")

        if "artifact_system_available" in structure_tags and "has_symbolic_objects" in content_tags:
            labels.append("benchmark_artifact_driven_world")

        if "research_grade_structure_candidate" in complexity_tags:
            labels.append("benchmark_research_grade_world_system")

        if not labels:
            labels.append("benchmark_general_world")

        return labels

    def _build_curation_notes(
        self,
        *,
        training_eligible: bool,
        human_review_required: bool,
        do_not_train: bool,
        risk_tags: List[str],
        genre_tags: List[str],
        structure_tags: List[str],
    ) -> List[str]:
        notes = []

        if training_eligible:
            notes.append("World can be considered for curated future training datasets after storage and audit.")
        else:
            notes.append("World should not enter training data yet.")

        if human_review_required:
            notes.append("Human review required before promotion to train_candidate.")

        if do_not_train:
            notes.append("Do not train on this sample unless risk tags are resolved and provenance is verified.")

        if "quality_scored" not in structure_tags:
            notes.append("Run WorldQualityEngine before final dataset decision.")

        if not genre_tags:
            notes.append("Genre tags are weak; add clearer world identity or template metadata.")

        if risk_tags:
            notes.append("Resolve risk tags: " + ", ".join(risk_tags))

        return notes
