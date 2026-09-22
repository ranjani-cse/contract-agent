"""Test which field of clauses_used maps to propose_clause_deviation's clause_key."""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

doc_id = "0826ccba-16cb-4a79-9e92-f2eb3336a57c"  # Pipe Wrench — tooling change
clause = {
    "_clause_id_display": "Confidentiality — Tool Room",
    "clause_id": "8d4bd634-c2a9-488e-b7bc-b9e836d58b6d",
    "is_modified": False,
    "order": 895.11,
}

candidates = [
    ("clause_id (UUID)",        clause["clause_id"]),
    ("_clause_id_display",      clause["_clause_id_display"]),
    ("literal UUID string",     "8d4bd634-c2a9-488e-b7bc-b9e836d58b6d"),
]

for label, key in candidates:
    r = call_tool("endpoint.contracts.propose_clause_deviation", {
        "document_id": doc_id,
        "clause_key": key,
        "rationale": "Automated playbook review — test of clause_key field mapping.",
    })
    print(f"--- {label}: {key!r}")
    print(f"  is_failure: {is_failure(r)}")
    print(f"  reason:     {failure_reason(r)}")
    if not is_failure(r):
        print(f"  result:     {json.dumps(_unwrap(r), default=str)[:400]}")
    print()
