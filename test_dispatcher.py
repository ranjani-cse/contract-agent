"""Test the LLM dispatcher (with keyword fallback)."""
from agent.agent import route_task_llm

prompts = [
    "Which agreements lapse soon?",
    "What is overdue on our side?",
    "Show liability exposure",
    "Run a portfolio audit",
    "A customer disputes last quarter",
]

for p in prompts:
    r = route_task_llm(p)
    keys = list(r.keys())[:3] if isinstance(r, dict) else type(r).__name__
    print(f"{p:48} -> {keys}")
