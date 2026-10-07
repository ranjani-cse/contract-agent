"""Test: tools.describe reports foreign tools as not_available."""
import json
from agent.mcp_client import call


def test_foreign_tool_is_reported_not_available():
    r = call("tools/call", {
        "name": "tools.describe",
        "arguments": {"names": ["SalarySlip.list"]},
    })
    body = r["body"]
    assert "result" in body, "tools.describe should return a result"
    text = body["result"]["content"][0]["text"]
    parsed = json.loads(text)
    not_available = parsed.get("not_available", [])
    assert "SalarySlip.list" in not_available, \
        "SalarySlip.list should be reported as not_available"


def test_available_tool_is_reported():
    r = call("tools/call", {
        "name": "tools.describe",
        "arguments": {"names": ["Contract.list"]},
    })
    body = r["body"]
    text = body["result"]["content"][0]["text"]
    parsed = json.loads(text)
    not_available = parsed.get("not_available", [])
    assert "Contract.list" not in not_available, \
        "Contract.list should be available"
