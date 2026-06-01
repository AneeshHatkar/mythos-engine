from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from backend.app.schemas.story_generation import (
    GeneratedStoryDeltaReport,
    StoryExportPackage,
    StoryGenerationOrchestrationReport,
    StoryMemoryUpdateContract,
    StoryProvenanceRecord,
)


class StoryExportStore:
    """Stores approved story generation artifacts as local export packages.

    Locked Chunk 5.44. This is a local JSON export store, not a cloud store.
    Later chunks can extend this into PDF/Docx/script exporters or object storage.
    """

    engine_name = "story_generation.story_export_store"

    def build_export_package(
        self,
        *,
        source_id: str,
        draft_id: str,
        request_id: str = "",
        story_payload: Dict[str, Any] | None = None,
        orchestration_report: StoryGenerationOrchestrationReport | None = None,
        provenance_record: StoryProvenanceRecord | None = None,
        delta_report: GeneratedStoryDeltaReport | None = None,
        memory_update_contract: StoryMemoryUpdateContract | None = None,
        export_root: str | Path = "exports/story_generation",
        export_format: str = "json",
        force_stage: bool = False,
    ) -> Dict[str, Any]:
        story_payload = story_payload or {}
        export_root = Path(export_root)

        export_package_id = f"story_export_{source_id}_{draft_id}_{request_id or 'default'}"
        export_dir = export_root / self._safe_id(source_id) / self._safe_id(request_id or "default") / self._safe_id(draft_id)

        export_checks = self._export_checks(
            story_payload=story_payload,
            orchestration_report=orchestration_report,
            provenance_record=provenance_record,
            delta_report=delta_report,
            memory_update_contract=memory_update_contract,
        )
        blocked_reasons = self._blocked_reasons(export_checks=export_checks, force_stage=force_stage)

        approved_for_export = not blocked_reasons and not force_stage
        export_status = "approved" if approved_for_export else "staged_blocked"

        artifact_paths = self._artifact_paths(export_dir=export_dir)
        manifest = self._export_manifest(
            export_package_id=export_package_id,
            source_id=source_id,
            draft_id=draft_id,
            request_id=request_id,
            export_format=export_format,
            approved_for_export=approved_for_export,
            export_status=export_status,
            artifact_paths=artifact_paths,
        )

        package = StoryExportPackage(
            export_package_id=export_package_id,
            source_id=source_id,
            draft_id=draft_id,
            request_id=request_id,
            export_status=export_status,
            export_format=export_format,
            approved_for_export=approved_for_export,
            export_path=str(export_dir),
            manifest_path=str(export_dir / "manifest.json"),
            artifact_paths={key: str(value) for key, value in artifact_paths.items()},
            export_manifest=manifest,
            story_payload=story_payload,
            orchestration_snapshot=self._model_snapshot(orchestration_report),
            provenance_snapshot=self._model_snapshot(provenance_record),
            delta_snapshot=self._model_snapshot(delta_report),
            memory_contract_snapshot=self._model_snapshot(memory_update_contract),
            export_checks=export_checks,
            blocked_reasons=blocked_reasons,
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                draft_id=draft_id,
                request_id=request_id,
                approved_for_export=approved_for_export,
                export_dir=export_dir,
                artifact_paths=artifact_paths,
            ),
            warnings=self._warnings(
                approved_for_export=approved_for_export,
                blocked_reasons=blocked_reasons,
                story_payload=story_payload,
            ),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_export_package": package,
            "story_export_package_dict": package.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_benchmark_pack",
                "payload_keys": [
                    "story_export_package",
                    "story_generation_orchestration_report",
                    "story_context",
                ],
            },
        }

    def write_export_package(self, *, package: StoryExportPackage) -> Dict[str, Any]:
        export_dir = Path(package.export_path)
        export_dir.mkdir(parents=True, exist_ok=True)

        payloads = {
            "manifest": package.export_manifest,
            "story_payload": package.story_payload,
            "orchestration_snapshot": package.orchestration_snapshot,
            "provenance_snapshot": package.provenance_snapshot,
            "delta_snapshot": package.delta_snapshot,
            "memory_contract_snapshot": package.memory_contract_snapshot,
            "export_package": package.model_dump(mode="json"),
        }

        written_files = {}

        for name, payload in payloads.items():
            path = export_dir / f"{name}.json"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            written_files[name] = str(path)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "export_package_id": package.export_package_id,
            "export_path": str(export_dir),
            "written_files": written_files,
        }

    def read_export_package(self, *, export_path: str | Path) -> Dict[str, Any]:
        export_path = Path(export_path)
        package_path = export_path / "export_package.json"

        if not package_path.exists():
            return {
                "success": False,
                "engine_name": self.engine_name,
                "error": f"Export package not found: {package_path}",
            }

        payload = json.loads(package_path.read_text(encoding="utf-8"))
        package = StoryExportPackage(**payload)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "story_export_package": package,
            "story_export_package_dict": package.model_dump(mode="json"),
        }

    def validate_export_package(self, *, package: StoryExportPackage) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if package.export_package_id:
            passed.append("export_package_id_present")
        else:
            blockers.append("export_package_id missing")

        if package.source_id:
            passed.append("source_id_present")
        else:
            blockers.append("source_id missing")

        if package.export_manifest:
            passed.append("export_manifest_present")
        else:
            blockers.append("export manifest missing")

        if package.export_path:
            passed.append("export_path_present")
        else:
            blockers.append("export path missing")

        if package.approved_for_export and package.blocked_reasons:
            blockers.append("package cannot be approved while blocked reasons exist")

        if not package.story_payload:
            warnings.append("story payload is empty")

        if package.blocked_reasons:
            warnings.append("export package has blocked reasons")

        if package.warnings:
            warnings.extend(package.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_export_package(self, *, package: StoryExportPackage) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "export_package_id": package.export_package_id,
                "source_id": package.source_id,
                "draft_id": package.draft_id,
                "request_id": package.request_id,
                "export_status": package.export_status,
                "approved_for_export": package.approved_for_export,
                "export_format": package.export_format,
                "artifact_count": len(package.artifact_paths),
                "export_check_count": len(package.export_checks),
                "blocked_reason_count": len(package.blocked_reasons),
                "warning_count": len(package.warnings),
                "export_path": package.export_path,
            },
        }

    def build_export_text(self, *, package: StoryExportPackage) -> Dict[str, Any]:
        lines = [
            f"# Story Export Package: {package.source_id}",
            "",
            f"Package ID: {package.export_package_id}",
            f"Draft ID: {package.draft_id}",
            f"Request ID: {package.request_id}",
            f"Status: {package.export_status}",
            f"Approved for export: {package.approved_for_export}",
            f"Export path: {package.export_path}",
            "",
            "## Export Checks",
        ]

        for item in package.export_checks:
            lines.append(f"- {item.get('check_name')}: {item.get('status')}")

        lines.append("")
        lines.append("## Blocked Reasons")
        for item in package.blocked_reasons:
            lines.append(f"- [{item.get('severity')}] {item.get('reason_type')}: {item.get('description')}")

        lines.append("")
        lines.append("## Artifact Paths")
        for key, value in package.artifact_paths.items():
            lines.append(f"- {key}: {value}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "export_text": "\n".join(lines),
        }

    def _export_checks(
        self,
        *,
        story_payload: Dict[str, Any],
        orchestration_report: StoryGenerationOrchestrationReport | None,
        provenance_record: StoryProvenanceRecord | None,
        delta_report: GeneratedStoryDeltaReport | None,
        memory_update_contract: StoryMemoryUpdateContract | None,
    ) -> List[Dict[str, Any]]:
        checks = []

        checks.append(
            {
                "check_id": "check_story_payload_present",
                "check_name": "story_payload_present",
                "status": "passed" if story_payload else "warning",
                "severity": "medium" if not story_payload else "none",
                "description": "Story payload is present." if story_payload else "Story payload is empty.",
            }
        )

        checks.append(
            {
                "check_id": "check_orchestration_ready_for_export",
                "check_name": "orchestration_ready_for_export",
                "status": "passed" if orchestration_report and orchestration_report.ready_for_export else "failed",
                "severity": "critical",
                "description": "Orchestration report must be ready for export.",
            }
        )

        checks.append(
            {
                "check_id": "check_provenance_approved_for_export",
                "check_name": "provenance_approved_for_export",
                "status": "passed" if provenance_record and provenance_record.approved_for_export else "failed",
                "severity": "critical",
                "description": "Provenance must be approved for export.",
            }
        )

        checks.append(
            {
                "check_id": "check_delta_available",
                "check_name": "delta_report_available",
                "status": "passed" if delta_report is not None else "warning",
                "severity": "medium",
                "description": "Delta report should be included for memory and audit trace.",
            }
        )

        checks.append(
            {
                "check_id": "check_memory_contract_available",
                "check_name": "memory_contract_available",
                "status": "passed" if memory_update_contract is not None else "warning",
                "severity": "medium",
                "description": "Memory update contract should be included for audit trace.",
            }
        )

        return checks

    def _blocked_reasons(self, *, export_checks: List[Dict[str, Any]], force_stage: bool) -> List[Dict[str, Any]]:
        reasons = []

        if force_stage:
            reasons.append(
                {
                    "reason_id": "force_stage_enabled",
                    "reason_type": "force_stage",
                    "severity": "medium",
                    "description": "Export package was intentionally staged instead of approved.",
                }
            )

        for check in export_checks:
            if check.get("status") == "failed":
                reasons.append(
                    {
                        "reason_id": f"blocked_{check.get('check_id')}",
                        "reason_type": check.get("check_name"),
                        "severity": check.get("severity", "high"),
                        "description": check.get("description"),
                    }
                )

        return reasons

    def _artifact_paths(self, *, export_dir: Path) -> Dict[str, Path]:
        return {
            "manifest": export_dir / "manifest.json",
            "story_payload": export_dir / "story_payload.json",
            "orchestration_snapshot": export_dir / "orchestration_snapshot.json",
            "provenance_snapshot": export_dir / "provenance_snapshot.json",
            "delta_snapshot": export_dir / "delta_snapshot.json",
            "memory_contract_snapshot": export_dir / "memory_contract_snapshot.json",
            "export_package": export_dir / "export_package.json",
        }

    def _export_manifest(
        self,
        *,
        export_package_id: str,
        source_id: str,
        draft_id: str,
        request_id: str,
        export_format: str,
        approved_for_export: bool,
        export_status: str,
        artifact_paths: Dict[str, Path],
    ) -> Dict[str, Any]:
        return {
            "export_package_id": export_package_id,
            "source_id": source_id,
            "draft_id": draft_id,
            "request_id": request_id,
            "export_format": export_format,
            "approved_for_export": approved_for_export,
            "export_status": export_status,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "artifact_paths": {key: str(path) for key, path in artifact_paths.items()},
            "store_version": "chunk_5_44_local_json_v1",
        }

    def _model_snapshot(self, model: Any) -> Dict[str, Any]:
        if model is None:
            return {"available": False}
        if hasattr(model, "model_dump"):
            payload = model.model_dump(mode="json")
            payload["available"] = True
            return payload
        if isinstance(model, dict):
            payload = dict(model)
            payload["available"] = True
            return payload
        return {"available": True, "value": str(model)}

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        draft_id: str,
        request_id: str,
        approved_for_export: bool,
        export_dir: Path,
        artifact_paths: Dict[str, Path],
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "draft_id": draft_id,
            "request_id": request_id,
            "approved_for_export": approved_for_export,
            "export_path": str(export_dir),
            "artifact_paths": {key: str(path) for key, path in artifact_paths.items()},
            "rules": [
                "Do not publish staged_blocked exports.",
                "Every export must carry orchestration and provenance snapshots.",
                "Every export should preserve memory contract and delta trace for auditability.",
                "Future PDF/script/novel exporters should read from this package instead of raw engine state.",
            ],
        }

    def _warnings(
        self,
        *,
        approved_for_export: bool,
        blocked_reasons: List[Dict[str, Any]],
        story_payload: Dict[str, Any],
    ) -> List[str]:
        warnings = []
        if not approved_for_export:
            warnings.append("Export package is not approved for publishing.")
        if blocked_reasons:
            warnings.append(f"{len(blocked_reasons)} export blocker(s) present.")
        if not story_payload:
            warnings.append("Story payload is empty.")
        return warnings

    def _safe_id(self, value: Any) -> str:
        return "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value)).strip("_")[:80] or "item"

    def _unique(self, values: List[str]) -> List[str]:
        result = []
        seen = set()
        for value in values:
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result
