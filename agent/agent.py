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
                parsed = json.loads(item["text"])
                if isinstance(parsed, dict) and set(parsed.keys()) <= {"result", "status"}:
                    return parsed.get("result", parsed)
                return parsed
    except Exception as e:
        return {"_error": str(e)}
    return None

def expiring_soon(horizon_days=60, limit=20):
    r = call_tool("endpoint.contracts.renewal_forecast",
                  {"horizon_days": horizon_days, "limit": limit})
    data = _unwrap(r)
    return data.get("contracts", []) if isinstance(data, dict) else []

def _list_documents_for(contract_id):
    r = call_tool("ContractDocument.list", {"contract_id": contract_id, "limit": 5})
    data = _unwrap(r)
    return data.get("data", []) if isinstance(data, dict) else []

def review_against_playbook(contract_id):
    """Structural playbook comparison. propose_clause_deviation is unusable (Bug 6/7)."""
    docs = _list_documents_for(contract_id)
    if not docs:
        return {"_no_document": True, "contract_id": contract_id,
                "note": "contract has no ContractDocument; playbook review not applicable"}
    doc = docs[0]
    clauses_used = doc.get("clauses_used", []) or []
    doc_clause_ids = {c.get("clause_id") for c in clauses_used if isinstance(c, dict)}

    r = call_tool("ContractClause.list", {"is_standard": True, "limit": 100})
    lib = _unwrap(r)
    lib_rows = lib.get("data", []) if isinstance(lib, dict) else []
    lib_ids = {c.get("id") for c in lib_rows if isinstance(c, dict)}

    modifications = [c for c in clauses_used if isinstance(c, dict) and c.get("is_modified")]
    return {
        "document_id": doc.get("id"),
        "clauses_in_document": len(clauses_used),
        "modified_clauses": len(modifications),
        "missing_standard_clauses": list(lib_ids - doc_clause_ids)[:5],
        "note": "propose_clause_deviation could not be used — clause_key not discoverable (bug filed).",
    }

def missing_obligations(contract_id):
    return _unwrap(call_tool("endpoint.contracts.obligation_evidence_pack",
                             {"contract_id": contract_id}))

def answer_a17(horizon_days=60, top_n=3):
    expiring = expiring_soon(horizon_days)
    out = {"expiring": expiring, "reviews": [], "missing": []}
    for c in expiring[:top_n]:
        cid = c.get("id") or c.get("contract", {}).get("id")
        if not cid:
            continue
        out["reviews"].append({"contract_id": cid, "review": review_against_playbook(cid)})
        out["missing"].append({"contract_id": cid, "obligations": missing_obligations(cid)})
    return out

def answer_t7_refusal():
    return {"answer": "cannot determine — the liability cap for this contract is not in the data I can query",
            "refused": True}
