import os, sys, json, requests, re, datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
# Tools to test
# ─────────────────────────────────────────────────────────────────────────────
TOOLS_TO_TEST = [
    "ContractPlaybook.list",
"ContractPlaybook.get",
"ContractPreferences.list",
"ContractPreferences.get",
"ContractPreferences.create",
"ContractPreferences.update",
"ContractAmendment.list",
"ContractAmendment.get",
"ContractObligation.list",
"ContractObligation.get",
"ContractObligation.create",
"ContractObligation.update",
"ContractRenewal.list",
"ContractRenewal.get",
"ContractRenewal.create",
"ContractRenewal.update",
"ContractClause.list",
"ContractClause.get",
"ContractClauseDeviation.list",
"ContractClauseDeviation.get",
"ContractClauseDeviation.create",
"ContractClauseDeviation.update",
"ContractDocument.list",
"ContractDocument.get",
"ContractDocument.create",
"ContractDocument.update",
"ContractTemplate.list",
"ContractTemplate.get",
"Contract.list",
"Contract.get",
"Contract.create",
"Contract.update",
"ContractObligation.start",
"ContractObligation.mark_complete",
"ContractObligation.mark_overdue.in_progress.overdue",
"ContractObligation.mark_overdue.pending.overdue",
"ContractObligation.complete_late",
"ContractRenewal.submit_for_approval",
"ContractRenewal.revise",
"ContractClauseDeviation.submit_for_approval",
"ContractClauseDeviation.revise",
"ContractClauseDeviation.withdraw.draft.withdrawn",
"ContractDocument.submit_for_review",
"ContractDocument.send_for_signature",
"ContractDocument.mark_signed",
"ContractDocument.archive",
"ContractDocument.archive_draft",
"Contract.submit_for_approval",
"Contract.mark_expiring",
"Contract.mark_expired",
"endpoint.contracts.obligation_evidence_pack",
"endpoint.contracts.attest_obligation",
"endpoint.contracts.document_redline",
"endpoint.contracts.capture_document_revision",
"endpoint.contracts.propose_clause_deviation",
"endpoint.contracts.bind_deviation_approval",
"endpoint.contracts.recheck_deviation_coverage",
"endpoint.contracts.renewal_forecast",
"endpoint.contracts.record_renewal_decision"
]

# ─────────────────────────────────────────────────────────────────────────────
# Schema-driven test arguments (derived from mcp_tools_schema.txt +
# contracts_schema.txt required fields).
#
# For .list  → send {"limit": 1}  (entity field auto-handled by the tool wrapper)
# For .get   → send {"id": DUMMY_UUID}
# For .update→ send {"id": DUMMY_UUID, "data": {<one optional field>}}
# For .create→ send all required fields (from contracts_schema.txt)
# For transitions → send {"id": DUMMY_UUID, "action": ..., "target_state": ...}
# ─────────────────────────────────────────────────────────────────────────────
DUMMY_UUID = "00000000-0000-0000-0000-000000000000"

TOOL_ARGS = {
    # ── ContractPlaybook ──────────────────────────────────────────────────────
    "ContractPlaybook.list":   {"limit": 1},
    "ContractPlaybook.get":    {"id": DUMMY_UUID},

    # ── ContractPreferences (config entity — no required fields for create) ───
    "ContractPreferences.list":   {"limit": 1},
    "ContractPreferences.get":    {"id": DUMMY_UUID},
    "ContractPreferences.create": {"data": {
        "default_contract_duration_months": 12,
        "auto_renewal_enabled": False,
        "renewal_reminder_days": 30,
    }},
    "ContractPreferences.update": {"id": DUMMY_UUID, "data": {"renewal_reminder_days": 60}},

    # ── ContractAmendment ─────────────────────────────────────────────────────
    # required: title, contract_id, effective_date, description
    "ContractAmendment.list": {"limit": 1},
    "ContractAmendment.get":  {"id": DUMMY_UUID},

    # ── ContractObligation ────────────────────────────────────────────────────
    # required: title, contract_id
    "ContractObligation.list":   {"limit": 1},
    "ContractObligation.get":    {"id": DUMMY_UUID},
    "ContractObligation.create": {"data": {
        "title": "Sanity-test obligation",
        "contract_id": DUMMY_UUID,
    }},
    "ContractObligation.update": {"id": DUMMY_UUID, "data": {"title": "Updated obligation"}},

    # ── ContractRenewal ───────────────────────────────────────────────────────
    # required: title, contract_id, new_start_date, new_end_date
    "ContractRenewal.list":   {"limit": 1},
    "ContractRenewal.get":    {"id": DUMMY_UUID},
    "ContractRenewal.create": {"data": {
        "title": "Sanity-test renewal",
        "contract_id": DUMMY_UUID,
        "new_start_date": "2027-01-01",
        "new_end_date": "2028-01-01",
    }},
    "ContractRenewal.update": {"id": DUMMY_UUID, "data": {"title": "Updated renewal"}},

    # ── ContractClause ────────────────────────────────────────────────────────
    # required: name, content
    "ContractClause.list": {"limit": 1},
    "ContractClause.get":  {"id": DUMMY_UUID},
}


