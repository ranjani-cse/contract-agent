"""Probe: which value does propose_clause_deviation accept as clause_key?"""
from agent.mcp_client import call_tool, is_failure, failure_reason

doc_id = "0826ccba-16cb-4a79-9e92-f2eb3336a57c"

candidates = [
    "confidentiality",
    "data_protection",
    "dispute_resolution",
    "Confidentiality — Tool Room",
    "8d4bd634-c2a9-488e-b7bc-b9e836d58b6d",
]

for key in candidates:
    r = call_tool("endpoint.contracts.propose_clause_deviation", {
        "document_id": doc_id,
        "clause_key": key,
        "rationale": "Testing clause_key format.",
    })
    print(f"clause_key={key!r}")
    print(f"  is_failure: {is_failure(r)}")
    print(f"  reason: {failure_reason(r)}")
    print()
