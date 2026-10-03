"""
Probe: attempt transitions from states where they should be invalid.
A state machine that accepts these is a real bug — silent data corruption.
"""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap
from collections import Counter

# 1) get one contract per status
r = call_tool("Contract.list", {"limit": 200})
rows = _unwrap(r).get("data", [])

by_status = {}
for c in rows:
    s = c.get("status")
    if s and s not in by_status:
        by_status[s] = c

print("targets:")
for s, c in by_status.items():
    print(f"  {s:20} {c.get('id')}  {c.get('number')}")
print()

# 2) transitions and their logically-valid source states
# (my best reading of what "should" be allowed)
TRANSITIONS = {
    "Contract.submit_for_approval": {"valid_from": {"draft"}},
    "Contract.mark_expiring":       {"valid_from": {"active"}},
    "Contract.mark_expired":        {"valid_from": {"active", "expiring_soon"}},
}

# 3) for each target status, try each transition; flag any that SUCCEEDS from an invalid source
findings = []
for status, contract in by_status.items():
    cid = contract.get("id")
    for tool, rule in TRANSITIONS.items():
        if status in rule["valid_from"]:
            continue  # skip: this one is legitimately allowed
        r = call_tool(tool, {"id": cid})
        if is_failure(r):
            print(f"OK     {tool:35} from {status:18} -> {failure_reason(r)}")
        else:
            print(f"ACCEPT {tool:35} from {status:18} (SHOULD have been rejected)")
            findings.append({"tool": tool, "from": status, "contract_id": cid, "result": _unwrap(r)})

print()
print(f"=== {len(findings)} accepted from invalid state ===")
for f in findings:
    print(json.dumps(f, indent=2, default=str)[:500])
