from typing import Any, Dict, List, Optional


class SimulationLearningAdapter:
    """Converts simulation outputs into safe learning metadata.

    This adapter does not train a model directly. It prepares structured signals
    from simulation runs, quality reports, anti-genericity reports, benchmark
    reports, handoff packages, and generation-control payloads.

    Later chunks can use these signals for:
    - model evaluation
    - prompt tuning
    - preference learning
    - story-quality scoring
    - abstract pattern learning from user-approved corpora
    """

    engine_name = "simulation.simulation_learning_adapter"

    SIGNAL_TYPES = {
        "quality_signal",
        "anti_genericity_signal",
        "benchmark_signal",
        "handoff_signal",
        "generation_control_signal",
        "failure_signal",
        "recommendation_signal",
        "corpus_learning_signal",
        "feedback_signal",
    }

    def create_learning_signal(
        self,
        *,
        signal_id: str,
        signal_type: str,
        source_type: str,
        source_id: str,
        target_area: str,
        value: float = 0.0,
        label: str = "",
        features: Dict[str, Any] | None = None,
        recommendations: List[str] | None = None,
        requires_human_review: bool = False,
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        if signal_type not in self.SIGNAL_TYPES:
            signal_type = "feedback_signal"

        return {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "source_type": source_type,
            "source_id": source_id,
            "target_area": target_area,
            "value": self._bounded(value),
            "label": label,
            "features": features or {},
            "recommendations": recommendations or [],
            "requires_human_review": bool(requires_human_review),
            "metadata": metadata or {},
        }

    def build_learning_signals_from_run(
        self,
        *,
        state: Any,
        run_id: str,
    ) -> Dict[str, Any]:
        run = state.metadata.get("simulation_runs", {}).get(run_id)
        if not run:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": [f"simulation run {run_id} not found"],
            }

        outputs = run.get("outputs", {})
        signals = []

        signals.append(
            self.create_learning_signal(
                signal_id=f"signal_{run_id}_run_completion",
                signal_type="quality_signal",
                source_type="simulation_run",
                source_id=run_id,
                target_area="run_completion",
                value=1.0 if run.get("status") == "completed" else 0.5,
                label=run.get("status", "unknown"),
                features={
                    "step_count": len(run.get("steps", [])),
                    "selected_character_count": len(run.get("selected_character_ids", [])),
                    "event_count": len(run.get("event_ids", [])),
                    "warning_count": len(run.get("warnings", [])),
                    "error_count": len(run.get("errors", [])),
                },
                recommendations=[] if not run.get("errors") else ["fix run errors before generation"],
            )
        )

        signals.append(
            self.create_learning_signal(
                signal_id=f"signal_{run_id}_handoff_readiness",
                signal_type="handoff_signal",
                source_type="simulation_run",
                source_id=run_id,
                target_area="handoff_readiness",
                value=1.0 if outputs.get("handoff_package_id") and outputs.get("generation_control_payload_id") else 0.0,
                label="ready" if outputs.get("handoff_package_id") and outputs.get("generation_control_payload_id") else "not_ready",
                features={
                    "handoff_package_id": outputs.get("handoff_package_id"),
                    "generation_control_payload_id": outputs.get("generation_control_payload_id"),
                    "scene_payload_id": outputs.get("scene_payload_id"),
                    "plot_payload_id": outputs.get("plot_payload_id"),
                },
                recommendations=[] if outputs.get("handoff_package_id") else ["build handoff package before generation"],
            )
        )

        if run.get("warnings"):
            signals.append(
                self.create_learning_signal(
                    signal_id=f"signal_{run_id}_warnings",
                    signal_type="failure_signal",
                    source_type="simulation_run",
                    source_id=run_id,
                    target_area="simulation_warnings",
                    value=max(0.0, 1.0 - len(run.get("warnings", [])) * 0.05),
                    label="warnings_present",
                    features={"warnings": run.get("warnings", [])},
                    recommendations=["review recurring warnings and convert into validation rules"],
                    requires_human_review=False,
                )
            )

        if run.get("errors"):
            signals.append(
                self.create_learning_signal(
                    signal_id=f"signal_{run_id}_errors",
                    signal_type="failure_signal",
                    source_type="simulation_run",
                    source_id=run_id,
                    target_area="simulation_errors",
                    value=0.0,
                    label="errors_present",
                    features={"errors": run.get("errors", [])},
                    recommendations=["fix simulation errors before downstream generation"],
                    requires_human_review=True,
                )
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "learning_signals": signals,
            "signal_count": len(signals),
        }

    def build_learning_signals_from_quality_report(
        self,
        *,
        quality_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        report_id = quality_report.get("quality_report_id")
        run_id = quality_report.get("run_id")
        dimensions = quality_report.get("dimension_scores", {})
        signals = []

        signals.append(
            self.create_learning_signal(
                signal_id=f"signal_{report_id}_overall_quality",
                signal_type="quality_signal",
                source_type="simulation_quality_report",
                source_id=report_id,
                target_area="overall_quality",
                value=float(quality_report.get("overall_quality_score", 0.0)),
                label=quality_report.get("quality_label", ""),
                features={
                    "ready_for_generation": quality_report.get("ready_for_generation", False),
                    "blocker_count": len(quality_report.get("blockers", [])),
                    "warning_count": len(quality_report.get("warnings", [])),
                },
                recommendations=quality_report.get("recommendations", []),
            )
        )

        for dimension, score in dimensions.items():
            signals.append(
                self.create_learning_signal(
                    signal_id=f"signal_{report_id}_{dimension}",
                    signal_type="quality_signal",
                    source_type="simulation_quality_report",
                    source_id=report_id,
                    target_area=dimension,
                    value=float(score),
                    label=self._score_label(float(score)),
                    features={"dimension": dimension, "run_id": run_id},
                    recommendations=self._dimension_recommendation(dimension, float(score)),
                )
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "quality_report_id": report_id,
            "learning_signals": signals,
            "signal_count": len(signals),
        }

    def build_learning_signals_from_anti_genericity_report(
        self,
        *,
        anti_genericity_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        report_id = anti_genericity_report.get("anti_genericity_report_id")
        checks = anti_genericity_report.get("checks", {})
        signals = []

        signals.append(
            self.create_learning_signal(
                signal_id=f"signal_{report_id}_overall_anti_genericity",
                signal_type="anti_genericity_signal",
                source_type="simulation_anti_genericity_report",
                source_id=report_id,
                target_area="anti_genericity",
                value=float(anti_genericity_report.get("anti_genericity_score", 0.0)),
                label=anti_genericity_report.get("label", ""),
                features={
                    "genericity_risk": anti_genericity_report.get("genericity_risk", 0.0),
                    "passes": anti_genericity_report.get("passes", False),
                    "blocker_count": len(anti_genericity_report.get("blockers", [])),
                },
                recommendations=anti_genericity_report.get("recommendations", []),
            )
        )

        for check_name, check in checks.items():
            signals.append(
                self.create_learning_signal(
                    signal_id=f"signal_{report_id}_{check_name}",
                    signal_type="anti_genericity_signal",
                    source_type="simulation_anti_genericity_report",
                    source_id=report_id,
                    target_area=check_name,
                    value=float(check.get("score", 0.0)),
                    label=self._score_label(float(check.get("score", 0.0))),
                    features={
                        "check_name": check_name,
                        "warnings": check.get("warnings", []),
                    },
                    recommendations=self._anti_genericity_recommendation(check_name, float(check.get("score", 0.0))),
                )
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "anti_genericity_report_id": report_id,
            "learning_signals": signals,
            "signal_count": len(signals),
        }

    def build_learning_signals_from_benchmark_report(
        self,
        *,
        benchmark_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        report_id = benchmark_report.get("benchmark_report_id")
        benchmark_id = benchmark_report.get("benchmark_id")

        signals = [
            self.create_learning_signal(
                signal_id=f"signal_{report_id}_benchmark_pass",
                signal_type="benchmark_signal",
                source_type="simulation_benchmark_report",
                source_id=report_id,
                target_area="benchmark_pass",
                value=1.0 if benchmark_report.get("passed") else 0.0,
                label="passed" if benchmark_report.get("passed") else "failed",
                features={
                    "benchmark_id": benchmark_id,
                    "quality_score": benchmark_report.get("quality_score", 0.0),
                    "anti_genericity_score": benchmark_report.get("anti_genericity_score", 0.0),
                    "ready_for_chunk5": benchmark_report.get("ready_for_chunk5", False),
                    "selected_character_count": benchmark_report.get("selected_character_count", 0),
                    "event_count": benchmark_report.get("event_count", 0),
                },
                recommendations=[] if benchmark_report.get("passed") else ["inspect failed benchmark thresholds and warnings"],
            ),
            self.create_learning_signal(
                signal_id=f"signal_{report_id}_benchmark_quality",
                signal_type="benchmark_signal",
                source_type="simulation_benchmark_report",
                source_id=report_id,
                target_area="benchmark_quality",
                value=float(benchmark_report.get("quality_score", 0.0)),
                label=self._score_label(float(benchmark_report.get("quality_score", 0.0))),
                features={"benchmark_id": benchmark_id},
                recommendations=[],
            ),
            self.create_learning_signal(
                signal_id=f"signal_{report_id}_benchmark_specificity",
                signal_type="benchmark_signal",
                source_type="simulation_benchmark_report",
                source_id=report_id,
                target_area="benchmark_anti_genericity",
                value=float(benchmark_report.get("anti_genericity_score", 0.0)),
                label=self._score_label(float(benchmark_report.get("anti_genericity_score", 0.0))),
                features={"benchmark_id": benchmark_id},
                recommendations=[],
            ),
        ]

        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_report_id": report_id,
            "learning_signals": signals,
            "signal_count": len(signals),
        }

    def build_learning_dataset_from_state(
        self,
        *,
        state: Any,
        dataset_id: str = "simulation_learning_dataset_latest",
    ) -> Dict[str, Any]:
        signals: List[Dict[str, Any]] = []

        for run_id in state.metadata.get("simulation_runs", {}):
            result = self.build_learning_signals_from_run(state=state, run_id=run_id)
            if result.get("success"):
                signals.extend(result.get("learning_signals", []))

        for report in state.metadata.get("simulation_quality_reports", {}).values():
            result = self.build_learning_signals_from_quality_report(quality_report=report)
            signals.extend(result.get("learning_signals", []))

        for report in state.metadata.get("simulation_anti_genericity_reports", {}).values():
            result = self.build_learning_signals_from_anti_genericity_report(
                anti_genericity_report=report
            )
            signals.extend(result.get("learning_signals", []))

        for report in state.metadata.get("simulation_benchmark_reports", {}).values():
            result = self.build_learning_signals_from_benchmark_report(
                benchmark_report=report
            )
            signals.extend(result.get("learning_signals", []))

        dataset = {
            "dataset_id": dataset_id,
            "engine_name": self.engine_name,
            "signal_count": len(signals),
            "signals": signals,
            "summary": self._summarize_signals(signals),
            "safety_contract": {
                "contains_source_text": False,
                "contains_user_private_text": False,
                "abstract_learning_only": True,
                "requires_human_review_for_corpus_style_transfer": True,
                "safe_for_evaluation_metadata": True,
            },
        }

        state.metadata.setdefault("simulation_learning_datasets", {})[dataset_id] = dataset
        state.metadata.setdefault("simulation_learning_history", []).append(
            {
                "action": "build_learning_dataset_from_state",
                "dataset_id": dataset_id,
                "signal_count": len(signals),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dataset": dataset,
            "updated_state": state,
        }

    def build_feedback_learning_record(
        self,
        *,
        feedback_id: str,
        run_id: str,
        user_rating: float,
        user_notes: str = "",
        accepted: bool = False,
        rejected: bool = False,
        target_area: str = "story_generation",
    ) -> Dict[str, Any]:
        label = "accepted" if accepted else "rejected" if rejected else "rated"

        signal = self.create_learning_signal(
            signal_id=f"signal_feedback_{feedback_id}",
            signal_type="feedback_signal",
            source_type="user_feedback",
            source_id=feedback_id,
            target_area=target_area,
            value=user_rating,
            label=label,
            features={
                "run_id": run_id,
                "user_notes_summary": user_notes[:300],
                "accepted": accepted,
                "rejected": rejected,
            },
            recommendations=self._feedback_recommendations(user_rating, accepted, rejected),
            requires_human_review=True,
            metadata={
                "contains_user_feedback": True,
                "abstract_for_learning": True,
            },
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "feedback_id": feedback_id,
            "learning_signal": signal,
        }

    def register_learning_dataset_on_state(
        self,
        *,
        state: Any,
        dataset: Dict[str, Any],
    ) -> Dict[str, Any]:
        dataset_id = dataset.get("dataset_id")
        if not dataset_id:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": ["dataset requires dataset_id"],
            }

        state.metadata.setdefault("simulation_learning_datasets", {})[dataset_id] = dataset
        state.metadata.setdefault("simulation_learning_history", []).append(
            {
                "action": "register_learning_dataset",
                "dataset_id": dataset_id,
                "signal_count": dataset.get("signal_count", 0),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dataset_id": dataset_id,
            "updated_state": state,
        }

    def build_learning_map(self, *, state: Any) -> Dict[str, Any]:
        datasets = state.metadata.get("simulation_learning_datasets", {})
        compact = {}

        for dataset_id, dataset in datasets.items():
            compact[dataset_id] = {
                "dataset_id": dataset_id,
                "signal_count": dataset.get("signal_count", 0),
                "target_area_counts": dataset.get("summary", {}).get("target_area_counts", {}),
                "signal_type_counts": dataset.get("summary", {}).get("signal_type_counts", {}),
                "average_signal_value": dataset.get("summary", {}).get("average_signal_value", 0.0),
                "safe_for_evaluation_metadata": dataset.get("safety_contract", {}).get("safe_for_evaluation_metadata", False),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dataset_count": len(compact),
            "learning_datasets": compact,
            "warnings": [] if compact else ["no simulation learning datasets registered"],
        }

    def _summarize_signals(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        signal_type_counts: Dict[str, int] = {}
        target_area_counts: Dict[str, int] = {}
        review_required = 0
        values = []

        for signal in signals:
            signal_type = signal.get("signal_type", "unknown")
            target_area = signal.get("target_area", "unknown")
            signal_type_counts[signal_type] = signal_type_counts.get(signal_type, 0) + 1
            target_area_counts[target_area] = target_area_counts.get(target_area, 0) + 1
            values.append(float(signal.get("value", 0.0)))
            if signal.get("requires_human_review"):
                review_required += 1

        return {
            "signal_type_counts": signal_type_counts,
            "target_area_counts": target_area_counts,
            "average_signal_value": self._average(values),
            "human_review_signal_count": review_required,
            "low_value_signal_count": sum(1 for value in values if value < 0.45),
        }

    def _dimension_recommendation(self, dimension: str, score: float) -> List[str]:
        if score >= 0.60:
            return []

        mapping = {
            "causal_coherence": "improve choice-event-consequence-delta graph links",
            "character_readiness": "add role, backstory, psychology, goals, and voice metadata",
            "relationship_continuity": "add richer relationship states between selected characters",
            "emotional_continuity": "add emotional carryover and activation context",
            "stakes_clarity": "make stakes concrete and multi-dimensional",
            "tension_pacing": "add escalation/release pacing beats",
            "conflict_usefulness": "sharpen core issue and opposing goals",
            "consequence_traceability": "connect consequences to source choices/events and generated deltas",
            "cast_balance": "rebalance cast role/function coverage",
            "handoff_readiness": "rebuild handoff package",
            "generation_control_readiness": "add generation control payload with genre/format contracts",
        }

        return [mapping.get(dimension, f"improve {dimension}")]

    def _anti_genericity_recommendation(self, check_name: str, score: float) -> List[str]:
        if score >= 0.60:
            return []

        mapping = {
            "user_specificity": "capture more distinctive user wants and constraints",
            "character_specificity": "make each character non-interchangeable",
            "relationship_specificity": "add unique relationship history, secrets, imbalance, and tension",
            "world_specificity": "add world rules, factions, locations, culture, and consequences",
            "conflict_specificity": "avoid template conflict; add concrete opposing goals",
            "stakes_specificity": "define what changes if the scene succeeds or fails",
            "causal_specificity": "add concrete cause-effect chain",
            "handoff_specificity": "include richer scene/plot/cast/causal context in handoff",
        }

        return [mapping.get(check_name, f"improve {check_name}")]

    def _feedback_recommendations(self, rating: float, accepted: bool, rejected: bool) -> List[str]:
        if accepted or rating >= 0.75:
            return ["reinforce patterns from this run"]
        if rejected or rating < 0.40:
            return ["avoid repeating weak patterns from this run", "inspect user notes for correction targets"]
        return ["use feedback as neutral preference signal"]

    def _score_label(self, score: float) -> str:
        if score >= 0.85:
            return "excellent"
        if score >= 0.70:
            return "strong"
        if score >= 0.60:
            return "usable"
        if score >= 0.45:
            return "needs_revision"
        return "weak"

    def _bounded(self, value: float) -> float:
        return round(max(0.0, min(1.0, float(value))), 3)

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)
