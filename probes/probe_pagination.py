"""Probe: pagination boundaries on Contract.list."""
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

cases = [
    {"limit": 0}, {"limit": -1}, {"limit": 1}, {"limit": 1000}, {"limit": 1001},
    {"offset": -1}, {"offset": 0}, {"offset": 999999},
    {"limit": 10, "offset": 999999},
]

for args in cases:
    r = call_tool("Contract.list", args)
    if is_failure(r):
        print(f"{str(args):40} REJECTED {failure_reason(r)}")
    else:
        data = _unwrap(r)
        rows = data.get("data", []) if isinstance(data, dict) else []
        print(f"{str(args):40} OK rows={len(rows)}")
