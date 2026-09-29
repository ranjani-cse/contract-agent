"""Test: propose_clause_deviation's clause_key expects the clause UUID.

Bug 6 was filed 2026-09-22. Investigation on 2026-09-29 found the correct
value: clause_id (a UUID) from the document's clauses_used array. Display
names and clause types are rejected.
"""
from agent.mcp_client import call_tool, is_failure


def test_display_name_is_rejected():
    """A human-readable clause name is not a valid clause_key."""
    r = call_tool("endpoint.contracts.propose_clause_deviation", {
        "document_id": "0826ccba-16cb-4a79-9e92-f2eb3336a57c",
        "clause_key": "Confidentiality - Tool Room",
        "rationale": "test",
        "proposed_content": "test content",
    })
    assert is_failure(r), "display name should be rejected"


def test_clause_type_is_rejected():
    """A clause type string is not a valid clause_key."""
    r = call_tool("endpoint.contracts.propose_clause_deviation", {
        "document_id": "0826ccba-16cb-4a79-9e92-f2eb3336a57c",
        "clause_key": "confidentiality",
        "rationale": "test",
        "proposed_content": "test content",
    })
    assert is_failure(r), "clause type should be rejected"
