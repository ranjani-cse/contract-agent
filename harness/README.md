# Harness — Contracts Agent (Team 17)

A 7-task evaluation of the A17 agent against live AgentSwitch data.

## How to run

    export AS_URL=https://agentswitch.theschoolofai.in
    export AS_TOKEN=<your token>
    export PYTHONPATH=<repo root>
    python3 -u harness/run_harness.py

## Files

| File | Purpose |
|---|---|
| `run_harness.py` | Loop: load tasks, run agent, verify, log |
| `tasks.jsonl` | 7 tasks including 2 refusal tasks |
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

## Design

- Verifiers re-query MCP independently; they never trust the agent's text
- Every run is written to `runs/run_<timestamp>.jsonl` before scoring
- A JSON-RPC error or auth failure is surfaced with a reason

## Current status

7/7 PASS. Latest run: `../harness_live_run.txt`
