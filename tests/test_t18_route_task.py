"""t18 — dispatcher routes free-text prompt."""
from agent.agent import answer_t18_route_task
from harness.verifiers import verify_t18_route_task


def test_t18_pass():
    ans = answer_t18_route_task()
    v = verify_t18_route_task(ans)
    assert v["pass"], v
