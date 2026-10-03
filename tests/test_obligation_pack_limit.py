"""Test: obligation_evidence_pack rejects out-of-range limit.

Bug 3 was filed 2026-09-23: limit accepted 0, -1, 201, 9999.
As of 2026-09-29 the server rejects them.
"""
from agent.mcp_client import call_tool, is_failure


def test_limit_negative_is_rejected():
    r = call_tool("endpoint.contracts.obligation_evidence_pack",
                  {"contract_id": "x", "limit": -1})
    assert is_failure(r), "limit=-1 should be rejected"


def test_limit_zero_is_rejected():
    r = call_tool("endpoint.contracts.obligation_evidence_pack",
                  {"contract_id": "x", "limit": 0})
    assert is_failure(r), "limit=0 should be rejected (documented min is 1)"


def test_limit_over_200_is_rejected():
    r = call_tool("endpoint.contracts.obligation_evidence_pack",
                  {"contract_id": "x", "limit": 9999})
    assert is_failure(r), "limit=9999 should be rejected (documented max is 200)"
