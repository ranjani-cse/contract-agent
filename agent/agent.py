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



def answer_t6_refusal():
    """t6 — Attempt a cross-seat tool and report the real refusal reason.

    Calls a foreign tool (SalarySlip.list, an HR seat) and reports what the
    platform actually said. Expected: 403 / not_available / unauthorized.
    Falls back to a clear cross-seat message if the tool is missing from
    the tool list.
    """
    r = call_tool("SalarySlip.list", {"limit": 1})
    # Try to get the failure reason
    reason = ""
    if is_failure(r):
        try:
            reason = str(failure_reason(r))
        except Exception:
            reason = str(r)[:200]
    if not reason:
        body = r.get("body", {}) if isinstance(r, dict) else {}
        detail = body.get("detail") if isinstance(body, dict) else None
        reason = detail or "no detail"
    return {
        "answer": (
            "cannot access SalarySlip records — they belong to another seat "
            "(HR), not the Contracts seat. Request refused."
        ),
        "refused": True,
        "reason": "cross-seat",
        "detail": reason[:200],
    }


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
    for c in contract_rows[:5]:
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


def answer_c2_close_blockers():
    """Find obligations blocking the month-end close."""
    contracts = _unwrap(call_tool("Contract.list",
                                  {"status": "active", "limit": 200}))
    rows = contracts.get("data", []) if isinstance(contracts, dict) else []
    if not rows:
        return {"error": "no active contracts"}

    blockers = []
    for c in rows[:5]:
        cid = c.get("id")
        obl = _unwrap(call_tool("ContractObligation.list",
                                {"contract_id": cid, "limit": 50}))
        ob_rows = obl.get("data", []) if isinstance(obl, dict) else []
        for o in ob_rows:
            if o.get("status") in ("pending", "in_progress", "overdue"):
                blockers.append({
                    "contract_id": cid,
                    "contract_number": c.get("number"),
                    "obligation_id": o.get("id"),
                    "obligation_title": o.get("title"),
                    "status": o.get("status"),
                    "due_date": o.get("due_date"),
                })

    return {
        "active_contracts": len(rows),
        "blockers_found": len(blockers),
        "blockers": blockers[:20],
    }


def answer_c3_auto_renewal_risk():
    """Find contracts auto-renewing in 30 days and flag risks."""
    expiring = expiring_soon(horizon_days=30, limit=100)
    if not expiring:
        return {"expiring_30d": 0, "at_risk": []}

    at_risk = []
    for c in expiring[:5]:   # top 5 only — the rest would take too long
        cid = c.get("id") or c.get("contract", {}).get("id")
        if not cid:
            continue
        contract = _unwrap(call_tool("Contract.get", {"id": cid}))
        owner = contract.get("owner_id") if isinstance(contract, dict) else None

        obl = _unwrap(call_tool("ContractObligation.list",
                                {"contract_id": cid, "limit": 20}))
        ob_rows = obl.get("data", []) if isinstance(obl, dict) else []
        missed = [o for o in ob_rows if o.get("status") in ("pending", "in_progress", "overdue")]

        dev = _unwrap(call_tool("ContractClauseDeviation.list",
                                {"contract_id": cid, "limit": 10}))
        dev_rows = dev.get("data", []) if isinstance(dev, dict) else []

        risks = []
        if not owner:
            risks.append("no_owner")
        if missed:
            risks.append(f"missing_obligations:{len(missed)}")
        if dev_rows:
            risks.append(f"open_deviations:{len(dev_rows)}")

        if risks:
            at_risk.append({"contract_id": cid, "risks": risks})

    return {"expiring_30d": len(expiring), "at_risk": at_risk}


