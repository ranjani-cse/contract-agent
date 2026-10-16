"""c10 — overdue + unattested obligations."""
from agent.agent import answer_c10_overdue_unattested
from harness.verifiers import verify_c10_overdue_unattested


def test_c10_pass():
    ans = answer_c10_overdue_unattested()
    v = verify_c10_overdue_unattested(ans)
    assert v["pass"], v
    assert v["total_scanned"] >= 1
    assert v["overdue_unattested_count"] >= 1
