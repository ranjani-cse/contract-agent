"""Agent loop — plan, act, observe, repeat. Week 2 Day 9 deliverable.

Prints a step-by-step trace of the agent answering the A17 request:
  "What expires in 60 days, review this draft against our playbook,
   and list the obligations we are missing."
"""
from agent.agent import expiring_soon, review_against_playbook, missing_obligations


class ContractAgent:
    """Answers Team 17's A17 request via MCP tool calls, one step at a time."""

    def __init__(self, horizon_days=60, top_n=3):
        self.horizon_days = horizon_days
        self.top_n = top_n
        self.history = []

    def run(self, goal):
        print(f"Goal: {goal}\n")
        self.history.append({"role": "user", "content": goal})

        # Step 1 — list expiring contracts
        print("--- Step 1 ---")
        print("Plan: list_expiring")
        expiring = expiring_soon(self.horizon_days)
        print(f"Observed: {len(expiring)} contracts expiring in {self.horizon_days} days")
        self.history.append({"action": "list_expiring", "count": len(expiring)})

        # Step 2 — playbook review on the top N
        print("\n--- Step 2 ---")
        print("Plan: review_playbook")
        reviews = []
        for c in expiring[: self.top_n]:
            cid = c.get("id") or c.get("contract", {}).get("id")
            if cid:
                reviews.append({"contract_id": cid,
                                "review": review_against_playbook(cid)})
        print(f"Observed: reviewed {len(reviews)} contracts against playbook")
        self.history.append({"action": "review_playbook", "count": len(reviews)})

        # Step 3 — missing obligations
        print("\n--- Step 3 ---")
        print("Plan: list_missing_obligations")
        missing = []
        for c in expiring[: self.top_n]:
            cid = c.get("id") or c.get("contract", {}).get("id")
            if cid:
                missing.append({"contract_id": cid,
                                "obligations": missing_obligations(cid)})
        print(f"Observed: checked obligations for {len(missing)} contracts")
        self.history.append({"action": "list_missing_obligations", "count": len(missing)})

        # Step 4 — done
        print("\n--- Step 4 ---")
        print("Plan: done")
        answer = (
            f"{len(expiring)} contracts expire in {self.horizon_days} days; "
            f"reviewed {len(reviews)} against playbook; "
            f"checked obligations for {len(missing)}."
        )
        print(f"\nFinal answer:\n{answer}")
        return answer


if __name__ == "__main__":
    ContractAgent().run(
        "What expires in 60 days, review this draft against our playbook, "
        "and list the obligations we are missing."
    )
