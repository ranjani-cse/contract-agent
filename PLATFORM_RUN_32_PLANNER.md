# Platform Run — Planner Included (32 tasks)

**Date:** 2026-10-20 15:49
**Commit:** faf47af
**Instance:** suryodaya
**Result:** **32/32 PASS**
**Tokens used:** 196
**Next submit window:** 2026-10-23 15:49

## Confirms
- Planner (L1 hybrid, LLM + rule fallback) on `main` does not regress any task
- LLM dispatcher activates on server (`source: "llm"` in t19)
- Rule 1: no hard-coded URL — auth flows from `AGENTSWITCH_BASE_URL`
- Rule 6: 401/429 correctly handled
- `failure_reason` NameError fixed (t13 passes)

## Evidence highlights
- t0: tool_count 253
- t19: source "llm"
- c7: 100 templates, 100 playbooks
- c10: 75 overdue + unattested
- c11: 100 contracts with approval status breakdown
- c12: 0 without owner (valid — all have owners)
