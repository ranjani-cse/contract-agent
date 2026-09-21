"""Bug probes against AgentSwitch Contracts MCP surface."""
import json, os, requests
from agent.mcp_client import call_tool, call, AS, TOKEN

def probe_closed_schema():
    r = call_tool("Contract.get", {"id": "NOPE", "extra_field": "should_be_rejected"})
    return {"probe": "closed_schema", "http": r["http_status"], "body": r["body"]}

def probe_cross_seat_leak():
    r = call_tool("SalarySlip.list", {})
    return {"probe": "cross_seat_leak", "http": r["http_status"], "body": r["body"]}

def probe_error_http_status():
    r = requests.post(f"{AS}/api/mcp",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/call",
              "params": {"name": "SalarySlip.list", "arguments": {}}})
    try:
        body = r.json()
    except Exception:
        body = {"_raw": r.text}
    return {"probe": "error_http_status", "http": r.status_code, "body": body}

def probe_expiry_boundary():
    r = call_tool("endpoint.contracts.renewal_forecast", {"horizon_days": 60})
    return {"probe": "expiry_boundary", "http": r["http_status"], "body": r["body"]}

def probe_tools_list_scoping():
    r = call("tools/list", {})
    names = [t["name"] for t in r["body"]["result"]["tools"]]
    foreign = [n for n in names if any(k in n for k in
               ["SalarySlip", "Employee", "Payroll", "Ticket", "WorkOrder", "StockEntry"])]
    return {"probe": "tools_list_scoping", "count": len(names), "foreign_tools": foreign}

if __name__ == "__main__":
    for fn in [probe_closed_schema, probe_cross_seat_leak,
               probe_error_http_status, probe_expiry_boundary,
               probe_tools_list_scoping]:
        try:
            print(json.dumps(fn(), indent=2))
        except Exception as e:
            print(json.dumps({"probe": fn.__name__, "error": str(e)}, indent=2))
