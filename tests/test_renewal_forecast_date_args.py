"""Test: renewal_forecast silently ignores from_date and to_date.

Bug 8 was filed 2026-09-23. As of 2026-09-29 the tool still accepts malformed
and inverted date ranges and returns the default window instead.
"""
from agent.mcp_client import call_tool
from agent.agent import _unwrap


def test_malformed_from_date_is_not_rejected():
    """A malformed from_date should be rejected, not silently ignored."""
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": 60, "from_date": "not-a-date"})
    data = _unwrap(r)
    assert "contracts" in data, "malformed date should have been rejected"


def test_inverted_date_range_returns_default_window():
    """An inverted date range should return 0 contracts."""
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": 60, "from_date": "2026-12-01", "to_date": "2026-01-01"})
    data = _unwrap(r)
    n = len(data.get("contracts", []))
    assert n > 0, "inverted range should return 0 contracts, but returned the default window"
