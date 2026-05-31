from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult
from backend.app.schemas.learning import (
    DatasetProvenanceRecord,
    EmbeddingMetadata,
    EngineLearningMetadata,
    LearnedOntologyRecord,
    LearnedTypeRegistryRecord,
    TrainingEligibility,
)


class CharacterQualityScorer(BaseEngine):
    """Scores final character quality across the whole character-intelligence layer.

    This is the gate before full orchestration, export, benchmark packs, and
    future training queues. It is intentionally multi-axis instead of relying on
    one vague "quality" score.
    """

    engine_name = "character.quality_scorer"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        consistency_report = payload.get("consistency_report") or character_seed.get("consistency_report", {})
        originality_report = payload.get("originality_report") or character_seed.get("originality_report", {})
        anti_genericity_report = payload.get("anti_genericity_report") or character_seed.get("anti_genericity_report", {})
        repair_plan = payload.get("repair_plan") or character_seed.get("repair_plan", {})

        origin_profile = payload.get("origin_profile") or character_seed.get("origin_profile", {})
        family_profile = payload.get("family_profile") or character_seed.get("family_profile", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        emotional_arc_profile = payload.get("emotional_arc_profile") or character_seed.get("emotional_arc_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        adaptability_profile = payload.get("adaptability_profile") or character_seed.get("adaptability_profile", {})
        limit_break_rules = payload.get("limit_break_rules") or character_seed.get("limit_break_rules", {})
        destiny_profile = payload.get("destiny_profile") or character_seed.get("destiny_profile", {})
        prophecy_model = payload.get("prophecy_model") or character_seed.get("prophecy_model", {})
        relationship_readiness_profile = payload.get("relationship_readiness_profile") or character_seed.get("relationship_readiness_profile", {})
        boundary_model = payload.get("boundary_model") or character_seed.get("relationship_boundary_model", {})
        dialogue_voice_profile = payload.get("dialogue_voice_profile") or character_seed.get("dialogue_voice_profile", {})
        speech_pattern_model = payload.get("speech_pattern_model") or character_seed.get("speech_pattern_model", {})
        forbidden_dialogue_patterns = payload.get("forbidden_dialogue_patterns") or character_seed.get("forbidden_dialogue_patterns", {})

        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; quality scorer used partial defaults.")

        character_id = (
            character_seed.get("character_id")
            or origin_profile.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or dialogue_voice_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        axis_scores = self._build_axis_scores(
            character_seed=character_seed,
            consistency_report=consistency_report,
            originality_report=originality_report,
            anti_genericity_report=anti_genericity_report,
            repair_plan=repair_plan,
            origin_profile=origin_profile,
            family_profile=family_profile,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            moral_profile=moral_profile,
            memory_records=memory_records,
            emotional_arc_profile=emotional_arc_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            relationship_readiness_profile=relationship_readiness_profile,
            boundary_model=boundary_model,
            dialogue_voice_profile=dialogue_voice_profile,
            speech_pattern_model=speech_pattern_model,
            forbidden_dialogue_patterns=forbidden_dialogue_patterns,
        )

        quality_report = self._build_quality_report(
            character_id=character_id,
            axis_scores=axis_scores,
            consistency_report=consistency_report,
            originality_report=originality_report,
            anti_genericity_report=anti_genericity_report,
            repair_plan=repair_plan,
        )

        readiness_report = self._build_readiness_report(
            quality_report=quality_report,
            axis_scores=axis_scores,
            repair_plan=repair_plan,
        )

        recommendation_report = self._build_recommendation_report(
            quality_report=quality_report,
            readiness_report=readiness_report,
            axis_scores=axis_scores,
            repair_plan=repair_plan,
        )

        diagnostics = self._build_diagnostics(
            quality_report=quality_report,
            readiness_report=readiness_report,
            recommendation_report=recommendation_report,
        )

        ontology_record = self._build_ontology_record(
            quality_report=quality_report,
            axis_scores=axis_scores,
            readiness_report=readiness_report,
            recommendation_report=recommendation_report,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_quality",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=quality_report["similarity_tags"],
            novelty_score=quality_report["novelty_score"],
            originality_score=axis_scores["originality"]["score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            quality_report=quality_report,
            readiness_report=readiness_report,
            diagnostics=diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=quality_report["quality_name"],
            type_family="character_quality",
            type_subfamily=quality_report["quality_tier"],
            type_scope="character_quality_control",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=quality_report["similarity_tags"],
            generation_constraints=recommendation_report["quality_constraints"],
            counter_patterns=recommendation_report["major_risks"],
            learned_axes={
                "axis_scores": axis_scores,
                "quality_report": quality_report,
                "readiness_report": readiness_report,
                "recommendation_report": recommendation_report,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_quality",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=quality_report["retrieval_context_queries"],
            generated_training_labels={
                "quality_tier": quality_report["quality_tier"],
                "overall_quality_score": quality_report["overall_quality_score"],
                "billion_dollar_franchise_potential_score": quality_report["franchise_potential_score"],
                "character_bible_ready": readiness_report["character_bible_ready"],
                "orchestrator_ready": readiness_report["orchestrator_ready"],
                "training_queue_ready": readiness_report["training_queue_ready"],
                "chunk4_relationship_ready": readiness_report["chunk4_relationship_ready"],
            },
            learning_notes=[
                "Quality scoring is a multi-axis gate before export/orchestration/training.",
                "Future learned quality models should train from human-rated characters, reviews, and benchmark outcomes.",
                "High quality requires consistency, originality, depth, agency, relationship hooks, and non-generic voice.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            quality_report=quality_report,
            axis_scores=axis_scores,
            readiness_report=readiness_report,
            recommendation_report=recommendation_report,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "character_quality_axis_scores": axis_scores,
                "quality_report": quality_report,
                "readiness_report": readiness_report,
                "quality_recommendation_report": recommendation_report,
                "quality_diagnostics": diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "quality_summary": {
                    "character_id": character_id,
                    "overall_quality_score": quality_report["overall_quality_score"],
                    "quality_tier": quality_report["quality_tier"],
                    "franchise_potential_score": quality_report["franchise_potential_score"],
                    "character_bible_ready": readiness_report["character_bible_ready"],
                    "orchestrator_ready": readiness_report["orchestrator_ready"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_full_profile_orchestrator": readiness_report["orchestrator_ready"],
                    "ready_for_character_bible_export": readiness_report["character_bible_ready"],
                    "ready_for_chunk8_training_later": readiness_report["training_queue_ready"],
                },
                "training_notes": [
                    "This score is not final model intelligence; it is the quality-control scaffold for later learned scoring.",
                    "Future Chunk 8 should learn weights from human ratings and downstream story-performance outcomes.",
                    "Profiles below export thresholds should be repaired before benchmark/export.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                quality_report["quality_report_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _build_axis_scores(self, **ctx: Any) -> Dict[str, Dict[str, Any]]:
        return {
            "consistency": self._score_consistency(ctx["consistency_report"]),
            "originality": self._score_originality(ctx["originality_report"], ctx["anti_genericity_report"]),
            "world_grounding": self._score_world_grounding(ctx["character_seed"], ctx["origin_profile"], ctx["character_type_ontology"]),
            "psychological_depth": self._score_psychological_depth(ctx["psychology_profile"], ctx["memory_records"], ctx["emotional_arc_profile"]),
            "goal_agency": self._score_goal_agency(ctx["goal_profile"], ctx["moral_profile"]),
            "skill_integrity": self._score_skill_integrity(ctx["skill_ontology"]),
            "adaptability_integrity": self._score_adaptability(ctx["adaptability_profile"], ctx["limit_break_rules"]),
            "destiny_agency": self._score_destiny(ctx["destiny_profile"], ctx["prophecy_model"]),
            "relationship_readiness": self._score_relationship(ctx["relationship_readiness_profile"], ctx["boundary_model"]),
            "dialogue_voice": self._score_dialogue(ctx["dialogue_voice_profile"], ctx["speech_pattern_model"], ctx["forbidden_dialogue_patterns"]),
            "repair_status": self._score_repair_status(ctx["repair_plan"]),
        }

    def _score_consistency(self, report: Dict[str, Any]) -> Dict[str, Any]:
        score = float(report.get("overall_consistency_score", 0.55))
        return self._axis("consistency", score, "cross-engine contradiction control", report.get("critical_issues", []))

    def _score_originality(self, report: Dict[str, Any], anti_generic: Dict[str, Any]) -> Dict[str, Any]:
        score = float(report.get("overall_originality_score", 0.55))
        genericity = float(anti_generic.get("genericity_risk_score", 0.0))
        adjusted = self._clamp(score - genericity * 0.15)
        return self._axis("originality", adjusted, "uncommon coherent character construction", anti_generic.get("genericity_risks", []))

    def _score_world_grounding(self, seed: Dict[str, Any], origin: Dict[str, Any], ctype: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.35
        if seed.get("social_class") or origin.get("social_class"):
            score += 0.18
        if seed.get("family_name_status") or origin.get("family_name_status"):
            score += 0.14
        if ctype.get("type_family"):
            score += 0.16
        if origin.get("education_access") is not None:
            score += 0.08
        return self._axis("world_grounding", self._clamp(score), "world/social origin grounding", [])

    def _score_psychological_depth(self, psychology: Dict[str, Any], memories: List[Dict[str, Any]], arc: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.25
        issues = []
        if psychology.get("core_wound"):
            score += 0.18
        else:
            issues.append("missing core wound")
        if psychology.get("betrayal_response") or psychology.get("love_response"):
            score += 0.12
        if memories:
            score += 0.16
        else:
            issues.append("missing memory anchors")
        if arc:
            score += 0.1
        return self._axis("psychological_depth", self._clamp(score), "wound, memory, emotion, healing", issues)

    def _score_goal_agency(self, goal: Dict[str, Any], moral: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.28
        issues = []
        if goal.get("true_need"):
            score += 0.18
        else:
            issues.append("missing true need")
        if goal.get("false_need"):
            score += 0.12
        if goal.get("hidden_goal") or goal.get("surface_goal"):
            score += 0.12
        if moral.get("forbidden_lines") or moral.get("dominant_moral_value"):
            score += 0.14
        return self._axis("goal_agency", self._clamp(score), "agency, needs, morality", issues)

    def _score_skill_integrity(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.25
        issues = []
        if skill.get("skill_family"):
            score += 0.16
        else:
            issues.append("missing skill ontology")
        if skill.get("cost_family"):
            score += 0.18
        else:
            issues.append("missing skill cost")
        if skill.get("counter_family"):
            score += 0.18
        else:
            issues.append("missing skill counterplay")
        if skill.get("growth_model") or skill.get("skill_subtype"):
            score += 0.08
        return self._axis("skill_integrity", self._clamp(score), "skill cost/counterplay/growth", issues)

    def _score_adaptability(self, adapt: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.35
        issues = []
        if adapt.get("adaptability_family"):
            score += 0.16
        if adapt.get("trigger_model"):
            score += 0.14
        else:
            issues.append("missing adaptation trigger")
        if adapt.get("cost_model"):
            score += 0.14
        else:
            issues.append("missing adaptation cost")
        if rules.get("hard_prohibitions"):
            score += 0.12
        else:
            issues.append("missing limit-break prohibitions")
        return self._axis("adaptability_integrity", self._clamp(score), "rule-breaking with conditions/cost", issues)

    def _score_destiny(self, destiny: Dict[str, Any], prophecy: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.3
        issues = []
        if destiny.get("destiny_family"):
            score += 0.14
        if destiny.get("destiny_burdens"):
            score += 0.16
        else:
            issues.append("missing destiny burden")
        if prophecy.get("prophecy_requires_choice") is True:
            score += 0.16
        else:
            issues.append("prophecy choice not confirmed")
        if destiny.get("destiny_is_absolute") is False:
            score += 0.08
        return self._axis("destiny_agency", self._clamp(score), "destiny without removing agency", issues)

    def _score_relationship(self, readiness: Dict[str, Any], boundary: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.28
        issues = []
        if readiness.get("relationship_readiness_family"):
            score += 0.16
        if readiness.get("attachment_pattern") or readiness.get("trust_model"):
            score += 0.16
        if readiness.get("intimacy_risk") is not None:
            score += 0.08
        if boundary.get("relationship_boundaries"):
            score += 0.18
        else:
            issues.append("missing relationship boundaries")
        return self._axis("relationship_readiness", self._clamp(score), "relationship hooks/boundaries", issues)

    def _score_dialogue(self, voice: Dict[str, Any], speech: Dict[str, Any], forbidden: Dict[str, Any]) -> Dict[str, Any]:
        score = 0.25
        issues = []
        if voice.get("voice_family"):
            score += 0.18
        else:
            issues.append("missing voice family")
        if speech.get("sentence_rhythm"):
            score += 0.14
        if speech.get("subtext_density"):
            score += 0.1
        if forbidden.get("generic_voice_failure_modes"):
            score += 0.14
        else:
            issues.append("missing forbidden generic voice patterns")
        return self._axis("dialogue_voice", self._clamp(score), "distinct dialogue voice", issues)

    def _score_repair_status(self, repair: Dict[str, Any]) -> Dict[str, Any]:
        requires = repair.get("requires_repair", False)
        count = repair.get("repair_count", 0)
        if not requires and count == 0:
            score = 0.95
            issues = []
        else:
            score = max(0.25, 0.75 - count * 0.08)
            issues = ["repair plan still has unresolved items"]
        return self._axis("repair_status", self._clamp(score), "remaining repair burden", issues)

    def _axis(self, axis: str, score: float, purpose: str, issues: List[str]) -> Dict[str, Any]:
        return {
            "axis": axis,
            "score": self._clamp(score),
            "purpose": purpose,
            "issues": issues,
            "passed": score >= 0.7,
        }

    def _build_quality_report(
        self,
        *,
        character_id: str,
        axis_scores: Dict[str, Dict[str, Any]],
        consistency_report: Dict[str, Any],
        originality_report: Dict[str, Any],
        anti_genericity_report: Dict[str, Any],
        repair_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        weights = {
            "consistency": 0.14,
            "originality": 0.13,
            "world_grounding": 0.08,
            "psychological_depth": 0.11,
            "goal_agency": 0.09,
            "skill_integrity": 0.09,
            "adaptability_integrity": 0.08,
            "destiny_agency": 0.08,
            "relationship_readiness": 0.08,
            "dialogue_voice": 0.08,
            "repair_status": 0.04,
        }

        overall = sum(axis_scores[key]["score"] * weight for key, weight in weights.items())
        overall = self._clamp(overall)

        franchise = self._franchise_potential(axis_scores, originality_report, anti_genericity_report)

        if overall >= 0.88 and franchise >= 0.82:
            tier = "elite_franchise_ready"
        elif overall >= 0.8:
            tier = "strong_character_ready"
        elif overall >= 0.68:
            tier = "good_but_needs_polish"
        elif overall >= 0.55:
            tier = "repair_needed"
        else:
            tier = "major_rebuild_needed"

        weak_axes = [axis for axis, item in axis_scores.items() if item["score"] < 0.7]
        strong_axes = [axis for axis, item in axis_scores.items() if item["score"] >= 0.82]

        return {
            "quality_report_id": f"qual_{uuid4().hex[:12]}",
            "character_id": character_id,
            "quality_name": f"character_quality:{tier}",
            "overall_quality_score": overall,
            "quality_tier": tier,
            "franchise_potential_score": franchise,
            "axis_weights": weights,
            "strong_axes": strong_axes,
            "weak_axes": weak_axes,
            "export_blockers": self._export_blockers(axis_scores, consistency_report, repair_plan),
            "training_blockers": self._training_blockers(axis_scores, consistency_report, originality_report),
            "quality_signature": self._quality_signature(axis_scores),
            "similarity_tags": [
                "character_quality",
                tier,
                f"quality_{round(overall, 2)}",
                f"franchise_{round(franchise, 2)}",
            ],
            "retrieval_context_queries": [
                f"character quality profile {tier}",
                "multi-axis character quality scoring",
                "franchise potential character depth originality consistency",
            ],
            "novelty_score": originality_report.get("novelty_score", 0.62),
        }

    def _franchise_potential(self, axis_scores: Dict[str, Dict[str, Any]], originality_report: Dict[str, Any], anti_genericity_report: Dict[str, Any]) -> float:
        score = 0.0
        score += axis_scores["originality"]["score"] * 0.18
        score += axis_scores["psychological_depth"]["score"] * 0.14
        score += axis_scores["goal_agency"]["score"] * 0.12
        score += axis_scores["relationship_readiness"]["score"] * 0.14
        score += axis_scores["dialogue_voice"]["score"] * 0.12
        score += axis_scores["destiny_agency"]["score"] * 0.1
        score += axis_scores["world_grounding"]["score"] * 0.1
        score += axis_scores["consistency"]["score"] * 0.1

        genericity = anti_genericity_report.get("genericity_risk_score", 0.0)
        score -= genericity * 0.08

        if originality_report.get("strong_originality_sources"):
            score += min(0.08, len(originality_report["strong_originality_sources"]) * 0.015)

        return self._clamp(score)

    def _export_blockers(self, axes: Dict[str, Dict[str, Any]], consistency: Dict[str, Any], repair: Dict[str, Any]) -> List[str]:
        blockers = []
        if consistency.get("critical_issue_count", 0) > 0:
            blockers.append("critical consistency issues")
        if consistency.get("violation_count", 0) > 0:
            blockers.append("consistency violations")
        if repair.get("requires_repair", False):
            blockers.append("unresolved repair plan")
        for axis in ["skill_integrity", "destiny_agency", "relationship_readiness", "dialogue_voice"]:
            if axes[axis]["score"] < 0.6:
                blockers.append(f"{axis} below export threshold")
        return blockers

    def _training_blockers(self, axes: Dict[str, Dict[str, Any]], consistency: Dict[str, Any], originality: Dict[str, Any]) -> List[str]:
        blockers = []
        if consistency.get("overall_consistency_score", 0.0) < 0.82:
            blockers.append("consistency below training threshold")
        if originality.get("overall_originality_score", 0.0) < 0.7:
            blockers.append("originality below training threshold")
        if axes["dialogue_voice"]["score"] < 0.7:
            blockers.append("dialogue voice below training threshold")
        if axes["relationship_readiness"]["score"] < 0.7:
            blockers.append("relationship readiness below training threshold")
        return blockers

    def _quality_signature(self, axes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        ordered = sorted(axes.values(), key=lambda item: item["score"], reverse=True)
        return {
            "top_strengths": [item["axis"] for item in ordered[:4]],
            "lowest_axes": [item["axis"] for item in ordered[-3:]],
            "average_axis_score": self._clamp(sum(item["score"] for item in axes.values()) / len(axes)),
        }

    def _build_readiness_report(self, *, quality_report: Dict[str, Any], axis_scores: Dict[str, Dict[str, Any]], repair_plan: Dict[str, Any]) -> Dict[str, Any]:
        no_export_blockers = not quality_report["export_blockers"]
        no_training_blockers = not quality_report["training_blockers"]

        return {
            "readiness_report_id": f"qready_{uuid4().hex[:12]}",
            "character_bible_ready": no_export_blockers and quality_report["overall_quality_score"] >= 0.78,
            "orchestrator_ready": quality_report["overall_quality_score"] >= 0.74 and not repair_plan.get("requires_repair", False),
            "benchmark_ready": quality_report["overall_quality_score"] >= 0.72,
            "chunk4_relationship_ready": axis_scores["relationship_readiness"]["score"] >= 0.7,
            "dialogue_simulation_ready": axis_scores["dialogue_voice"]["score"] >= 0.7,
            "training_queue_ready": no_training_blockers and quality_report["overall_quality_score"] >= 0.78,
            "human_review_recommended": quality_report["overall_quality_score"] < 0.85 or bool(quality_report["training_blockers"]),
        }

    def _build_recommendation_report(self, *, quality_report: Dict[str, Any], readiness_report: Dict[str, Any], axis_scores: Dict[str, Dict[str, Any]], repair_plan: Dict[str, Any]) -> Dict[str, Any]:
        weak_axes = quality_report["weak_axes"]
        major_risks = list(quality_report["export_blockers"]) + list(quality_report["training_blockers"])

        recommendations = []
        for axis in weak_axes:
            recommendations.append(f"improve {axis}: {axis_scores[axis]['purpose']}")

        if not recommendations:
            recommendations.append("preserve current structure; proceed to orchestrator/export")

        return {
            "recommendation_report_id": f"qrec_{uuid4().hex[:12]}",
            "major_risks": major_risks,
            "recommended_next_steps": recommendations,
            "quality_constraints": [
                "do not export with unresolved consistency violations",
                "do not train on profiles with unapproved provenance",
                "do not optimize originality by adding random traits",
                "preserve agency in destiny and relationships",
                "preserve cost/counterplay in skills and adaptability",
                "preserve distinct voice across relationship contexts",
            ],
            "upgrade_path": [
                "run full character orchestrator",
                "persist quality report",
                "export character bible if ready",
                "include in benchmark pack",
                "send high-quality approved records to Chunk 8 training queue later",
            ],
        }

    def _build_diagnostics(self, *, quality_report: Dict[str, Any], readiness_report: Dict[str, Any], recommendation_report: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "quality_scorer_completeness_score": 1.0,
            "has_axis_scores": True,
            "has_quality_report": True,
            "has_readiness_report": True,
            "has_recommendations": True,
            "ready_for_orchestrator": readiness_report["orchestrator_ready"],
            "ready_for_export": readiness_report["character_bible_ready"],
            "training_ready_schema": True,
        }

    def _build_ontology_record(self, *, quality_report: Dict[str, Any], axis_scores: Dict[str, Dict[str, Any]], readiness_report: Dict[str, Any], recommendation_report: Dict[str, Any]) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="character_quality",
            name=quality_report["quality_name"],
            family="character_quality",
            subtype=quality_report["quality_tier"],
            description=f"Overall quality score {quality_report['overall_quality_score']}",
            axes={
                "axis_scores": axis_scores,
                "quality_report": quality_report,
                "readiness_report": readiness_report,
                "recommendation_report": recommendation_report,
            },
            tags=quality_report["similarity_tags"],
            examples=[quality_report["quality_name"]],
            counterexamples=recommendation_report["major_risks"],
            confidence_score=quality_report["overall_quality_score"],
            novelty_score=quality_report["novelty_score"],
            quality_score=quality_report["overall_quality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(self, *, quality_report: Dict[str, Any], readiness_report: Dict[str, Any], diagnostics: Dict[str, Any], source_mode: str, user_rating: Any, provenance: DatasetProvenanceRecord) -> TrainingEligibility:
        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8
        eligible = (
            approved_source
            and provenance.usage_allowed
            and quality_report["overall_quality_score"] >= 0.78
            and readiness_report["training_queue_ready"]
            and high_rating
        )

        rejection_reasons = []
        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if quality_report["overall_quality_score"] < 0.78:
            rejection_reasons.append("overall quality below training threshold")
        if not readiness_report["training_queue_ready"]:
            rejection_reasons.append("training queue readiness failed")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=quality_report["overall_quality_score"],
            consistency_score=quality_report["overall_quality_score"],
            originality_score=quality_report["franchise_potential_score"],
            safety_score=0.88 if readiness_report["character_bible_ready"] else 0.72,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Quality scorer is the main training/export gate for character profiles.",
                "Future Chunk 8 should learn quality weights from human-rated benchmark results.",
            ],
        )

    def _build_next_engine_payload(self, *, character_seed: Dict[str, Any], quality_report: Dict[str, Any], axis_scores: Dict[str, Dict[str, Any]], readiness_report: Dict[str, Any], recommendation_report: Dict[str, Any], learning_metadata: EngineLearningMetadata) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["quality_report"] = quality_report
        merged_seed["character_quality_axis_scores"] = axis_scores
        merged_seed["readiness_report"] = readiness_report
        merged_seed["quality_recommendation_report"] = recommendation_report
        merged_seed["quality_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "full_profile_orchestrator_payload": {
                "character_seed": merged_seed,
                "quality_report": quality_report,
                "readiness_report": readiness_report,
            },
            "character_bible_export_payload": {
                "character_seed": merged_seed,
                "quality_report": quality_report,
                "readiness_report": readiness_report,
            },
            "benchmark_payload": {
                "character_id": quality_report["character_id"],
                "quality_report": quality_report,
                "axis_scores": axis_scores,
                "readiness_report": readiness_report,
            },
            "chunk8_training_payload_later": {
                "target_type": "character_quality",
                "quality_report": quality_report,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
