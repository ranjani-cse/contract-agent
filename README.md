# Contract Agent — AgentSwitch Project (Team 17)

An agent for the Contracts seat that reviews contracts against a playbook, flags risks, and alerts on expirations.

## Week 1 — Gap Report

- [Gap Report vs Ironclad](reports/gap-report-ironclad.md)
- [Raw research notes](research/ironclad.md)

## Week 2 — Agent, Harness, Tests

- **Agent** (`agent/agent.py`) answers the A17 request against live data:
  expiring contracts, playbook review (writes real deviations), missing
  obligations, renewal decisions, and deviation approvals.
- **Harness** (`harness/`) — 31 tasks: 18 base (t0-t17), 12 complex (c1-c12),
  plus a dispatcher test (t18). Verifiers read the database, not the agent's
  output. 31/31 PASS locally.
- **Tests** (`tests/`) — 25+ hand-written tests: base behaviors, complex
  handlers (c1-c12), dispatcher (t18), and one file per filed bug.
- **Bugs** — 9 filed against `endpoint.contracts.*` and `tools.search`.
  Six were fixed by the platform within a week. See `BUGS.md`.
- **Findings** — see `FINDINGS.md` for the pattern across all bugs.

## Repo layout

    agent/          MCP client, agent, agent loop
    harness/        Loop, task set, DB-reading verifiers
    probes/         11 bug-hunting classes
    tests/          25+ hand-written tests
    evidence/
      team17/       Evidence for filed bugs
      teammate/     Group member's tool-testing outputs
    runs/           Harness run logs
    BUGS.md         Bug index with fix status
    WEEK2.md        Week 2 write-up
    FINDINGS.md     One-page summary of the investigation
    STATUS.md       Session log and milestones
    PLATFORM_RUN_24.md  First platform result (24 tasks)
    PLATFORM_RUN_31.md  Second platform result (31 tasks)

## Documentation

| File | What it covers |
|---|---|
| `README.md` | This file — overview |
| `WEEK2.md` | Week 2 write-up |
| `DESIGN.md` | Agent and harness architecture |
| `FINDINGS.md` | The pattern across all 9 bugs |
| `BUGS.md` | Bug index with fix status |
| `DEFERRED.md` | What's not built and why |
| `harness/README.md` | Harness tasks and design |
| `STATUS.md` | Session log and platform milestones |
| `PLATFORM_RUN_24.md` | First platform result (24 tasks) |
| `PLATFORM_RUN_31.md` | Second platform result (31 tasks) |

## Current status

- **31 tasks** in the suite: 18 base (t0-t17), 12 complex (c1-c12), 1 dispatcher (t18)
- **Local run:** 31/31 PASS
- **Latest commit:** 2094c13 (origin/main)
- **Server run:** pending — will be recorded in `PLATFORM_RUN_31.md`
- **Dispatcher:** `route_task` (keyword, deterministic) + `route_task_llm`
  (14-label LLM classifier, falls back to keyword on failure)

