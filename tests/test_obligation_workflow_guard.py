"""Test: ContractObligation state machine rejects invalid transitions."""
from agent.mcp_client import call_tool, is_failure
from harness.verifiers import _extract, _rows


def test_pending_obligation_cannot_be_marked_complete():
    r = call_tool("ContractObligation.list", {"limit": 200})
    rows = _rows(_extract(r))
    pending = next((o for o in rows if isinstance(o, dict) and o.get("status") == "pending"), None)
    if not pending:
        return
    rr = call_tool("ContractObligation.mark_complete", {"id": pending.get("id")})
    assert is_failure(rr), "mark_complete on a pending obligation should be rejected"