# ─────────────────────────────────────────────────────────────────────────────
# Auth — expects AS and TOKEN env vars (set by run_harness.py or manually)
# ─────────────────────────────────────────────────────────────────────────────
def setup_auth():
    """Use existing AS and TOKEN environment variables."""
    if "AS" not in os.environ or "TOKEN" not in os.environ:
        print("ERROR: Environment variables AS and TOKEN must be set before running.")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# Bug ID counter — always starts at 8 each run
# ─────────────────────────────────────────────────────────────────────────────
NEXT_BUG_ID = 8

def get_next_bug_id():
    """Return sequential bug IDs starting from 8."""
    global NEXT_BUG_ID
    bug_id = NEXT_BUG_ID
    NEXT_BUG_ID += 1
    return bug_id


# ─────────────────────────────────────────────────────────────────────────────
# BUGS.md update
# ─────────────────────────────────────────────────────────────────────────────
def update_bugs_md(bug_id, tool_name, reason, evidence_filename, bugs_file="BUGS.md"):
    """Append a new bug row at the end of the markdown table."""
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    new_row = (
        f"| {bug_id} | {date_str} | {tool_name} | {reason} | High "
        f"| [{evidence_filename}]({evidence_filename}) |\n"
    )
    with open(bugs_file, "r") as f:
        lines = f.readlines()

    insert_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("|"):
            insert_idx = i + 1
            break

    if insert_idx == -1:
        print("Could not find table in BUGS.md")
        return

    lines.insert(insert_idx, new_row)
    with open(bugs_file, "w") as f:
        f.writelines(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Evidence file
# ─────────────────────────────────────────────────────────────────────────────
def generate_evidence_file(bug_id, tool_name, args, response):
    """Write args + full response to a text file."""
    filename = f"bug{bug_id}_evidence.txt"
    with open(filename, "w") as f:
        f.write(f"Tool: {tool_name}\n")
        f.write(f"Arguments: {json.dumps(args, indent=2)}\n\n")
        f.write(f"Response:\n{json.dumps(response, indent=2)}\n")
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# Main test loop
# ─────────────────────────────────────────────────────────────────────────────
def main():
    setup_auth()
    from agent.mcp_client import list_tools, call_tool, is_failure, failure_reason

    print("Fetching tools from MCP server...")
    all_tools = list_tools()
    tool_schemas = {t["name"]: t for t in all_tools}

    for t_name in TOOLS_TO_TEST:
        print(f"\n--- Probing {t_name} ---")

        if t_name not in tool_schemas:
            print(f"  SKIP: Tool not found on server.")
            continue

        # Look up schema-driven args; fall back to a safe default
        args = TOOL_ARGS.get(t_name)
        if args is None:
            # Generic fallbacks for unknown patterns
            if ".list" in t_name:
                args = {"limit": 1}
            elif ".get" in t_name:
                args = {"id": DUMMY_UUID}
            elif ".update" in t_name:
                args = {"id": DUMMY_UUID, "data": {}}
            elif ".create" in t_name:
                args = {"data": {}}
            else:
                args = {}

        print(f"  Sending args: {json.dumps(args)}")
        resp = call_tool(t_name, args)

        if is_failure(resp):
            reason = failure_reason(resp) or "Unknown automated failure"
            reason = reason.replace("|", "").replace("\n", " ")
            print(f"  FAILURE: {reason}")

            bug_id = get_next_bug_id()
            evidence_file = generate_evidence_file(bug_id, t_name, args, resp)
            update_bugs_md(bug_id, t_name, reason, evidence_file)
            print(f"  Logged Bug #{bug_id} → {evidence_file}")
        else:
            print("  SUCCESS: No bug detected.")


if __name__ == "__main__":
    main()
