"""Server entry point for the AgentSwitch harness.

Runs all 18 tasks against the live instance and writes results.json
in the platform's expected format.

The platform provides:
  AGENTSWITCH_BASE_URL, AGENTSWITCH_TOKEN, AGENTSWITCH_INSTANCE
  OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
"""
import json
import os
import time
from pathlib import Path

from agent.agent import (
    answer_a17,
    answer_c1_disputed_quarter,
    answer_c2_close_blockers,
    answer_c3_auto_renewal_risk,
    answer_c4_playbook_drift,
    answer_c5_renewal_package,
    answer_c6_portfolio_audit,
    answer_c7_templates_and_playbooks,
    answer_c8_contract_preferences,
    answer_c9_active_amendments,
    answer_c10_overdue_unattested,
    answer_c11_approval_history,
    answer_c12_contracts_without_owner,
    answer_c13_auto_renewal_overdue,
    answer_c16_pending_approval_overdue,
    answer_c15_top_party_drift,
    answer_c14_orphan_amendments,
    answer_t18_route_task,
    answer_t19_route_task_llm,
    answer_t21_route_c4,
    answer_t6_refusal,
    answer_t7_refusal,
)
from harness.verifiers import (
    verify_health_check,
    verify_renewal_forecast,
    verify_playbook_review,
    verify_missing_obligations,
    verify_renewal_decision,
    verify_deviation_approval,
    verify_refusal,
    verify_refusal_cross_seat,
    verify_refusal_or_empty,
    verify_pagination,
    verify_workflow_guard,
    verify_tools_list_scoping,
    verify_concurrency,
    verify_malformed_id,
    verify_offset_past_end,
    verify_tools_describe_foreign,
    verify_obligation_workflow_guard,
    verify_contract_get_missing,
    verify_tools_describe_available,
    verify_c1_disputed_quarter,
    verify_c2_close_blockers,
    verify_c3_auto_renewal_risk,
    verify_c4_playbook_drift,
    verify_c5_renewal_package,
    verify_c6_portfolio_audit,
    verify_c7_templates_and_playbooks,
    verify_c8_contract_preferences,
    verify_c9_active_amendments,
    verify_c10_overdue_unattested,
    verify_c11_approval_history,
    verify_c12_contracts_without_owner,
    verify_c13_auto_renewal_overdue,
    verify_c16_pending_approval_overdue,
    verify_c15_top_party_drift,
    verify_c14_orphan_amendments,
    verify_t18_route_task,
    verify_t19_route_task_llm,
    verify_t21_route_c4,
)

RESULTS = Path("results.json")

TASKS = [
    ("t0_health_check", "Auth works and tools/list returns tools", verify_health_check),
    ("t1_renewal_forecast", "Expiring contracts match the DB", verify_renewal_forecast),
    ("t2_playbook_review", "A real clause deviation was written", verify_playbook_review),
    ("t3_missing_obligations", "Evidence packs retrieved per contract", verify_missing_obligations),
    ("t4_renewal_decision", "A ContractRenewal moved off undecided", verify_renewal_decision),
    ("t5_deviation_approval", "A deviation entered the approval flow", verify_deviation_approval),
    ("t6_refusal_cross_seat", "Agent declines another seat's data", verify_refusal_cross_seat),
    ("t7_refusal_unsupported", "Agent declines unsupported questions", verify_refusal_or_empty),
    ("t8_pagination", "Contract.list returns bounded rows", verify_pagination),
    ("t9_workflow_guard", "Invalid state transitions are rejected", verify_workflow_guard),
    ("t10_tools_list_scoping", "No foreign tools exposed", verify_tools_list_scoping),
    ("t11_concurrency", "Platform state is mutable", verify_concurrency),
    ("t12_malformed_id", "Malformed UUID is rejected", verify_malformed_id),
    ("t13_offset_past_end", "Past-end offset returns zero rows", verify_offset_past_end),
    ("t14_tools_describe_foreign", "tools.describe reports foreign tools", verify_tools_describe_foreign),
    ("t15_obligation_workflow_guard", "Invalid obligation transitions are rejected", verify_obligation_workflow_guard),
    ("t16_contract_get_missing", "Missing UUID returns not_found", verify_contract_get_missing),
    ("t17_tools_describe_available", "tools.describe returns schema", verify_tools_describe_available),
    ("c1_disputed_quarter", "Multi-step party contract summary", verify_c1_disputed_quarter),
    ("c2_close_blockers", "Find obligations blocking close", verify_c2_close_blockers),
    ("c3_auto_renewal_risk", "Flag at-risk auto-renewals", verify_c3_auto_renewal_risk),
    ("c4_playbook_drift", "Portfolio playbook analysis", verify_c4_playbook_drift),
    ("c5_renewal_package", "Renewal decision package", verify_c5_renewal_package),
    ("c6_portfolio_audit", "Full portfolio audit — blockers, risk, drift", verify_c6_portfolio_audit),
    ("c7_templates_and_playbooks", "List templates and playbooks", verify_c7_templates_and_playbooks),
    ("c8_contract_preferences", "Read contract preferences", verify_c8_contract_preferences),
    ("c9_active_amendments", "Amendments on active contracts", verify_c9_active_amendments),
    ("c10_overdue_unattested", "Overdue and unattested obligations", verify_c10_overdue_unattested),
    ("c11_approval_history", "Approval history across contracts", verify_c11_approval_history),
    ("c12_contracts_without_owner", "Contracts without an owner", verify_c12_contracts_without_owner),
    ("c13_auto_renewal_overdue", "Auto-renewing contracts with overdue obligations", verify_c13_auto_renewal_overdue),
    ("c14_orphan_amendments", "Contracts without owner that have amendments", verify_c14_orphan_amendments),
    ("c15_top_party_drift", "Party with most amendments — their playbook drift", verify_c15_top_party_drift),
    ("c16_pending_overdue", "Pending-approval contracts with overdue obligations", verify_c16_pending_approval_overdue),
    ("t18_route_task", "Dispatcher routes to correct handler", verify_t18_route_task),
    ("t19_route_task_llm", "LLM dispatcher routes prompt (fallback-safe)", verify_t19_route_task_llm),
    ("t21_route_c4", "LLM routes c4 prompt to playbook drift handler", verify_t21_route_c4),
]

