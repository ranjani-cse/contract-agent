# Week 2 — Contracts Agent (Team 17)

## What I Built

- **MCP client** (`agent/mcp_client.py`) — JSON-RPC over HTTP, `tools/call`,
  `tools/list`, auth via bearer token, failure detection across all three
  envelope shapes (`error`, `result.isError`, `detail`).
- **Agent** (`agent/agent.py`) — answers the A17 request end-to-end:
  1. `endpoint.contracts.renewal_forecast` → expiring contracts
  2. `ContractDocument.list` + `ContractClause.list` → playbook comparison
  3. `endpoint.contracts.obligation_evidence_pack` → missing obligations
- **Agent loop** (`agent/agent_loop.py`) — plan → act → observe → done.
- **Harness** (`harness/`) — task set, DB-reading verifiers, run logs written
  before scoring.
- **Probes** (`probes/`) — 11 bug-hunting classes tested against the live
  platform.
- **Tests** (`tests/`) — 12 hand-written tests across 6 files.

## Architecture

    agent.py
      └── mcp_client.py  ──HTTP──►  agentswitch.theschoolofai.in/api/mcp
      └── harness/run_harness.py
            └── tasks.jsonl
            └── verifiers.py
      └── tests/
            └── test_*.py

## What Works

- MCP connection — 239 tools listed
- Tool calling — auth, JSON-RPC envelope handled correctly
- Expiring contracts — 16 returned in the 60-day window
- Playbook comparison — structural (propose_clause_deviation unusable, Bug 6)
- Obligation evidence pack — per-contract retrieval
- Refusal tasks (t6, t7) — agent declines unavailable / unsupportable questions
- Harness — 5/7 honest PASS, 2 tasks deferred

## Known Issues

- `propose_clause_deviation` rejects every `clause_key` from `clauses_used`
  (Bug 6). Workaround: structural playbook comparison instead of writing a
  deviation row.
- `renewal_forecast` `counts.in_horizon` varies with `limit` (Bug 7).
- `renewal_forecast` `from_date`/`to_date` silently ignored (Bug 8).
- `renewal_forecast` `offset` upper bound missing (partial fix).
- Harness tasks t4/t5 deferred — `record_renewal_decision` and
  `bind_deviation_approval` paths not built.

## Bugs Filed

Nine bugs filed against `endpoint.contracts.*` and `tools.search`, all with
reproducible evidence in this repo. Four were fixed by the platform between
2026-09-23 and 2026-09-29 (Bugs 1, 2, 3, 4). Full list in `BUGS.md`.

## Tests Written

12 hand-written tests in `tests/`:

| File | Tests | Bug |
|---|---|---|
| `test_horizon_days_bounds.py` | 2 | Bug 1 (fixed) |
| `test_obligation_pack_envelope.py` | 1 | Bug 2 (fixed) |
| `test_obligation_pack_limit.py` | 3 | Bug 3 (fixed) |
| `test_offset_bounds.py` | 2 | Bug 4 (partial) |
| `test_counts_in_horizon.py` | 2 | Bug 7 (open) |
| `test_renewal_forecast_date_args.py` | 2 | Bug 8 (open) |

## Next Week

- Build the `record_renewal_decision` and `bind_deviation_approval` agent paths
  to complete t4/t5 in the harness.
- Investigate `propose_clause_deviation`'s `clause_key` field further — a
  working call may exist using a field not documented in the schema.
- Add a task to the harness that detects changes made by other teams between
  reads.
