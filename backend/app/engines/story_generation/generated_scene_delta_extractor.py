from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.story_generation import GeneratedChapter, GeneratedStoryDeltaReport, StoryProvenanceRecord


class GeneratedSceneDeltaExtractor:
    """Extracts memory-safe story deltas from generated scene/chapter text.

    Locked Chunk 5.40. This engine converts generated narrative output into
    structured deltas that can later feed the Story Memory Update Contract.
    """

    engine_name = "story_generation.generated_scene_delta_extractor"

    def extract_deltas(
        self,
        *,
        source_id: str,
        draft_id: str,
        generated_text: str | None = None,
        chapter: GeneratedChapter | None = None,
        provenance_record: StoryProvenanceRecord | None = None,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}
        text = self._combined_text(generated_text=generated_text, chapter=chapter)

        character_deltas = self._character_deltas(text=text, chapter=chapter, story_context=story_context)
        relationship_deltas = self._relationship_deltas(text=text, chapter=chapter, story_context=story_context)
        secret_deltas = self._secret_deltas(text=text, chapter=chapter, story_context=story_context)
        causal_deltas = self._causal_deltas(text=text, chapter=chapter, story_context=story_context)
        world_deltas = self._world_deltas(text=text, chapter=chapter, story_context=story_context)
        object_deltas = self._object_deltas(text=text, story_context=story_context)
        open_loop_deltas = self._open_loop_deltas(text=text, chapter=chapter, story_context=story_context)
        resolved_loop_deltas = self._resolved_loop_deltas(text=text, story_context=story_context)

        protected_impacts = self._protected_element_impacts(
            text=text,
            provenance_record=provenance_record,
            all_deltas=character_deltas
            + relationship_deltas
            + secret_deltas
            + causal_deltas
            + world_deltas
            + object_deltas
            + open_loop_deltas
            + resolved_loop_deltas,
        )

        memory_candidates = self._memory_update_candidates(
            character_deltas=character_deltas,
            relationship_deltas=relationship_deltas,
            secret_deltas=secret_deltas,
            causal_deltas=causal_deltas,
            world_deltas=world_deltas,
            object_deltas=object_deltas,
            open_loop_deltas=open_loop_deltas,
            resolved_loop_deltas=resolved_loop_deltas,
            provenance_record=provenance_record,
        )

        report = GeneratedStoryDeltaReport(
            delta_report_id=f"generated_story_delta_{source_id}_{draft_id}",
            source_id=source_id,
            draft_id=draft_id,
            extraction_status="completed",
            character_deltas=character_deltas,
            relationship_deltas=relationship_deltas,
            secret_deltas=secret_deltas,
            causal_deltas=causal_deltas,
            world_deltas=world_deltas,
            object_deltas=object_deltas,
            open_loop_deltas=open_loop_deltas,
            resolved_loop_deltas=resolved_loop_deltas,
            memory_update_candidates=memory_candidates,
            protected_element_impacts=protected_impacts,
            delta_summary=self._delta_summary(
                character_deltas=character_deltas,
                relationship_deltas=relationship_deltas,
                secret_deltas=secret_deltas,
                causal_deltas=causal_deltas,
                world_deltas=world_deltas,
                object_deltas=object_deltas,
                open_loop_deltas=open_loop_deltas,
                resolved_loop_deltas=resolved_loop_deltas,
                memory_candidates=memory_candidates,
                protected_impacts=protected_impacts,
            ),
            downstream_constraints=self._downstream_constraints(
                source_id=source_id,
                draft_id=draft_id,
                memory_candidates=memory_candidates,
                provenance_record=provenance_record,
            ),
            warnings=self._warnings(text=text, provenance_record=provenance_record, memory_candidates=memory_candidates),
        )

        return {
            "success": True,
            "engine_name": self.engine_name,
            "generated_story_delta_report": report,
            "generated_story_delta_report_dict": report.model_dump(mode="json"),
            "handoff_to_next_engine": {
                "next_engine": "story_generation.story_memory_update_contract",
                "payload_keys": [
                    "generated_story_delta_report",
                    "story_provenance_record",
                    "story_context",
                ],
            },
        }

    def validate_delta_report(self, *, report: GeneratedStoryDeltaReport) -> Dict[str, Any]:
        blockers: List[str] = []
        warnings: List[str] = []
        passed: List[str] = []

        if report.delta_report_id:
            passed.append("delta_report_id_present")
        else:
            blockers.append("delta_report_id missing")

        if report.source_id and report.draft_id:
            passed.append("source_and_draft_ids_present")
        else:
            blockers.append("source_id or draft_id missing")

        if report.delta_summary:
            passed.append("delta_summary_present")
        else:
            warnings.append("delta summary missing")

        if report.downstream_constraints:
            passed.append("downstream_constraints_present")
        else:
            warnings.append("downstream constraints missing")

        if not report.memory_update_candidates:
            warnings.append("no memory update candidates extracted")

        if report.warnings:
            warnings.extend(report.warnings)

        return {
            "success": True,
            "engine_name": self.engine_name,
            "valid": not blockers,
            "blockers": blockers,
            "warnings": self._unique(warnings),
            "passed_checks": passed,
        }

    def summarize_delta_report(self, *, report: GeneratedStoryDeltaReport) -> Dict[str, Any]:
        return {
            "success": True,
            "engine_name": self.engine_name,
            "summary": {
                "delta_report_id": report.delta_report_id,
                "source_id": report.source_id,
                "draft_id": report.draft_id,
                "character_delta_count": len(report.character_deltas),
                "relationship_delta_count": len(report.relationship_deltas),
                "secret_delta_count": len(report.secret_deltas),
                "causal_delta_count": len(report.causal_deltas),
                "world_delta_count": len(report.world_deltas),
                "object_delta_count": len(report.object_deltas),
                "open_loop_delta_count": len(report.open_loop_deltas),
                "resolved_loop_delta_count": len(report.resolved_loop_deltas),
                "memory_candidate_count": len(report.memory_update_candidates),
                "protected_impact_count": len(report.protected_element_impacts),
                "warning_count": len(report.warnings),
            },
        }

    def build_delta_report_text(self, *, report: GeneratedStoryDeltaReport) -> Dict[str, Any]:
        lines = [
            f"# Generated Story Delta Report: {report.source_id}",
            "",
            f"Draft ID: {report.draft_id}",
            f"Status: {report.extraction_status}",
            "",
            "## Delta Summary",
        ]

        for key, value in report.delta_summary.items():
            lines.append(f"- {key}: {value}")

        lines.append("")
        lines.append("## Memory Update Candidates")
        for item in report.memory_update_candidates:
            lines.append(f"- {item.get('candidate_type')}: {item.get('value')}")

        lines.append("")
        lines.append("## Protected Element Impacts")
        for item in report.protected_element_impacts:
            lines.append(f"- {item.get('impact_type')}: {item.get('value')}")

        return {
            "success": True,
            "engine_name": self.engine_name,
            "delta_report_text": "\n".join(lines),
        }

    def _combined_text(self, *, generated_text: str | None, chapter: GeneratedChapter | None) -> str:
        parts = []
        if generated_text:
            parts.append(generated_text)
        if chapter and chapter.chapter_text:
            parts.append(chapter.chapter_text)
        return "\n".join(parts).strip()

    def _character_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = list(chapter.used_character_ids if chapter else [])
        ids += story_context.get("known_character_ids", [])
        return self._presence_deltas(ids, text, "character", "character_state")

    def _relationship_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = list(chapter.used_relationship_ids if chapter else [])
        ids += story_context.get("known_relationship_ids", [])
        return self._presence_deltas(ids, text, "relationship", "relationship_state")

    def _secret_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = list(chapter.used_secret_ids if chapter else [])
        ids += story_context.get("known_secret_ids", [])
        deltas = self._presence_deltas(ids, text, "secret", "secret_state")
        lowered = text.lower()
        for delta in deltas:
            if any(marker in lowered for marker in ["reveals", "revealed", "exposes", "confesses", "admits"]):
                delta["delta_action"] = "reveal_or_pressure"
        return deltas

    def _causal_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = list(chapter.used_causal_ids if chapter else [])
        ids += story_context.get("known_causal_ids", [])
        deltas = self._presence_deltas(ids, text, "causal", "causal_state")
        lowered = text.lower()
        for delta in deltas:
            if any(marker in lowered for marker in ["therefore", "because", "forces", "causes", "consequence"]):
                delta["delta_action"] = "causal_progression"
        return deltas

    def _world_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = list(chapter.used_world_details if chapter else [])
        ids += story_context.get("known_world_details", [])
        return self._presence_deltas(ids, text, "world_detail", "world_state")

    def _object_deltas(self, *, text: str, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = story_context.get("known_object_ids", []) + story_context.get("known_artifacts", [])
        return self._presence_deltas(ids, text, "object", "object_state")

    def _open_loop_deltas(self, *, text: str, chapter: GeneratedChapter | None, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        ids = [item.get("loop_id") for item in chapter.open_loops if item.get("loop_id")] if chapter else []
        ids += story_context.get("known_open_loop_ids", [])
        return self._presence_deltas(ids, text, "open_loop", "open_loop_state")

    def _resolved_loop_deltas(self, *, text: str, story_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        lowered = text.lower()
        resolved = []
        markers = ["resolved", "finally answers", "closes the loop", "truth is known", "case is closed"]
        if any(marker in lowered for marker in markers):
            for loop_id in story_context.get("known_open_loop_ids", []):
                resolved.append(
                    {
                        "delta_id": f"resolved_loop_{self._safe_id(loop_id)}",
                        "delta_type": "resolved_loop",
                        "target_id": loop_id,
                        "candidate_type": "resolved_loop_state",
                        "delta_action": "resolved",
                        "value": loop_id,
                    }
                )
        return resolved

    def _presence_deltas(self, ids: List[str], text: str, delta_type: str, candidate_type: str) -> List[Dict[str, Any]]:
        deltas = []
        seen = set()
        lowered = text.lower()

        for raw in ids:
            value = str(raw)
            if not value or value in seen:
                continue
            seen.add(value)
            if value.lower() in lowered:
                deltas.append(
                    {
                        "delta_id": f"{delta_type}_delta_{self._safe_id(value)}",
                        "delta_type": delta_type,
                        "target_id": value,
                        "candidate_type": candidate_type,
                        "delta_action": "mentioned_or_preserved",
                        "value": value,
                    }
                )

        return deltas

    def _protected_element_impacts(
        self,
        *,
        text: str,
        provenance_record: StoryProvenanceRecord | None,
        all_deltas: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        if not provenance_record:
            return []

        impacted = []
        delta_values = {str(item.get("value", "")).lower() for item in all_deltas}
        lowered = text.lower()

        for item in provenance_record.protected_elements_snapshot:
            value = str(item.get("value", ""))
            if value and (value.lower() in lowered or value.lower() in delta_values):
                impacted.append(
                    {
                        "impact_id": f"protected_impact_{self._safe_id(value)}",
                        "impact_type": "protected_element_preserved_or_updated",
                        "element_type": item.get("element_type"),
                        "value": value,
                    }
                )

        return self._unique_dicts(impacted, key="impact_id")

    def _memory_update_candidates(
        self,
        *,
        character_deltas: List[Dict[str, Any]],
        relationship_deltas: List[Dict[str, Any]],
        secret_deltas: List[Dict[str, Any]],
        causal_deltas: List[Dict[str, Any]],
        world_deltas: List[Dict[str, Any]],
        object_deltas: List[Dict[str, Any]],
        open_loop_deltas: List[Dict[str, Any]],
        resolved_loop_deltas: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> List[Dict[str, Any]]:
        candidates = []
        for delta in (
            character_deltas
            + relationship_deltas
            + secret_deltas
            + causal_deltas
            + world_deltas
            + object_deltas
            + open_loop_deltas
            + resolved_loop_deltas
        ):
            candidates.append(
                {
                    "candidate_id": f"memory_candidate_{delta.get('delta_id')}",
                    "candidate_type": delta.get("candidate_type"),
                    "value": delta.get("value"),
                    "source_delta_id": delta.get("delta_id"),
                    "delta_action": delta.get("delta_action"),
                }
            )

        if provenance_record:
            for item in provenance_record.memory_update_candidates:
                if item.get("candidate_id"):
                    candidates.append(item)

        return self._unique_dicts(candidates, key="candidate_id")

    def _delta_summary(self, **kwargs: Any) -> Dict[str, Any]:
        return {
            "character_deltas": len(kwargs["character_deltas"]),
            "relationship_deltas": len(kwargs["relationship_deltas"]),
            "secret_deltas": len(kwargs["secret_deltas"]),
            "causal_deltas": len(kwargs["causal_deltas"]),
            "world_deltas": len(kwargs["world_deltas"]),
            "object_deltas": len(kwargs["object_deltas"]),
            "open_loop_deltas": len(kwargs["open_loop_deltas"]),
            "resolved_loop_deltas": len(kwargs["resolved_loop_deltas"]),
            "memory_candidates": len(kwargs["memory_candidates"]),
            "protected_impacts": len(kwargs["protected_impacts"]),
        }

    def _downstream_constraints(
        self,
        *,
        source_id: str,
        draft_id: str,
        memory_candidates: List[Dict[str, Any]],
        provenance_record: StoryProvenanceRecord | None,
    ) -> Dict[str, Any]:
        return {
            "source_id": source_id,
            "draft_id": draft_id,
            "provenance_record_id": getattr(provenance_record, "provenance_record_id", None),
            "memory_candidate_ids": [item.get("candidate_id") for item in memory_candidates],
            "rules": [
                "Only memory candidates from approved provenance should be applied automatically.",
                "Do not update memory for copy-risk-blocked drafts.",
                "Preserve protected character, secret, causal, and world-state deltas.",
            ],
        }

    def _warnings(
        self,
        *,
        text: str,
        provenance_record: StoryProvenanceRecord | None,
        memory_candidates: List[Dict[str, Any]],
    ) -> List[str]:
        warnings = []
        if not text:
            warnings.append("No text supplied; delta extraction may be sparse.")
        if not provenance_record:
            warnings.append("No provenance record supplied; approval safety is limited.")
        elif not provenance_record.approved_for_memory_update:
            warnings.append("Provenance record is not approved for automatic memory update.")
        if not memory_candidates:
            warnings.append("No memory candidates extracted.")
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

    def _unique_dicts(self, values: List[Dict[str, Any]], *, key: str) -> List[Dict[str, Any]]:
        result = []
        seen = set()
        for value in values:
            marker = value.get(key) or str(value)
            if marker and marker not in seen:
                seen.add(marker)
                result.append(value)
        return result