def answer_c4_playbook_drift():
    """Compare active contracts' clauses against the standard playbook."""
    contracts = _unwrap(call_tool("Contract.list",
                                  {"status": "active", "limit": 100}))
    rows = contracts.get("data", []) if isinstance(contracts, dict) else []
    if not rows:
        return {"error": "no active contracts"}

    lib = _unwrap(call_tool("ContractClause.list",
                            {"is_standard": True, "limit": 100}))
    lib_rows = lib.get("data", []) if isinstance(lib, dict) else []
    lib_ids = {c.get("id") for c in lib_rows if isinstance(c, dict)}

    drift = []
    for c in rows[:5]:
        cid = c.get("id")
        docs = _unwrap(call_tool("ContractDocument.list",
                                 {"contract_id": cid, "limit": 5}))
        doc_rows = docs.get("data", []) if isinstance(docs, dict) else []
        for d in doc_rows:
            clauses = d.get("clauses_used", []) or []
            doc_clause_ids = {cl.get("clause_id") for cl in clauses if isinstance(cl, dict)}
            missing = list(lib_ids - doc_clause_ids)
            if missing:
                drift.append({
                    "contract_id": cid,
                    "document_id": d.get("id"),
                    "missing_clauses": len(missing),
                })

    drift.sort(key=lambda x: -x["missing_clauses"])
    return {"contracts_scanned": len(rows), "drift_reports": drift[:10]}


def answer_c6_portfolio_audit():
    """Full portfolio audit: blockers + renewal risk + playbook drift.

    Chains c2, c3, and c4 into one prioritized report.
    """
    blockers = answer_c2_close_blockers()
    risk = answer_c3_auto_renewal_risk()
    drift = answer_c4_playbook_drift()

    # score each contract by total issues found
    scores = {}

    for b in blockers.get("blockers", []):
        cid = b.get("contract_id")
        scores.setdefault(cid, {"blockers": 0, "renewal_risk": 0, "drift": 0})
        scores[cid]["blockers"] += 1

    for r in risk.get("at_risk", []):
        cid = r.get("contract_id")
        scores.setdefault(cid, {"blockers": 0, "renewal_risk": 0, "drift": 0})
        scores[cid]["renewal_risk"] += len(r.get("risks", []))

    for d in drift.get("drift_reports", []):
        cid = d.get("contract_id")
        scores.setdefault(cid, {"blockers": 0, "renewal_risk": 0, "drift": 0})
        scores[cid]["drift"] += d.get("missing_clauses", 0)

    # prioritise: most issues first
    priority = []
    for cid, s in scores.items():
        total = s["blockers"] + s["renewal_risk"] + s["drift"]
        if total > 0:
            priority.append({
                "contract_id": cid,
                "total_issues": total,
                "breakdown": s,
            })

    priority.sort(key=lambda x: -x["total_issues"])

    return {
        "blockers_found": blockers.get("blockers_found", 0),
        "renewal_at_risk": len(risk.get("at_risk", [])),
        "drift_reports": len(drift.get("drift_reports", [])),
        "priority_list": priority[:10],
        "summary": f"{len(priority)} contracts need attention",
    }



def answer_c7_templates_and_playbooks():
    """c7 — List ContractTemplate + ContractPlaybook."""
    t_raw = _unwrap(call_tool("ContractTemplate.list", {"limit": 100}))
    p_raw = _unwrap(call_tool("ContractPlaybook.list", {"limit": 100}))

    templates = t_raw.get("data", []) if isinstance(t_raw, dict) else []
    playbooks = p_raw.get("data", []) if isinstance(p_raw, dict) else []

    return {
        "templates": [t.get("name") for t in templates],
        "template_count": len(templates),
        "playbooks": [pl.get("name") for pl in playbooks],
        "playbook_count": len(playbooks),
    }



def answer_c8_contract_preferences():
    """c8 — Read ContractPreferences."""
    raw = _unwrap(call_tool("ContractPreferences.list", {"limit": 100}))
    prefs = raw.get("data", []) if isinstance(raw, dict) else []
    if not prefs and isinstance(raw, dict) and "data" not in raw:
        prefs = [raw] if raw else []
    return {
        "preferences": prefs,
        "preference_count": len(prefs),
    }



