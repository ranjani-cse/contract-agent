"""c8 — contract preferences are returned."""
from agent.agent import answer_c8_contract_preferences
from harness.verifiers import verify_c8_contract_preferences


def test_c8_pass():
    ans = answer_c8_contract_preferences()
    v = verify_c8_contract_preferences(ans)
    assert v["pass"], v
    assert v["preference_count"] >= 1
