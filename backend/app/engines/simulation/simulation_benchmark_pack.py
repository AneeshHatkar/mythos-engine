from typing import Any, Dict, List, Optional

from backend.app.engines.simulation.interaction_simulation_orchestrator import InteractionSimulationOrchestrator
from backend.app.engines.simulation.simulation_anti_genericity_validator import SimulationAntiGenericityValidator
from backend.app.engines.simulation.simulation_quality_scorer import SimulationQualityScorer


class SimulationBenchmarkPack:
    """Benchmark scenarios for Chunk 4 simulation."""

    engine_name = "simulation.simulation_benchmark_pack"

    def __init__(self) -> None:
        self.orchestrator = InteractionSimulationOrchestrator()
        self.quality_scorer = SimulationQualityScorer()
        self.anti_genericity_validator = SimulationAntiGenericityValidator()

    def list_benchmarks(self) -> Dict[str, Any]:
        benchmarks = self.get_benchmark_definitions()
        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_count": len(benchmarks),
            "benchmarks": [
                {
                    "benchmark_id": item["benchmark_id"],
                    "name": item["name"],
                    "format": item["story_request"].get("format"),
                    "event_count": len(item.get("event_specs", [])),
                    "target_cast_size": item.get("target_cast_size"),
                }
                for item in benchmarks
            ],
        }

    def get_benchmark_definitions(self) -> List[Dict[str, Any]]:
        return [
            self._dark_academy_trial_benchmark(),
            self._romance_betrayal_benchmark(),
            self._faction_conflict_benchmark(),
            self._minimal_scene_benchmark(),
            self._large_ensemble_benchmark(),
        ]

    def get_benchmark(self, *, benchmark_id: str) -> Dict[str, Any]:
        for benchmark in self.get_benchmark_definitions():
            if benchmark["benchmark_id"] == benchmark_id:
                return {
                    "success": True,
                    "engine_name": self.engine_name,
                    "benchmark": benchmark,
                }

        return {
            "success": False,
            "engine_name": self.engine_name,
            "benchmark_id": benchmark_id,
            "errors": [f"benchmark {benchmark_id} not found"],
        }

    def run_benchmark(
        self,
        *,
        state: Any,
        benchmark_id: str,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        benchmark_result = self.get_benchmark(benchmark_id=benchmark_id)
        if not benchmark_result.get("success"):
            return benchmark_result

        benchmark = benchmark_result["benchmark"]
        actual_run_id = run_id or f"benchmark_{benchmark_id}"

        run_result = self.orchestrator.run_interaction_simulation(
            state=state,
            run_id=actual_run_id,
            story_request=benchmark["story_request"],
            event_specs=benchmark.get("event_specs", []),
            candidate_ids=benchmark.get("candidate_ids"),
            target_cast_size=benchmark.get("target_cast_size"),
        )

        quality_result = self.quality_scorer.score_simulation_run(state=state, run_id=actual_run_id)
        anti_result = self.anti_genericity_validator.validate_simulation_run(state=state, run_id=actual_run_id)

        benchmark_report = self._build_benchmark_report(
            benchmark=benchmark,
            run_result=run_result,
            quality_report=quality_result.get("quality_report"),
            anti_genericity_report=anti_result.get("anti_genericity_report"),
        )

        state.metadata.setdefault("simulation_benchmark_reports", {})[
            benchmark_report["benchmark_report_id"]
        ] = benchmark_report

        state.metadata.setdefault("simulation_benchmark_history", []).append(
            {
                "action": "run_benchmark",
                "benchmark_id": benchmark_id,
                "run_id": actual_run_id,
                "passed": benchmark_report["passed"],
                "quality_score": benchmark_report["quality_score"],
                "anti_genericity_score": benchmark_report["anti_genericity_score"],
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_report": benchmark_report,
            "run_result": run_result,
            "quality_report": quality_result.get("quality_report"),
            "anti_genericity_report": anti_result.get("anti_genericity_report"),
            "updated_state": state,
        }

    def run_all_benchmarks(self, *, state: Any) -> Dict[str, Any]:
        reports = []
        for benchmark in self.get_benchmark_definitions():
            result = self.run_benchmark(
                state=state,
                benchmark_id=benchmark["benchmark_id"],
                run_id=f"benchmark_{benchmark['benchmark_id']}",
            )
            reports.append(result["benchmark_report"])

        aggregate = self._aggregate_reports(reports)

        state.metadata.setdefault("simulation_benchmark_aggregate_reports", {})[
            aggregate["aggregate_report_id"]
        ] = aggregate

        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_count": len(reports),
            "benchmark_reports": reports,
            "aggregate_report": aggregate,
            "updated_state": state,
        }

    def build_benchmark_map(self, *, state: Any) -> Dict[str, Any]:
        reports = state.metadata.get("simulation_benchmark_reports", {})
        compact = {}

        for report_id, report in reports.items():
            compact[report_id] = {
                "benchmark_report_id": report_id,
                "benchmark_id": report.get("benchmark_id"),
                "run_id": report.get("run_id"),
                "passed": report.get("passed"),
                "quality_score": report.get("quality_score"),
                "anti_genericity_score": report.get("anti_genericity_score"),
                "ready_for_chunk5": report.get("ready_for_chunk5"),
                "warning_count": len(report.get("warnings", [])),
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "benchmark_report_count": len(compact),
            "benchmark_reports": compact,
            "passing_count": sum(1 for item in compact.values() if item.get("passed")),
            "warnings": [] if compact else ["no benchmark reports registered"],
        }

    def _build_benchmark_report(
        self,
        *,
        benchmark: Dict[str, Any],
        run_result: Dict[str, Any],
        quality_report: Optional[Dict[str, Any]],
        anti_genericity_report: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        run_record = run_result.get("run_record", {})
        quality_score = float((quality_report or {}).get("overall_quality_score", 0.0))
        anti_score = float((anti_genericity_report or {}).get("anti_genericity_score", 0.0))

        passed = (
            run_result.get("success", False)
            and quality_score >= benchmark.get("min_quality_score", 0.50)
            and anti_score >= benchmark.get("min_anti_genericity_score", 0.40)
            and bool(run_record.get("outputs", {}).get("handoff_package_id"))
            and bool(run_record.get("outputs", {}).get("generation_control_payload_id"))
        )

        warnings = []
        warnings.extend(run_record.get("warnings", []))
        warnings.extend((quality_report or {}).get("warnings", []))
        warnings.extend((anti_genericity_report or {}).get("warnings", []))

        return {
            "benchmark_report_id": f"benchmark_report_{benchmark['benchmark_id']}",
            "benchmark_id": benchmark["benchmark_id"],
            "name": benchmark["name"],
            "run_id": run_record.get("run_id"),
            "passed": passed,
            "ready_for_chunk5": bool((quality_report or {}).get("ready_for_generation", False)),
            "quality_score": quality_score,
            "anti_genericity_score": anti_score,
            "min_quality_score": benchmark.get("min_quality_score", 0.50),
            "min_anti_genericity_score": benchmark.get("min_anti_genericity_score", 0.40),
            "run_status": run_record.get("status"),
            "selected_character_count": len(run_record.get("selected_character_ids", [])),
            "event_count": len(run_record.get("event_ids", [])),
            "step_count": len(run_record.get("steps", [])),
            "handoff_package_id": run_record.get("outputs", {}).get("handoff_package_id"),
            "generation_control_payload_id": run_record.get("outputs", {}).get("generation_control_payload_id"),
            "warnings": self._unique(warnings),
        }

    def _aggregate_reports(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        passed_count = sum(1 for report in reports if report.get("passed"))
        return {
            "aggregate_report_id": "simulation_benchmark_aggregate_latest",
            "benchmark_count": len(reports),
            "passed_count": passed_count,
            "failed_count": len(reports) - passed_count,
            "pass_rate": round(passed_count / max(1, len(reports)), 3),
            "average_quality_score": self._average([float(r.get("quality_score", 0.0)) for r in reports]),
            "average_anti_genericity_score": self._average([float(r.get("anti_genericity_score", 0.0)) for r in reports]),
            "ready_for_chunk5_count": sum(1 for report in reports if report.get("ready_for_chunk5")),
            "benchmark_ids": [report.get("benchmark_id") for report in reports],
            "warnings": self._aggregate_warnings(reports),
        }

    def _dark_academy_trial_benchmark(self) -> Dict[str, Any]:
        return {
            "benchmark_id": "dark_academy_trial",
            "name": "Dark Academy Trial Truth Reveal",
            "min_quality_score": 0.50,
            "min_anti_genericity_score": 0.40,
            "target_cast_size": 3,
            "story_request": {
                "story_request_id": "benchmark_story_dark_academy_trial",
                "cast_id": "cast_benchmark_dark_academy_trial",
                "scene_id": "scene_benchmark_trial",
                "plot_arc_id": "arc_benchmark_trial",
                "format": "novel",
                "primary_genres": ["dark_academy", "romance"],
                "tone_tags": ["tense", "courtly", "mythic"],
                "distinctive_elements": [
                    "oath court ranking ritual",
                    "cracked badge evidence",
                    "public proof harms the person loved",
                ],
                "constraints": {"must_preserve": "truth has emotional cost"},
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist", "love_interest", "antagonist"],
                "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
                "scene_goal": "Kael reveals the cracked badge in the oath court.",
                "plot_goal": "Make truth save Kael but damage Seren.",
                "conflicts": [
                    {
                        "conflict_id": "conflict_benchmark_truth",
                        "conflict_type": "truth",
                        "title": "Proof that Saves Kael Breaks Seren",
                        "participant_ids": ["char_kael", "char_seren"],
                        "core_issue": "Kael needs public proof, but the proof exposes Seren's protected source.",
                        "opposing_goals": {
                            "char_kael": "reveal the corrupted ranking",
                            "char_seren": "protect the source",
                        },
                        "linked_secret_ids": ["secret_rank_system_edited"],
                        "linked_evidence_ids": ["evidence_cracked_badge"],
                        "intensity": 0.85,
                        "stakes_score": 0.9,
                        "tension_score": 0.85,
                        "moral_complexity": 0.9,
                    }
                ],
            },
            "event_specs": [
                {
                    "event_id": "evt_benchmark_trial",
                    "event_type": "trial",
                    "event_name": "Kael places the cracked badge before the oath court.",
                    "actor_ids": ["char_kael"],
                    "target_ids": ["char_seren"],
                    "witness_ids": ["char_vask"],
                    "location_id": "location_court",
                    "visibility": "public",
                    "intensity": 0.85,
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"],
                }
            ],
        }

    def _romance_betrayal_benchmark(self) -> Dict[str, Any]:
        return {
            "benchmark_id": "romance_betrayal",
            "name": "Romance Betrayal Emotional Carryover",
            "min_quality_score": 0.45,
            "min_anti_genericity_score": 0.35,
            "target_cast_size": 2,
            "story_request": {
                "story_request_id": "benchmark_story_romance_betrayal",
                "cast_id": "cast_benchmark_romance_betrayal",
                "scene_id": "scene_benchmark_romance_betrayal",
                "format": "chapter",
                "primary_genres": ["romance", "drama"],
                "tone_tags": ["intimate", "restrained", "painful"],
                "distinctive_elements": ["love confession after betrayal", "private oath scar"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist", "love_interest"],
                "required_story_functions": ["drive_plot", "anchor_romance"],
                "scene_goal": "Seren privately confesses why she betrayed Kael.",
            },
            "event_specs": [
                {
                    "event_id": "evt_benchmark_confession",
                    "event_type": "private_confession",
                    "event_name": "Seren confesses the betrayal in the empty court.",
                    "actor_ids": ["char_seren"],
                    "target_ids": ["char_kael"],
                    "location_id": "location_court",
                    "visibility": "private",
                    "intensity": 0.78,
                }
            ],
        }

    def _faction_conflict_benchmark(self) -> Dict[str, Any]:
        return {
            "benchmark_id": "faction_conflict",
            "name": "Faction Political Conflict",
            "min_quality_score": 0.45,
            "min_anti_genericity_score": 0.35,
            "target_cast_size": 3,
            "story_request": {
                "story_request_id": "benchmark_story_faction_conflict",
                "cast_id": "cast_benchmark_faction_conflict",
                "scene_id": "scene_benchmark_faction",
                "format": "screenplay",
                "primary_genres": ["political_intrigue", "dark_fantasy"],
                "tone_tags": ["formal", "threatening", "ritualistic"],
                "distinctive_elements": ["ranking law", "court faction pressure"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist", "antagonist"],
                "required_story_functions": ["drive_plot", "create_conflict", "force_choice"],
                "scene_goal": "Vask uses faction pressure to corner Kael.",
            },
            "event_specs": [
                {
                    "event_id": "evt_benchmark_faction_pressure",
                    "event_type": "public_humiliation",
                    "event_name": "Vask challenges Kael's right to speak before the court.",
                    "actor_ids": ["char_vask"],
                    "target_ids": ["char_kael"],
                    "witness_ids": ["char_seren"],
                    "location_id": "location_court",
                    "visibility": "public",
                    "intensity": 0.8,
                }
            ],
        }

    def _minimal_scene_benchmark(self) -> Dict[str, Any]:
        return {
            "benchmark_id": "minimal_scene",
            "name": "Minimal Scene No Event Stress Test",
            "min_quality_score": 0.30,
            "min_anti_genericity_score": 0.25,
            "target_cast_size": 1,
            "story_request": {
                "story_request_id": "benchmark_story_minimal",
                "cast_id": "cast_benchmark_minimal",
                "scene_id": "scene_benchmark_minimal",
                "format": "scene",
                "primary_genres": ["drama"],
                "tone_tags": ["quiet"],
                "distinctive_elements": ["silent aftermath in the oath court"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist"],
                "required_story_functions": ["drive_plot"],
                "scene_goal": "A quiet aftermath scene after a public loss.",
            },
            "event_specs": [],
        }

    def _large_ensemble_benchmark(self) -> Dict[str, Any]:
        return {
            "benchmark_id": "large_ensemble",
            "name": "Large Ensemble Mixed Cast Request",
            "min_quality_score": 0.40,
            "min_anti_genericity_score": 0.30,
            "target_cast_size": 3,
            "story_request": {
                "story_request_id": "benchmark_story_large_ensemble",
                "cast_id": "cast_benchmark_large_ensemble",
                "scene_id": "scene_benchmark_large_ensemble",
                "format": "series_episode",
                "primary_genres": ["dark_academy", "mystery", "romance"],
                "tone_tags": ["tense", "ensemble", "secretive"],
                "distinctive_elements": ["many character types can be mixed without hard constraints"],
                "allow_any_character_count": True,
                "allow_project_created_characters": True,
                "required_roles": ["protagonist", "love_interest", "antagonist"],
                "required_story_functions": ["drive_plot", "anchor_romance", "create_conflict"],
                "scene_goal": "The core cast splits into alliances after the evidence appears.",
            },
            "event_specs": [
                {
                    "event_id": "evt_benchmark_ensemble_split",
                    "event_type": "public_event",
                    "event_name": "The court divides after the badge is revealed.",
                    "actor_ids": ["char_kael"],
                    "target_ids": ["char_seren", "char_vask"],
                    "location_id": "location_court",
                    "visibility": "public",
                    "intensity": 0.82,
                    "linked_secret_ids": ["secret_rank_system_edited"],
                    "linked_evidence_ids": ["evidence_cracked_badge"],
                }
            ],
        }

    def _aggregate_warnings(self, reports: List[Dict[str, Any]]) -> List[str]:
        failed = [report["benchmark_id"] for report in reports if not report.get("passed")]
        return [f"failed benchmarks: {failed}"] if failed else []

    def _average(self, values: List[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

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
