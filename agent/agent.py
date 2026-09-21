"""Contracts agent (Team 17). Answers the A17 request over MCP."""
import json
from agent.mcp_client import call_tool, is_failure, failure_reason

def _unwrap(response):
    if is_failure(response):
        return {"_error": failure_reason(response)}
    try:
        content = response["body"]["result"]["content"]
        for item in content:
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except Exception:
                    return item["text"]
    except Exception as e:
        return {"_error": str(e)}
    return None

def expiring_soon(horizon_days=60, limit=20):
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": horizon_days, "limit": limit})
    data = _unwrap(r)
    if isinstance(data, dict):
        return data.get("data", [])
    return []

def review_against_playbook(contract_id):
    return _unwrap(call_tool("endpoint.contracts.propose_clause_deviation",
                             {"contract_id": contract_id}))

def missing_obligations(contract_id):
    return _unwrap(call_tool("endpoint.contracts.obligation_evidence_pack",
                             {"contract_id": contract_id}))

def answer_a17(horizon_days=60, top_n=3):
    """A17: what expires in 60 days + playbook review + missing obligations."""
    expiring = expiring_soon(horizon_days)
    out = {"expiring": expiring, "reviews": [], "missing": []}
    for c in expiring[:top_n]:
        cid = c.get("id")
        if not cid:
            continue
        out["reviews"].append({"contract_id": cid, "review": review_against_playbook(cid)})
        out["missing"].append({"contract_id": cid, "obligations": missing_obligations(cid)})
    return out
