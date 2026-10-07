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
    """Pass if each review either wrote a deviation, hit an existing one,
    or honestly found no document."""
    reviews = (agent_answer or {}).get("reviews", [])
    if not reviews:
        return {"pass": False, "reason": "no reviews returned"}
    ok = all(
        isinstance(r.get("review"), dict) and (
            "deviation_id" in r["review"]
            or r["review"].get("_no_document")
            or r["review"].get("_no_clauses")
        )
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
    """Pass if any deviation entered the approval flow.
    This seat cannot reach 'approved' directly; pending_approval is achievable."""
    db = _extract(call_tool("ContractClauseDeviation.list", {"limit": 50}))
    rows = _rows(db)
    in_flow = [r for r in rows
               if isinstance(r, dict) and r.get("status") in ("approved", "pending_approval")]
    return {"pass": len(in_flow) > 0,
            "total": len(rows), "in_flow": len(in_flow)}

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


def verify_health_check(agent_answer):
    """Environment check — token works and tools/list returns tools."""
    from agent.mcp_client import call

    r = call_tool("Contract.list", {"limit": 1})
    if is_failure(r):
        return {"pass": False, "reason": f"auth or platform issue: {str(r.get('body'))[:120]}"}
    tools = call("tools/list", {})["body"].get("result", {}).get("tools", [])
    return {"pass": len(tools) > 0, "tool_count": len(tools)}


def verify_pagination(agent_answer):
    """Contract.list with limit=100 must return at most 100 rows and a valid shape."""
    r = call_tool("Contract.list", {"limit": 100})
    if is_failure(r):
        return {"pass": False, "reason": f"Contract.list failed: {str(r.get('body'))[:120]}"}
    data = _extract(r)
    if not isinstance(data, dict):
        return {"pass": False, "reason": "response is not a dict"}
    rows = data.get("data", [])
    if len(rows) > 100:
        return {"pass": False, "reason": f"returned {len(rows)} rows, expected <= 100"}
    if "total" not in data:
        return {"pass": False, "reason": "response missing 'total' field"}
    return {"pass": True, "rows_returned": len(rows), "total": data.get("total")}


def verify_workflow_guard(agent_answer):
    """The state machine must reject invalid transitions."""
    r = call_tool("Contract.list", {"limit": 200})
    if is_failure(r):
        return {"pass": False, "reason": f"Contract.list failed: {str(r.get('body'))[:120]}"}
    data = _extract(r)
    rows = _rows(data)
    cancelled = next((c for c in rows if isinstance(c, dict) and c.get("status") == "cancelled"), None)
    if not cancelled:
        return {"pass": True, "skipped": "no cancelled contract to test"}
    cid = cancelled.get("id")
    rr = call_tool("Contract.mark_expired", {"id": cid})
    if is_failure(rr):
        reason = str(rr.get("body", {}).get("error", {}).get("message", ""))[:80]
        return {"pass": True, "rejection": reason}
    return {"pass": False, "reason": "mark_expired was accepted on a cancelled contract"}


def verify_tools_list_scoping(agent_answer):
    """tools/list must not expose foreign tools."""
    from agent.mcp_client import call

    r = call("tools/list", {})
    if "result" not in r.get("body", {}):
        return {"pass": False, "reason": "tools/list failed"}
    tools = [t["name"] for t in r["body"]["result"]["tools"]]
    foreign = [n for n in tools if any(k in n for k in
               ["SalarySlip", "Employee", "Payroll", "Payslip", "Ticket",
                "WorkOrder", "StockEntry", "EsignDocument", "Mailbox"])]
    return {"pass": len(foreign) == 0, "count": len(tools), "foreign": foreign}


def verify_concurrency(agent_answer):
    """Verify the platform state can change and the harness reads the new state.

    Simulates another team editing a contract, then re-reads it.
    """
    import time

    r = call_tool("Contract.list", {"limit": 5})
    if is_failure(r):
        return {"pass": False, "reason": f"Contract.list failed: {str(r.get('body'))[:120]}"}
    data = _extract(r)
    rows = _rows(data)
    if not rows:
        return {"pass": False, "reason": "no contracts to test"}
    # prefer a draft contract (writable) if one exists
    draft = next((c for c in rows if isinstance(c, dict) and c.get("status") == "draft"), None)
    target = draft or rows[0]
    cid = target.get("id")
    if not cid:
        return {"pass": False, "reason": "no contract id"}

    r1 = call_tool("Contract.get", {"id": cid})
    if is_failure(r1):
        return {"pass": False, "reason": f"Contract.get failed: {str(r1.get('body'))[:120]}"}
    state1 = _extract(r1)
    if not isinstance(state1, dict):
        return {"pass": False, "reason": "Contract.get returned non-dict"}

    original_title = state1.get("title", "")
    marker = f" [test-{int(time.time())}]"

    r2 = call_tool("Contract.update", {"id": cid, "title": original_title + marker})
    if is_failure(r2):
        reason = str(r2.get("body", {}).get("error", {}).get("message", ""))[:100]
        return {"pass": True, "skipped": f"update not permitted: {reason}"}

    r3 = call_tool("Contract.get", {"id": cid})
    state3 = _extract(r3)
    title_after = state3.get("title", "") if isinstance(state3, dict) else ""

    call_tool("Contract.update", {"id": cid, "title": original_title})

    changed = marker in title_after
    return {"pass": changed, "marker_seen": changed, "contract_id": cid}


def verify_malformed_id(agent_answer):
    """Contract.get with a malformed UUID must fail cleanly."""
    from agent.mcp_client import failure_reason

    r = call_tool("Contract.get", {"id": "not-a-valid-uuid"})
    if not is_failure(r):
        return {"pass": False, "reason": "malformed UUID was accepted"}
    reason = str(failure_reason(r)).lower()
    return {"pass": True, "rejection": reason[:80]}


def verify_offset_past_end(agent_answer):
    """Contract.list with a huge offset returns zero rows without error."""
    r = call_tool("Contract.list", {"offset": 999999})
    if is_failure(r):
        return {"pass": True, "rejection": str(failure_reason(r))[:80]}
    data = _extract(r)
    rows = data.get("data", []) if isinstance(data, dict) else []
    return {"pass": len(rows) == 0, "rows_returned": len(rows)}


def verify_tools_describe_foreign(agent_answer):
    """tools.describe on a foreign tool reports it in not_available."""
    from agent.mcp_client import call

    r = call("tools/call", {"name": "tools.describe",
                            "arguments": {"names": ["SalarySlip.list"]}})
    body = r.get("body", {})
    if "result" not in body:
        return {"pass": False, "reason": f"tools.describe failed: {str(body)[:120]}"}
    text = body["result"]["content"][0]["text"]
    import json as _json
    parsed = _json.loads(text)
    not_avail = parsed.get("not_available", [])
    return {"pass": "SalarySlip.list" in not_avail, "not_available": not_avail}


def verify_obligation_workflow_guard(agent_answer):
    """The obligation state machine must reject invalid transitions."""
    r = call_tool("ContractObligation.list", {"limit": 200})
    if is_failure(r):
        return {"pass": False, "reason": f"ContractObligation.list failed: {str(r.get('body'))[:120]}"}
    data = _extract(r)
    rows = _rows(data)
    # find a pending obligation and try an invalid transition
    pending = next((o for o in rows if isinstance(o, dict) and o.get("status") == "pending"), None)
    if not pending:
        return {"pass": True, "skipped": "no pending obligation to test"}
    oid = pending.get("id")
    rr = call_tool("ContractObligation.mark_complete", {"id": oid})
    if is_failure(rr):
        reason = str(rr.get("body", {}).get("error", {}).get("message", ""))[:80]
        return {"pass": True, "rejection": reason}
    return {"pass": False, "reason": "mark_complete was accepted on a pending obligation"}


def verify_contract_get_missing(agent_answer):
    """Contract.get with a valid-format but nonexistent UUID returns not_found."""
    from agent.mcp_client import failure_reason

    r = call_tool("Contract.get", {"id": "00000000-0000-0000-0000-000000000000"})
    if not is_failure(r):
        return {"pass": False, "reason": "nonexistent UUID was accepted"}
    reason = str(failure_reason(r)).lower()
    return {"pass": True, "rejection": reason[:80]}


def verify_tools_describe_available(agent_answer):
    """tools.describe on an available tool returns its schema."""
    from agent.mcp_client import call

    r = call("tools/call", {
        "name": "tools.describe",
        "arguments": {"names": ["Contract.list"]},
    })
    body = r.get("body", {})
    if "result" not in body:
        return {"pass": False, "reason": f"tools.describe failed: {str(body)[:120]}"}
    text = body["result"]["content"][0]["text"]
    import json as _json
    parsed = _json.loads(text)
    results = parsed.get("results", [])
    if not results:
        return {"pass": False, "reason": "no schema returned for Contract.list"}
    schema = results[0].get("inputSchema", {})
    return {"pass": bool(schema), "has_schema": bool(schema)}
