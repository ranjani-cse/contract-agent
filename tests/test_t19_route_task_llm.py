"""t19 — LLM dispatcher (with keyword fallback)."""
from agent.agent import answer_t19_route_task_llm
from harness.verifiers import verify_t19_route_task_llm


def test_t19_pass():
    ans = answer_t19_route_task_llm()
    v = verify_t19_route_task_llm(ans)
    assert v["pass"], v
