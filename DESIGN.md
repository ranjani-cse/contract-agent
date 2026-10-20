# Design — Contracts Agent (Team 17)

How the agent and harness work, and why they're built this way.

## The request (A17)

> "What expires in 60 days, review this draft against our playbook,
> and list the obligations we are missing."

Three sub-goals, each answered by a different MCP tool.

## Agent architecture

The agent is a **fixed plan executed against live data**. It does not
plan dynamically — the sequence is coded, and the interesting work is
in the tool calls and error handling.

    agent/agent.py
      answer_a17(horizon_days=60)
        ├── expiring_soon(60)
        │     → endpoint.contracts.renewal_forecast
        ├── review_against_playbook(contract_id)
        │     ├── ContractDocument.list
        │     └── endpoint.contracts.propose_clause_deviation
        ├── missing_obligations(contract_id)
        │     → endpoint.contracts.obligation_evidence_pack
        ├── record_renewal_decision(contract_id)
        │     → endpoint.contracts.record_renewal_decision
        └── bind_deviation_approval(deviation_id)
              → endpoint.contracts.bind_deviation_approval

### Why fixed, not dynamic

The A17 request is well-defined. A dynamic planner would add cost and
failure modes without changing the answer. The value is in executing
each step correctly against live data — not in choosing the steps.

### Error handling

Three failure envelope shapes exist on the platform:

| Shape | When |
|---|---|
| `body["error"]` | Standard JSON-RPC error (entity tools) |
| `body["result"]["isError"]` | Some endpoint tools (Bug 2) |
| `body["detail"]` | Auth failure (401) |

`is_failure()` in `mcp_client.py` detects all three. Without this, a
client reading only `body["error"]` would treat a failure as success.

### Concurrency

Other teams share the CRM spine and may edit contracts during a run.
The agent re-reads before acting — it does not trust a row read earlier
in the same run.

## Harness architecture

The harness proves the agent works. It is not a test suite of the
agent's code — it is a **live evaluation** against the running platform.

    harness/run_harness.py
      load_tasks() → tasks.jsonl
      for each task:
        answer = run_agent(task)      ← real MCP calls
        write(answer)                 ← BEFORE scoring (spec requirement)
        verdict = score(task, answer) ← verifier re-queries the DB
        write(verdict)
        print(PASS/FAIL + reason)

### Verifiers read the database

Every verifier calls a tool independently and compares against what the
agent claimed. It never inspects the agent's text.

    def verify_renewal_forecast(agent_answer):
        db = call_tool("endpoint.contracts.renewal_forecast", {...})
        db_ids = set of IDs from db
        agent_ids = set of IDs from agent_answer
        return {"pass": db_ids == agent_ids, ...}

### Why "write before score" matters

If the verifier crashes or the process is killed, the agent's raw answer
is already on disk. Every run is auditable even if scoring fails.

### Tasks

12 tasks, chosen to cover:

| Category | Tasks |
|---|---|
| Environment | t0 |
| Read operations | t1, t3, t8, t10 |
| Write operations | t2, t4, t5, t11 |
| Refusal | t6, t7 |
| State-machine guard | t9 |

### Refusal tasks

t6 and t7 ask for data the agent cannot access or that doesn't exist.
The correct answer is refusal, not a confident guess. An agent that
invents an answer fails, no matter how well-written it is.

## Key design decisions

| Decision | Reason |
|---|---|
| MCP over REST | MCP is the primary interface; tool schemas drive the code |
| Fixed plan | The A17 request is well-defined; planning adds cost, not value |
| DB-reading verifiers | Trusting the agent's prose would let it fabricate |
| Write before score | Spec requirement; also makes failures debuggable |
| 3-way error detection | The platform uses three different failure envelopes |
| Refusal tasks | The spec requires testing that the agent declines |

## What's not built

| Item | Why |
|---|---|
| Dynamic planning | Not required; fixed plan covers the request |
| Keystone (US instance) testing | Requires separate credentials |
| t4/t5 agent paths | Would push harness to 14/14; not required |
| Full memory across runs | Agent is stateless per run |

## Files

| File | Purpose |
|---|---|
| `agent/mcp_client.py` | JSON-RPC client, 3-way failure detection |
| `agent/agent.py` | The five operations that answer A17 |
| `agent/agent_loop.py` | Plan → act → observe trace |
| `harness/run_harness.py` | The loop |
| `harness/tasks.jsonl` | 12 tasks |
| `harness/verifiers.py` | DB-reading verifiers, one per task |


---

