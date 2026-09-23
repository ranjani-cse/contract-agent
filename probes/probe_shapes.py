"""Probe: how does each tool return data and errors?"""
import json
from agent.mcp_client import call_tool

tools = [
    "Contract.list", "Contract.get",
    "ContractDocument.list", "ContractClause.list",
    "ContractObligation.list", "ContractRenewal.list",
    "ContractPlaybook.list", "ContractClauseDeviation.list",
    "ContractAmendment.list", "ContractTemplate.list",
    "ContractPreferences.list",
]

for tool in tools:
    args = {"id": "00000000-0000-0000-0000-000000000000"} if tool.endswith(".get") else {"limit": 2}
    r = call_tool(tool, args)
    body = r["body"]
    top_error = "error" in body
    is_err = bool(body.get("result", {}).get("isError"))
    has_detail = "detail" in body
    payload = "?"
    if body.get("result", {}).get("content"):
        try:
            text = body["result"]["content"][0]["text"]
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                keys = list(parsed.keys())
                if set(keys) <= {"result", "status"}:
                    payload = "DOUBLE_WRAP"
                elif "data" in parsed:
                    payload = "data"
                else:
                    payload = str(keys)[:40]
        except Exception:
            payload = "non-json"
    print(f"{tool:35} top_error={top_error} isError={is_err} detail={has_detail} payload={payload}")
