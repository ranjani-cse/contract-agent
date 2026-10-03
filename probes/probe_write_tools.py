"""Probe: schema vs behavior on write-side entity tools."""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason
from agent.agent import _unwrap

with open("tools_raw.json") as f:
    tools = {t["name"]: t for t in json.load(f)["result"]["tools"]}

write_tools = [
    "Contract.create", "Contract.update",
    "ContractClauseDeviation.create", "ContractClauseDeviation.update", "ContractClauseDeviation.revise",
    "ContractObligation.create", "ContractObligation.update",
    "ContractRenewal.create", "ContractRenewal.update", "ContractRenewal.revise",
    "ContractDocument.create", "ContractDocument.update",
    "ContractPreferences.create", "ContractPreferences.update",
]

for name in write_tools:
    t = tools.get(name)
    if not t:
        print(f"{name:45} NOT IN TOOLS LIST")
        continue
    schema = t.get("inputSchema", {})
    props = schema.get("properties", {})
    required = schema.get("required", [])
    numeric_unbounded = [
        k for k, v in props.items()
        if v.get("type") in ("integer", "number")
        and "minimum" not in v and "maximum" not in v
        and any(w in v.get("description", "").lower() for w in ["min", "max", "clamp", "range", "positive", "greater"])
    ]
    print(f"{name:45} required={required} unbounded_numerics={numeric_unbounded}")
