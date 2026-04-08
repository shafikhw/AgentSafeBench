import json
from benchmark.schema import ScenarioState as StateSchema

class ScenarioState:
    def __init__(self):
        self.inbox = {}
        self.notes = []
        self.files = {}
        self.tool_trace = []
        self.drafts = []
        self.sent_emails = []

    def load_from_schema(self, state: StateSchema):
        self.inbox = state.inbox.copy()
        self.notes = list(state.notes)
        self.files = state.files.copy()
        self.tool_trace = []
        self.drafts = []
        self.sent_emails = []

    def record_tool_call(self, tool_name: str, kwargs: dict, status: str, result_preview: str = "", blocked_by: str = None):
        self.tool_trace.append({
            "tool_name": tool_name,
            "arguments": kwargs,
            "status": status,
            "result_preview": result_preview,
            "blocked_by": blocked_by
        })

# Global state for the current run
current_state = ScenarioState()
