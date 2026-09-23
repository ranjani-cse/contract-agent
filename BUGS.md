# Bugs filed against AgentSwitch — Contracts seat (Team 17)

All bugs filed via the platform's "Report a problem" form, with evidence committed to this repo.

| # | Date | Tool | Summary | Severity | Evidence |
|---|------|------|---------|----------|----------|
| 1 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts `horizon_days` below documented "min 1"; schema declares no `minimum` | Medium | [bug2_evidence.txt](bug2_evidence.txt) |
| 2 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Reports failure via `result.isError` instead of the JSON-RPC `error` field used by entity tools | High | [bug3_evidence.txt](bug3_evidence.txt) |
| 3 | 2026-09-21 | endpoint.contracts.obligation_evidence_pack | Accepts `limit` outside documented 1-200 clamp; schema declares no bounds | Medium | [bug4_evidence.txt](bug4_evidence.txt) |
| 4 | 2026-09-21 | endpoint.contracts.renewal_forecast | Accepts out-of-range `offset`; schema declares no `minimum` | Low | [bug5_evidence.txt](bug5_evidence.txt) |
| 5 | 2026-09-21 | endpoint.contracts.renewal_forecast | Nests payload under extra "result" key | Medium-High | [bug6_evidence.txt](bug6_evidence.txt) |
| 6 | 2026-09-22 | endpoint.contracts.propose_clause_deviation | Rejects every clause_key from clauses_used; no discoverable value | High | [bug7_clause_key_evidence.txt](bug7_clause_key_evidence.txt) |
| 7 | 2026-09-22 | ContractClauseDeviation.get | ContractClauseDeviation not found. (not_found) | High | [bug7_evidence.txt](bug7_evidence.txt) |
| 8 | 2026-09-22 | ContractPlaybook.get | ContractPlaybook not found. (not_found) | High | [bug8_evidence.txt](bug8_evidence.txt) |
| 9 | 2026-09-22 | ContractPreferences.get | ContractPreferences not found. (not_found) | High | [bug9_evidence.txt](bug9_evidence.txt) |
| 10 | 2026-09-22 | ContractPreferences.create | Invalid tool arguments. (invalid_arguments) | High | [bug10_evidence.txt](bug10_evidence.txt) |
| 11 | 2026-09-22 | ContractPreferences.update | Invalid tool arguments. (invalid_arguments) | High | [bug11_evidence.txt](bug11_evidence.txt) |
| 12 | 2026-09-22 | ContractAmendment.get | ContractAmendment not found. (not_found) | High | [bug12_evidence.txt](bug12_evidence.txt) |
| 13 | 2026-09-22 | ContractObligation.get | ContractObligation not found. (not_found) | High | [bug13_evidence.txt](bug13_evidence.txt) |
| 14 | 2026-09-22 | ContractObligation.create | Invalid tool arguments. (invalid_arguments) | High | [bug14_evidence.txt](bug14_evidence.txt) |
| 15 | 2026-09-22 | ContractObligation.update | Invalid tool arguments. (invalid_arguments) | High | [bug15_evidence.txt](bug15_evidence.txt) |
| 16 | 2026-09-22 | ContractRenewal.get | ContractRenewal not found. (not_found) | High | [bug16_evidence.txt](bug16_evidence.txt) |
| 17 | 2026-09-22 | ContractRenewal.create | Invalid tool arguments. (invalid_arguments) | High | [bug17_evidence.txt](bug17_evidence.txt) |
| 18 | 2026-09-22 | ContractRenewal.update | Invalid tool arguments. (invalid_arguments) | High | [bug18_evidence.txt](bug18_evidence.txt) |
| 19 | 2026-09-22 | ContractClause.get | ContractClause not found. (not_found) | High | [bug19_evidence.txt](bug19_evidence.txt) |
| 20 | 2026-09-22 | ContractClauseDeviation.get | ContractClauseDeviation not found. (not_found) | High | [bug20_evidence.txt](bug20_evidence.txt) |
| 21 | 2026-09-22 | ContractClauseDeviation.create | Invalid tool arguments. (invalid_arguments) | High | [bug21_evidence.txt](bug21_evidence.txt) |
| 22 | 2026-09-22 | ContractClauseDeviation.update | Invalid tool arguments. (invalid_arguments) | High | [bug22_evidence.txt](bug22_evidence.txt) |
| 23 | 2026-09-22 | ContractDocument.get | ContractDocument not found. (not_found) | High | [bug23_evidence.txt](bug23_evidence.txt) |
| 24 | 2026-09-22 | ContractDocument.create | Invalid tool arguments. (invalid_arguments) | High | [bug24_evidence.txt](bug24_evidence.txt) |
| 25 | 2026-09-22 | ContractDocument.update | Invalid tool arguments. (invalid_arguments) | High | [bug25_evidence.txt](bug25_evidence.txt) |
| 26 | 2026-09-22 | ContractTemplate.get | ContractTemplate not found. (not_found) | High | [bug26_evidence.txt](bug26_evidence.txt) |
| 27 | 2026-09-22 | Contract.get | Contract not found. (not_found) | High | [bug27_evidence.txt](bug27_evidence.txt) |
| 28 | 2026-09-22 | Contract.create | Invalid tool arguments. (invalid_arguments) | High | [bug28_evidence.txt](bug28_evidence.txt) |
| 29 | 2026-09-22 | Contract.update | Invalid tool arguments. (invalid_arguments) | High | [bug29_evidence.txt](bug29_evidence.txt) |
| 30 | 2026-09-22 | ContractObligation.start | Invalid tool arguments. (invalid_arguments) | High | [bug30_evidence.txt](bug30_evidence.txt) |
| 31 | 2026-09-22 | ContractObligation.mark_complete | Invalid tool arguments. (invalid_arguments) | High | [bug31_evidence.txt](bug31_evidence.txt) |
| 32 | 2026-09-22 | ContractObligation.mark_overdue.in_progress.overdue | Invalid tool arguments. (invalid_arguments) | High | [bug32_evidence.txt](bug32_evidence.txt) |
| 33 | 2026-09-22 | ContractObligation.mark_overdue.pending.overdue | Invalid tool arguments. (invalid_arguments) | High | [bug33_evidence.txt](bug33_evidence.txt) |
| 34 | 2026-09-22 | ContractObligation.complete_late | Invalid tool arguments. (invalid_arguments) | High | [bug34_evidence.txt](bug34_evidence.txt) |
| 35 | 2026-09-22 | ContractRenewal.submit_for_approval | Invalid tool arguments. (invalid_arguments) | High | [bug35_evidence.txt](bug35_evidence.txt) |
| 36 | 2026-09-22 | ContractRenewal.revise | Invalid tool arguments. (invalid_arguments) | High | [bug36_evidence.txt](bug36_evidence.txt) |
| 37 | 2026-09-22 | ContractClauseDeviation.submit_for_approval | Invalid tool arguments. (invalid_arguments) | High | [bug37_evidence.txt](bug37_evidence.txt) |
| 38 | 2026-09-22 | ContractClauseDeviation.revise | Invalid tool arguments. (invalid_arguments) | High | [bug38_evidence.txt](bug38_evidence.txt) |
| 39 | 2026-09-22 | ContractClauseDeviation.withdraw.draft.withdrawn | Invalid tool arguments. (invalid_arguments) | High | [bug39_evidence.txt](bug39_evidence.txt) |
| 40 | 2026-09-22 | ContractDocument.submit_for_review | Invalid tool arguments. (invalid_arguments) | High | [bug40_evidence.txt](bug40_evidence.txt) |
| 41 | 2026-09-22 | ContractDocument.send_for_signature | Invalid tool arguments. (invalid_arguments) | High | [bug41_evidence.txt](bug41_evidence.txt) |
| 42 | 2026-09-22 | ContractDocument.mark_signed | Invalid tool arguments. (invalid_arguments) | High | [bug42_evidence.txt](bug42_evidence.txt) |
| 43 | 2026-09-22 | ContractDocument.archive | Invalid tool arguments. (invalid_arguments) | High | [bug43_evidence.txt](bug43_evidence.txt) |
| 44 | 2026-09-22 | ContractDocument.archive_draft | Invalid tool arguments. (invalid_arguments) | High | [bug44_evidence.txt](bug44_evidence.txt) |
| 45 | 2026-09-22 | Contract.submit_for_approval | Invalid tool arguments. (invalid_arguments) | High | [bug45_evidence.txt](bug45_evidence.txt) |
| 46 | 2026-09-22 | Contract.mark_expiring | Invalid tool arguments. (invalid_arguments) | High | [bug46_evidence.txt](bug46_evidence.txt) |
| 47 | 2026-09-22 | Contract.mark_expired | Invalid tool arguments. (invalid_arguments) | High | [bug47_evidence.txt](bug47_evidence.txt) |
| 48 | 2026-09-22 | endpoint.contracts.obligation_evidence_pack | Invalid tool arguments. (invalid_arguments) | High | [bug48_evidence.txt](bug48_evidence.txt) |
| 49 | 2026-09-22 | endpoint.contracts.attest_obligation | Invalid tool arguments. (invalid_arguments) | High | [bug49_evidence.txt](bug49_evidence.txt) |
| 50 | 2026-09-22 | endpoint.contracts.document_redline | Invalid tool arguments. (invalid_arguments) | High | [bug50_evidence.txt](bug50_evidence.txt) |
| 51 | 2026-09-22 | endpoint.contracts.capture_document_revision | Invalid tool arguments. (invalid_arguments) | High | [bug51_evidence.txt](bug51_evidence.txt) |
| 52 | 2026-09-22 | endpoint.contracts.propose_clause_deviation | Invalid tool arguments. (invalid_arguments) | High | [bug52_evidence.txt](bug52_evidence.txt) |
| 53 | 2026-09-22 | endpoint.contracts.bind_deviation_approval | Invalid tool arguments. (invalid_arguments) | High | [bug53_evidence.txt](bug53_evidence.txt) |
| 54 | 2026-09-22 | endpoint.contracts.recheck_deviation_coverage | Invalid tool arguments. (invalid_arguments) | High | [bug54_evidence.txt](bug54_evidence.txt) |
| 55 | 2026-09-22 | endpoint.contracts.record_renewal_decision | Invalid tool arguments. (invalid_arguments) | High | [bug55_evidence.txt](bug55_evidence.txt) |


## Pattern

endpoint.contracts.* tools document contracts (bounds, field names) but do not enforce or expose them consistently. Bug 6 blocks the A17 playbook-review task.

## Withdrawn / corrected

An earlier report on renewal_forecast rejecting days was filed with the wrong argument name and withdrawn with an honest correction.

## Total

6 valid bugs filed. 1 withdrawn with correction.
