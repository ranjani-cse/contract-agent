"""Test: renewal_forecast payload shape.

Bug 5 was filed 2026-09-21: the tool nested its payload under an extra
{"result": {...}} envelope, unlike entity tools. Fixed by 2026-09-29 —
the payload now puts 'contracts' at the top level.
"""
import json
from agent.mcp_client import call_tool


def test_renewal_forecast_payload_is_not_double_nested():
    """The payload now exposes data at the top level (fixed 2026-09-29)."""
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": 60, "limit": 5})
    text = r["body"]["result"]["content"][0]["text"]
    parsed = json.loads(text)
    assert isinstance(parsed, dict), "payload should be a JSON object"
    assert "result" not in parsed, "payload should no longer double-wrap (fixed)"
    assert "contracts" in parsed, "contracts should be at the top level"


def test_entity_tools_are_not_double_nested():
    """Contract.list also puts its payload at the top level."""
    r = call_tool("Contract.list", {"limit": 2})
    text = r["body"]["result"]["content"][0]["text"]
    parsed = json.loads(text)
    assert "result" not in parsed, "Contract.list should not double-wrap"
    assert "data" in parsed, "Contract.list payload should have 'data' at the top"
