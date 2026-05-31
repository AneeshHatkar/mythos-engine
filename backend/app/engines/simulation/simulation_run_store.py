import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SimulationRunStore:
    """Simple JSON-backed store for simulation runs and Chunk 4 reports.

    This is intentionally lightweight. Later chunks can replace or extend this
    with SQLite/Postgres, but this store gives us stable local persistence now.
    """

    engine_name = "simulation.simulation_run_store"

    def __init__(self, base_dir: str | Path = "reports/simulation_runs") -> None:
        self.base_dir = Path(base_dir)
        self.runs_dir = self.base_dir / "runs"
        self.bundles_dir = self.base_dir / "bundles"
        self.reports_dir = self.base_dir / "reports"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.bundles_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def save_run(
        self,
        *,
        run_record: Dict[str, Any],
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        run_id = run_record.get("run_id")
        if not run_id:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": ["run_record requires run_id"],
            }

        path = self.runs_dir / f"{run_id}.json"
        if path.exists() and not overwrite:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "path": str(path),
                "errors": ["run already exists and overwrite is false"],
            }

        self._write_json(path, run_record)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "path": str(path),
        }

    def load_run(self, *, run_id: str) -> Dict[str, Any]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": [f"run {run_id} not found"],
            }

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "run_record": self._read_json(path),
            "path": str(path),
        }

    def list_runs(self) -> Dict[str, Any]:
        records = []
        for path in sorted(self.runs_dir.glob("*.json")):
            data = self._read_json(path)
            records.append(
                {
                    "run_id": data.get("run_id", path.stem),
                    "status": data.get("status"),
                    "selected_character_count": len(data.get("selected_character_ids", [])),
                    "event_count": len(data.get("event_ids", [])),
                    "step_count": len(data.get("steps", [])),
                    "warning_count": len(data.get("warnings", [])),
                    "error_count": len(data.get("errors", [])),
                    "path": str(path),
                }
            )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_count": len(records),
            "runs": records,
        }

    def delete_run(self, *, run_id: str) -> Dict[str, Any]:
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": [f"run {run_id} not found"],
            }

        path.unlink()

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "deleted_path": str(path),
        }

    def save_quality_report(
        self,
        *,
        quality_report: Dict[str, Any],
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        report_id = quality_report.get("quality_report_id")
        if not report_id:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": ["quality_report requires quality_report_id"],
            }

        path = self.reports_dir / f"{report_id}.json"
        if path.exists() and not overwrite:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "report_id": report_id,
                "errors": ["quality report already exists and overwrite is false"],
            }

        self._write_json(path, quality_report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "report_id": report_id,
            "path": str(path),
        }

    def save_anti_genericity_report(
        self,
        *,
        anti_genericity_report: Dict[str, Any],
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        report_id = anti_genericity_report.get("anti_genericity_report_id")
        if not report_id:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": ["anti_genericity_report requires anti_genericity_report_id"],
            }

        path = self.reports_dir / f"{report_id}.json"
        if path.exists() and not overwrite:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "report_id": report_id,
                "errors": ["anti-genericity report already exists and overwrite is false"],
            }

        self._write_json(path, anti_genericity_report)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "report_id": report_id,
            "path": str(path),
        }

    def export_run_bundle(
        self,
        *,
        state: Any,
        run_id: str,
        include_quality: bool = True,
        include_anti_genericity: bool = True,
        include_handoff: bool = True,
        include_generation_control: bool = True,
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
        bundle = {
            "bundle_id": f"bundle_{run_id}",
            "run_id": run_id,
            "run_record": run,
            "quality_report": None,
            "anti_genericity_report": None,
            "handoff_package": None,
            "generation_control_payload": None,
            "metadata": {
                "engine_name": self.engine_name,
                "included_sections": [],
            },
        }

        if include_quality:
            quality_id = f"quality_{run_id}"
            bundle["quality_report"] = state.metadata.get("simulation_quality_reports", {}).get(quality_id)
            if bundle["quality_report"]:
                bundle["metadata"]["included_sections"].append("quality_report")

        if include_anti_genericity:
            anti_id = f"anti_genericity_{run_id}"
            bundle["anti_genericity_report"] = state.metadata.get("simulation_anti_genericity_reports", {}).get(anti_id)
            if bundle["anti_genericity_report"]:
                bundle["metadata"]["included_sections"].append("anti_genericity_report")

        if include_handoff:
            handoff_id = outputs.get("handoff_package_id")
            bundle["handoff_package"] = state.metadata.get("handoff_packages", {}).get(handoff_id)
            if bundle["handoff_package"]:
                bundle["metadata"]["included_sections"].append("handoff_package")

        if include_generation_control:
            control_id = outputs.get("generation_control_payload_id")
            bundle["generation_control_payload"] = state.metadata.get("generation_control_payloads", {}).get(control_id)
            if bundle["generation_control_payload"]:
                bundle["metadata"]["included_sections"].append("generation_control_payload")

        path = self.bundles_dir / f"bundle_{run_id}.json"
        self._write_json(path, bundle)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "bundle_id": bundle["bundle_id"],
            "bundle": bundle,
            "path": str(path),
        }

    def import_run_bundle(
        self,
        *,
        state: Any,
        bundle_path: str | Path,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        path = Path(bundle_path)
        if not path.exists():
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": [f"bundle path {path} not found"],
            }

        bundle = self._read_json(path)
        run = bundle.get("run_record")
        if not run or not run.get("run_id"):
            return {
                "success": False,
                "engine_name": self.engine_name,
                "errors": ["bundle has no valid run_record"],
            }

        run_id = run["run_id"]
        if run_id in state.metadata.get("simulation_runs", {}) and not overwrite:
            return {
                "success": False,
                "engine_name": self.engine_name,
                "run_id": run_id,
                "errors": ["run already exists in state and overwrite is false"],
            }

        state.metadata.setdefault("simulation_runs", {})[run_id] = run

        quality = bundle.get("quality_report")
        if quality and quality.get("quality_report_id"):
            state.metadata.setdefault("simulation_quality_reports", {})[quality["quality_report_id"]] = quality

        anti = bundle.get("anti_genericity_report")
        if anti and anti.get("anti_genericity_report_id"):
            state.metadata.setdefault("simulation_anti_genericity_reports", {})[anti["anti_genericity_report_id"]] = anti

        handoff = bundle.get("handoff_package")
        if handoff and handoff.get("package_id"):
            state.metadata.setdefault("handoff_packages", {})[handoff["package_id"]] = handoff

        control = bundle.get("generation_control_payload")
        if control and control.get("payload_id"):
            state.metadata.setdefault("generation_control_payloads", {})[control["payload_id"]] = control

        state.metadata.setdefault("simulation_run_store_history", []).append(
            {
                "action": "import_run_bundle",
                "run_id": run_id,
                "bundle_path": str(path),
                "included_sections": bundle.get("metadata", {}).get("included_sections", []),
            }
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "run_id": run_id,
            "bundle_id": bundle.get("bundle_id"),
            "updated_state": state,
        }

    def save_state_run_index(
        self,
        *,
        state: Any,
        index_id: str = "simulation_run_index",
    ) -> Dict[str, Any]:
        runs = state.metadata.get("simulation_runs", {})
        quality = state.metadata.get("simulation_quality_reports", {})
        anti = state.metadata.get("simulation_anti_genericity_reports", {})

        index = {
            "index_id": index_id,
            "run_count": len(runs),
            "quality_report_count": len(quality),
            "anti_genericity_report_count": len(anti),
            "runs": [
                {
                    "run_id": run_id,
                    "status": run.get("status"),
                    "handoff_package_id": run.get("outputs", {}).get("handoff_package_id"),
                    "generation_control_payload_id": run.get("outputs", {}).get("generation_control_payload_id"),
                    "quality_report_id": f"quality_{run_id}" if f"quality_{run_id}" in quality else None,
                    "anti_genericity_report_id": f"anti_genericity_{run_id}" if f"anti_genericity_{run_id}" in anti else None,
                }
                for run_id, run in runs.items()
            ],
        }

        path = self.base_dir / f"{index_id}.json"
        self._write_json(path, index)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "index_id": index_id,
            "path": str(path),
            "index": index,
        }

    def _write_json(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str), encoding="utf-8")

    def _read_json(self, path: Path) -> Dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))
