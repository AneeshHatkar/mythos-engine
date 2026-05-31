from pathlib import Path

from backend.app.engines.simulation.simulation_run_store import SimulationRunStore
from backend.app.schemas.simulation import SimulationState, SimulationWorldState


def build_state():
    return SimulationState(
        simulation_id="sim_store_001",
        world_state=SimulationWorldState(world_id="world_velmora"),
        metadata={
            "simulation_runs": {
                "run_store": {
                    "run_id": "run_store",
                    "status": "completed",
                    "selected_character_ids": ["char_kael", "char_seren"],
                    "event_ids": ["evt_trial"],
                    "steps": ["cast_selected", "events_registered", "handoff_payloads_built"],
                    "outputs": {
                        "handoff_package_id": "handoff_run_store",
                        "generation_control_payload_id": "generation_control_run_store",
                    },
                    "warnings": [],
                    "errors": [],
                }
            },
            "simulation_quality_reports": {
                "quality_run_store": {
                    "quality_report_id": "quality_run_store",
                    "run_id": "run_store",
                    "overall_quality_score": 0.82,
                    "quality_label": "strong",
                    "ready_for_generation": True,
                }
            },
            "simulation_anti_genericity_reports": {
                "anti_genericity_run_store": {
                    "anti_genericity_report_id": "anti_genericity_run_store",
                    "run_id": "run_store",
                    "anti_genericity_score": 0.78,
                    "label": "specific",
                    "passes": True,
                }
            },
            "handoff_packages": {
                "handoff_run_store": {
                    "package_id": "handoff_run_store",
                    "generation_contract": {"preserve_causal_continuity": True},
                }
            },
            "generation_control_payloads": {
                "generation_control_run_store": {
                    "payload_id": "generation_control_run_store",
                    "format_contract": {"output_format": "novel"},
                }
            },
        },
    )


def test_run_store_saves_loads_and_lists_runs(tmp_path):
    store = SimulationRunStore(base_dir=tmp_path)
    run = {
        "run_id": "run_001",
        "status": "completed",
        "selected_character_ids": ["char_kael"],
        "event_ids": ["evt_1"],
        "steps": ["created"],
        "warnings": [],
        "errors": [],
    }

    saved = store.save_run(run_record=run)
    loaded = store.load_run(run_id="run_001")
    listed = store.list_runs()

    assert saved["success"] is True
    assert Path(saved["path"]).exists()
    assert loaded["success"] is True
    assert loaded["run_record"]["run_id"] == "run_001"
    assert listed["success"] is True
    assert listed["run_count"] == 1
    assert listed["runs"][0]["run_id"] == "run_001"


def test_run_store_prevents_overwrite_when_requested(tmp_path):
    store = SimulationRunStore(base_dir=tmp_path)
    run = {"run_id": "run_001", "status": "completed"}

    assert store.save_run(run_record=run)["success"] is True
    result = store.save_run(run_record=run, overwrite=False)

    assert result["success"] is False
    assert "overwrite is false" in result["errors"][0]


def test_run_store_saves_reports(tmp_path):
    store = SimulationRunStore(base_dir=tmp_path)

    quality = {
        "quality_report_id": "quality_run_001",
        "run_id": "run_001",
        "overall_quality_score": 0.8,
    }
    anti = {
        "anti_genericity_report_id": "anti_genericity_run_001",
        "run_id": "run_001",
        "anti_genericity_score": 0.75,
    }

    q = store.save_quality_report(quality_report=quality)
    a = store.save_anti_genericity_report(anti_genericity_report=anti)

    assert q["success"] is True
    assert a["success"] is True
    assert Path(q["path"]).exists()
    assert Path(a["path"]).exists()


def test_run_store_exports_and_imports_run_bundle(tmp_path):
    state = build_state()
    store = SimulationRunStore(base_dir=tmp_path)

    exported = store.export_run_bundle(state=state, run_id="run_store")

    assert exported["success"] is True
    assert Path(exported["path"]).exists()
    assert exported["bundle"]["quality_report"]["quality_report_id"] == "quality_run_store"
    assert exported["bundle"]["anti_genericity_report"]["anti_genericity_report_id"] == "anti_genericity_run_store"
    assert exported["bundle"]["handoff_package"]["package_id"] == "handoff_run_store"

    new_state = SimulationState(
        simulation_id="sim_store_imported",
        world_state=SimulationWorldState(world_id="world_velmora"),
    )

    imported = store.import_run_bundle(state=new_state, bundle_path=exported["path"])

    assert imported["success"] is True
    assert "run_store" in new_state.metadata["simulation_runs"]
    assert "quality_run_store" in new_state.metadata["simulation_quality_reports"]
    assert "anti_genericity_run_store" in new_state.metadata["simulation_anti_genericity_reports"]
    assert "handoff_run_store" in new_state.metadata["handoff_packages"]
    assert "generation_control_run_store" in new_state.metadata["generation_control_payloads"]


def test_run_store_saves_state_run_index(tmp_path):
    state = build_state()
    store = SimulationRunStore(base_dir=tmp_path)

    result = store.save_state_run_index(state=state)

    assert result["success"] is True
    assert Path(result["path"]).exists()
    assert result["index"]["run_count"] == 1
    assert result["index"]["quality_report_count"] == 1
    assert result["index"]["anti_genericity_report_count"] == 1
    assert result["index"]["runs"][0]["run_id"] == "run_store"


def test_run_store_deletes_run(tmp_path):
    store = SimulationRunStore(base_dir=tmp_path)
    run = {"run_id": "run_delete", "status": "completed"}

    store.save_run(run_record=run)
    deleted = store.delete_run(run_id="run_delete")
    loaded = store.load_run(run_id="run_delete")

    assert deleted["success"] is True
    assert loaded["success"] is False
