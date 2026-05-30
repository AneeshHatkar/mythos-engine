from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from backend.app.engines.base import BaseEngine
from backend.app.schemas.foundation import EngineRunResult


class WorldBibleExportEngine(BaseEngine):
    """Builds export-ready World Bible packages.

    This engine turns generated world state into a structured export package.

    It produces:
    - Markdown world bible
    - JSON world bible payload
    - executive summary
    - section completeness report
    - quality summary
    - dataset metadata summary
    - snapshot metadata
    - export readiness score

    Later, this can be connected to actual files, frontend downloads,
    PDF/DOCX exports, and project reports.
    """

    engine_name = "world.world_bible_export_engine"

    WORLD_BIBLE_SECTIONS = [
        ("identity", "World Identity"),
        ("world_dna", "World DNA"),
        ("scale_granularity", "Scale and Granularity"),
        ("rules", "World Rules"),
        ("chronology", "Chronology and Historical Wounds"),
        ("geography", "Geography"),
        ("environment", "Environment"),
        ("infrastructure", "Infrastructure"),
        ("demographics", "Demographics"),
        ("society", "Society and Class"),
        ("power_structure", "Power Structures and Factions"),
        ("military_security", "Military and Security"),
        ("economy", "Economy and Resources"),
        ("law", "Law and Justice"),
        ("belief", "Religion, Philosophy, and Myth"),
        ("culture", "Culture, Language, Ritual, and Naming"),
        ("knowledge_education", "Knowledge and Education"),
        ("institutions", "Institutions"),
        ("technology_magic_science", "Technology, Magic, and Science"),
        ("species_creatures", "Species and Creatures"),
        ("artifacts", "Artifacts and Symbolic Objects"),
        ("aesthetic_texture", "Aesthetic and Sensory Texture"),
        ("civilization_pressure", "Civilization Pressure"),
        ("causality_graph", "World Causality Graph"),
        ("quality_summary", "Quality Summary"),
        ("dataset_metadata", "Dataset and Training Metadata"),
        ("snapshot", "Snapshot and Version Metadata"),
    ]

    def run(self, payload: Dict[str, Any]) -> EngineRunResult:
        world_state = payload.get("world_state", {})
        export_format = payload.get("export_format", "markdown_and_json")
        export_title = payload.get("export_title") or self._infer_title(world_state)
        audience = payload.get("audience", "internal_research_and_development")
        include_training_metadata = payload.get("include_training_metadata", True)
        include_snapshot_metadata = payload.get("include_snapshot_metadata", True)

        warnings: List[str] = []

        if not world_state:
            warnings.append("No world_state provided; export package will be mostly empty.")

        if export_format not in {"markdown", "json", "markdown_and_json"}:
            warnings.append(
                f"Unknown export_format '{export_format}'. Falling back to markdown_and_json."
            )
            export_format = "markdown_and_json"

        completeness = self._section_completeness(world_state)
        readiness = self._export_readiness_score(completeness=completeness, world_state=world_state)
        executive_summary = self._build_executive_summary(
            world_state=world_state,
            export_title=export_title,
            readiness=readiness,
        )

        json_payload = self._build_json_payload(
            world_state=world_state,
            export_title=export_title,
            audience=audience,
            completeness=completeness,
            readiness=readiness,
            executive_summary=executive_summary,
            include_training_metadata=include_training_metadata,
            include_snapshot_metadata=include_snapshot_metadata,
        )

        markdown = self._build_markdown(
            json_payload=json_payload,
            include_training_metadata=include_training_metadata,
            include_snapshot_metadata=include_snapshot_metadata,
        )

        package = {
            "export_id": f"wbible_{uuid4().hex[:12]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "export_title": export_title,
            "export_format": export_format,
            "audience": audience,
            "section_completeness": completeness,
            "export_readiness": readiness,
            "executive_summary": executive_summary,
        }

        if export_format in {"json", "markdown_and_json"}:
            package["world_bible_json"] = json_payload

        if export_format in {"markdown", "markdown_and_json"}:
            package["world_bible_markdown"] = markdown

        return self.build_result(
            success=True,
            data={
                "export_package": package,
                "training_notes": [
                    "This engine creates export payloads, not physical files yet.",
                    "Later export services can write markdown, JSON, PDF, DOCX, or frontend downloadable files.",
                    "World Bible export should run after orchestrator, quality, dataset metadata, and snapshot engines.",
                    "Export readiness is separate from training readiness.",
                ],
            },
            warnings=warnings,
            errors=[],
            generated_object_ids=[package["export_id"]],
        )

    def _infer_title(self, world_state: Dict[str, Any]) -> str:
        identity = world_state.get("identity", {})

        if isinstance(identity, dict):
            for key in ["world_name", "name", "title"]:
                if identity.get(key):
                    return f"{identity[key]} World Bible"

        if world_state.get("world_name"):
            return f"{world_state['world_name']} World Bible"

        return "MythOS World Bible"

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

    def _section_completeness(self, world_state: Dict[str, Any]) -> Dict[str, Any]:
        sections = []

        filled_count = 0

        for key, title in self.WORLD_BIBLE_SECTIONS:
            value = world_state.get(key)
            present = value not in (None, {}, [], "")

            if present:
                filled_count += 1

            sections.append(
                {
                    "key": key,
                    "title": title,
                    "present": present,
                    "word_count_estimate": len(self._flatten_text(value).split()) if present else 0,
                }
            )

        total = len(self.WORLD_BIBLE_SECTIONS)

        return {
            "filled_sections": filled_count,
            "total_sections": total,
            "completion_ratio": round(filled_count / total, 3),
            "missing_sections": [section["key"] for section in sections if not section["present"]],
            "sections": sections,
        }

    def _export_readiness_score(
        self,
        *,
        completeness: Dict[str, Any],
        world_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        completion_ratio = completeness["completion_ratio"]

        text = self._flatten_text(world_state).lower()

        quality_summary = world_state.get("quality_summary", {})
        dataset_metadata = world_state.get("dataset_metadata", {})
        snapshot = world_state.get("snapshot", {})

        quality_bonus = 0.0
        if quality_summary:
            quality_bonus += 0.12
            if quality_summary.get("quality_tier") in {"strong", "excellent"}:
                quality_bonus += 0.08

        dataset_bonus = 0.0
        if dataset_metadata:
            dataset_bonus += 0.08
            if dataset_metadata.get("training_eligible") is True:
                dataset_bonus += 0.04

        snapshot_bonus = 0.0
        if snapshot:
            snapshot_bonus += 0.08
            rollback = snapshot.get("rollback", {})
            if rollback.get("rollback_ready") is True:
                snapshot_bonus += 0.04

        specificity_bonus = 0.0
        for term in ["oath", "relic", "archive", "destiny", "class", "law", "artifact", "causality"]:
            if term in text:
                specificity_bonus += 0.015

        specificity_bonus = min(0.12, specificity_bonus)

        score = min(
            1.0,
            (completion_ratio * 0.68)
            + quality_bonus
            + dataset_bonus
            + snapshot_bonus
            + specificity_bonus,
        )

        blockers = []

        if completion_ratio < 0.7:
            blockers.append("World Bible has too many missing sections.")

        if "quality_summary" in completeness["missing_sections"]:
            blockers.append("Quality summary missing.")

        if "civilization_pressure" in completeness["missing_sections"]:
            blockers.append("Civilization pressure missing.")

        if "causality_graph" in completeness["missing_sections"]:
            blockers.append("Causality graph missing.")

        readiness_tier = "draft"
        if score >= 0.9 and not blockers:
            readiness_tier = "publication_ready_internal"
        elif score >= 0.78:
            readiness_tier = "strong_internal_export"
        elif score >= 0.6:
            readiness_tier = "review_needed"

        return {
            "score": round(score, 3),
            "readiness_tier": readiness_tier,
            "blockers": blockers,
            "recommended_next_step": (
                "export_to_markdown_or_docx"
                if score >= 0.78
                else "complete_missing_sections_before_export"
            ),
        }

    def _build_executive_summary(
        self,
        *,
        world_state: Dict[str, Any],
        export_title: str,
        readiness: Dict[str, Any],
    ) -> Dict[str, Any]:
        identity = world_state.get("identity", {})
        quality = world_state.get("quality_summary", {})
        dataset = world_state.get("dataset_metadata", {})

        world_name = "Unknown World"

        if isinstance(identity, dict):
            world_name = identity.get("world_name") or identity.get("name") or world_name

        text = self._flatten_text(world_state).lower()

        major_motifs = [
            motif
            for motif in [
                "academy",
                "oath",
                "relic",
                "archive",
                "destiny",
                "class",
                "border",
                "law",
                "prophecy",
                "artifact",
                "civilization",
                "collapse",
            ]
            if motif in text
        ]

        return {
            "title": export_title,
            "world_name": world_name,
            "one_line_positioning": self._one_line_positioning(major_motifs),
            "major_motifs": major_motifs,
            "quality_tier": quality.get("quality_tier"),
            "training_eligible": dataset.get("training_eligible"),
            "export_readiness_tier": readiness["readiness_tier"],
        }

    def _one_line_positioning(self, motifs: List[str]) -> str:
        if {"academy", "oath", "relic", "destiny"}.issubset(set(motifs)):
            return (
                "A high-complexity dark academy political fantasy world where oath law, relic economies, "
                "forbidden archives, and destiny pressure destabilize civilization."
            )

        if "civilization" in motifs and "collapse" in motifs:
            return (
                "A civilization-scale world designed around system pressure, collapse risk, and long-term evolution."
            )

        if "archive" in motifs and "law" in motifs:
            return (
                "A mystery-driven institutional world where truth, law, and memory compete for legitimacy."
            )

        return "A structured MythOS world prepared for internal review and future expansion."

    def _build_json_payload(
        self,
        *,
        world_state: Dict[str, Any],
        export_title: str,
        audience: str,
        completeness: Dict[str, Any],
        readiness: Dict[str, Any],
        executive_summary: Dict[str, Any],
        include_training_metadata: bool,
        include_snapshot_metadata: bool,
    ) -> Dict[str, Any]:
        sections = {}

        for key, title in self.WORLD_BIBLE_SECTIONS:
            if key == "dataset_metadata" and not include_training_metadata:
                continue

            if key == "snapshot" and not include_snapshot_metadata:
                continue

            sections[key] = {
                "title": title,
                "content": world_state.get(key),
            }

        return {
            "schema_version": "world-bible-export-v0.1",
            "title": export_title,
            "audience": audience,
            "executive_summary": executive_summary,
            "section_completeness": completeness,
            "export_readiness": readiness,
            "sections": sections,
        }

    def _format_value_markdown(self, value: Any, level: int = 0) -> str:
        indent = "  " * level

        if value is None:
            return "_Not provided._"

        if isinstance(value, str):
            return value

        if isinstance(value, (int, float, bool)):
            return str(value)

        if isinstance(value, list):
            if not value:
                return "_None._"

            lines = []

            for item in value:
                if isinstance(item, (dict, list)):
                    lines.append(f"{indent}- {self._format_value_markdown(item, level + 1)}")
                else:
                    lines.append(f"{indent}- {item}")

            return "\n".join(lines)

        if isinstance(value, dict):
            if not value:
                return "_Not provided._"

            lines = []

            for key, item in value.items():
                clean_key = str(key).replace("_", " ").title()

                if isinstance(item, (dict, list)):
                    lines.append(f"{indent}- **{clean_key}:**")
                    lines.append(self._format_value_markdown(item, level + 1))
                else:
                    lines.append(f"{indent}- **{clean_key}:** {item}")

            return "\n".join(lines)

        return str(value)

    def _build_markdown(
        self,
        *,
        json_payload: Dict[str, Any],
        include_training_metadata: bool,
        include_snapshot_metadata: bool,
    ) -> str:
        lines = []

        lines.append(f"# {json_payload['title']}")
        lines.append("")
        lines.append("## Executive Summary")
        lines.append("")

        summary = json_payload["executive_summary"]

        lines.append(f"**World Name:** {summary.get('world_name')}")
        lines.append("")
        lines.append(f"**Positioning:** {summary.get('one_line_positioning')}")
        lines.append("")
        lines.append(f"**Major Motifs:** {', '.join(summary.get('major_motifs', [])) or 'None detected'}")
        lines.append("")
        lines.append(f"**Export Readiness:** {summary.get('export_readiness_tier')}")
        lines.append("")

        lines.append("## Export Readiness Report")
        lines.append("")
        readiness = json_payload["export_readiness"]
        lines.append(f"- **Score:** {readiness['score']}")
        lines.append(f"- **Tier:** {readiness['readiness_tier']}")
        lines.append(f"- **Recommended Next Step:** {readiness['recommended_next_step']}")

        if readiness["blockers"]:
            lines.append("- **Blockers:**")
            for blocker in readiness["blockers"]:
                lines.append(f"  - {blocker}")

        lines.append("")
        lines.append("## Section Completeness")
        lines.append("")
        completeness = json_payload["section_completeness"]
        lines.append(
            f"{completeness['filled_sections']} / {completeness['total_sections']} sections complete "
            f"({completeness['completion_ratio']})"
        )
        lines.append("")

        for key, section in json_payload["sections"].items():
            if key == "dataset_metadata" and not include_training_metadata:
                continue

            if key == "snapshot" and not include_snapshot_metadata:
                continue

            lines.append(f"## {section['title']}")
            lines.append("")
            lines.append(self._format_value_markdown(section["content"]))
            lines.append("")

        return "\n".join(lines)
