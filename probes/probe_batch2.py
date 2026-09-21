"""Bug probes batch 2 — within real schemas."""
import json
from agent.mcp_client import call_tool

def probe_missing_required():
    r = call_tool("Contract.get", {})
    return {"probe": "missing_required", "http": r["http_status"], "body": r["body"]}

def probe_type_confusion():
    r = call_tool("Contract.get", {"id": {"$ne": None}})
    return {"probe": "type_confusion", "http": r["http_status"], "body": r["body"]}

def probe_pagination():
    out = {}
    for lim in [0, -1, 10**9]:
        r = call_tool("Contract.list", {"limit": lim})
        out[f"limit_{lim}"] = r["body"]
    return {"probe": "pagination", "results": out}

def probe_null_id():
    out = {}
    for val in ["", None]:
        r = call_tool("Contract.get", {"id": val})
        out[repr(val)] = {"http": r["http_status"], "body": r["body"]}
    return {"probe": "null_id", "results": out}

ENDPOINTS = [
    "endpoint.contracts.attest_obligation",
    "endpoint.contracts.bind_deviation_approval",
    "endpoint.contracts.capture_document_revision",
    "endpoint.contracts.document_redline",
    "endpoint.contracts.obligation_evidence_pack",
    "endpoint.contracts.propose_clause_deviation",
    "endpoint.contracts.recheck_deviation_coverage",
    "endpoint.contracts.record_renewal_decision",
    "endpoint.contracts.renewal_forecast",
]

def probe_endpoints_empty():
    out = {}
    for e in ENDPOINTS:
        r = call_tool(e, {})
        out[e] = {"http": r["http_status"], "body": r["body"]}
    return {"probe": "endpoints_empty", "results": out}

if __name__ == "__main__":
    for fn in [probe_missing_required, probe_type_confusion,
               probe_pagination, probe_null_id, probe_endpoints_empty]:
        try:
            print(json.dumps(fn(), indent=2))
        except Exception as e:
            print(json.dumps({"probe": fn.__name__, "error": str(e)}, indent=2))
