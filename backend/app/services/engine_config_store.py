import json
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.schemas.engine_ops import EngineConfigRecord, EngineThresholdConfig


class EngineConfigStore:
    """Stores engine thresholds and weights outside hidden hardcoded logic."""

    DEFAULT_THRESHOLDS = {
        "minimum_originality_score": 0.65,
        "minimum_consistency_score": 0.70,
        "minimum_quality_score": 0.75,
        "genericity_risk_threshold": 0.50,
        "max_relationship_delta_per_event": 0.18,
        "rumor_distortion_rate": 0.12,
        "blackmail_backfire_threshold": 0.35,
        "trust_repair_threshold": 0.55,
        "agency_block_threshold": 0.72,
    }

    def __init__(self, root: str | Path = "reports/engine_configs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_config(self, config: EngineConfigRecord | Dict[str, Any]) -> Dict[str, Any]:
        record = config if isinstance(config, EngineConfigRecord) else EngineConfigRecord.model_validate(config)
        path = self._path_for(record.engine_name)
        path.write_text(json.dumps(record.model_dump(), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
        return {
            "success": True,
            "config_id": record.config_id,
            "engine_name": record.engine_name,
            "path": str(path),
        }

    def get_config(self, engine_name: str) -> Dict[str, Any]:
        path = self._path_for(engine_name)
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))

        config = self.build_default_config(engine_name)
        self.save_config(config)
        return config.model_dump()

    def get_threshold(self, engine_name: str, threshold_name: str, default: Optional[float] = None) -> float:
        config = self.get_config(engine_name)
        thresholds = config.get("thresholds", {})
        if threshold_name in thresholds:
            return float(thresholds[threshold_name]["value"])
        if default is not None:
            return float(default)
        return float(self.DEFAULT_THRESHOLDS.get(threshold_name, 0.0))

    def build_default_config(self, engine_name: str) -> EngineConfigRecord:
        thresholds = {
            name: EngineThresholdConfig(
                threshold_name=name,
                value=value,
                min_value=0.0,
                max_value=1.0,
                description=f"Default configurable threshold for {name}.",
            )
            for name, value in self.DEFAULT_THRESHOLDS.items()
        }

        return EngineConfigRecord(
            engine_name=engine_name,
            thresholds=thresholds,
            weights={
                "quality": 0.30,
                "originality": 0.25,
                "consistency": 0.25,
                "non_genericity": 0.20,
            },
            flags={
                "blackmail_auto_compliance_forbidden": True,
                "require_provenance_for_training": True,
                "require_causal_explanation_for_major_event": True,
            },
            notes=[
                "Defaults are deterministic v0.1 values and can later be replaced by learned model outputs.",
                "Thresholds are stored outside engine logic to avoid hidden hardcoding.",
            ],
        )

    def _path_for(self, engine_name: str) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in ["_", "-"] else "_" for ch in engine_name)
        return self.root / f"{safe}.json"
