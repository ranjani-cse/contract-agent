# Harness — Contracts Agent (Team 17)

An 18-task evaluation of the A17 agent against live AgentSwitch data.

## How to run

    export AS_URL=https://agentswitch.theschoolofai.in
    export AS_TOKEN=<your token>
    export PYTHONPATH=<repo root>
    python3 -u harness/run_harness.py

## Files

| File | Purpose |
|---|---|
| `run_harness.py` | Loop: load tasks, run agent, verify, log |
| `tasks.jsonl` | 18 tasks including 2 refusal tasks |
| `verifiers.py` | DB-reading verifiers, one per task |

## Tasks

| ID | What it checks |
|---|---|
| t1_renewal_forecast | Expiring contracts match the DB |
| t2_playbook_review | Agent wrote a real clause deviation |
| t3_missing_obligations | Evidence packs retrieved per contract |
| t4_renewal_decision | A ContractRenewal moved off "undecided" |
| t5_deviation_approval | A deviation entered the approval flow |
| t6_refusal_cross_seat | Agent declines another seat's data |
| t7_refusal_unsupported | Agent declines unsupported questions |
| t8_pagination | `Contract.list` with limit=100 returns bounded rows |
| t9_workflow_guard | Invalid state transitions are rejected |
| t10_tools_list_scoping | No foreign tools exposed |
| t11_concurrency | Platform state is mutable; harness reads the new state |
| t12_malformed_id | Contract.get rejects a malformed UUID |
| t13_offset_past_end | Contract.list with a past-end offset returns zero rows |
| t14_tools_describe_foreign | tools.describe reports foreign tools as not_available |
| t15_obligation_workflow_guard | Invalid obligation transitions are rejected |
| t16_contract_get_missing | Contract.get on a valid-format UUID returns not_found |
| t17_tools_describe_available | tools.describe returns schema for available tools |

## Design

- Verifiers re-query MCP independently; they never trust the agent's text
- Every run is written to `runs/run_<timestamp>.jsonl` before scoring
- A JSON-RPC error or auth failure is surfaced with a reason

## Current status

18/18 PASS. Latest run: `../harness_live_run.txt`
