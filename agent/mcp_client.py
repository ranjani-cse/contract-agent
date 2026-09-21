"""MCP client for AgentSwitch Contracts seat (Team 17)."""
import os, requests

AS = os.environ.get("AS", "https://agentswitch.theschoolofai.in")
TOKEN = os.environ.get("TOKEN")

def _post(payload, timeout=30):
    r = requests.post(
        f"{AS}/api/mcp",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json=payload, timeout=timeout,
    )
    return r

def call(method, params=None, id=1):
    r = _post({"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}})
    try:
        body = r.json()
    except Exception:
        body = {"_raw": r.text, "_status": r.status_code}
    return {"http_status": r.status_code, "body": body}

def call_tool(name, arguments=None):
    return call("tools/call", {"name": name, "arguments": arguments or {}})

def list_tools():
    return call("tools/list", {})["body"]["result"]["tools"]
