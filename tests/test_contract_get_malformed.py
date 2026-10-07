"""Test: Contract.get rejects malformed UUIDs cleanly."""
from agent.mcp_client import call_tool, is_failure, failure_reason


def test_malformed_uuid_is_rejected():
    r = call_tool("Contract.get", {"id": "not-a-valid-uuid"})
    assert is_failure(r), "malformed UUID should be rejected"
    reason = str(failure_reason(r)).lower()
    assert "not found" in reason or "invalid" in reason, \
        f"expected a bounded error, got: {reason}"


def test_empty_id_is_rejected():
    r = call_tool("Contract.get", {"id": ""})
    assert is_failure(r), "empty id should be rejected"