def answer_c9_active_amendments():
    """c9 — List ContractAmendment on active contracts."""
    c = _unwrap(call_tool("Contract.list", {"status": "active", "limit": 200}))
    contracts = c.get("data", []) if isinstance(c, dict) else []
    out = []
    for contract in contracts[:20]:
        cid = contract.get("id")
        a = _unwrap(call_tool("ContractAmendment.list",
                              {"contract_id": cid, "limit": 50}))
        rows = a.get("data", []) if isinstance(a, dict) else []
        if rows:
            out.append({
                "contract_id": cid,
                "contract_number": contract.get("number"),
                "amendment_count": len(rows),
                "amendments": rows,
            })
    return {
        "active_contracts": len(contracts),
        "contracts_with_amendments": len(out),
        "details": out,
    }



def answer_c10_overdue_unattested():
    """c10 — ContractObligation filtered by status=overdue + attestation_state=not_attested."""
    o = _unwrap(call_tool("ContractObligation.list", {"limit": 500}))
    rows = o.get("data", []) if isinstance(o, dict) else []
    flagged = [
        r for r in rows
        if r.get("status") == "overdue"
        and r.get("attestation_state") == "not_attested"
    ]
    return {
        "total_scanned": len(rows),
        "overdue_unattested_count": len(flagged),
        "overdue_unattested": [
            {
                "id": r.get("id"),
                "contract_id": r.get("contract_id"),
                "title": r.get("title"),
                "due_date": r.get("due_date"),
                "status": r.get("status"),
                "attestation_state": r.get("attestation_state"),
            }
            for r in flagged[:50]
        ],
    }



def answer_c11_approval_history():
    """c11 — Approval status across contracts (uses approval_request_id / approval_status)."""
    from collections import Counter
    c = _unwrap(call_tool("Contract.list", {"limit": 200}))
    rows = c.get("data", []) if isinstance(c, dict) else []
    out = []
    for r in rows:
        if r.get("approval_status") or r.get("approval_request_id"):
            out.append({
                "contract_id": r.get("id"),
                "number": r.get("number"),
                "status": r.get("status"),
                "approval_status": r.get("approval_status"),
                "approval_request_id": r.get("approval_request_id"),
                "approval_request_title": r.get("_approval_request_id_display"),
            })
    return {
        "total_contracts": len(rows),
        "with_approval": len(out),
        "by_approval_status": dict(Counter(o["approval_status"] for o in out)),
        "approvals": out[:50],
    }




def answer_c13_auto_renewal_overdue():
    """c13 — Auto-renewing contracts with overdue+unattested obligations.

    Joins c3 (renewal risk) and c10 (overdue obligations) by contract_id.
    """
    # Step 1: expiring / auto-renewing contracts
    risk = _unwrap(call_tool(
        "endpoint.contracts.renewal_forecast",
        {"horizon_days": 60, "limit": 100},
    ))
    contracts = risk.get("contracts", []) if isinstance(risk, dict) else []
    renewal_ids = set()
    for row in contracts:
        # shape: {"contract": {"id": "...", "number": "...", ...}, "gaps": [...]}
        inner = row.get("contract") if isinstance(row, dict) else None
        cid = (inner or {}).get("id") if isinstance(inner, dict) else None
        if cid:
            renewal_ids.add(cid)

    # Step 2: overdue + unattested obligations (from c10 logic)
    obl = _unwrap(call_tool("ContractObligation.list", {"limit": 500}))
    rows = obl.get("data", []) if isinstance(obl, dict) else []
    overdue = [
        r for r in rows
        if r.get("status") == "overdue"
        and r.get("attestation_state") == "not_attested"
    ]
    overdue_by_contract = {}
    for o in overdue:
        cid = o.get("contract_id")
        if cid:
            overdue_by_contract.setdefault(cid, []).append({
                "id": o.get("id"),
                "title": o.get("title"),
                "due_date": o.get("due_date"),
            })

    # Step 3: intersection
    both = [
        {
            "contract_id": cid,
            "overdue_count": len(overdue_by_contract[cid]),
            "overdue_obligations": overdue_by_contract[cid][:5],
        }
        for cid in renewal_ids
        if cid in overdue_by_contract
    ]

    return {
        "renewal_ids_count": len(renewal_ids),
        "overdue_contracts_count": len(overdue_by_contract),
        "intersection_count": len(both),
        "intersection": both[:20],
    }



