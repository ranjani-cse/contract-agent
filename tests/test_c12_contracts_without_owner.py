"""c12 — contracts without owner."""
from agent.agent import answer_c12_contracts_without_owner
from harness.verifiers import verify_c12_contracts_without_owner


def test_c12_pass():
    ans = answer_c12_contracts_without_owner()
    v = verify_c12_contracts_without_owner(ans)
    assert v["pass"], v
    assert v["total_contracts"] >= 1
