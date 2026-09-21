# Bugs filed against AgentSwitch — Contracts seat (Team 17)

All bugs filed via the platform's "Report a problem" form, with evidence committed to this repo.

| # | Date | Tool | Summary | Severity | Evidence |
|---|------|------|---------|----------|----------|
| 1 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts `horizon_days` below documented "min 1"; schema declares no `minimum` | Medium | [bug2_evidence.txt](bug2_evidence.txt) |
| 2 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Reports failure via `result.isError` instead of the JSON-RPC `error` field used by entity tools — silent-failure path | High | [bug3_evidence.txt](bug3_evidence.txt) |

## Withdrawn / corrected

An earlier report on `renewal_forecast` rejecting `days` was filed with the wrong argument name and withdrawn with an honest correction on the same form. See `bug1_evidence.txt` for the original probe output.
