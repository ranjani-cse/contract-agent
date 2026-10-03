"""Test the full propose_clause_deviation call with correct args."""
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

r = call_tool("endpoint.contracts.propose_clause_deviation", {
    "document_id": "0826ccba-16cb-4a79-9e92-f2eb3336a57c",
    "clause_key": "8d4bd634-c2a9-488e-b7bc-b9e836d58b6d",
    "rationale": "Automated playbook review: clause departs from standard position.",
    "proposed_content": "The receiving party shall hold all Confidential Information in strict confidence for a period of five (5) years.",
})
print("is_failure:", is_failure(r))
print("reason:", failure_reason(r))
print()
import json
print(json.dumps(_unwrap(r), indent=2, default=str)[:600])
