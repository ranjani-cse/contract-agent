"""MCP client for AgentSwitch Contracts seat (Team 17).

On the AgentSwitch server, reads:
  AGENTSWITCH_BASE_URL — instance base (POST to /api/mcp)
  AGENTSWITCH_TOKEN    — bearer token

Locally, falls back to AS_URL / AS_TOKEN if the platform vars are
not set, so the same code runs in both places.
"""
import os
import requests

AS_URL = (
    os.environ.get("AGENTSWITCH_BASE_URL")
    or os.environ.get("AS_URL")
    or "https://agentswitch.theschoolofai.in"
)
TOKEN = (
    os.environ.get("AGENTSWITCH_TOKEN")
    or os.environ.get("AS_TOKEN")
)


def _post(payload, timeout=30):
    r = requests.post(
        f"{AS_URL}/api/mcp",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
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
    body = response.get("body", {})
    if "detail" in body and "result" not in body:
        return True
    if "error" in body:
        return True
    if body.get("result", {}).get("isError"):
        return True
    meta = body.get("result", {}).get("_meta", {}).get("agentswitch", {})
    return bool(meta.get("status") and meta["status"] >= 400)


def failure_reason(response):
    body = response.get("body", {})
    if "detail" in body and "result" not in body:
        return f"auth: {body['detail']}"
    if "error" in body:
        err = body["error"]
        return f"{err.get('message')} ({err.get('data', {}).get('code')})"
    if body.get("result", {}).get("isError"):
        meta = body["result"].get("_meta", {}).get("agentswitch", {})
        return f"{meta.get('message')} ({meta.get('reason_code')}) status={meta.get('status')}"
    return None


def list_tools():
    return call("tools/list", {})["body"]["result"]["tools"]
