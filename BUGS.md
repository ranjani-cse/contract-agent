# Bugs filed against AgentSwitch — Contracts seat (Team 17)

All bugs filed via the platform's "Report a problem" form, with evidence committed to this repo.

| # | Date | Tool | Summary | Severity | Evidence |
|---|------|------|---------|----------|----------|
| 1 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts `horizon_days` below documented "min 1"; schema declares no `minimum` | Medium | [bug2_evidence.txt](evidence/team17/bug2_evidence.txt) |
| 2 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Reports failure via `result.isError` instead of the JSON-RPC `error` field used by entity tools | High | [bug3_evidence.txt](evidence/team17/bug3_evidence.txt) |
| 3 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Accepts `limit` outside documented 1-200 clamp; schema declares no bounds | Medium | [bug4_evidence.txt](evidence/team17/bug4_evidence.txt) |
| 4 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts out-of-range `offset`; schema declares no `minimum` | Low | [bug5_evidence.txt](evidence/team17/bug5_evidence.txt) |
| 5 | 2026-09-21 | endpoint.contracts.renewal_forecast | Nests payload under extra `"result"` key | Medium-High | [bug6_evidence.txt](evidence/team17/bug6_evidence.txt) |
| 6 | 2026-09-22 | endpoint.contracts.propose_clause_deviation | Rejects every `clause_key` from clauses_used; no discoverable value | High | [bug7_clause_key_evidence.txt](evidence/team17/bug7_clause_key_evidence.txt) |
| 7 | 2026-09-23 | endpoint.contracts.renewal_forecast | `counts.in_horizon` varies with `limit`, contradicting horizon semantics | High | [bug8_counts_horizon_evidence.txt](evidence/team17/bug8_counts_horizon_evidence.txt) |
| 8 | 2026-09-23 | endpoint.contracts.renewal_forecast | Silently ignores `from_date`/`to_date`; accepts malformed and inverted ranges and returns the default window | High | [bug9_date_args_ignored_evidence.txt](evidence/team17/bug9_date_args_ignored_evidence.txt) |
| 9 | 2026-09-23 | tools.search + endpoint.people_directory | `tools.search` returns a tool absent from the seat's tools/list; calling it reports `invalid_arguments` instead of `tool_not_available` | Medium-High | [bug10_people_directory_evidence.txt](evidence/team17/bug10_people_directory_evidence.txt) |

## Pattern

`endpoint.contracts.*` tools document behavior but do not enforce or expose it consistently. The `tools.*` discovery tools surface unavailable tools with misleading errors.

## Withdrawn / corrected

- An earlier report on `renewal_forecast` rejecting `days` was filed with the wrong argument name and withdrawn.
- The `counts.in_horizon` bug was filed twice; the second copy was closed as duplicate.

## Total

9 valid bugs filed. 1 withdrawn. 1 duplicate closed.

## Fixed by the platform

Confirmed fixed on 2026-09-29. Six of the nine filed bugs now behave correctly.

- **Bug 1** — `renewal_forecast` accepts `horizon_days` below documented min 1.
  Server now returns `invalid_arguments: /horizon_days must be at least 1`.

- **Bug 2** — `obligation_evidence_pack` reported failure via `result.isError`.
  Now uses the JSON-RPC `error` field, consistent with entity tools.

- **Bug 3** — `obligation_evidence_pack` accepted `limit` outside 1-200.
  Now rejects out-of-range values with `invalid_arguments`.

- **Bug 4** — `renewal_forecast` accepted negative `offset`.
  Negative now rejected; the upper bound is still missing (partial fix).

- **Bug 5** — `renewal_forecast` nested its payload under an extra `"result"` key.
  Now returns `contracts` at the top level, matching entity tools.

- **Bug 6** — `propose_clause_deviation` rejected every `clause_key` tried.
  Correct value is the clause's UUID from `clauses_used`; `proposed_content`
  is required (schema says optional). Workaround implemented in the agent.

- **Bug 9** — `tools.search` returned `endpoint.people_directory` not in `tools/list`.
  The seat was expanded from 239 to 247 tools; the tool is now callable.

## Updates

**Bug 6 — updated 2026-09-29.** Investigation identified the correct value for `clause_key`: the clause's **UUID** from the document's `clauses_used` array. With the correct UUID and a `proposed_content` value, `propose_clause_deviation` succeeds. Two schema documentation defects:

- `clause_key` is described as "Key of a clause present in the document's clauses_used" — but `clauses_used` has no `clause_key` field. The accepted value is `clause_id` (a UUID).
- `proposed_content` is documented as optional with a default, but the server requires it (`proposed_content_required`, 422).

Evidence: `bug6_UPDATE_evidence.txt`. The agent's `review_against_playbook` now uses the correct format.

## Test data note

The harness run on 2026-09-29 created deviations to prove the playbook write
path works. Two were moved to `pending_approval` by `bind_deviation_approval`
and cannot be withdrawn from this seat.

The state machine's error message says:
  "From 'pending_approval' you can go to: approved (Approve); draft (Send Back); rejected (Reject)"
but no Approve, Send Back, or Reject tool exists in this seat's `tools/list`.
The withdraw tool only accepts `draft`.

**Observation:** the error message suggests actions a client cannot perform
from this seat. A discoverability gap similar to Bug 6's clause_key.

IDs in `pending_approval`:
- 9fd4003f-fd0b-4900-b918-97621be92a38
- a84262dc-2cc0-4269-92fd-893daf715f7c
