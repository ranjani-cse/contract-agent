"""Verifiers read the DATABASE via MCP. Never trust agent prose."""
import json
from agent.mcp_client import call_tool, is_failure

def _extract(result):
    if is_failure(result):
        return {"_error": "call failed"}
    try:
        content = result["body"]["result"]["content"]
        for item in content:
            if item.get("type") == "text":
                parsed = json.loads(item["text"])
                if isinstance(parsed, dict) and set(parsed.keys()) <= {"result", "status"}:
                    return parsed.get("result", parsed)
                return parsed
    except Exception as e:
        return {"_error": str(e)}
    return None

def _rows(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("contracts", "data", "items", "obligations"):
            if key in payload and isinstance(payload[key], list):
                return payload[key]
    return []

def _row_id(row):
    if not isinstance(row, dict):
        return None
    if "id" in row:
        return row["id"]
    for wrapper in ("contract", "obligation", "renewal"):
        inner = row.get(wrapper)
        if isinstance(inner, dict) and "id" in inner:
            return inner["id"]
    return None

def verify_renewal_forecast(agent_answer):
    db = _extract(call_tool("endpoint.contracts.renewal_forecast",
                            {"horizon_days": 60, "limit": 20}))
    db_ids = {_row_id(r) for r in _rows(db) if _row_id(r)}
    agent_ids = {_row_id(r) for r in (agent_answer or {}).get("expiring", []) if _row_id(r)}
    return {"pass": db_ids == agent_ids,
            "db_count": len(db_ids), "agent_count": len(agent_ids)}

def verify_playbook_review(agent_answer):
    reviews = (agent_answer or {}).get("reviews", [])
    if not reviews:
        return {"pass": False, "reason": "no reviews returned"}
    ok = all(
        isinstance(r.get("review"), dict) and
        ("document_id" in r["review"] or r["review"].get("_no_document"))
        for r in reviews
    )
    return {"pass": ok, "reviews_returned": len(reviews)}

def verify_missing_obligations(agent_answer):
    missing = (agent_answer or {}).get("missing", [])
    if not missing:
        return {"pass": False, "reason": "no missing-obligation entries"}
    ok = all(
        isinstance(m.get("obligations"), dict) and
        "counts" in m["obligations"]
        for m in missing
    )
    return {"pass": ok, "entries": len(missing)}

def verify_renewal_decision(agent_answer):
    db = _extract(call_tool("ContractRenewal.list", {"limit": 50}))
    rows = _rows(db)
    decided = [r for r in rows
               if isinstance(r, dict) and r.get("decision")
               and r.get("decision") != "undecided"]
    return {"pass": len(decided) > 0,
            "total_renewals": len(rows), "decided": len(decided)}

def verify_deviation_approval(agent_answer):
    db = _extract(call_tool("ContractClauseDeviation.list", {"limit": 50}))
    rows = _rows(db)
    approved = [r for r in rows
                if isinstance(r, dict) and r.get("status") == "approved"]
    return {"pass": len(approved) > 0,
            "total": len(rows), "approved": len(approved)}

def verify_refusal(agent_answer):
    text = str(agent_answer).lower()
    refused = any(p in text for p in [
        "refuse", "refusal", "cannot", "can't", "not permitted",
        "not available", "not allowed", "unauthorized", "forbidden", "403",
    ])
    return {"pass": refused, "agent_said": text[:200]}

def verify_refusal_or_empty(agent_answer):
    text = str(agent_answer).lower()
    honest = any(p in text for p in [
        "not in the data", "no liability cap", "cannot determine",
        "unable to find", "not available", "not found", "refused",
    ])
    return {"pass": honest, "agent_said": text[:200]}
