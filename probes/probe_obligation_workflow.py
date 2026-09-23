"""Probe: ContractObligation workflow transitions from invalid states."""
import json
from collections import Counter
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

# 1) get obligations and their statuses
r = call_tool("ContractObligation.list", {"limit": 200})
rows = _unwrap(r).get("data", [])
print("obligations:", len(rows))
print("statuses:", Counter(o.get("status") for o in rows))
print()

# 2) find one per status
by_status = {}
for o in rows:
    s = o.get("status")
    if s and s not in by_status:
        by_status[s] = o

for s, o in by_status.items():
    print(f"  {s:20} {o.get('id')}  {o.get('title','')[:40]}  type={o.get('obligation_type')}")
print()

# 3) try transitions from wrong states
TRANSITIONS = {
    "ContractObligation.start":                                  {"valid_from": {"pending"}},
    "ContractObligation.mark_complete":                          {"valid_from": {"in_progress"}},
    "ContractObligation.mark_overdue.in_progress.overdue":       {"valid_from": {"in_progress"}},
    "ContractObligation.mark_overdue.pending.overdue":           {"valid_from": {"pending"}},
    "ContractObligation.complete_late":                          {"valid_from": {"overdue"}},
}

findings = []
for status, ob in by_status.items():
    oid = ob.get("id")
    for tool, rule in TRANSITIONS.items():
        if status in rule["valid_from"]:
            continue
        r = call_tool(tool, {"id": oid})
        if is_failure(r):
            print(f"OK     {tool:48} from {status:15} -> {failure_reason(r)[:80]}")
        else:
            print(f"ACCEPT {tool:48} from {status:15} (SHOULD HAVE BEEN REJECTED)")
            findings.append({"tool": tool, "from": status, "obligation_id": oid, "result": _unwrap(r)})

print()
print(f"=== {len(findings)} accepted from invalid state ===")
for f in findings:
    print(json.dumps(f, indent=2, default=str)[:400])
