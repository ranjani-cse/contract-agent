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
    answer_c5_renewal_package,
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
)

RESULTS = Path("results.json")

TASKS = [
    ("t0_health_check", "Auth works and tools/list returns tools", verify_health_check),
    ("t1_renewal_forecast", "Expiring contracts match the DB", verify_renewal_forecast),
    ("t2_playbook_review", "A real clause deviation was written", verify_playbook_review),
    ("t3_missing_obligations", "Evidence packs retrieved per contract", verify_missing_obligations),
    ("t4_renewal_decision", "A ContractRenewal moved off undecided", verify_renewal_decision),
    ("t5_deviation_approval", "A deviation entered the approval flow", verify_deviation_approval),
    ("t6_refusal_cross_seat", "Agent declines another seat's data", verify_refusal),
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
        elif task_id.startswith(("t6_", "t7_")):
            answer = answer_t7_refusal()
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
