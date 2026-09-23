"""Probe: how does Contract.get handle malformed IDs?"""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

cases = [
    "not-a-uuid",
    "",
    "00000000-0000-0000-0000-000000000000",
    "00000000-0000-0000-0000-00000000000",  # truncated UUID
    "' OR 1=1 --",
    "../../../etc/passwd",
    "x" * 10000,
]

for cid in cases:
    r = call_tool("Contract.get", {"id": cid})
    if is_failure(r):
        print(f"{cid[:40]!r:45} REJECTED {failure_reason(r)}")
    else:
        data = _unwrap(r)
        print(f"{cid[:40]!r:45} ACCEPTED keys={list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
