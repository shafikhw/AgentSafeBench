import os
import json
import pytest
from benchmark.loader import load_scenarios

def test_load_scenarios(tmp_path):
    data = [{
        "id": "t1",
        "title": "T",
        "split": "test",
        "family": "clean",
        "difficulty": "easy",
        "user_input": "hello",
        "applicable_policies": [],
        "initial_state": {"inbox": {}, "notes": [], "files": {}},
        "gold": {"expected_decision": "safe_comply"},
        "optimal_tool_calls": 0,
        "tool_budget_slack": 0,
        "tags": []
    }]
    p = tmp_path / "scenarios.json"
    p.write_text(json.dumps(data))
    
    scenarios = load_scenarios(str(p))
    assert len(scenarios) == 1
    assert scenarios[0].id == "t1"
    assert scenarios[0].gold.expected_decision == "safe_comply"
