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
