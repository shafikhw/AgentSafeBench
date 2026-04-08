import pytest
from pydantic import ValidationError
from benchmark.schema import Scenario, GoldStandard, ScenarioState, RunRecord

def test_gold_standard_valid():
    gold = GoldStandard(expected_decision="safe_comply")
    assert gold.expected_decision == "safe_comply"
    assert len(gold.must_call_tools) == 0

def test_gold_standard_invalid():
    with pytest.raises(ValidationError):
        GoldStandard() # missing required expected_decision

def test_scenario_valid():
    state = ScenarioState()
    gold = GoldStandard(expected_decision="safe_comply")
    s = Scenario(id="t1", title="T", split="test", family="clean", difficulty="easy", user_input="hello", applicable_policies=[], initial_state=state, gold=gold)
    assert s.id == "t1"

def test_run_record_valid():
    record = RunRecord(
        run_id="r1",
        scenario_id="s1",
        user_input="hi",
        system_prompt="sys",
        agent_name="agent",
        timestamp=0.0,
        final_decision="safe_comply",
        final_output="out",
        tool_calls=[]
    )
    assert record.scenario_id == "s1"
