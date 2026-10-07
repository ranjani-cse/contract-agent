# Contract Agent — AgentSwitch Project (Team 17)

An agent for the Contracts seat that reviews contracts against a playbook, flags risks, and alerts on expirations.

## Week 1 — Gap Report

- [Gap Report vs Ironclad](reports/gap-report-ironclad.md)
- [Raw research notes](research/ironclad.md)

## Week 2 — Agent, Harness, Tests

- **Agent** (`agent/agent.py`) answers the A17 request against live data:
  expiring contracts, playbook review (writes real deviations), missing
  obligations, renewal decisions, and deviation approvals.
- **Harness** (`harness/`) — 7 tasks including 2 refusal tasks. Verifiers
  read the database, not the agent's output. 7/7 PASS.
- **Tests** (`tests/`) — 18 hand-written tests, one file per bug.
- **Bugs** — 9 filed against `endpoint.contracts.*` and `tools.search`.
  Six were fixed by the platform within a week. See `BUGS.md`.
- **Findings** — see `FINDINGS.md` for the pattern across all bugs.

## Repo layout

    agent/          MCP client, agent, agent loop
    harness/        Loop, task set, DB-reading verifiers
    probes/         11 bug-hunting classes
    tests/          18 hand-written tests
    evidence/
      team17/       Evidence for filed bugs
      teammate/     Group member's tool-testing outputs
    runs/           Harness run logs
    BUGS.md         Bug index with fix status
    WEEK2.md        Week 2 write-up
    FINDINGS.md     One-page summary of the investigation

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
