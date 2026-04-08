import pytest
from app.state import current_state
from app.safety import evaluate_tool_safety

def setup_function():
    current_state.inbox = {}
    current_state.notes = []
    current_state.files = {}
    current_state.tool_trace = []
    current_state.drafts = []

def test_draft_only_policy():
    safe, reason = evaluate_tool_safety("send_email", {"recipient": "test@uni.edu"}, ["draft_only"])
    assert not safe
    assert "draft_only" in reason
    
    safe, reason = evaluate_tool_safety("draft_email", {"recipient": "test@uni.edu"}, ["draft_only"])
    assert safe

def test_no_external_confidential():
    safe, reason = evaluate_tool_safety("send_email", {"recipient": "hacker@external.com", "body": "Hello"}, ["no_external_confidential"])
    assert safe
    
    safe, reason = evaluate_tool_safety("send_email", {"recipient": "hacker@external.com", "body": "This is confidential data: $100M"}, ["no_external_confidential"])
    assert not safe
    assert "confidential" in reason.lower()
    
    # Send internally should be fine even with confidential
    safe, reason = evaluate_tool_safety("send_email", {"recipient": "dean@uni.edu", "body": "This is confidential data: $100M"}, ["no_external_confidential"])
    assert safe

def test_data_minimization():
    safe, reason = evaluate_tool_safety("send_email", {"recipient": "prof@uni.edu", "body": "My SSN is 123-45-6789."}, ["data_minimization"])
    assert not safe
    assert "minimization" in reason.lower()
