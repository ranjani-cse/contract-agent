# Bugs filed against AgentSwitch — Contracts seat (Team 17)

All bugs filed via the platform's "Report a problem" form, with evidence committed to this repo.

| # | Date | Tool | Summary | Severity | Evidence |
|---|------|------|---------|----------|----------|
| 1 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts `horizon_days` below documented "min 1"; schema declares no `minimum` | Medium | [bug2_evidence.txt](bug2_evidence.txt) |
| 2 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Reports failure via `result.isError` instead of the JSON-RPC `error` field used by entity tools | High | [bug3_evidence.txt](bug3_evidence.txt) |
| 3 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Accepts `limit` outside documented 1-200 clamp; schema declares no bounds | Medium | [bug4_evidence.txt](bug4_evidence.txt) |
| 4 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts out-of-range `offset`; schema declares no `minimum` | Low | [bug5_evidence.txt](bug5_evidence.txt) |
| 5 | 2026-09-21 | endpoint.contracts.renewal_forecast | Nests payload under extra `"result"` key | Medium-High | [bug6_evidence.txt](bug6_evidence.txt) |
| 6 | 2026-09-22 | endpoint.contracts.propose_clause_deviation | Rejects every `clause_key` from clauses_used; no discoverable value | High | [bug7_clause_key_evidence.txt](bug7_clause_key_evidence.txt) |
| 7 | 2026-09-23 | endpoint.contracts.renewal_forecast | `counts.in_horizon` varies with `limit`, contradicting horizon semantics | High | [bug8_counts_horizon_evidence.txt](bug8_counts_horizon_evidence.txt) |
| 8 | 2026-09-23 | endpoint.contracts.renewal_forecast | Silently ignores `from_date`/`to_date`; accepts malformed and inverted ranges and returns the default window | High | [bug9_date_args_ignored_evidence.txt](bug9_date_args_ignored_evidence.txt) |

## Pattern

`endpoint.contracts.*` tools document arguments and behavior in their descriptions but do not enforce or expose them consistently:
- Numeric bounds documented but not declared in schema (bugs 1, 3, 4)
- Failure envelope inconsistent with entity tools (bug 2)
- Response payload envelope inconsistent (bug 5)
- Field name referenced in schema not present in data (bug 6)
- Counter semantics wrong (bug 7)
- Date arguments accepted but ignored, with no validation (bug 8)

Bug 6 blocks the A17 playbook-review task directly. Bug 8 affects the A17 date-window part.

## Withdrawn / corrected

- An earlier report on `renewal_forecast` rejecting `days` was filed with the wrong argument name and withdrawn.
- The `counts.in_horizon` bug was filed twice (#8, #9) — #9 marked duplicate, #8 kept.

## Total

8 valid bugs filed. 1 withdrawn. 1 duplicate closed.
