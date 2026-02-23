import json
import pytest
from pathlib import Path

STAGES_DIR = Path(__file__).parent.parent / "stages"
REQUIRED_STAGE_KEYS = {"stage", "order", "description", "trigger", "inputs", "outputs", "tools", "governance", "next_stage"}


def get_stage_files():
    return list(STAGES_DIR.glob("*/stage.json"))


@pytest.mark.parametrize("stage_file", get_stage_files(), ids=lambda f: f.parent.name)
def test_stage_json_valid(stage_file):
    """Every stage.json must be valid JSON with required keys."""
    data = json.loads(stage_file.read_text())
    missing = REQUIRED_STAGE_KEYS - set(data.keys())
    assert not missing, f"Stage {stage_file.parent.name} missing keys: {missing}"


def test_stage_order_unique():
    """No two stages should have the same order."""
    orders = []
    for sf in get_stage_files():
        data = json.loads(sf.read_text())
        orders.append(data["order"])
    assert len(orders) == len(set(orders))


def test_pipeline_json_valid():
    pipeline_file = Path(__file__).parent.parent / "pipeline.json"
    data = json.loads(pipeline_file.read_text())
    assert "stages" in data
    assert len(data["stages"]) == 8


def test_next_stage_forms_cycle():
    """scale's next_stage should be discovery (forms a loop)."""
    scale = json.loads((STAGES_DIR / "scale" / "stage.json").read_text())
    assert scale["next_stage"] == "discovery"
