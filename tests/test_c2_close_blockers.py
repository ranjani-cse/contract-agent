"""Test: c2 returns blockers from active contracts."""
from agent.agent import answer_c2_close_blockers


def test_c2_returns_blockers():
    r = answer_c2_close_blockers()
    assert isinstance(r, dict)
    assert isinstance(r.get("active_contracts"), int)
    assert isinstance(r.get("blockers_found"), int)
    assert isinstance(r.get("blockers"), list)


def test_c2_blockers_have_required_fields():
    r = answer_c2_close_blockers()
    for b in r.get("blockers", [])[:3]:
        assert "contract_id" in b
        assert "obligation_id" in b
        assert "status" in b
