"""c7 — templates + playbooks are listed."""
from agent.agent import answer_c7_templates_and_playbooks
from harness.verifiers import verify_c7_templates_and_playbooks


def test_c7_pass():
    ans = answer_c7_templates_and_playbooks()
    v = verify_c7_templates_and_playbooks(ans)
    assert v["pass"], v
    assert v["template_count"] >= 1
    assert v["playbook_count"] >= 1
