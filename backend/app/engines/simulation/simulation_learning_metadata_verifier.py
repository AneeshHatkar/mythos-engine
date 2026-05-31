from typing import Any, Dict, List


class SimulationLearningMetadataVerifier:
    """Verifies simulation learning metadata before it is used downstream.

    This protects the project from broken or unsafe learning data:
    - malformed signals
    - duplicate signal IDs
    - out-of-range scores
    - missing safety contracts
    - accidental source-text storage
    - missing quality/anti-genericity/benchmark signal coverage
    """

    engine_name = "simulation.simulation_learning_metadata_verifier"

    REQUIRED_SIGNAL_FIELDS = {
        "signal_id",
        "signal_type",
        "source_type",
        "source_id",
        "target_area",
        "value",
        "label",
        "features",
        "recommendations",
        "requires_human_review",
        "metadata",
    }

    EXPECTED_SIGNAL_TYPES = {
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

    def verify_learning_dataset(
        self,
        *,
        dataset: Dict[str, Any],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        if not dataset.get("dataset_id"):
            blockers.append("dataset_id is missing")
        else:
            passed_checks.append("dataset_id_present")

        signals = dataset.get("signals", [])
        if not isinstance(signals, list):
            blockers.append("signals must be a list")
            signals = []
        elif not signals:
            blockers.append("dataset has no learning signals")
        else:
            passed_checks.append("signals_present")

        signal_report = self.verify_signals(signals=signals)
        blockers.extend(signal_report["blockers"])
        warnings.extend(signal_report["warnings"])
        passed_checks.extend(signal_report["passed_checks"])

        safety_report = self.verify_safety_contract(dataset=dataset)
        blockers.extend(safety_report["blockers"])
        warnings.extend(safety_report["warnings"])
        passed_checks.extend(safety_report["passed_checks"])

        coverage_report = self.verify_signal_coverage(signals=signals)
        warnings.extend(coverage_report["warnings"])
        passed_checks.extend(coverage_report["passed_checks"])

        summary_report = self.verify_summary(dataset=dataset, signals=signals)
        blockers.extend(summary_report["blockers"])
        warnings.extend(summary_report["warnings"])
        passed_checks.extend(summary_report["passed_checks"])

        verification_score = self._verification_score(
            blockers=blockers,
            warnings=warnings,
            passed_checks=passed_checks,
            total_signals=len(signals),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "dataset_id": dataset.get("dataset_id"),
            "valid": not blockers,
            "verification_score": verification_score,
            "verification_label": self._verification_label(verification_score, blockers),
            "signal_count": len(signals),
            "blockers": self._unique(blockers),
            "warnings": self._unique(warnings),
            "passed_checks": self._unique(passed_checks),
            "coverage_report": coverage_report,
            "safety_report": safety_report,
        }

    def verify_dataset_from_state(
        self,
        *,
        state: Any,
        dataset_id: str,
    ) -> Dict[str, Any]:
        dataset = state.metadata.get("simulation_learning_datasets", {}).get(dataset_id)
        if not dataset:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "dataset_id": dataset_id,
                "errors": [f"learning dataset {dataset_id} not found"],
            }

        report = self.verify_learning_dataset(dataset=dataset)
        report_id = f"learning_metadata_verification_{dataset_id}"

        verification_record = {
            "verification_report_id": report_id,
            "dataset_id": dataset_id,
            "valid": report["valid"],
            "verification_score": report["verification_score"],
            "verification_label": report["verification_label"],
            "signal_count": report["signal_count"],
            "blockers": report["blockers"],
            "warnings": report["warnings"],
            "passed_checks": report["passed_checks"],
        }

        state.metadata.setdefault("simulation_learning_metadata_verifications", {})[
            report_id
        ] = verification_record

        state.metadata.setdefault("simulation_learning_metadata_verification_history", []).append(
            {
                "action": "verify_dataset_from_state",
                "dataset_id": dataset_id,
                "verification_report_id": report_id,
                "valid": report["valid"],
                "verification_score": report["verification_score"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "verification_report": verification_record,
            "updated_state": state,
        }

    def verify_signals(self, *, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        seen_ids = set()

        for index, signal in enumerate(signals):
            prefix = f"signal[{index}]"

            if not isinstance(signal, dict):
                blockers.append(f"{prefix} is not a dict")
                continue

            missing = self.REQUIRED_SIGNAL_FIELDS - set(signal.keys())
            if missing:
                blockers.append(f"{prefix} missing required fields: {sorted(missing)}")
            else:
                passed_checks.append(f"{prefix}_required_fields_present")

            signal_id = signal.get("signal_id")
            if not signal_id:
                blockers.append(f"{prefix} missing signal_id")
            elif signal_id in seen_ids:
                blockers.append(f"duplicate signal_id found: {signal_id}")
            else:
                seen_ids.add(signal_id)

            signal_type = signal.get("signal_type")
            if signal_type not in self.EXPECTED_SIGNAL_TYPES:
                warnings.append(f"{prefix} has unexpected signal_type: {signal_type}")
            else:
                passed_checks.append(f"{prefix}_signal_type_valid")

            value = signal.get("value")
            if not isinstance(value, (int, float)):
                blockers.append(f"{prefix} value must be numeric")
            elif not 0.0 <= float(value) <= 1.0:
                blockers.append(f"{prefix} value out of bounds: {value}")
            else:
                passed_checks.append(f"{prefix}_value_bounded")

            if not isinstance(signal.get("features", {}), dict):
                blockers.append(f"{prefix} features must be a dict")

            if not isinstance(signal.get("recommendations", []), list):
                blockers.append(f"{prefix} recommendations must be a list")

            if not isinstance(signal.get("requires_human_review", False), bool):
                blockers.append(f"{prefix} requires_human_review must be bool")

            text_leak_warnings = self._detect_source_text_leak(signal)
            warnings.extend([f"{prefix} {item}" for item in text_leak_warnings])

        if signals:
            passed_checks.append("signal_iteration_completed")
            passed_checks.append("signal_ids_checked")

        return {
            "blockers": self._unique(blockers),
            "warnings": self._unique(warnings),
            "passed_checks": self._unique(passed_checks),
        }

    def verify_safety_contract(self, *, dataset: Dict[str, Any]) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        contract = dataset.get("safety_contract")
        if not isinstance(contract, dict):
            blockers.append("safety_contract missing or not dict")
            return {
                "blockers": blockers,
                "warnings": warnings,
                "passed_checks": passed_checks,
            }

        if contract.get("contains_source_text") is False:
            passed_checks.append("contains_source_text_false")
        else:
            blockers.append("safety_contract must declare contains_source_text=False")

        if contract.get("abstract_learning_only") is True:
            passed_checks.append("abstract_learning_only_true")
        else:
            blockers.append("safety_contract must declare abstract_learning_only=True")

        if contract.get("safe_for_evaluation_metadata") is True:
            passed_checks.append("safe_for_evaluation_metadata_true")
        else:
            warnings.append("safe_for_evaluation_metadata not explicitly true")

        if contract.get("requires_human_review_for_corpus_style_transfer") is True:
            passed_checks.append("human_review_for_corpus_style_transfer_true")
        else:
            warnings.append("corpus style transfer human review flag missing")

        if contract.get("contains_user_private_text") is True:
            warnings.append("dataset declares contains_user_private_text=True; review before training/export")

        return {
            "blockers": self._unique(blockers),
            "warnings": self._unique(warnings),
            "passed_checks": self._unique(passed_checks),
        }

    def verify_signal_coverage(self, *, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        warnings: List[str] = []
        passed_checks: List[str] = []

        signal_types = {signal.get("signal_type") for signal in signals if isinstance(signal, dict)}
        target_areas = {signal.get("target_area") for signal in signals if isinstance(signal, dict)}

        expected_core_types = {
            "quality_signal",
            "anti_genericity_signal",
            "benchmark_signal",
            "handoff_signal",
        }

        for signal_type in expected_core_types:
            if signal_type in signal_types:
                passed_checks.append(f"{signal_type}_present")
            else:
                warnings.append(f"{signal_type} missing from dataset")

        expected_target_areas = {
            "overall_quality",
            "anti_genericity",
            "handoff_readiness",
        }

        for target_area in expected_target_areas:
            if target_area in target_areas:
                passed_checks.append(f"{target_area}_target_present")
            else:
                warnings.append(f"{target_area} target area missing")

        return {
            "signal_types": sorted([str(item) for item in signal_types if item]),
            "target_areas": sorted([str(item) for item in target_areas if item]),
            "warnings": self._unique(warnings),
            "passed_checks": self._unique(passed_checks),
        }

    def verify_summary(
        self,
        *,
        dataset: Dict[str, Any],
        signals: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed_checks: List[str] = []

        summary = dataset.get("summary")
        if not isinstance(summary, dict):
            blockers.append("summary missing or not dict")
            return {
                "blockers": blockers,
                "warnings": warnings,
                "passed_checks": passed_checks,
            }

        if dataset.get("signal_count") != len(signals):
            warnings.append("dataset signal_count does not match actual signal length")
        else:
            passed_checks.append("signal_count_matches_actual_length")

        if isinstance(summary.get("signal_type_counts"), dict):
            passed_checks.append("summary_signal_type_counts_present")
        else:
            warnings.append("summary signal_type_counts missing")

        if isinstance(summary.get("target_area_counts"), dict):
            passed_checks.append("summary_target_area_counts_present")
        else:
            warnings.append("summary target_area_counts missing")

        avg = summary.get("average_signal_value")
        if isinstance(avg, (int, float)) and 0.0 <= float(avg) <= 1.0:
            passed_checks.append("summary_average_signal_value_bounded")
        else:
            warnings.append("summary average_signal_value missing or out of bounds")

        return {
            "blockers": self._unique(blockers),
            "warnings": self._unique(warnings),
            "passed_checks": self._unique(passed_checks),
        }

    def build_verification_map(self, *, state: Any) -> Dict[str, Any]:
        records = state.metadata.get("simulation_learning_metadata_verifications", {})
        compact = {}

        for report_id, report in records.items():
            compact[report_id] = {
                "verification_report_id": report_id,
                "dataset_id": report.get("dataset_id"),
                "valid": report.get("valid"),
                "verification_score": report.get("verification_score"),
                "verification_label": report.get("verification_label"),
                "signal_count": report.get("signal_count", 0),
                "blocker_count": len(report.get("blockers", [])),
                "warning_count": len(report.get("warnings", [])),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "verification_count": len(compact),
            "verification_records": compact,
            "valid_count": sum(1 for item in compact.values() if item.get("valid")),
            "warnings": [] if compact else ["no learning metadata verifications registered"],
        }

    def _detect_source_text_leak(self, signal: Dict[str, Any]) -> List[str]:
        warnings = []

        suspicious_keys = {
            "full_text",
            "source_text",
            "verbatim",
            "raw_pdf_text",
            "chapter_text",
            "novel_text",
            "document_text",
        }

        def walk(value: Any, path: str = "") -> None:
            if isinstance(value, dict):
                for key, inner in value.items():
                    lower_key = str(key).lower()
                    if lower_key in suspicious_keys:
                        warnings.append(f"possible source-text field found at {path}.{key}")
                    walk(inner, f"{path}.{key}" if path else str(key))
            elif isinstance(value, list):
                for idx, inner in enumerate(value):
                    walk(inner, f"{path}[{idx}]")
            elif isinstance(value, str):
                if len(value) > 1500:
                    warnings.append(f"very long text field may be unsafe at {path}")

        walk(signal)
        return warnings

    def _verification_score(
        self,
        *,
        blockers: List[str],
        warnings: List[str],
        passed_checks: List[str],
        total_signals: int,
    ) -> float:
        base = 0.55
        base += min(0.25, len(passed_checks) * 0.006)
        base += min(0.10, total_signals * 0.003)
        base -= min(0.60, len(blockers) * 0.12)
        base -= min(0.25, len(warnings) * 0.02)
        return round(max(0.0, min(1.0, base)), 3)

    def _verification_label(self, score: float, blockers: List[str]) -> str:
        if blockers:
            return "blocked"
        if score >= 0.85:
            return "excellent"
        if score >= 0.70:
            return "verified"
        if score >= 0.55:
            return "usable"
        return "needs_revision"

    def _unique(self, values: List[Any]) -> List[Any]:
        result = []
        seen = set()
        for value in values:
            if value is None:
                continue
            key = str(value)
            if key not in seen:
                seen.add(key)
                result.append(value)
        return result
