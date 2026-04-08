import pytest
from app.state import current_state
from app.tools import read_inbox, search_notes, draft_email

def setup_function():
    current_state.inbox = {"msg_1": {"sender": "test@uni.edu", "subject": "Test", "body": "Body test"}}
    current_state.notes = ["Note 1", "Secret code 1234"]
    current_state.files = {}
    current_state.tool_trace = []
    current_state.drafts = []

def test_read_inbox():
    res = read_inbox("msg_1")
    assert "Body test" in res
    assert len(current_state.tool_trace) == 1
    assert current_state.tool_trace[0]["tool_name"] == "read_inbox"

def test_search_notes():
    res = search_notes("Secret")
    assert "1234" in res

def test_draft_email():
    res = draft_email("recipient@uni.edu", "Sub", "Bod")
    assert "drafted" in res
    assert len(current_state.drafts) == 1
    assert current_state.drafts[0]["recipient"] == "recipient@uni.edu"
