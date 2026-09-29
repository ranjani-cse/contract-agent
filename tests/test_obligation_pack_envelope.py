"""Test: obligation_evidence_pack failure envelope.

Bug 2 was filed 2026-09-21: the tool reported failures via result.isError
while entity tools used the JSON-RPC error field. Fixed as of 2026-09-29.
"""
from agent.mcp_client import call_tool


def test_not_found_uses_jsonrpc_error_field():
    r = call_tool("endpoint.contracts.obligation_evidence_pack",
                  {"contract_id": "00000000-0000-0000-0000-000000000000"})
    body = r["body"]
    assert "error" in body, "failure should be reported via the JSON-RPC error field"
    assert "result" not in body or not body["result"].get("isError"), \
        "failure should not be reported via result.isError"
