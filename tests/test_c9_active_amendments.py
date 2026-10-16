"""c9 — amendments on active contracts."""
from agent.agent import answer_c9_active_amendments
from harness.verifiers import verify_c9_active_amendments


def test_c9_pass():
    ans = answer_c9_active_amendments()
    v = verify_c9_active_amendments(ans)
    assert v["pass"], v
    assert v["active_contracts"] >= 1
    assert v["contracts_with_amendments"] >= 1
