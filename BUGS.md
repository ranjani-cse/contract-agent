# Bugs filed against AgentSwitch — Contracts seat (Team 17)

All bugs filed via the platform's "Report a problem" form, with evidence committed to this repo.

| # | Date | Tool | Summary | Severity | Evidence |
|---|------|------|---------|----------|----------|
| 1 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts `horizon_days` below documented "min 1"; schema declares no `minimum` | Medium | [bug2_evidence.txt](bug2_evidence.txt) |
| 2 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Reports failure via `result.isError` instead of the JSON-RPC `error` field used by entity tools — silent-failure path | High | [bug3_evidence.txt](bug3_evidence.txt) |
| 3 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Accepts `limit` values outside documented 1-200 clamp; schema declares no `minimum`/`maximum` | Medium | [bug4_evidence.txt](bug4_evidence.txt) |
| 4 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts out-of-range `offset` values; schema declares no `minimum` | Low | [bug5_evidence.txt](bug5_evidence.txt) |

## Pattern

The `endpoint.contracts.*` tools document numeric bounds in their descriptions ("min 1", "clamped to 1-200", "negative treated as 0") but neither enforce them server-side nor declare `minimum`/`maximum` in the JSON schema. Same class of defect on two tools, four arguments.

## Withdrawn / corrected

An earlier report on `renewal_forecast` rejecting `days` was filed with the wrong argument name and withdrawn with an honest correction on the same form.

## Total

4 valid bugs filed. 1 withdrawn with correction.
