"""Test: c1 returns a party's contracts with obligations and deviations."""
from agent.agent import answer_c1_disputed_quarter


def test_c1_returns_party_and_contracts():
    r = answer_c1_disputed_quarter()
    assert isinstance(r, dict)
    assert r.get("party_id"), "should pick a party"
    assert isinstance(r.get("summary"), list)
    assert len(r["summary"]) > 0, "should have at least one contract"
    assert isinstance(r.get("contracts_found"), int)


def test_c1_flags_seat_limitation():
    """c1 cannot see Bill/Invoice — must say so honestly."""
    r = answer_c1_disputed_quarter()
    note = str(r.get("note", "")).lower()
    assert "bill" in note or "invoice" in note or "seat" in note, \
        "c1 should flag the seat limitation"
