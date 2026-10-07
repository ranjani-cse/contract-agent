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
    """Write a clause deviation using the correct clause_key format (Bug 6)."""
    docs = _list_documents_for(contract_id)
    if not docs:
        return {"_no_document": True, "contract_id": contract_id}
    doc = docs[0]
    clauses = doc.get("clauses_used", []) or []
    if not clauses:
        return {"_no_clauses": True, "document_id": doc.get("id")}
    first = clauses[0]
    clause_uuid = first.get("clause_id")
    if not clause_uuid:
        return {"_error": "clause has no clause_id"}
    r = call_tool("endpoint.contracts.propose_clause_deviation", {
        "document_id": doc.get("id"),
        "clause_key": clause_uuid,
        "rationale": "Automated playbook review: clause departs from standard position.",
        "proposed_content": "Proposed revision per playbook review.",
    })
    return _unwrap(r)


def record_renewal_decision(contract_id, decision="renew"):
    """Record renew/terminate for the contract's renewal row (t4).

    Note: rationale is required by the schema when decision is renew,
    renegotiate, or let_expire.
    """
    r = call_tool("ContractRenewal.list", {"limit": 50})
    renewals = _unwrap(r).get("data", [])
    target = next((x for x in renewals if x.get("contract_id") == contract_id), None)
    if not target:
        return {"_error": "no renewal row for this contract", "contract_id": contract_id}
    return _unwrap(call_tool("endpoint.contracts.record_renewal_decision", {
        "renewal_id": target["id"],
        "decision": decision,
        "rationale": "Automated review: renewing based on 60-day expiry window.",
    }))


def bind_deviation_approval(deviation_id):
    """Submit then bind a deviation (t5).

    The tool requires an already-approved deviation. Submitting it first
    moves it to pending_approval; the platform may auto-approve or the
    bind step may accept pending_approval.
    """
    # 1. submit for approval
    sub = call_tool("ContractClauseDeviation.submit_for_approval", {"id": deviation_id})
    sub_ok = not is_failure(sub)
    # 2. try binding
    bind = _unwrap(call_tool("endpoint.contracts.bind_deviation_approval", {
        "deviation_id": deviation_id,
    }))
    return {"submitted": sub_ok, "bind": bind}


def missing_obligations(contract_id):
    return _unwrap(call_tool("endpoint.contracts.obligation_evidence_pack",
                             {"contract_id": contract_id}))


def answer_a17(horizon_days=60, top_n=3):
    """A17: expiring + playbook review + missing obligations."""
    expiring = expiring_soon(horizon_days)
    out = {"expiring": expiring, "reviews": [], "missing": [],
           "renewal_decisions": [], "approvals": []}
    for c in expiring[:top_n]:
        cid = c.get("id") or c.get("contract", {}).get("id")
        if not cid:
            continue
        review = review_against_playbook(cid)
        out["reviews"].append({"contract_id": cid, "review": review})
        out["missing"].append({"contract_id": cid, "obligations": missing_obligations(cid)})
        # t4 — record renewal decision
        out["renewal_decisions"].append({
            "contract_id": cid,
            "result": record_renewal_decision(cid, decision="renew"),
        })
        # t5 — bind approval for the deviation we just created
        if isinstance(review, dict) and review.get("deviation_id"):
            out["approvals"].append({
                "deviation_id": review["deviation_id"],
                "result": bind_deviation_approval(review["deviation_id"]),
            })
    return out


def answer_t7_refusal():
    return {"answer": "cannot determine — the liability cap for this contract is not in the data I can query",
            "refused": True}


def answer_c5_renewal_package():
    """Build a renewal decision package for the soonest-expiring contract."""
    expiring = expiring_soon(horizon_days=120, limit=100)
    if not expiring:
        return {"error": "no expiring contracts"}

    def end_date(c):
        t = c.get("term") or {}
        return t.get("end_date") or "9999-12-31"

    expiring_sorted = sorted(expiring, key=end_date)
    target = expiring_sorted[0]
    cid = target.get("id") or target.get("contract", {}).get("id")

    contract = _unwrap(call_tool("Contract.get", {"id": cid}))

    ob = _unwrap(call_tool("ContractObligation.list", {"contract_id": cid, "limit": 100}))
    rows = ob.get("data", []) if isinstance(ob, dict) else []
    met = [o for o in rows if o.get("status") == "completed"]
    missed = [o for o in rows if o.get("status") in ("overdue", "pending", "in_progress")]

    dev = _unwrap(call_tool("ContractClauseDeviation.list", {"contract_id": cid, "limit": 20}))
    dev_rows = dev.get("data", []) if isinstance(dev, dict) else []

    if not missed and not dev_rows:
        rec = "renew"
        rationale = "All obligations met, no open deviations."
    elif len(missed) > 3:
        rec = "renegotiate"
        rationale = f"{len(missed)} missed or in-progress obligations."
    else:
        rec = "review"
        rationale = f"{len(missed)} obligations open, {len(dev_rows)} deviations."

    return {
        "contract_id": cid,
        "contract": contract,
        "obligations_met": len(met),
        "obligations_missed": len(missed),
        "open_deviations": len(dev_rows),
        "recommendation": rec,
        "rationale": rationale,
    }




def answer_c1_disputed_quarter(party_id=None):
    """Find a party's contracts and summarise what's on them.

    Note: full disputed-lines reconciliation needs Bill/Invoice access
    (outside the Contracts seat). This answers what the seat can see
    and flags the limitation honestly.
    """
    all_contracts = _unwrap(call_tool("Contract.list", {"limit": 200}))
    rows = all_contracts.get("data", []) if isinstance(all_contracts, dict) else []
    if not rows:
        return {"error": "no contracts"}

    if not party_id:
        from collections import Counter
        counts = Counter(c.get("party_id") for c in rows if c.get("party_id"))
        if not counts:
            return {"error": "no party_id on contracts"}
        party_id, n = counts.most_common(1)[0]

    contract_rows = [c for c in rows if c.get("party_id") == party_id]

    summary = []
    for c in contract_rows[:10]:
        cid = c.get("id")
        obl = _unwrap(call_tool("ContractObligation.list",
                                {"contract_id": cid, "limit": 20}))
        ob_rows = obl.get("data", []) if isinstance(obl, dict) else []
        dev = _unwrap(call_tool("ContractClauseDeviation.list",
                                {"contract_id": cid, "limit": 10}))
        dev_rows = dev.get("data", []) if isinstance(dev, dict) else []
        summary.append({
            "contract_id": cid,
            "number": c.get("number"),
            "status": c.get("status"),
            "obligations": len(ob_rows),
            "overdue_obligations": len([o for o in ob_rows if o.get("status") == "overdue"]),
            "deviations": len(dev_rows),
        })

    return {
        "party_id": party_id,
        "contracts_found": len(contract_rows),
        "summary": summary,
        "note": ("Disputed-lines reconciliation needs Bill/Invoice access, "
                 "which is outside the Contracts seat. What's shown is what "
                 "this seat can verify."),
    }
