"""Planner — produce a plan (list of tool calls) from a goal.

LLM-first; if no LLM is available (no openai package / no env vars),
falls back to a small rule-based planner that composes existing
answer_* handlers.

A plan is a list of steps:
    [{"kind": "handler", "name": "renewal_risk"},
     {"kind": "handler", "name": "overdue_obligations"}]
"""

import json
import os


# Available handler intents the rule-based planner can chain
INTENTS = {
    "renewal_risk":        ["auto-renew", "renew", "expiring", "expiry", "at risk"],
    "overdue_obligations": ["overdue", "unattested", "attest"],
    "missing_owner":       ["without owner", "no owner", "missing owner"],
    "amendments":          ["amendment"],
    "approvals":           ["approval", "approv"],
    "templates":           ["template"],
    "preferences":         ["preference"],
    "blockers":            ["blocker", "close"],
    "drift":               ["drift", "playbook"],
    "dispute":             ["dispute", "party"],
}


def _rule_plan(goal):
    """Fallback planner: match goal keywords to 1-3 chained intents."""
    p = (goal or "").lower()
    hits = []
    for intent, kws in INTENTS.items():
        if any(k in p for k in kws):
            hits.append(intent)
    if not hits:
        return None
    seen = set()
    ordered = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return [{"kind": "handler", "name": h} for h in ordered[:3]]


def _llm_plan(goal):
    """Ask the platform LLM to produce a plan as JSON."""
    try:
        from openai import OpenAI
    except ImportError:
        return None
    try:
        client = OpenAI()
    except Exception:
        return None

    system = (
        "You are a planner for a contracts agent. Given a goal and a list "
        "of available handler intents, return a JSON list of steps to run.\n"
        'Each step is {"kind":"handler","name":"<intent>"}.\n'
        "Available intents: " + ", ".join(INTENTS.keys()) + "\n"
        "Return ONLY the JSON array, no prose."
    )
    try:
        r = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": goal},
            ],
            temperature=0,
        )
        raw = r.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        plan = json.loads(raw)
        if isinstance(plan, list):
            return plan
    except Exception:
        return None
    return None


def make_plan(goal):
    """Return {'source': 'llm'|'rule'|'none', 'steps': [...]}."""
    steps = _llm_plan(goal)
    if steps:
        return {"source": "llm", "steps": steps}
    steps = _rule_plan(goal)
    if steps:
        return {"source": "rule", "steps": steps}
    return {"source": "none", "steps": []}
