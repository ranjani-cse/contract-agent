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

def is_failure(response):
    """True if the call failed, regardless of which envelope is used."""
    body = response.get("body", {})
    if "error" in body:
        return True
    if body.get("result", {}).get("isError"):
        return True
    meta = body.get("result", {}).get("_meta", {}).get("agentswitch", {})
    return bool(meta.get("status") and meta["status"] >= 400)

def failure_reason(response):
    """Extract a human-readable failure reason from either envelope."""
    body = response.get("body", {})
    if "error" in body:
        err = body["error"]
        return f"{err.get('message')} ({err.get('data', {}).get('code')})"
    if body.get("result", {}).get("isError"):
        meta = body["result"].get("_meta", {}).get("agentswitch", {})
        return f"{meta.get('message')} ({meta.get('reason_code')}) status={meta.get('status')}"
    return None

def list_tools():
    return call("tools/list", {})["body"]["result"]["tools"]
