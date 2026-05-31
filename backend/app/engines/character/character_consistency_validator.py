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


class CharacterConsistencyValidator(BaseEngine):
    """Validates cross-engine character consistency.

    This validator prevents the character layer from becoming a pile of
    impressive but contradictory outputs.

    It checks:
    - identity consistency
    - world constraint consistency
    - origin/social-class consistency
    - family consistency
    - psychology/goal consistency
    - morality consistency
    - skill/power consistency
    - adaptability consistency
    - destiny/agency consistency
    - relationship readiness consistency
    - dialogue voice consistency
    - memory/emotional continuity
    """

    engine_name = "character.consistency_validator"

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        character_seed = payload.get("character_seed", {})
        world_state = payload.get("world_state", {})
        world_constraints = payload.get("world_constraints", {})
        origin_profile = payload.get("origin_profile") or character_seed.get("origin_profile", {})
        family_profile = payload.get("family_profile") or character_seed.get("family_profile", {})
        psychology_profile = payload.get("psychology_profile") or character_seed.get("psychology", {})
        goal_profile = payload.get("goal_profile") or character_seed.get("goal_profile", {})
        moral_profile = payload.get("moral_profile") or character_seed.get("moral_profile", {})
        memory_records = payload.get("memory_records") or character_seed.get("memories", [])
        emotional_arc_profile = payload.get("emotional_arc_profile") or character_seed.get("emotional_arc_profile", {})
        skill_profile = payload.get("skill_profile") or character_seed.get("skill_profile", {})
        skill_ontology = payload.get("skill_ontology") or character_seed.get("skill_ontology", {})
        character_type_ontology = payload.get("character_type_ontology") or character_seed.get("character_type_ontology", {})
        adaptability_profile = payload.get("adaptability_profile") or character_seed.get("adaptability_profile", {})
        limit_break_rules = payload.get("limit_break_rules") or character_seed.get("limit_break_rules", {})
        destiny_profile = payload.get("destiny_profile") or character_seed.get("destiny_profile", {})
        prophecy_model = payload.get("prophecy_model") or character_seed.get("prophecy_model", {})
        legacy_model = payload.get("legacy_model") or character_seed.get("legacy_model", {})
        relationship_readiness_profile = payload.get("relationship_readiness_profile") or character_seed.get("relationship_readiness_profile", {})
        boundary_model = payload.get("boundary_model") or character_seed.get("relationship_boundary_model", {})
        dialogue_voice_profile = payload.get("dialogue_voice_profile") or character_seed.get("dialogue_voice_profile", {})
        speech_pattern_model = payload.get("speech_pattern_model") or character_seed.get("speech_pattern_model", {})
        forbidden_dialogue_patterns = payload.get("forbidden_dialogue_patterns") or character_seed.get("forbidden_dialogue_patterns", {})
        source_mode = payload.get("source_mode", "human_approved_synthetic")
        user_rating = payload.get("user_rating")

        warnings: List[str] = []

        if not character_seed:
            warnings.append("No character_seed provided; validator used partial profile defaults.")

        character_id = (
            character_seed.get("character_id")
            or origin_profile.get("character_id")
            or psychology_profile.get("character_id")
            or goal_profile.get("character_id")
            or dialogue_voice_profile.get("character_id")
            or f"char_{uuid4().hex[:12]}"
        )

        validation_checks = self._run_validation_checks(
            character_id=character_id,
            character_seed=character_seed,
            world_state=world_state,
            world_constraints=world_constraints,
            origin_profile=origin_profile,
            family_profile=family_profile,
            psychology_profile=psychology_profile,
            goal_profile=goal_profile,
            moral_profile=moral_profile,
            memory_records=memory_records,
            emotional_arc_profile=emotional_arc_profile,
            skill_profile=skill_profile,
            skill_ontology=skill_ontology,
            character_type_ontology=character_type_ontology,
            adaptability_profile=adaptability_profile,
            limit_break_rules=limit_break_rules,
            destiny_profile=destiny_profile,
            prophecy_model=prophecy_model,
            legacy_model=legacy_model,
            relationship_readiness_profile=relationship_readiness_profile,
            boundary_model=boundary_model,
            dialogue_voice_profile=dialogue_voice_profile,
            speech_pattern_model=speech_pattern_model,
            forbidden_dialogue_patterns=forbidden_dialogue_patterns,
        )

        consistency_report = self._build_consistency_report(
            character_id=character_id,
            validation_checks=validation_checks,
        )

        repair_plan = self._build_repair_plan(validation_checks=validation_checks)

        validator_diagnostics = self._build_diagnostics(
            validation_checks=validation_checks,
            consistency_report=consistency_report,
            repair_plan=repair_plan,
        )

        ontology_record = self._build_ontology_record(
            consistency_report=consistency_report,
            validation_checks=validation_checks,
            repair_plan=repair_plan,
        )

        provenance = DatasetProvenanceRecord(
            source_name=source_mode,
            source_type="synthetic_or_user_generated",
            dataset_family="character_consistency_validation",
            usage_allowed=source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            human_review_required=source_mode not in {"human_approved_synthetic", "user_owned", "licensed_dataset"},
            genre_tags=character_seed.get("genre_tags", []),
            culture_tags=character_seed.get("culture_tags", []),
        )

        embedding_metadata = EmbeddingMetadata(
            embedding_model="future_embedding_model_not_computed_yet",
            similarity_tags=consistency_report["similarity_tags"],
            novelty_score=consistency_report["novelty_score"],
            originality_score=consistency_report["originality_score"],
            similarity_threshold_used=0.82,
        )

        training_eligibility = self._training_eligibility(
            consistency_report=consistency_report,
            validator_diagnostics=validator_diagnostics,
            source_mode=source_mode,
            user_rating=user_rating,
            provenance=provenance,
        )

        learned_type_candidate = LearnedTypeRegistryRecord(
            type_name=consistency_report["validator_name"],
            type_family="character_validation",
            type_subfamily=consistency_report["consistency_tier"],
            type_scope="character_quality_control",
            ontology_ids=[ontology_record.ontology_id],
            embedding_metadata=embedding_metadata,
            provenance_records=[provenance],
            training_eligibility=training_eligibility,
            reusable_prompt_tags=consistency_report["similarity_tags"],
            generation_constraints=repair_plan["global_repair_constraints"],
            counter_patterns=consistency_report["critical_issues"],
            learned_axes={
                "consistency_report": consistency_report,
                "validation_checks": validation_checks,
                "repair_plan": repair_plan,
                "validator_diagnostics": validator_diagnostics,
            },
        )

        learning_metadata = EngineLearningMetadata(
            engine_name=self.engine_name,
            target_object_id=character_id,
            target_object_type="character_consistency_validation",
            ontology_records=[ontology_record],
            learned_type_candidates=[learned_type_candidate],
            provenance_records=[provenance],
            embedding_metadata=embedding_metadata,
            training_eligibility=training_eligibility,
            retrieval_context_used=consistency_report["retrieval_context_queries"],
            generated_training_labels={
                "consistency_tier": consistency_report["consistency_tier"],
                "overall_consistency_score": consistency_report["overall_consistency_score"],
                "critical_issue_count": consistency_report["critical_issue_count"],
                "warning_count": consistency_report["warning_count"],
                "character_bible_ready": validator_diagnostics["character_bible_ready"],
                "orchestrator_ready": validator_diagnostics["orchestrator_ready"],
                "training_ready_schema": validator_diagnostics["training_ready_schema"],
            },
            learning_notes=[
                "Consistency validation is required before character export, benchmarking, or training queues.",
                "Future training should prefer profiles that pass cross-engine consistency checks.",
                "Repair plans should feed back into generation/orchestration before final export.",
            ],
        )

        next_engine_payload = self._build_next_engine_payload(
            character_seed=character_seed,
            consistency_report=consistency_report,
            validation_checks=validation_checks,
            repair_plan=repair_plan,
            learning_metadata=learning_metadata,
        )

        return self.build_result(
            success=True,
            data={
                "consistency_report": consistency_report,
                "validation_checks": validation_checks,
                "repair_plan": repair_plan,
                "validator_diagnostics": validator_diagnostics,
                "ontology_record": ontology_record.model_dump(),
                "learned_type_candidate": learned_type_candidate.model_dump(),
                "learning_metadata": learning_metadata.model_dump(),
                "next_engine_payload": next_engine_payload,
                "consistency_summary": {
                    "character_id": character_id,
                    "overall_consistency_score": consistency_report["overall_consistency_score"],
                    "consistency_tier": consistency_report["consistency_tier"],
                    "critical_issue_count": consistency_report["critical_issue_count"],
                    "warning_count": consistency_report["warning_count"],
                    "character_bible_ready": validator_diagnostics["character_bible_ready"],
                    "orchestrator_ready": validator_diagnostics["orchestrator_ready"],
                    "training_eligible": training_eligibility.training_eligible,
                    "ready_for_originality_engine": True,
                    "ready_for_quality_scorer": True,
                    "ready_for_character_bible_export": validator_diagnostics["character_bible_ready"],
                },
                "training_notes": [
                    "Only consistent profiles should become high-confidence training examples.",
                    "Contradictions should become repair instructions, not ignored.",
                    "Validator outputs are part of the research-grade quality-control layer.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[
                consistency_report["consistency_report_id"],
                ontology_record.ontology_id,
                learned_type_candidate.registry_id,
                learning_metadata.learning_metadata_id,
            ],
        )

    def _run_validation_checks(self, **kwargs: Any) -> List[Dict[str, Any]]:
        checks = [
            self._identity_check(kwargs),
            self._world_origin_check(kwargs),
            self._family_origin_check(kwargs),
            self._psychology_goal_check(kwargs),
            self._morality_goal_check(kwargs),
            self._memory_psychology_check(kwargs),
            self._skill_limit_check(kwargs),
            self._adaptability_check(kwargs),
            self._destiny_agency_check(kwargs),
            self._relationship_boundary_check(kwargs),
            self._dialogue_voice_check(kwargs),
            self._training_metadata_check(kwargs),
        ]
        return checks

    def _identity_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        character_id = ctx["character_id"]
        seed = ctx["character_seed"]

        status = "pass"
        severity = "none"
        issues = []
        fixes = []

        if not character_id:
            status = "violation"
            severity = "critical"
            issues.append("missing character_id")
            fixes.append("assign a stable character_id before persistence or export")

        if not seed.get("name") and not seed.get("character_name"):
            status = "warning" if status == "pass" else status
            severity = "medium" if severity == "none" else severity
            issues.append("missing character name")
            fixes.append("add a stable character name or generated placeholder")

        return self._check("identity_consistency", status, severity, issues, fixes)

    def _world_origin_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        seed = ctx["character_seed"]
        origin = ctx["origin_profile"]
        world_constraints = ctx["world_constraints"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        social_class = seed.get("social_class") or origin.get("social_class")
        education_access = origin.get("education_access")

        if social_class in {"erased", "underclass"} and education_access is not None and education_access > 0.75:
            status = "violation"
            severity = "high"
            issues.append("low-status character has high education access without access route")
            fixes.append("add sponsor, forged identity, patron, scholarship, illegal tutor, or explicit exception")

        if world_constraints.get("commoner_royal_magic_restricted") and "royal" in str(seed).lower():
            if social_class not in {"old_nobility", "imperial_elite", "royal"}:
                status = "violation"
                severity = "high"
                issues.append("restricted royal power conflicts with social class")
                fixes.append("add legal exception, hidden lineage, illegal access, or remove restricted power")

        return self._check("world_origin_consistency", status, severity, issues, fixes)

    def _family_origin_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        seed = ctx["character_seed"]
        origin = ctx["origin_profile"]
        family = ctx["family_profile"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        seed_status = seed.get("family_name_status")
        origin_status = origin.get("family_name_status")
        family_status = family.get("family_name_status") or family.get("name_status")

        statuses = {item for item in [seed_status, origin_status, family_status] if item}

        if len(statuses) >= 2:
            status = "warning"
            severity = "medium"
            issues.append(f"family name status varies across engines: {sorted(statuses)}")
            fixes.append("normalize family_name_status or explain status change by time/context")

        return self._check("family_origin_consistency", status, severity, issues, fixes)

    def _psychology_goal_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        psychology = ctx["psychology_profile"]
        goal = ctx["goal_profile"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        core_wound = str(psychology.get("core_wound", "")).lower()
        false_need = str(goal.get("false_need", "")).lower()
        true_need = str(goal.get("true_need", "")).lower()

        if psychology and goal:
            if core_wound and false_need and not self._shares_theme(core_wound, false_need):
                status = "warning"
                severity = "medium"
                issues.append("core wound and false need may not be thematically connected")
                fixes.append("align false_need with core wound or add bridging memory")

            if true_need and false_need and true_need == false_need:
                status = "violation"
                severity = "high"
                issues.append("true_need and false_need are identical")
                fixes.append("separate what character wants from what character actually needs")

        return self._check("psychology_goal_consistency", status, severity, issues, fixes)

    def _morality_goal_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        moral = ctx["moral_profile"]
        goal = ctx["goal_profile"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        forbidden_lines = [str(line).lower() for line in moral.get("forbidden_lines", [])]
        surface_goal = str(goal.get("surface_goal", "")).lower()
        hidden_goal = str(goal.get("hidden_goal", "")).lower()

        for line in forbidden_lines:
            if line and (line in surface_goal or line in hidden_goal):
                status = "violation"
                severity = "high"
                issues.append("goal appears to directly violate forbidden moral line")
                fixes.append("make this an intentional moral dilemma or revise goal")

        if moral.get("corruption_risk", 0.0) >= 0.7 and not goal.get("corruption_test"):
            status = "warning" if status == "pass" else status
            severity = "medium" if severity == "none" else severity
            issues.append("high corruption risk lacks explicit corruption test")
            fixes.append("add corruption_test or moral turning point")

        return self._check("morality_goal_consistency", status, severity, issues, fixes)

    def _memory_psychology_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        psychology = ctx["psychology_profile"]
        memories = ctx["memory_records"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if psychology.get("core_wound") and not memories:
            status = "warning"
            severity = "medium"
            issues.append("core wound exists without supporting memory record")
            fixes.append("add at least one memory record explaining the wound")

        memory_text = str(memories).lower()
        if "family secret" in str(psychology).lower() and "secret" not in memory_text:
            status = "warning"
            severity = "medium"
            issues.append("family-secret psychology lacks memory anchor")
            fixes.append("add family secret memory or remove secret-based response")

        return self._check("memory_psychology_consistency", status, severity, issues, fixes)

    def _skill_limit_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        skill = ctx["skill_profile"]
        skill_ontology = ctx["skill_ontology"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        skill_name = skill.get("primary_skill") or skill_ontology.get("skill_name")

        if skill_name and not skill_ontology:
            status = "warning"
            severity = "medium"
            issues.append("skill exists without skill ontology")
            fixes.append("run SkillOntologyEngine before validator")

        if skill_ontology:
            costs = skill_ontology.get("cost_family", [])
            counters = skill_ontology.get("counter_family", [])
            if not costs:
                status = "violation"
                severity = "high"
                issues.append("skill ontology has no cost family")
                fixes.append("add cost family before using skill in major plot resolution")
            if not counters:
                status = "violation"
                severity = "high"
                issues.append("skill ontology has no counter family")
                fixes.append("add counterplay before export/training")

        return self._check("skill_limit_consistency", status, severity, issues, fixes)

    def _adaptability_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        adaptability = ctx["adaptability_profile"]
        rules = ctx["limit_break_rules"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if adaptability:
            if not adaptability.get("trigger_model"):
                status = "violation"
                severity = "high"
                issues.append("adaptability lacks trigger model")
                fixes.append("add trigger_model before allowing adaptation")

            if not adaptability.get("cost_model"):
                status = "violation"
                severity = "high"
                issues.append("adaptability lacks cost model")
                fixes.append("add cost_model before allowing limit-break")

        if rules.get("limit_break_allowed") and not rules.get("hard_prohibitions"):
            status = "violation"
            severity = "high"
            issues.append("limit-break allowed without hard prohibitions")
            fixes.append("add hard_prohibitions so power is not unlimited")

        return self._check("adaptability_consistency", status, severity, issues, fixes)

    def _destiny_agency_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        destiny = ctx["destiny_profile"]
        prophecy = ctx["prophecy_model"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if destiny:
            if destiny.get("destiny_is_absolute") is True and not destiny.get("agency_exception"):
                status = "warning"
                severity = "medium"
                issues.append("absolute destiny lacks agency exception")
                fixes.append("add agency_exception, refusal path, or reinterpretation path")

            if not destiny.get("destiny_burdens"):
                status = "warning"
                severity = "medium"
                issues.append("destiny lacks burden")
                fixes.append("add destiny burden so it is not generic chosen-one power")

        if prophecy:
            if prophecy.get("prophecy_requires_choice") is False:
                status = "violation"
                severity = "high"
                issues.append("prophecy removes choice")
                fixes.append("make prophecy pressure-based or add multiple valid interpretations")

        return self._check("destiny_agency_consistency", status, severity, issues, fixes)

    def _relationship_boundary_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        readiness = ctx["relationship_readiness_profile"]
        boundary = ctx["boundary_model"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if readiness and not boundary:
            status = "warning"
            severity = "medium"
            issues.append("relationship readiness exists without boundary model")
            fixes.append("run RelationshipReadinessEngine with boundary output")

        if boundary:
            boundaries = boundary.get("relationship_boundaries", [])
            if not boundaries:
                status = "violation"
                severity = "high"
                issues.append("relationship boundary model has no boundaries")
                fixes.append("add agency, consent, betrayal, and repair boundaries")

            if "destiny cannot force love, loyalty, or forgiveness" not in boundaries and ctx["destiny_profile"]:
                status = "warning" if status == "pass" else status
                severity = "medium" if severity == "none" else severity
                issues.append("destiny relationship boundary missing")
                fixes.append("add boundary: destiny cannot force love, loyalty, or forgiveness")

        return self._check("relationship_boundary_consistency", status, severity, issues, fixes)

    def _dialogue_voice_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        voice = ctx["dialogue_voice_profile"]
        speech = ctx["speech_pattern_model"]
        forbidden = ctx["forbidden_dialogue_patterns"]

        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if voice:
            if not speech:
                status = "warning"
                severity = "medium"
                issues.append("dialogue voice lacks speech pattern model")
                fixes.append("run DialogueVoiceEngine speech model output")

            if not forbidden:
                status = "warning"
                severity = "medium"
                issues.append("dialogue voice lacks forbidden generic patterns")
                fixes.append("add forbidden_dialogue_patterns to prevent generic voice")

        if speech:
            if not speech.get("sentence_rhythm") or not speech.get("subtext_density"):
                status = "violation"
                severity = "high"
                issues.append("speech pattern lacks rhythm or subtext density")
                fixes.append("add sentence_rhythm and subtext_density")

        return self._check("dialogue_voice_consistency", status, severity, issues, fixes)

    def _training_metadata_check(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # This check is intentionally light for now; full global learning integration
        # will be upgraded after Chunk 3 in the approved Chunk 1-3 upgrade pass.
        issues = []
        fixes = []
        status = "pass"
        severity = "none"

        if not ctx["skill_ontology"] and not ctx["character_type_ontology"]:
            status = "warning"
            severity = "low"
            issues.append("profile has little ontology metadata")
            fixes.append("run ontology engines before training/export readiness")

        return self._check("training_metadata_readiness", status, severity, issues, fixes)

    def _check(self, check_id: str, status: str, severity: str, issues: List[str], fixes: List[str]) -> Dict[str, Any]:
        return {
            "check_id": check_id,
            "status": status,
            "severity": severity,
            "issues": issues,
            "recommended_fixes": fixes,
            "passed": status == "pass",
        }

    def _build_consistency_report(self, *, character_id: str, validation_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        critical = [check for check in validation_checks if check["severity"] == "critical"]
        violations = [check for check in validation_checks if check["status"] == "violation"]
        warnings = [check for check in validation_checks if check["status"] == "warning"]
        passes = [check for check in validation_checks if check["status"] == "pass"]

        score = max(
            0.0,
            1.0
            - len(critical) * 0.25
            - len(violations) * 0.12
            - len(warnings) * 0.04
        )

        score = self._clamp(score)

        if score >= 0.9 and not violations:
            tier = "excellent_consistency"
        elif score >= 0.78:
            tier = "strong_consistency"
        elif score >= 0.62:
            tier = "repair_needed"
        else:
            tier = "major_revision_needed"

        all_issues = []
        for check in validation_checks:
            all_issues.extend(check["issues"])

        similarity_tags = [
            "character_consistency",
            tier,
            f"violations_{len(violations)}",
            f"warnings_{len(warnings)}",
        ]

        return {
            "consistency_report_id": f"consistency_{uuid4().hex[:12]}",
            "character_id": character_id,
            "validator_name": f"character_consistency:{tier}",
            "overall_consistency_score": score,
            "consistency_tier": tier,
            "pass_count": len(passes),
            "warning_count": len(warnings),
            "violation_count": len(violations),
            "critical_issue_count": len(critical),
            "critical_issues": [issue for check in critical + violations for issue in check["issues"]],
            "warning_issues": [issue for check in warnings for issue in check["issues"]],
            "passed_checks": [check["check_id"] for check in passes],
            "failed_checks": [check["check_id"] for check in validation_checks if check["status"] != "pass"],
            "similarity_tags": similarity_tags,
            "retrieval_context_queries": [
                f"character consistency profile {tier}",
                "cross-engine character contradiction validation",
                "character repair plan world psychology skill destiny dialogue",
            ],
            "novelty_score": 0.54,
            "originality_score": 0.82 if score >= 0.9 and not violations else (0.74 if score >= 0.78 else 0.48),
            "confidence_score": 0.86 if score >= 0.9 and not violations else (0.78 if score >= 0.78 else 0.62),
        }

    def _build_repair_plan(self, *, validation_checks: List[Dict[str, Any]]) -> Dict[str, Any]:
        ordered_repairs = []

        priority = {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}

        failing = [check for check in validation_checks if check["status"] != "pass"]
        failing.sort(key=lambda item: priority.get(item["severity"], 4))

        for check in failing:
            ordered_repairs.append(
                {
                    "check_id": check["check_id"],
                    "severity": check["severity"],
                    "issues": check["issues"],
                    "recommended_fixes": check["recommended_fixes"],
                }
            )

        return {
            "repair_plan_id": f"repair_{uuid4().hex[:12]}",
            "requires_repair": bool(ordered_repairs),
            "repair_count": len(ordered_repairs),
            "ordered_repairs": ordered_repairs,
            "global_repair_constraints": [
                "repair contradictions before export",
                "do not hide contradictions with prose",
                "every major power must keep cost and counterplay",
                "every destiny must preserve agency",
                "relationship logic must preserve boundaries",
                "dialogue voice must match wound, origin, and relationship context",
            ],
        }

    def _build_diagnostics(
        self,
        *,
        validation_checks: List[Dict[str, Any]],
        consistency_report: Dict[str, Any],
        repair_plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        score = consistency_report["overall_consistency_score"]
        has_critical = consistency_report["critical_issue_count"] > 0
        has_violations = consistency_report["violation_count"] > 0

        return {
            "validator_completeness_score": 1.0 if validation_checks else 0.0,
            "checked_engine_count": len(validation_checks),
            "has_critical_issues": has_critical,
            "has_violations": has_violations,
            "has_repair_plan": bool(repair_plan["ordered_repairs"]) or not has_violations,
            "character_bible_ready": score >= 0.82 and not has_critical and not has_violations,
            "orchestrator_ready": score >= 0.78 and not has_critical,
            "training_ready_schema": True,
        }

    def _build_ontology_record(
        self,
        *,
        consistency_report: Dict[str, Any],
        validation_checks: List[Dict[str, Any]],
        repair_plan: Dict[str, Any],
    ) -> LearnedOntologyRecord:
        return LearnedOntologyRecord(
            ontology_type="character_consistency_validation",
            name=consistency_report["validator_name"],
            family="character_validation",
            subtype=consistency_report["consistency_tier"],
            description=f"Consistency score {consistency_report['overall_consistency_score']}",
            axes={
                "consistency_report": consistency_report,
                "validation_checks": validation_checks,
                "repair_plan": repair_plan,
            },
            tags=consistency_report["similarity_tags"],
            examples=[consistency_report["validator_name"]],
            counterexamples=consistency_report["critical_issues"],
            confidence_score=consistency_report["confidence_score"],
            novelty_score=consistency_report["novelty_score"],
            quality_score=consistency_report["originality_score"],
            learned_from_data=False,
            generated_by_engine=self.engine_name,
        )

    def _training_eligibility(
        self,
        *,
        consistency_report: Dict[str, Any],
        validator_diagnostics: Dict[str, Any],
        source_mode: str,
        user_rating: Any,
        provenance: DatasetProvenanceRecord,
    ) -> TrainingEligibility:
        quality = min(
            consistency_report["overall_consistency_score"],
            consistency_report["confidence_score"],
            consistency_report["originality_score"],
            0.95,
        )

        approved_source = source_mode in {"human_approved_synthetic", "user_owned", "licensed_dataset"}
        high_rating = user_rating is None or float(user_rating) >= 8
        eligible = (
            approved_source
            and provenance.usage_allowed
            and quality >= 0.75
            and high_rating
            and validator_diagnostics["character_bible_ready"]
        )

        rejection_reasons = []
        if not approved_source:
            rejection_reasons.append("source mode is not approved for training")
        if not provenance.usage_allowed:
            rejection_reasons.append("source usage is not allowed")
        if quality < 0.75:
            rejection_reasons.append("quality score below threshold")
        if not high_rating:
            rejection_reasons.append("human rating below training threshold")
        if not validator_diagnostics["character_bible_ready"]:
            rejection_reasons.append("character profile not bible-ready")

        return TrainingEligibility(
            training_eligible=eligible,
            human_review_required=not eligible,
            do_not_train=not eligible,
            recommended_split="train" if eligible else "human_review_queue",
            quality_score=round(quality, 3),
            consistency_score=consistency_report["overall_consistency_score"],
            originality_score=consistency_report["originality_score"],
            safety_score=0.88 if validator_diagnostics["character_bible_ready"] else 0.72,
            rejection_reasons=rejection_reasons,
            approval_notes=[
                "Consistency validator output controls export/training readiness.",
                "Training eligibility requires clean validation and approved provenance.",
            ],
        )

    def _build_next_engine_payload(
        self,
        *,
        character_seed: Dict[str, Any],
        consistency_report: Dict[str, Any],
        validation_checks: List[Dict[str, Any]],
        repair_plan: Dict[str, Any],
        learning_metadata: EngineLearningMetadata,
    ) -> Dict[str, Any]:
        merged_seed = dict(character_seed)
        merged_seed["consistency_report"] = consistency_report
        merged_seed["validation_checks"] = validation_checks
        merged_seed["repair_plan"] = repair_plan
        merged_seed["consistency_learning_metadata"] = learning_metadata.model_dump()

        return {
            "character_seed": merged_seed,
            "originality_engine_payload": {
                "character_seed": merged_seed,
                "consistency_report": consistency_report,
            },
            "quality_scorer_payload": {
                "character_seed": merged_seed,
                "consistency_report": consistency_report,
                "repair_plan": repair_plan,
            },
            "character_bible_export_payload": {
                "character_seed": merged_seed,
                "consistency_report": consistency_report,
                "validation_checks": validation_checks,
            },
            "chunk8_training_payload_later": {
                "target_type": "character_consistency_validation",
                "consistency_report": consistency_report,
                "learning_metadata": learning_metadata.model_dump(),
            },
        }

    def _shares_theme(self, left: str, right: str) -> bool:
        left_terms = set(left.replace("_", " ").split())
        right_terms = set(right.replace("_", " ").split())
        meaningful = {term for term in left_terms.intersection(right_terms) if len(term) >= 5}
        return bool(meaningful)

    def _clamp(self, value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)
