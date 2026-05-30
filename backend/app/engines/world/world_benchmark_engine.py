from typing import Any, Dict, List

from backend.app.engines.base import BaseEngine
from backend.app.engines.world.world_orchestrator_engine import WorldOrchestratorEngine
from backend.app.engines.world.world_template_engine import WorldTemplateEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldBenchmarkEngine(BaseEngine):
    """Runs benchmark scenarios across multiple world templates.

    This validates that Chunk 2 is not overfit to a single world like Velmora.

    It checks:
    - dark academy empire
    - civilization simulation
    - dystopian megacity
    - romance kingdom
    - mythic religious world
    - movie-scale world
    - seven-novel saga

    Later this can become an evaluation suite for:
    - model regressions
    - dataset quality
    - template coverage
    - originality benchmarks
    - world generation dashboards
    """

    engine_name = "world.benchmark_engine"

    BENCHMARK_CASES: List[Dict[str, Any]] = [
        {
            "benchmark_id": "bench_dark_academy_empire",
            "template_id": "dark_academy_empire",
            "world_name": "Velmora",
            "seed_premise": (
                "A late imperial academy empire where noble schools, oath law, relic debt, "
                "forbidden archives, and destiny-bearing students destabilize society."
            ),
            "minimum_quality_score": 0.65,
            "required_sections": [
                "identity",
                "rules",
                "chronology",
                "geography",
                "society",
                "power_structure",
                "economy",
                "law",
                "belief",
                "culture",
                "quality_summary",
                "world_bible_export",
            ],
        },
        {
            "benchmark_id": "bench_civilization_simulation",
            "template_id": "civilization_simulation",
            "world_name": "Oranth",
            "seed_premise": (
                "A civilization-scale world where resource scarcity, regional autonomy, "
                "war readiness, infrastructure decay, and institutional collapse interact."
            ),
            "minimum_quality_score": 0.6,
            "required_sections": [
                "identity",
                "geography",
                "infrastructure",
                "economy",
                "law",
                "military_security",
                "civilization_pressure",
                "causality_graph",
                "quality_summary",
            ],
        },
        {
            "benchmark_id": "bench_dystopian_megacity",
            "template_id": "dystopian_megacity",
            "world_name": "Neon Veyr",
            "seed_premise": (
                "A controlled megacity where surveillance bureaus, movement permits, "
                "classification systems, data towers, and underground identity markets shape life."
            ),
            "minimum_quality_score": 0.55,
            "required_sections": [
                "identity",
                "geography",
                "society",
                "law",
                "knowledge_education",
                "technology_magic_science",
                "power_structure",
                "quality_summary",
            ],
        },
        {
            "benchmark_id": "bench_romance_kingdom",
            "template_id": "romance_kingdom",
            "world_name": "Caelivane",
            "seed_premise": (
                "A courtly kingdom where marriage law, inheritance politics, family honor, "
                "public reputation, class-coded rituals, and private desire drive political consequences."
            ),
            "minimum_quality_score": 0.55,
            "required_sections": [
                "identity",
                "society",
                "law",
                "culture",
                "power_structure",
                "belief",
                "artifacts",
                "quality_summary",
            ],
        },
        {
            "benchmark_id": "bench_mythic_religious_world",
            "template_id": "mythic_religious_world",
            "world_name": "Thyros",
            "seed_premise": (
                "A sacred world where dead gods, broken vows, pilgrimage roads, prophecy disputes, "
                "heresies, ritual law, and holy archives decide political legitimacy."
            ),
            "minimum_quality_score": 0.55,
            "required_sections": [
                "identity",
                "belief",
                "culture",
                "law",
                "chronology",
                "artifacts",
                "civilization_pressure",
                "quality_summary",
            ],
        },
        {
            "benchmark_id": "bench_movie_scale_world",
            "template_id": "movie_scale_world",
            "world_name": "One Bell City",
            "seed_premise": (
                "A focused cinematic city where one sealed archive, one forbidden bell, "
                "one political trial, and one impossible witness reveal a deeper national lie."
            ),
            "minimum_quality_score": 0.5,
            "required_sections": [
                "identity",
                "geography",
                "law",
                "artifacts",
                "aesthetic_texture",
                "civilization_pressure",
                "quality_summary",
                "world_bible_export",
            ],
        },
        {
            "benchmark_id": "bench_seven_novel_saga",
            "template_id": "seven_novel_saga",
            "world_name": "The Ashen Crown",
            "seed_premise": (
                "A seven-novel saga world where academy youth conflicts slowly reveal oath betrayal, "
                "relic memory, class collapse, forbidden romance, faction war, and destiny pressure."
            ),
            "minimum_quality_score": 0.65,
            "required_sections": [
                "identity",
                "rules",
                "chronology",
                "society",
                "power_structure",
                "economy",
                "belief",
                "culture",
                "artifacts",
                "civilization_pressure",
                "causality_graph",
                "quality_summary",
                "dataset_metadata",
                "world_bible_export",
            ],
        },
    ]

    def __init__(self) -> None:
        self.template_engine = WorldTemplateEngine()
        self.orchestrator_engine = WorldOrchestratorEngine()

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        selected_benchmark_ids = payload.get("benchmark_ids")
        run_full_orchestration = payload.get("run_full_orchestration", True)
        user_rating = payload.get("user_rating", 9)
        source_mode = payload.get("source_mode", "human_approved_synthetic")

        warnings: List[str] = []
        errors: List[str] = []

        benchmark_cases = self._select_cases(selected_benchmark_ids)

        if selected_benchmark_ids and not benchmark_cases:
            errors.append("No matching benchmark_ids found.")

        results = []

        for case in benchmark_cases:
            if run_full_orchestration:
                case_result = self._run_full_case(
                    case=case,
                    user_rating=user_rating,
                    source_mode=source_mode,
                )
            else:
                case_result = self._validate_template_case(case)

            results.append(case_result)

        summary = self._build_summary(results)

        return self.build_result(
            success=len(errors) == 0 and summary["failed_count"] == 0,
            data={
                "benchmark_summary": summary,
                "benchmark_results": results,
                "benchmark_cases": benchmark_cases,
                "training_notes": [
                    "Benchmark pack validates multiple world modes, not only one project world.",
                    "Full orchestration benchmarks can catch integration regressions.",
                    "Template-only benchmarks can quickly verify preset coverage.",
                    "Future ML chunks can add embedding originality checks and human preference scores.",
                ],
            },
            warnings=warnings,
            errors=errors,
            generated_object_ids=[],
        )

    def _select_cases(self, selected_benchmark_ids: Any) -> List[Dict[str, Any]]:
        if not selected_benchmark_ids:
            return list(self.BENCHMARK_CASES)

        selected = set(selected_benchmark_ids)

        return [
            case
            for case in self.BENCHMARK_CASES
            if case["benchmark_id"] in selected
        ]

    def _validate_template_case(self, case: Dict[str, Any]) -> Dict[str, Any]:
        template_result = self.template_engine.run(
            {
                "template_id": case["template_id"],
                "seed_premise": case["seed_premise"],
            }
        )

        passed = template_result.success and "orchestrator_payload" in template_result.data

        return {
            "benchmark_id": case["benchmark_id"],
            "template_id": case["template_id"],
            "world_name": case["world_name"],
            "mode": "template_validation_only",
            "passed": passed,
            "quality_score": None,
            "section_completion_ratio": None,
            "missing_required_sections": [],
            "warnings": template_result.warnings,
            "errors": template_result.errors,
        }

    def _run_full_case(
        self,
        *,
        case: Dict[str, Any],
        user_rating: int,
        source_mode: str,
    ) -> Dict[str, Any]:
        orchestrator_result = self.orchestrator_engine.run(
            {
                "template_id": case["template_id"],
                "world_name": case["world_name"],
                "seed_premise": case["seed_premise"],
                "user_rating": user_rating,
                "source_mode": source_mode,
                "export_format": "markdown_and_json",
            }
        )

        world_state = orchestrator_result.data.get("world_state", {})
        orchestration_summary = orchestrator_result.data.get("orchestration_summary", {})
        quality_summary = world_state.get("quality_summary", {})

        quality_score = self._average_quality_score(quality_summary)
        missing_required_sections = [
            section
            for section in case["required_sections"]
            if world_state.get(section) in (None, {}, [], "")
        ]

        passed = (
            orchestrator_result.success
            and quality_score >= case["minimum_quality_score"]
            and not missing_required_sections
            and orchestration_summary.get("failed_engine_count", 0) == 0
        )

        return {
            "benchmark_id": case["benchmark_id"],
            "template_id": case["template_id"],
            "world_name": case["world_name"],
            "mode": "full_orchestration",
            "passed": passed,
            "minimum_quality_score": case["minimum_quality_score"],
            "quality_score": quality_score,
            "quality_tier": quality_summary.get("quality_tier"),
            "section_completion_ratio": orchestration_summary.get("core_section_completion_ratio"),
            "missing_required_sections": missing_required_sections,
            "engine_count": orchestration_summary.get("engine_count"),
            "failed_engine_count": orchestration_summary.get("failed_engine_count"),
            "world_bible_export_id": world_state.get("world_bible_export", {}).get("export_id"),
            "snapshot_id": world_state.get("snapshot", {}).get("snapshot_id"),
            "warnings": orchestrator_result.warnings,
            "errors": orchestrator_result.errors,
        }

    def _average_quality_score(self, quality_summary: Dict[str, Any]) -> float:
        scores = [
            quality_summary.get("consistency_score"),
            quality_summary.get("originality_score"),
            quality_summary.get("story_potential_score"),
            quality_summary.get("training_readiness_score"),
        ]

        numeric_scores = [
            float(score)
            for score in scores
            if isinstance(score, (int, float))
        ]

        if not numeric_scores:
            return 0.0

        return round(sum(numeric_scores) / len(numeric_scores), 3)

    def _build_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = len(results)
        passed = [result for result in results if result["passed"]]
        failed = [result for result in results if not result["passed"]]

        quality_scores = [
            result["quality_score"]
            for result in results
            if isinstance(result.get("quality_score"), (int, float))
        ]

        average_quality_score = (
            round(sum(quality_scores) / len(quality_scores), 3)
            if quality_scores
            else None
        )

        return {
            "total_count": total,
            "passed_count": len(passed),
            "failed_count": len(failed),
            "pass_rate": round(len(passed) / total, 3) if total else 0.0,
            "average_quality_score": average_quality_score,
            "failed_benchmark_ids": [result["benchmark_id"] for result in failed],
            "passed_benchmark_ids": [result["benchmark_id"] for result in passed],
        }