_cached_a17 = None


def run_one(task_id, title, verifier):
    global _cached_a17
    try:
        if task_id.startswith(("t1_", "t2_", "t3_", "t4_", "t5_")):
            if _cached_a17 is None:
                print("  (running answer_a17 once — caching for t1-t5)")
                _cached_a17 = answer_a17(horizon_days=60)
            answer = _cached_a17
        elif task_id == "t6_refusal_cross_seat":
            answer = answer_t6_refusal()
        elif task_id == "t7_refusal_unsupported":
            answer = answer_t7_refusal()
        elif task_id == "c1_disputed_quarter":
            answer = answer_c1_disputed_quarter()
        elif task_id == "c2_close_blockers":
            answer = answer_c2_close_blockers()
        elif task_id == "c3_auto_renewal_risk":
            answer = answer_c3_auto_renewal_risk()
        elif task_id == "c4_playbook_drift":
            answer = answer_c4_playbook_drift()
        elif task_id == "c5_renewal_package":
            answer = answer_c5_renewal_package()
        elif task_id == "c6_portfolio_audit":
            answer = answer_c6_portfolio_audit()
        elif task_id == "c7_templates_and_playbooks":
            answer = answer_c7_templates_and_playbooks()
        elif task_id == "c8_contract_preferences":
            answer = answer_c8_contract_preferences()
        elif task_id == "c9_active_amendments":
            answer = answer_c9_active_amendments()
        elif task_id == "c10_overdue_unattested":
            answer = answer_c10_overdue_unattested()
        elif task_id == "c11_approval_history":
            answer = answer_c11_approval_history()
        elif task_id == "c12_contracts_without_owner":
            answer = answer_c12_contracts_without_owner()
        elif task_id == "c13_auto_renewal_overdue":
            answer = answer_c13_auto_renewal_overdue()
        elif task_id == "c14_orphan_amendments":
            answer = answer_c14_orphan_amendments()
        elif task_id == "c15_top_party_drift":
            answer = answer_c15_top_party_drift()
        elif task_id == "c16_pending_overdue":
            answer = answer_c16_pending_approval_overdue()
        elif task_id == "t18_route_task":
            answer = answer_t18_route_task()
        elif task_id == "t19_route_task_llm":
            answer = answer_t19_route_task_llm()
        elif task_id == "t21_route_c4":
            answer = answer_t21_route_c4()
        else:
            answer = None

        verdict = verifier(answer)
        passed = bool(verdict.get("pass"))
        score = 1.0 if passed else 0.0
        evidence = json.dumps(verdict, default=str)[:200]
        return {
            "id": task_id,
            "title": title,
            "passed": passed,
            "score": score,
            "evidence": evidence,
        }
    except Exception as e:
        return {
            "id": task_id,
            "title": title,
            "passed": False,
            "score": 0.0,
            "evidence": f"error: {e}",
        }


def main():
    instance = os.environ.get("AGENTSWITCH_INSTANCE", "unknown")
    print(f"running {len(TASKS)} tasks against instance {instance}")

    tasks = []
    passed = 0
    for tid, title, verifier in TASKS:
        start = time.time()
        result = run_one(tid, title, verifier)
        result["elapsed_s"] = round(time.time() - start, 2)
        tasks.append(result)
        if result["passed"]:
            passed += 1
        print(f"{tid}: {'PASS' if result['passed'] else 'FAIL'}  ({result['elapsed_s']}s)")

    summary = f"{passed}/{len(TASKS)} passed"
    output = {"tasks": tasks, "summary": summary}
    RESULTS.write_text(json.dumps(output, indent=2))
    print(f"\nwrote {RESULTS}  —  {summary}")


if __name__ == "__main__":
    main()
