# Status — Contracts Agent (Team 17)

One-page answer to "where are we now."

## What's built

| Component | Location | Status |
|---|---|---|
| MCP client | agent/mcp_client.py | Done |
| Agent | agent/agent.py | Done — 5 operations answering A17 |
| Agent loop | agent/agent_loop.py | Done |
| Harness | harness/ | Done — 16 tasks, all passing |
| Tests | tests/ | 23 tests covering all filed bugs + behavior |
| Probes | probes/ | 11 classes tested |
| Documentation | repo root | 8 files |

## What works

- Agent answers the A17 request against live data.
- Writes are real: clause deviations, renewal decisions, approvals.
- Harness 16/16 PASS. Verifiers re-query the database, never trust the agent.
- Refusal tasks pass (t6, t7).
- 23 hand-written tests pass.

## Bugs filed

| # | Tool | Status |
|---|---|---|
| 1 | renewal_forecast horizon_days | Fixed |
| 2 | obligation_evidence_pack envelope | Fixed |
| 3 | obligation_evidence_pack limit | Fixed |
| 4 | renewal_forecast offset | Partial |
| 5 | renewal_forecast double-nesting | Fixed |
| 6 | propose_clause_deviation clause_key | Solved (workaround) |
| 7 | renewal_forecast counts.in_horizon | Open |
| 8 | renewal_forecast date args | Open |
| 9 | tools.search unavailable tool | Fixed |

6 of 9 fixed by the platform within a week.

## Harness tasks

16 tasks (t0–t15):
- t0 health check
- t1-t5 real MCP calls
- t6, t7 refusal
- t8-t10 pagination, workflow guard, tool scoping
- t11 concurrency, t12 malformed id, t13 offset past end
- t14 tools.describe foreign, t15 obligation workflow guard

## What's not built

See DEFERRED.md:
- Top-N limited to 3 contracts per run
- Keystone (US instance) not tested
- Dynamic planning not implemented

## Documentation

- README.md — overview + doc index
- WEEK2.md — Week 2 write-up
- DESIGN.md — architecture
- FINDINGS.md — pattern across bugs
- BUGS.md — bug index with fix status
- DEFERRED.md — incomplete work
- harness/README.md — harness design
- STATUS.md — this file

## Repo

https://github.com/ranjani-cse/contract-agent

## Latest harness run

16/16 PASS. Log in harness_live_run.txt
