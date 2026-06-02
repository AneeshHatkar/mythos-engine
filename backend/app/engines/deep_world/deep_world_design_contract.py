from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.deep_world import Chunk6DeepWorldDesignContract


class DeepWorldDesignContractBuilder:
    def build_contract(
        self,
        *,
        source_id: str,
        story_context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        story_context = story_context or {}

        rules = [
            "Every generated thing must have a unique name with origin, meaning, and language/culture logic.",
            "People naming must be original and grounded in culture, region, family, class, religion, title customs, nickname customs, and lore.",
            "No final generated artifact can be one-line filler; summaries may be short, but structured outputs must be detailed.",
            "Major world elements must connect to deep lore, historical memory, public history, secret history, false history, and physical evidence.",
            "Chunk 6 must explicitly support multi-country and multi-political-unit worlds.",
            "Every generated world element must include story_use.",
            "Every generated world element must include character_effect.",
            "Every generated world element must include plot_effect.",
            "Every generated world element must include memory_effect.",
            "Every generated world element must include validation_status.",
            "Every generated world element must include provenance.",
            "Every generated world element must include compression_summary.",
            "Chunk 6 must connect through the Pre-Chunk 6 future compatibility bridge.",
            "Chunk 6 must not rewrite or replace Chunks 1-5.",
            "Chunk 6 must support thousands of worlds, regions, species, creatures, settlements, objects, and cultures.",
            "Chunk 6 must produce non-generic, consistent, story-useful world systems.",
            "Chunk 6 must prepare metadata for future Chunk 9 ML/data workflows without training models yet.",
        ]

        warnings: List[str] = []
        if not story_context.get("project_id"):
            warnings.append("No project_id supplied in story_context.")
        if not story_context.get("world_seed"):
            warnings.append("No world_seed supplied; deterministic generation may be limited.")

        contract = Chunk6DeepWorldDesignContract(
            contract_id=f"chunk6_deep_world_design_contract_{source_id}",
            source_id=source_id,
            non_negotiable_rules=rules,
            approved_for_implementation=True,
            warnings=warnings,
        )

        return {"chunk6_deep_world_design_contract": contract}

    def validate_contract(self, *, contract: Chunk6DeepWorldDesignContract) -> Dict[str, Any]:
        required = [
            "story_use",
            "character_effect",
            "plot_effect",
            "memory_effect",
            "validation_status",
            "provenance",
            "compression_summary",
        ]

        missing_required = [
            field for field in required
            if field not in contract.required_output_fields
        ]

        required_bridges = [
            "FutureWorldReferencePacket",
            "DeepWorldReferencePacket",
            "StoryWorldExpansionBridge",
            "ChunkFutureCompatibilityContract",
        ]

        bridge_ok = all(
            bridge in contract.bridge_contracts
            for bridge in required_bridges
        )

        passed = (
            contract.chunk_number == 6
            and contract.total_locked_steps == 55
            and not missing_required
            and bridge_ok
            and contract.approved_for_implementation is True
        )

        return {
            "passed": passed,
            "missing_required_output_fields": missing_required,
            "bridge_contracts_ok": bridge_ok,
            "chunk_number": contract.chunk_number,
            "total_locked_steps": contract.total_locked_steps,
            "warnings": contract.warnings,
        }

    def summarize_contract(self, *, contract: Chunk6DeepWorldDesignContract) -> Dict[str, Any]:
        return {
            "success": True,
            "summary": {
                "contract_id": contract.contract_id,
                "chunk_name": contract.chunk_name,
                "total_locked_steps": contract.total_locked_steps,
                "required_output_fields": contract.required_output_fields,
                "backward_connections": contract.backward_connections,
                "forward_connections": contract.forward_connections,
                "bridge_contracts": contract.bridge_contracts,
                "approved_for_implementation": contract.approved_for_implementation,
                "warning_count": len(contract.warnings),
            },
        }

    def build_contract_text(self, *, contract: Chunk6DeepWorldDesignContract) -> Dict[str, str]:
        lines = [
            "Chunk 6 Deep World Design Contract",
            f"Contract ID: {contract.contract_id}",
            f"Chunk: {contract.chunk_number} — {contract.chunk_name}",
            f"Total Locked Steps: {contract.total_locked_steps}",
            "",
            "Required Output Fields:",
        ]

        for field in contract.required_output_fields:
            lines.append(f"- {field}")

        lines.append("")
        lines.append("Backward Connections:")
        for item in contract.backward_connections:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Forward Connections:")
        for item in contract.forward_connections:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Bridge Contracts:")
        for item in contract.bridge_contracts:
            lines.append(f"- {item}")

        lines.append("")
        lines.append("Non-Negotiable Rules:")
        for rule in contract.non_negotiable_rules:
            lines.append(f"- {rule}")

        if contract.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in contract.warnings:
                lines.append(f"- {warning}")

        return {"contract_text": chr(10).join(lines)}
