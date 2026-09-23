"""MCP client — talks to AgentSwitch over JSON-RPC.

All tool calls go through ONE endpoint:  {AS_URL}/api/mcp
Methods used: initialize, tools/list, tools/call.
Auth: Authorization: Bearer <token> — anonymous is refused (401).
"""
import os
import json
import requests
from dotenv import load_dotenv

# .env wins over any stale value in the shell environment
load_dotenv(override=True)

AS_URL = os.getenv("AS_URL", "https://agentswitch.theschoolofai.in")
AS_TOKEN = os.getenv("AS_TOKEN")

_request_id = 0

def _next_id():
    global _request_id
    _request_id += 1
    return _request_id

def call_mcp(method, params=None):
    """Send a JSON-RPC 2.0 request to the MCP endpoint."""
    resp = requests.post(
        f"{AS_URL}/api/mcp",
        headers={
            "Authorization": f"Bearer {AS_TOKEN}",
            "Content-Type": "application/json",
        },
        json={"jsonrpc": "2.0", "id": _next_id(), "method": method, "params": params or {}},
        timeout=30,
    )
    try:
        body = resp.json()
    except Exception:
        body = {"_raw": resp.text, "_status": resp.status_code}
    return {"http_status": resp.status_code, "body": body}

def call(method, params=None, id=1):
    return call_mcp(method, params)

def call_tool(name, arguments=None):
    return call_mcp("tools/call", {"name": name, "arguments": arguments or {}})

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
    return call_mcp("tools/list", {})["body"]["result"]["tools"]

def initialize():
    return call_mcp("initialize", {
        "protocolVersion": "2025-11-25",
        "capabilities": {},
        "clientInfo": {"name": "team-17", "version": "0.1"},
    })
