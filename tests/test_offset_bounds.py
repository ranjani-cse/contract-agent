"""Test: renewal_forecast offset bounds.

Bug 4 was filed 2026-09-23. As of 2026-09-29: negative is now rejected,
but a very large offset (999999) is still accepted and returns 0 rows.
"""
from agent.mcp_client import call_tool, is_failure
from agent.agent import _unwrap


def test_offset_negative_is_rejected():
    r = call_tool("endpoint.contracts.renewal_forecast", {"offset": -1})
    assert is_failure(r), "offset=-1 should be rejected"


def test_offset_huge_is_accepted_with_zero_rows():
    """Very large offset is accepted; documents the still-open upper bound."""
    r = call_tool("endpoint.contracts.renewal_forecast", {"offset": 999999})
    assert not is_failure(r), "offset=999999 is currently accepted (upper bound missing)"
    data = _unwrap(r)
    assert len(data.get("contracts", [])) == 0, "past-end offset should return 0 rows"