# Complex Task Handlers (c1-c12) + Dispatcher (t18)

## Overview

The harness runs 32 tasks against the Contracts seat:

- t0-t17 - 18 base tasks (auth, pagination, workflow guards, refusals)
- c1-c12 - 12 complex tasks, each chaining multiple tool calls
- t18/t19 - dispatcher tests (keyword + LLM): proves free-text prompts route to the right handler

All 31 run through harness/runner.py, which invokes an answer_* in
agent/agent.py and a matching verify_* in harness/verifiers.py.

## Handler shape

Every complex handler follows the same pattern:

    def answer_cN_<name>():
        raw = _unwrap(call_tool("<Tool>.<method>", {...}))
        rows = raw.get("data", []) if isinstance(raw, dict) else []
        # filter / join / aggregate
        return {<structured result>}

The verifier then asserts on the structured result - counts, keys, or both.
No handler returns prose; every answer is machine-checkable.

## The 12 complex tasks

| ID  | Task                    | Tools used                                                    | Multi-step    |
|-----|-------------------------|---------------------------------------------------------------|---------------|
| c1  | Disputed quarter        | Contract.list + per-contract obligations                      | yes           |
| c2  | Close blockers          | Contract.list (active) + ContractObligation.list per contract | yes           |
| c3  | Auto-renewal risk       | endpoint.contracts.renewal_forecast                           | yes           |
| c4  | Playbook drift          | ContractDocument.list + propose_clause_deviation              | yes           |
| c5  | Renewal package         | renewal forecast + obligations + deviation history            | yes           |
| c6  | Portfolio audit         | c2 + c3 + c4 -> score -> prioritize                           | yes (3)       |
| c7  | Templates + playbooks   | ContractTemplate.list, ContractPlaybook.list                  | -             |
| c8  | Contract preferences    | ContractPreferences.list                                      | -             |
| c9  | Amendments on active    | Contract.list + ContractAmendment.list per contract           | yes           |
| c10 | Overdue + unattested    | ContractObligation.list -> filter status + attestation_state  | yes           |
| c11 | Approval history        | Contract.list -> approval_request_id / approval_status        | yes           |
| c12 | Contracts without owner | Contract.list -> filter missing owner_id                      | -             |

## Dispatcher

Two routing functions in agent/agent.py:

route_task(prompt) - deterministic keyword matching. Lowercases the prompt,
checks ordered if-branches (specific to general), calls the matching handler,
returns an error dict on miss.

route_task_llm(prompt) - LLM-based classification. Asks the platform model
to pick one of 14 labels: dispute, blockers, renewal_risk, playbook_drift,
renewal_package, portfolio_audit, expiry, templates, preferences, amendments,
overdue_obligations, approvals, missing_owner, unknown. Falls back to
route_task if the LLM is unavailable.

t18_route_task exercises route_task with
"Which obligations are overdue and unattested?" - must route to
answer_c10_overdue_unattested and return the correct keys.

## Design decisions

1. Keyword-first, LLM-optional. The deterministic router always works;
   the LLM router is a refinement layer.
2. Every handler returns structured data. Verifiers assert on counts and
   keys - no prose, reproducible results.
3. No false passes. Verifiers distinguish "empty but valid" (c12 with 0
   orphans) from "failed" (auth error, unknown tool).
4. Tool names verified against tools/list. Each handler uses the exact
   method name the seat exposes - validated live before commit.
5. Incremental coverage. One task at a time: write, test locally, commit.
   Suite was green at every step.

## Coverage matrix

| Entity              | Read | Filter | Aggregate |
|---------------------|------|--------|-----------|
| Contract            | yes  | yes    | yes       |
| ContractObligation  | yes  | yes    | yes       |
| ContractAmendment   | yes  | yes    | yes       |
| ContractTemplate    | yes  | -      | yes       |
| ContractPlaybook    | yes  | -      | yes       |
| ContractPreferences | yes  | -      | -         |
| ContractDocument    | yes  | -      | yes       |
| ContractRenewal     | yes  | yes    | yes       |
| PrivacyAuditEvent   | yes  | -      | -         |


## Planner

`agent/planner.py`, `agent/executor.py`, `agent/agent_loop.py` compose
multi-intent prompts into a sequence of handler calls.

- LLM planner: asks the platform model for a JSON plan of intents
- Rule fallback: matches keywords when no LLM is available

Wired into `route_task` as a fallback. Tests in `tests/test_planner.py`.
Verified on the platform: 32/32 PASS, 20 Oct 2026, commit faf47af.
