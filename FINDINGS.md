# Findings — Contracts Agent (Team 17)

A one-page summary of the investigation: what was tested, what was found,
what was fixed, and what it means.

## What was tested

Eleven classes of behavior against the AgentSwitch Contracts MCP surface:

| Class | Result |
|---|---|
| `Contract` workflow transitions | Guarded |
| `ContractObligation` workflow transitions | Guarded |
| `ContractDocument` workflow transitions | Guarded |
| Cross-seat boundary (12 foreign tools) | Enforced |
| Pagination on `Contract.list` | Correct |
| Response shapes (Contract + CRM + Agent tools) | Uniform |
| Malformed IDs | Safe |
| Empty args on endpoint tools | Rejected |
| Numeric bounds on `endpoint.contracts.*` | 9 bugs filed |
| Date arguments on `renewal_forecast` | Bug filed |
| `tools.describe` / `tools.search` | Bug filed |

## The pattern

Every bug found follows the same class: schema-vs-behavior drift.

The `endpoint.contracts.*` tools document behavior in their descriptions --
numeric bounds, argument names, required fields -- but the server does not
consistently enforce or expose what the descriptions claim.

Specific forms:

- **Bounds documented but not declared:** `horizon_days` says "min 1" but the
  schema has no `minimum`. `limit` says "clamped to 1-200" but the schema has
  no `maximum`.
- **Envelope inconsistency:** `obligation_evidence_pack` reported failures via
  `result.isError` while entity tools used the JSON-RPC `error` field.
- **Payload shape:** `renewal_forecast` nested its payload under an extra
  `"result"` key, unlike every other tool.
- **Field name mismatch:** `clause_key` says "Key of a clause present in the
  document's clauses_used" -- but `clauses_used` has no `clause_key` field.
  The accepted value is `clause_id` (a UUID).
- **Required vs optional:** `proposed_content` is documented as optional with
  a default, but the server requires it.
- **Non-functional arguments:** `from_date` and `to_date` are documented,
  accepted, and silently ignored.

## The bugs

Nine filed via the platform's "Report a problem" form, all with reproducible
evidence in `evidence/team17/`.

| # | Tool | Summary | Status |
|---|---|---|---|
| 1 | `renewal_forecast` | `horizon_days` below min 1 accepted | Fixed |
| 2 | `obligation_evidence_pack` | Failure via `result.isError` not `error` | Fixed |
| 3 | `obligation_evidence_pack` | `limit` outside 1-200 accepted | Fixed |
| 4 | `renewal_forecast` | Negative `offset` accepted | Partial |
| 5 | `renewal_forecast` | Payload double-nested | Fixed |
| 6 | `propose_clause_deviation` | `clause_key` format undiscoverable | Solved (workaround) |
| 7 | `renewal_forecast` | `counts.in_horizon` varies with `limit` | Open |
| 8 | `renewal_forecast` | `from_date`/`to_date` ignored | Open |
| 9 | `tools.search` | Returned a tool not in `tools/list` | Fixed |

Six of nine fixed by the platform within one week.

## The harness

The harness proves the agent works, not just that it returns something.

- 7 tasks, including 2 refusal tasks (t6, t7)
- Verifiers read the database -- they re-query the platform and compare
  against what the agent claimed, never trusting the agent's prose
- Runs are written to disk before scoring -- every row is auditable
- 7/7 PASS with a real agent

The refusal tasks ask the agent for data it cannot access (another seat's
SalarySlips) or that doesn't exist (a liability cap for a contract not in the
book). The agent declines -- an invented answer would fail the task.

## The tests

18 hand-written tests in `tests/`, one file per bug, documenting either the
bug (when open) or the fix (when closed).

| File | Bug | Tests |
|---|---|---|
| `test_horizon_days_bounds.py` | 1 | 2 |
| `test_obligation_pack_envelope.py` | 2 | 1 |
| `test_obligation_pack_limit.py` | 3 | 3 |
| `test_offset_bounds.py` | 4 | 2 |
| `test_renewal_forecast_double_nesting.py` | 5 | 2 |
| `test_propose_clause_deviation_clause_key.py` | 6 | 2 |
| `test_counts_in_horizon.py` | 7 | 2 |
| `test_renewal_forecast_date_args.py` | 8 | 2 |
| `test_search_unavailable_tool.py` | 9 | 2 |

## What this means

The Contracts MCP surface is well built where it matters most -- the workflow
state machines are correctly guarded, the cross-seat boundary is enforced, and
pagination is correct. The defects cluster in one seam: documented behavior
that the schema and server do not agree on.

The fix for the platform is straightforward: for every argument whose
description states a bound or constraint, declare it in the JSON schema and
enforce it in the validator. For every field whose description references
another field, verify that field actually exists.
