"""Planner — plan + execute on multi-intent prompts (LLM or rule fallback)."""
from agent.agent_loop import plan_and_execute
from agent.planner import make_plan


def test_plan_composes_two_intents():
    """Multi-intent prompt should produce >=2 chained steps."""
    p = make_plan("Which auto-renewing contracts have overdue obligations?")
    assert p["source"] in ("llm", "rule"), p
    names = [s.get("name") for s in p["steps"]]
    assert "renewal_risk" in names, names
    assert "overdue_obligations" in names, names


def test_plan_executes_and_returns_results():
    """plan_and_execute should run the plan and return aggregated results."""
    r = plan_and_execute("Which auto-renewing contracts have overdue obligations?")
    assert r.get("steps_run", 0) >= 2, r
    assert "renewal_risk" in r.get("results", {}), r
    assert "overdue_obligations" in r.get("results", {}), r
    assert r.get("errors") == [], r


def test_single_intent_still_routes_directly():
    """Single-intent prompt should route to c7, not the planner."""
    from agent.agent import route_task
    r = route_task("Show me our contract templates")
    assert "template_count" in r, r
    assert "plan_source" not in r, r
