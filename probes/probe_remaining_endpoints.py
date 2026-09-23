"""Probe: empty args + edge on the endpoints not yet deeply tested."""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

endpoints = [
    "endpoint.contracts.attest_obligation",
    "endpoint.contracts.bind_deviation_approval",
    "endpoint.contracts.capture_document_revision",
    "endpoint.contracts.document_redline",
    "endpoint.contracts.recheck_deviation_coverage",
]

test_cases = [
    {},
    {"limit": 0},
    {"limit": -1},
    {"offset": -1},
]

for e in endpoints:
    print(f"=== {e} ===")
    for args in test_cases:
        r = call_tool(e, args)
        if is_failure(r):
            print(f"  {str(args):20} REJECTED {failure_reason(r)}")
        else:
            data = _unwrap(r)
            print(f"  {str(args):20} ACCEPTED {json.dumps(data, default=str)[:120]}")
    print()