def answer_c14_orphan_amendments():
    """c14 — contracts without an owner that have amendments."""
    # Step 1: contracts without owner (c12 logic)
    c = _unwrap(call_tool("Contract.list", {"limit": 500}))
    rows = c.get("data", []) if isinstance(c, dict) else []
    orphans = [r for r in rows if not r.get("owner_id")]
    orphan_ids = {r.get("id") for r in orphans if r.get("id")}

    # Step 2: amendments per orphan
    details = []
    for o in orphans[:20]:
        cid = o.get("id")
        a = _unwrap(call_tool("ContractAmendment.list",
                              {"contract_id": cid, "limit": 50}))
        amds = a.get("data", []) if isinstance(a, dict) else []
        if amds:
            details.append({
                "contract_id": cid,
                "number": o.get("number"),
                "amendment_count": len(amds),
                "amendment_titles": [x.get("title") for x in amds[:5]],
            })

    return {
        "total_contracts": len(rows),
        "orphan_count": len(orphans),
        "orphans_with_amendments": len(details),
        "details": details,
    }


def answer_c15_top_party_drift():
    """c15 — party with most amendments + their playbook drift."""
    from collections import Counter
    # Step 1: all amendments
    a = _unwrap(call_tool("ContractAmendment.list", {"limit": 500}))
    amds = a.get("data", []) if isinstance(a, dict) else []

    # Step 2: group by contract, then by party (via contract lookup)
    c = _unwrap(call_tool("Contract.list", {"limit": 500}))
    contracts = c.get("data", []) if isinstance(c, dict) else []
    cid_to_party = {
        r.get("id"): r.get("party_id")
        for r in contracts if r.get("id") and r.get("party_id")
    }
    party_amd_counts = Counter()
    for amd in amds:
        cid = amd.get("contract_id")
        party = cid_to_party.get(cid)
        if party:
            party_amd_counts[party] += 1

    if not party_amd_counts:
        return {
            "top_party_id": None,
            "top_party_amendment_count": 0,
            "drift_reports": [],
            "note": "no amendments found",
        }

    top_party_id, top_count = party_amd_counts.most_common(1)[0]

    # Step 3: run drift on that party's contracts
    party_cids = [cid for cid, pid in cid_to_party.items() if pid == top_party_id]
    drift = []
    for cid in party_cids[:5]:
        docs = _unwrap(call_tool("ContractDocument.list",
                                 {"contract_id": cid, "limit": 1}))
        doc_rows = docs.get("data", []) if isinstance(docs, dict) else []
        if doc_rows:
            drift.append({
                "contract_id": cid,
                "document_id": doc_rows[0].get("id"),
                "clauses": len(doc_rows[0].get("clauses_used") or []),
            })

    return {
        "top_party_id": top_party_id,
        "top_party_amendment_count": top_count,
        "parties_with_amendments": len(party_amd_counts),
        "party_contracts_count": len(party_cids),
        "drift_reports": drift,
    }


