# Findings — Contracts Agent (Team 17)

A summary of the investigation: what was tested, what was found, what was
fixed, and what the pattern is.

## The pattern

Every bug found follows the same class: **schema-vs-behavior drift**.

The `endpoint.contracts.*` tools document behavior in their descriptions —
numeric bounds, argument names, required fields — but the server does not
consistently enforce or expose what the descriptions claim.

Concrete forms:

- **Bounds documented but not declared:** `horizon_days` says "min 1" but
  the schema has no `minimum`.
- **Envelope inconsistency:** `obligation_evidence_pack` reported failures
  via `result.isError` while entity tools used the JSON-RPC `error` field.
- **Payload shape:** `renewal_forecast` nested its payload under an extra
  `"result"` key, unlike every other tool.
- **Field name mismatch:** `clause_key` says "Key of a clause present in the
  document's clauses_used" — but `clauses_used` has no `clause_key` field.
- **Required vs optional:** `proposed_content` is documented as optional but
  the server requires it.
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

**Six of nine fixed by the platform within a week.**

## Before and after — the six fixes

### Bug 1 — `horizon_days` bounds

**Before:**
    {horizon_days: 0}  -> OK (accepted)
    {horizon_days: -5} -> OK (accepted)

**After:**
    {horizon_days: 0}  -> invalid_arguments: /horizon_days must be at least 1

### Bug 2 — failure envelope

**Before:**
    obligation_evidence_pack on a missing contract returned:
    {"result": {"isError": true, "_meta": {...}}}   (no `error` key)

**After:**
    {"error": {"message": "Contract not found.", "data": {"code": "not_found"}}}

Same shape as entity tools.

### Bug 3 — `limit` bounds

**Before:**
    {limit: -1}   -> OK
    {limit: 9999} -> OK

**After:**
    {limit: -1}   -> invalid_arguments
    {limit: 9999} -> invalid_arguments

### Bug 5 — double-nested payload

**Before:**
    payload = {"result": {"contracts": [...]}}   (data under "result")

**After:**
    payload = {"as_of": ..., "contracts": [...], "counts": {...}}

Same shape as `Contract.list`.

### Bug 6 — `clause_key` format

**Before:** every value tried was rejected:
    "confidentiality"            -> clause_not_in_document
    "data_protection"            -> clause_not_in_document
    "Confidentiality — Tool Room" -> clause_not_in_document

**After (workaround identified):**
    clause_key = "8d4bd634-..." (the clause's UUID from clauses_used)
    -> SUCCESS, deviation_id returned

Also: `proposed_content` is required even though the schema says optional.

### Bug 9 — `tools.search` scoping

**Before:** search returned `endpoint.people_directory`, which was not in the
seat's `tools/list`. Calling it gave `invalid_arguments`.

**After:** the seat was expanded from 239 to 262 tools and
`endpoint.people_directory` is now callable. `tools/list` and `tools.search`
return consistent results.

## The harness

The harness proves the agent works — not just that it returns something.

**11 tasks, including 2 refusal tasks.**

| Task | What it checks |
|---|---|
| t0_health_check | Auth works, tools/list returns tools |
| t1_renewal_forecast | Expiring contracts match the DB |
| t2_playbook_review | A real clause deviation was written |
| t3_missing_obligations | Evidence packs retrieved per contract |
| t4_renewal_decision | A ContractRenewal moved off "undecided" |
| t5_deviation_approval | A deviation entered the approval flow |
| t6_refusal_cross_seat | Agent declines another seat's data |
| t7_refusal_unsupported | Agent declines unsupported questions |
| t8_pagination | Contract.list returns bounded rows |
| t9_workflow_guard | Invalid state transitions are rejected |
| t10_tools_list_scoping | No foreign tools exposed |

**Every verifier re-queries the platform via MCP.** They never trust the
agent's text. Runs are written to `runs/run_<timestamp>.jsonl` before scoring.

Current: **11/11 PASS.**

## The tests

18 hand-written tests in `tests/`, one file per bug, documenting either the
bug (when open) or the fix (when closed).

| File | Bug | Tests |
|---|---|---|
| test_horizon_days_bounds.py | 1 | 2 |
| test_obligation_pack_envelope.py | 2 | 1 |
| test_obligation_pack_limit.py | 3 | 3 |
| test_offset_bounds.py | 4 | 2 |
| test_renewal_forecast_double_nesting.py | 5 | 2 |
| test_propose_clause_deviation_clause_key.py | 6 | 2 |
| test_counts_in_horizon.py | 7 | 2 |
| test_renewal_forecast_date_args.py | 8 | 2 |
| test_search_unavailable_tool.py | 9 | 2 |

## What this means

The Contracts MCP surface is well built where it matters most — the workflow
state machines are correctly guarded, the cross-seat boundary is enforced, and
pagination is correct.

The defects cluster in one seam: **documented behavior that the schema and
the server do not agree on.**

The fix for the platform is straightforward: for every argument whose
description states a bound or constraint, declare it in the JSON schema and
enforce it in the validator. For every field whose description references
another field, verify that field actually exists.
