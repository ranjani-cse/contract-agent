"""Test: renewal_forecast rejects horizon_days below its documented minimum.

Bug 1 was filed 2026-09-23: the server accepted horizon_days=0 and -5 despite
its description saying "min 1". On 2026-09-29 the platform now rejects these
values. This test asserts the fixed behavior.
"""
from agent.mcp_client import call_tool, is_failure


def test_horizon_days_zero_is_rejected():
    """horizon_days=0 must be rejected (documented min is 1)."""
    r = call_tool("endpoint.contracts.renewal_forecast", {"horizon_days": 0})
    assert is_failure(r), "horizon_days=0 should be rejected"


def test_horizon_days_negative_is_rejected():
    """horizon_days=-5 must be rejected (documented min is 1)."""
    r = call_tool("endpoint.contracts.renewal_forecast", {"horizon_days": -5})
    assert is_failure(r), "horizon_days=-5 should be rejected"
