from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class GoldStandard(BaseModel):
    expected_decision: str = Field(..., description="safe_comply or safe_refuse")
    must_call_tools: List[str] = []
    must_not_call_tools: List[str] = []
    required_files: List[str] = []
    forbidden_files: List[str] = []
    required_recipients: List[str] = []
    forbidden_recipients: List[str] = []
    must_include_all: List[str] = []
    must_include_any: List[str] = []
    must_not_include_any: List[str] = []
    attack_success_conditions: List[str] = []

class ScenarioState(BaseModel):
    inbox: Dict[str, Dict[str, str]] = {}  # msg_id -> {sender, subject, body}
    notes: List[str] = []
    files: Dict[str, str] = {}  # filename -> file content

class Scenario(BaseModel):
    id: str
    title: str
    split: str
    family: str  # clean, prompt_injection, unauthorized_disclosure, unsafe_tool_use
    difficulty: str  # easy, medium, hard
    user_input: str
    applicable_policies: List[str]
    initial_state: ScenarioState
    gold: GoldStandard
    optimal_tool_calls: int = 0
    tool_budget_slack: int = 0
    tags: List[str] = []

class RunRecord(BaseModel):
    run_id: str
    scenario_id: str
    user_input: str
    system_prompt: str
    agent_name: str
    timestamp: float
    final_decision: str
    final_output: str
    tool_calls: List[Dict[str, Any]]
    grader_outputs: Dict[str, Any] = {}
    metrics: Dict[str, float] = {}
