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

## Platform run — 2026-10-10

Official harness run on the AgentSwitch platform: **18/18 PASS**.

Ran via "Our harness → Submit for a run" against a fresh Suryodaya instance.
Uses the cached runner (harness/runner.py) — one answer_a17 call shared
across t1-t5, ~55 seconds total.

## 2026-10-12 — Complex tasks added

Added c1–c5 (multi-step business requests) to the harness:
- c1 disputed quarter — party contract summary (15.9s)
- c2 close blockers — incomplete obligations (8.1s)
- c3 auto-renewal risk — flag at-risk contracts (24.2s)
- c4 playbook drift — clause coverage analysis (9.9s)
- c5 renewal package — decision package with recommendation (7.2s)

Local run: **23/23 PASS** in ~2 minutes.
Next: submit on the platform when the 3-day window opens.

## Tests

43 hand-written tests:
- 23 covering the 9 filed bugs (t0-t17 behaviors)
- 12 covering c1-c6 complex tasks
- 8 covering the dispatcher

Run: `python3 -c "from tests.test_c1_disputed_quarter import *"` etc.
All passing locally.

## Platform run — 2026-10-13

**24/24 PASS** on the platform (Suryodaya instance).

All 18 base tasks + 6 complex tasks passed on the server.
See `PLATFORM_RUN_24.md` for full evidence.

## Platform run — 2026-10-13

**24/24 PASS** on the platform (Suryodaya instance).

All 18 base tasks + 6 complex tasks passed on the server.
See `PLATFORM_RUN_24.md` for full evidence.


## Session — 2026-10-16 (harness extension)

**Extended the harness from 24 to 32 tasks.** Added six complex handlers
(c7-c12) and one dispatcher self-test (t18).

| Task | Purpose | Local |
|---|---|---|
| c7 templates + playbooks   | List ContractTemplate + ContractPlaybook       | PASS |
| c8 contract preferences    | Read ContractPreferences                       | PASS |
| c9 active amendments       | Amendments per active contract                 | PASS |
| c10 overdue + unattested   | Filter obligations by status + attestation     | PASS |
| c11 approval history       | Read approval_request_id / approval_status     | PASS |
| c12 contracts without owner| Filter contracts missing owner_id              | PASS |
| t18 route_task             | Dispatcher routes free-text prompt to handler  | PASS |

**Local run:** 32/32 PASS
**Latest commit:** 42f553d (pushed to origin/main)

### Also updated

- `route_task`: six new keyword branches for c7-c12
- `route_task_llm`: expanded from 8 to 14 labels; handler dict now maps all 13
- `DESIGN.md`: documented c1-c12 handlers + dispatcher section

### Pending

- Server run (evening 2026-10-16) — record result in `PLATFORM_RUN_31.md`
- Update this file with the platform score after the run
- Message Rohan / Ranjani with the result


## Platform run — 2026-10-16

**32/32 PASS** on the platform (Suryodaya instance, commit 5f98bcf).

All 18 base tasks + 12 complex tasks (c1-c12) + 2 dispatcher tests
(t18, t19) passed on the server. Tokens used: 196.

See `PLATFORM_RUN_32.md` for full evidence.

Next submit window: 2026-10-19 15:10.


## Platform run — 2026-10-20 (planner on main)

**32/32 PASS** (Suryodaya, commit faf47af, tokens used: 196).

Confirms the planner (L1 hybrid) on `main` does not regress any task.
LLM dispatcher active on server (`source: "llm"` in t19).
Harness rules verified: no hard-coded URL, 401/429 handled, failure_reason fixed.

See `PLATFORM_RUN_32_PLANNER.md` for full evidence.

Next submit window: 2026-10-23 15:49.


## Capstone closeout — 2026-10-22

Extended harness to **37 tasks**:
- 18 base + 16 complex (c1-c16) + 3 dispatcher (t18, t19, t21)
- c13-c16: cross-entity joins (auto-renewal ∩ overdue, orphans ∩ amendments,
  top-party drift, pending-approval ∩ overdue)
- t6 fixed: genuine cross-seat refusal (tool_not_available)
- t21 added: model path exercised for a real c-task

Local run: 37/37 PASS. Awaiting 23 Oct submission window.

Real findings from joins:
- c13: 46 contracts auto-renewing AND have overdue obligations
- c15: top party with 24 amendments → 3 drift reports
- c16: 42 contracts pending approval AND have overdue obligations
