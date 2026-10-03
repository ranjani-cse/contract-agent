"""Test: renewal_forecast counts.in_horizon varies with limit.

Bug 7 was filed 2026-09-23. As of 2026-09-29 the counter still depends on the
scan window (limit) rather than the data window (horizon_days).
"""
from agent.mcp_client import call_tool, is_failure
from agent.agent import _unwrap


def test_in_horizon_varies_with_limit():
    """in_horizon should be the same regardless of limit; currently it is not."""
    r20 = call_tool("endpoint.contracts.renewal_forecast",
                    {"horizon_days": 60, "limit": 20})
    r100 = call_tool("endpoint.contracts.renewal_forecast",
                     {"horizon_days": 60, "limit": 100})
    c20 = _unwrap(r20).get("counts", {}).get("in_horizon")
    c100 = _unwrap(r100).get("counts", {}).get("in_horizon")
    assert c20 != c100, "in_horizon varied with limit; should be constant"


def test_limit_200_is_now_rejected():
    """As of 2026-09-29 the server caps limit at 100."""
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": 60, "limit": 200})
    assert is_failure(r), "limit=200 should be rejected (max is 100)"
