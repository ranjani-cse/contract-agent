"""Test: c5 returns a renewal decision package."""
from agent.agent import answer_c5_renewal_package


def test_c5_returns_recommendation():
    r = answer_c5_renewal_package()
    assert isinstance(r, dict)
    assert r.get("recommendation") in ("renew", "renegotiate", "review")
    assert isinstance(r.get("obligations_met"), int)
    assert isinstance(r.get("obligations_missed"), int)
    assert isinstance(r.get("open_deviations"), int)


def test_c5_has_contract_id():
    r = answer_c5_renewal_package()
    assert r.get("contract_id"), "should pick a contract"
