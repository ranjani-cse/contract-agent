"""c11 — approval history across contracts."""
from agent.agent import answer_c11_approval_history
from harness.verifiers import verify_c11_approval_history


def test_c11_pass():
    ans = answer_c11_approval_history()
    v = verify_c11_approval_history(ans)
    assert v["pass"], v
    assert v["total_contracts"] >= 1
    assert v["with_approval"] >= 1