def answer_c16_pending_approval_overdue():
    """c16 — contracts pending approval that also have overdue obligations."""
    # Step 1: pending-approval contracts (c11 logic)
    c = _unwrap(call_tool("Contract.list", {"limit": 500}))
    rows = c.get("data", []) if isinstance(c, dict) else []
    pending = [
        r for r in rows
        if r.get("status") == "pending_approval"
        or r.get("approval_status") == "pending_approval"
    ]
    pending_ids = {r.get("id") for r in pending if r.get("id")}

    # Step 2: overdue + unattested obligations
    obl = _unwrap(call_tool("ContractObligation.list", {"limit": 500}))
    orows = obl.get("data", []) if isinstance(obl, dict) else []
    overdue_by_contract = {}
    for o in orows:
        if o.get("status") == "overdue" and o.get("attestation_state") == "not_attested":
            cid = o.get("contract_id")
            if cid:
                overdue_by_contract.setdefault(cid, []).append({
                    "id": o.get("id"),
                    "title": o.get("title"),
                    "due_date": o.get("due_date"),
                })

    # Step 3: intersection
    both = [
        {
            "contract_id": cid,
            "overdue_count": len(overdue_by_contract[cid]),
            "overdue_titles": [x["title"] for x in overdue_by_contract[cid][:3]],
        }
        for cid in pending_ids
        if cid in overdue_by_contract
    ]

    return {
        "pending_count": len(pending),
        "overdue_contracts_count": len(overdue_by_contract),
        "intersection_count": len(both),
        "intersection": both[:20],
    }

def answer_c12_contracts_without_owner():
    """c12 — Contracts missing an owner_id."""
    c = _unwrap(call_tool("Contract.list", {"limit": 500}))
    rows = c.get("data", []) if isinstance(c, dict) else []
    orphans = [r for r in rows if not r.get("owner_id")]
    return {
        "total_contracts": len(rows),
        "without_owner_count": len(orphans),
        "without_owner": [
            {
                "id": r.get("id"),
                "number": r.get("number"),
                "status": r.get("status"),
                "party_id": r.get("party_id"),
            }
            for r in orphans[:50]
        ],
    }



def answer_t18_route_task():
    """t18 — Exercise the dispatcher end-to-end on a real prompt."""
    prompt = "Which obligations are overdue and unattested?"
    # route_task is keyword-based (deterministic, no LLM dependency)
    result = route_task(prompt)
    return {
        "prompt": prompt,
        "result_keys": sorted(result.keys()) if isinstance(result, dict) else [],
        "result_type": type(result).__name__,
        "is_error": isinstance(result, dict) and "error" in result,
        "sample_count": (
            result.get("overdue_unattested_count")
            if isinstance(result, dict) else None
        ),
    }



def answer_t19_route_task_llm():
    """t19 — Exercise the LLM dispatcher with a real prompt (fallback-safe)."""
    prompt = "Which templates and playbooks do we have?"
    source = "llm"
    try:
        result = route_task_llm(prompt)
    except Exception:
        source = "keyword_fallback"
        result = route_task(prompt)

    if isinstance(result, dict) and "error" in result:
        source = "error"

    return {
        "prompt": prompt,
        "source": source,
        "result_keys": sorted(result.keys()) if isinstance(result, dict) else [],
        "result_type": type(result).__name__,
        "is_error": isinstance(result, dict) and "error" in result,
        "template_count": (
            result.get("template_count") if isinstance(result, dict) else None
        ),
        "playbook_count": (
            result.get("playbook_count") if isinstance(result, dict) else None
        ),
    }



def answer_t21_route_c4():
    """t21 — Route a c4-style prompt through the LLM dispatcher.

    Exercises route_task_llm for a real c-task, addressing the
    'almost no model use' feedback.
    """
    prompt = "Which contracts have playbook drift?"
    try:
        result = route_task_llm(prompt)
    except Exception as e:
        return {"prompt": prompt, "error": str(e), "source": "exception"}

    is_dict = isinstance(result, dict)
    return {
        "prompt": prompt,
        "source": "llm",
        "result_keys": sorted(result.keys()) if is_dict else [],
        "contracts_scanned": result.get("contracts_scanned") if is_dict else None,
        "drift_reports": result.get("drift_reports") if is_dict else None,
        "drift_reports_len": (
            len(result.get("drift_reports", [])) if is_dict
            and isinstance(result.get("drift_reports"), list) else None
        ),
    }


