"""Probe: do CRM and Agent tools return the same envelope as Contract tools?"""
import json
from agent.mcp_client import call_tool

tools = json.load(open("tools_raw.json"))["result"]["tools"]
names = [t["name"] for t in tools]
sample = [
    n for n in names
    if n.endswith(".list") and n.startswith(("Lead.", "Deal.", "AccountPlan.",
                                              "AgentMemory.", "AgentTask.", "AgentMessage.",
                                              "AgentSkill.", "AgentEscalation.", "AgentRunbook."))
][:12]

print(f"testing {len(sample)} tools\n")

for name in sample:
    r = call_tool(name, {"limit": 2})
    body = r["body"]
    is_err = bool(body.get("result", {}).get("isError"))
    has_error = "error" in body
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
                elif "items" in parsed:
                    payload = "items"
                else:
                    payload = str(keys)[:40]
            elif isinstance(parsed, list):
                payload = "bare-list"
        except Exception:
            payload = "non-json"
    print(f"{name:40} top_error={has_error} isError={is_err} payload={payload}")
