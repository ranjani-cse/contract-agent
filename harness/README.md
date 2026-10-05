# Harness — Contracts Agent (Team 17)

An 12-task evaluation of the A17 agent against live AgentSwitch data.

## How to run

    export AS_URL=https://agentswitch.theschoolofai.in
    export AS_TOKEN=<your token>
    export PYTHONPATH=<repo root>
    python3 -u harness/run_harness.py

## Files

| File | Purpose |
|---|---|
| `run_harness.py` | Loop: load tasks, run agent, verify, log |
| `tasks.jsonl` | 12 tasks including 2 refusal tasks |
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

## Design

- Verifiers re-query MCP independently; they never trust the agent's text
- Every run is written to `runs/run_<timestamp>.jsonl` before scoring
- A JSON-RPC error or auth failure is surfaced with a reason

## Current status

12/12 PASS. Latest run: `../harness_live_run.txt`