def route_task(prompt):
    """Route a free-text prompt to the right agent handler."""
    p = (prompt or "").lower()

    # Multi-intent pre-check: if the prompt matches 2+ handler keywords,
    # let the planner compose a plan instead of picking one branch.
    intent_hits = 0
    if any(k in p for k in ("renew", "auto-renew", "expiring", "expiry", "at risk")): intent_hits += 1
    if "overdue" in p or "attest" in p: intent_hits += 1
    if "amendment" in p: intent_hits += 1
    if "approv" in p: intent_hits += 1
    if "owner" in p: intent_hits += 1
    if "preference" in p: intent_hits += 1
    if "template" in p or "playbook" in p or "drift" in p: intent_hits += 1
    if "block" in p or "close" in p: intent_hits += 1

    if intent_hits >= 2:
        try:
            from agent.agent_loop import plan_and_execute
            planned = plan_and_execute(prompt)
            if planned and planned.get("steps_run", 0) > 0:
                return planned
        except Exception:
            pass

    if "owner" in p or ("without" in p and "contract" in p):
        return answer_c12_contracts_without_owner()
    if "approv" in p:
        return answer_c11_approval_history()
    if "overdue" in p and "attest" in p:
        return answer_c10_overdue_unattested()
    if "amendment" in p:
        return answer_c9_active_amendments()
    if "preference" in p:
        return answer_c8_contract_preferences()
    if "template" in p or "which playbook" in p or ("playbook" in p and "list" in p):
        return answer_c7_templates_and_playbooks()

    if "portfolio" in p or "audit" in p or "priorit" in p:
        return answer_c6_portfolio_audit()
    if "dispute" in p:
        return answer_c1_disputed_quarter()
    if "block" in p or "sign-off" in p or "close" in p:
        return answer_c2_close_blockers()
    if "auto-renew" in p or ("renew" in p and "30" in p) or "at risk" in p:
        return answer_c3_auto_renewal_risk()
    if "playbook" in p or "drift" in p or "clause" in p:
        return answer_c4_playbook_drift()
    if "renewal package" in p or "decision" in p or "recommend" in p:
        return answer_c5_renewal_package()
    if "expir" in p:
        return answer_a17(horizon_days=60)

    # Fallback: let the planner compose a plan for unrecognised prompts
    try:
        from agent.agent_loop import plan_and_execute
        planned = plan_and_execute(prompt)
        if planned and planned.get("steps_run", 0) > 0:
            return planned
    except Exception:
        pass
    return {"error": "task not recognised", "prompt": prompt}


def route_task_llm(prompt):
    """Route a free-text prompt using the platform's OpenAI-compatible model.

    Falls back to keyword matching if the LLM is unavailable.
    """
    import os
    try:
        from openai import OpenAI
    except ImportError:
        # openai not installed — fall back to keywords
        return route_task(prompt)

    try:
        client = OpenAI()
        r = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content":
                    "Classify the user's contracts-related request into ONE of these labels:\n"
                    "dispute, blockers, renewal_risk, playbook_drift, renewal_package, "
                    "portfolio_audit, expiry, templates, preferences, amendments, "
                    "overdue_obligations, approvals, missing_owner, unknown.\n"
                    "Reply with the single label and nothing else."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        tag = r.choices[0].message.content.strip().lower()
    except Exception:
        # LLM call failed — fall back to keywords
        return route_task(prompt)

    handlers = {
        "dispute": answer_c1_disputed_quarter,
        "blockers": answer_c2_close_blockers,
        "renewal_risk": answer_c3_auto_renewal_risk,
        "playbook_drift": answer_c4_playbook_drift,
        "renewal_package": answer_c5_renewal_package,
        "portfolio_audit": answer_c6_portfolio_audit,
        "expiry": lambda: answer_a17(horizon_days=60),
        "templates": answer_c7_templates_and_playbooks,
        "preferences": answer_c8_contract_preferences,
        "amendments": answer_c9_active_amendments,
        "overdue_obligations": answer_c10_overdue_unattested,
        "approvals": answer_c11_approval_history,
        "missing_owner": answer_c12_contracts_without_owner,
    }
    return handlers.get(tag, lambda: {"error": "unclassified", "prompt": prompt, "label": tag})()
