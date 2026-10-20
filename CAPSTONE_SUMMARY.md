# Capstone Summary — Contract Agent Harness

## What was built

A contracts agent that answers business questions against the AgentSwitch
platform's Contracts seat, plus a harness that verifies the answers end-to-end.

### Agent (`agent/`)

- **MCP client** — calls platform tools via JSON-RPC with proper auth,
  error envelope handling (3 distinct failure shapes), 401/429 detection
- **18 base handlers** — auth, renewal forecast, playbook review, workflow
  guards, refusals, pagination, concurrency, malformed IDs, tool scoping
- **12 complex handlers (c1–c12)** — multi-step business queries covering
  disputes, close blockers, renewal risk, playbook drift, renewal packages,
  portfolio audits, templates, preferences, amendments, overdue obligations,
  approval history, and owner coverage
- **Dispatcher** — deterministic keyword router (`route_task`) +
  14-label LLM classifier (`route_task_llm`)
- **Planner (L1 hybrid)** — `agent/planner.py`, `agent/executor.py`,
  `agent/agent_loop.py`. Composes multi-intent prompts into a plan,
  executes via handlers, returns aggregated result. LLM-first with
  rule-based fallback.

### Harness (`harness/`)

- **32 tasks** — 18 base + 12 complex + 2 dispatcher (t18 keyword, t19 LLM)
- **Live verifiers** — each task reads the DB to confirm the agent's answer
- **Runner** — writes `results.json` in the platform format
- **Rules respected** — env vars only, no hard-coded URLs, no `.env` reads

## Verified results

| Run | Commit | Result | Date |
|---|---|---|---|
| Base only | 3912939 | 18/18 | 10 Oct |
| + c1–c6 | 8cd9ff8 | 24/24 | 13 Oct |
| + c7–c12 + t18/t19 | 5f98bcf | 32/32 | 16 Oct |
| + planner + rules fixes | faf47af | 32/32 | 20 Oct |

## Bug findings

Filed 9 bugs against the platform during the capstone; 6 fixed within
a week. Details in `BUGS.md`.

## What's next (post-capstone)

- L2 planner: re-planning + result synthesis
- Keystone instance support (second seat)
- Tool-level planning (compose raw tools, not just handlers)
