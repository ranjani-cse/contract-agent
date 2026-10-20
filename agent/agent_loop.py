"""Agent loop — L2 (plan -> act -> observe -> re-plan -> synthesize).

Falls back to L1 (single-shot plan) when the L2 LLM path is unavailable.
"""

from agent.planner import make_plan, _llm_next_step, _llm_synthesize
from agent.executor import execute


MAX_STEPS = 5


def _run_step(step):
    name = step.get("name")
    if step.get("kind") == "handler" and name:
        try:
            outcome = execute({"source": "l2", "steps": [step]})
            return outcome.get("results", {}).get(name)
        except Exception as e:
            return {"_error": str(e)}
    return {"_error": "invalid step"}


def plan_and_execute(goal):
    """L2 loop with L1 fallback."""
    history = []
    step = _llm_next_step(goal, history)

    if step is None:
        return _plan_and_execute_l1(goal)

    for _ in range(MAX_STEPS):
        if step.get("kind") == "done":
            break
        if step.get("kind") == "replan":
            history.append({"step": {"name": "_replan"},
                            "result": {"reason": step.get("reason")}})
            step = _llm_next_step(goal, history)
            if step is None:
                break
            continue
        result = _run_step(step)
        history.append({"step": step, "result": result})
        step = _llm_next_step(goal, history)
        if step is None:
            break

    synthesis = _llm_synthesize(goal, history)

    return {
        "goal": goal,
        "plan_source": "l2_llm",
        "steps_run": len([h for h in history if h["step"].get("name") != "_replan"]),
        "results": {h["step"].get("name"): h["result"]
                    for h in history if h["step"].get("name")},
        "errors": [],
        "synthesis": synthesis,
    }


def _plan_and_execute_l1(goal):
    """L1 fallback — single-shot plan + execute."""
    plan = make_plan(goal)
    if plan.get("source") == "none" or not plan.get("steps"):
        return {"error": "no plan", "goal": goal, "plan_source": plan.get("source")}

    outcome = execute(plan)
    res = outcome.get("results", {})
    if len(res) == 1:
        only = next(iter(res.values()))
        merged = dict(only) if isinstance(only, dict) else {}
        merged["plan_source"] = outcome.get("plan_source")
        merged["steps_run"] = outcome.get("steps_run")
        return merged

    return {
        "goal": goal,
        "plan_source": outcome.get("plan_source"),
        "steps_run": outcome.get("steps_run"),
        "results": outcome.get("results"),
        "errors": outcome.get("errors"),
    }
