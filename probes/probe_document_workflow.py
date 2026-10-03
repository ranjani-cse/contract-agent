"""Probe: ContractDocument workflow transitions from invalid states."""
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap
from collections import Counter

r = call_tool("ContractDocument.list", {"limit": 100})
rows = _unwrap(r).get("data", [])
print("documents:", len(rows))
print("statuses:", Counter(d.get("status") for d in rows))
print()

by_status = {}
for d in rows:
    s = d.get("status")
    if s and s not in by_status:
        by_status[s] = d

for s, d in by_status.items():
    print(f"  {s:25} {d.get('id')}  {d.get('title','')[:40]}")
print()

TRANSITIONS = {
    "ContractDocument.submit_for_review":  {"valid_from": {"draft"}},
    "ContractDocument.send_for_signature": {"valid_from": {"reviewed", "approved", "in_review"}},
    "ContractDocument.mark_signed":        {"valid_from": {"pending_signature", "sent_for_signature"}},
    "ContractDocument.archive":            {"valid_from": {"signed", "executed", "finalized"}},
    "ContractDocument.archive_draft":      {"valid_from": {"draft"}},
}

findings = []
for status, doc in by_status.items():
    did = doc.get("id")
    for tool, rule in TRANSITIONS.items():
        if status in rule["valid_from"]:
            continue
        r = call_tool(tool, {"id": did})
        if is_failure(r):
            print(f"OK     {tool:42} from {status:20} -> {failure_reason(r)[:80]}")
        else:
            print(f"ACCEPT {tool:42} from {status:20} (SHOULD HAVE BEEN REJECTED)")
            findings.append({"tool": tool, "from": status, "document_id": did})

print()
print(f"=== {len(findings)} accepted from invalid state ===")
for f in findings:
    print(f)
