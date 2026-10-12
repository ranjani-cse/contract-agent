"""Test: route_task dispatches prompts to the right handler."""
from agent.agent import route_task


def test_route_portfolio_audit():
    r = route_task("Run a portfolio audit")
    assert "priority_list" in r, "should route to c6"


def test_route_dispute():
    r = route_task("A customer disputes last quarter")
    assert "party_id" in r or "contracts_found" in r, "should route to c1"


def test_route_close_blockers():
    r = route_task("What is blocking our close?")
    assert "blockers" in r, "should route to c2"


def test_route_renewal_risk():
    r = route_task("Find auto-renewal risks in 30 days")
    assert "at_risk" in r, "should route to c3"


def test_route_playbook_drift():
    r = route_task("Check playbook drift")
    assert "drift_reports" in r, "should route to c4"


def test_route_renewal_package():
    r = route_task("Build a renewal decision package")
    assert "recommendation" in r, "should route to c5"


def test_route_expiry():
    r = route_task("What expires in 60 days?")
    assert "expiring" in r, "should route to a17"


def test_route_unknown_returns_error():
    r = route_task("Do something unrelated to contracts")
    assert "error" in r, "should return error for unknown prompt"
