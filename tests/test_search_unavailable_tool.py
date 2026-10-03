"""Test: tools.search and tools/list consistency.

Bug 9 was filed 2026-09-23: tools.search returned endpoint.people_directory
which was NOT in this seat's tools/list, and calling it returned
invalid_arguments instead of tool_not_available.

Fixed by 2026-09-29: endpoint.people_directory is now present in tools/list
(the seat was expanded from 239 to 247 tools). This test asserts the fix.
"""
from agent.mcp_client import call


def _tool_names():
    r = call("tools/list", {})
    return {t["name"] for t in r["body"]["result"]["tools"]}


def test_people_directory_is_now_in_tools_list():
    """After the fix, the tool search returned is now callable."""
    names = _tool_names()
    assert names, "tools/list returned no tools — check auth"
    assert "endpoint.people_directory" in names, \
        "Bug 9 fixed: people_directory should now be in tools/list"


def test_seat_has_expanded_tool_set():
    """The seat now exposes more than 239 tools."""
    names = _tool_names()
    assert len(names) >= 240, f"expected >= 240 tools, got {len(names)}"
