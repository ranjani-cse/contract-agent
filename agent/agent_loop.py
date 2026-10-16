"""Agent loop — plan -> act -> observe -> return.

Used as a fallback when route_task can't match a prompt.
"""

from agent.planner import make_plan
from agent.executor import execute


def plan_and_execute(goal):
    """Plan, execute, and return a combined result."""
    plan = make_plan(goal)
    if plan.get("source") == "none" or not plan.get("steps"):
        return {
            "error": "no plan",
            "goal": goal,
            "plan_source": plan.get("source"),
        }
    outcome = execute(plan)
    return {
        "goal": goal,
        "plan_source": outcome.get("plan_source"),
        "steps_run": outcome.get("steps_run"),
        "results": outcome.get("results"),
        "errors": outcome.get("errors"),
    }
