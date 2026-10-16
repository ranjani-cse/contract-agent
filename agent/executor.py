"""Executor — run a plan of handler steps and merge results."""

from agent.agent import (
    answer_c3_auto_renewal_risk,
    answer_c10_overdue_unattested,
    answer_c12_contracts_without_owner,
    answer_c9_active_amendments,
    answer_c11_approval_history,
    answer_c7_templates_and_playbooks,
    answer_c8_contract_preferences,
    answer_c2_close_blockers,
    answer_c4_playbook_drift,
    answer_c1_disputed_quarter,
)


HANDLERS = {
    "renewal_risk":        answer_c3_auto_renewal_risk,
    "overdue_obligations": answer_c10_overdue_unattested,
    "missing_owner":       answer_c12_contracts_without_owner,
    "amendments":          answer_c9_active_amendments,
    "approvals":           answer_c11_approval_history,
    "templates":           answer_c7_templates_and_playbooks,
    "preferences":         answer_c8_contract_preferences,
    "blockers":            answer_c2_close_blockers,
    "drift":               answer_c4_playbook_drift,
    "dispute":             answer_c1_disputed_quarter,
}


def execute(plan):
    """Run each step; collect results keyed by step name."""
    results = {}
    errors = []
    for step in plan.get("steps", []):
        kind = step.get("kind")
        name = step.get("name")
        if kind != "handler" or name not in HANDLERS:
            errors.append({"step": step, "error": "unknown step"})
            continue
        try:
            results[name] = HANDLERS[name]()
        except Exception as e:
            errors.append({"step": name, "error": str(e)})
    return {
        "plan_source": plan.get("source"),
        "steps_run": len(results),
        "results": results,
        "errors": errors,
    }
