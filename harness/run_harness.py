"""Harness loop. Every run written to disk BEFORE scoring."""
import json, time, importlib
from pathlib import Path
from agent.agent import answer_a17

RUNS = Path("runs"); RUNS.mkdir(exist_ok=True)
TASKS = Path("harness/tasks.jsonl")

def load_tasks():
    with open(TASKS) as f:
        return [json.loads(l) for l in f if l.strip()]

def run_agent(task):
    tid = task["id"]
    if tid.startswith("t1_"):
        return answer_a17(horizon_days=60)
    if tid.startswith("t6_") or tid.startswith("t7_"):
        # refusal tasks: real agent should recognise refusal; stub returns honest non-answer
        return {"refusal_expected": True, "note": "agent must refuse — not implemented yet"}
    return {"note": f"agent not implemented for {tid}"}

def score(task, agent_answer):
    mod = importlib.import_module("harness.verifiers")
    fn = getattr(mod, task["verifier"])
    try:
        return fn(agent_answer)
    except Exception as e:
        return {"pass": False, "error": str(e)}

def main():
    tasks = load_tasks()
    run_file = RUNS / f"run_{int(time.time())}.jsonl"
    with open(run_file, "w") as out:
        for t in tasks:
            start = time.time()
            answer = run_agent(t)
            row = {"task_id": t["id"], "prompt": t["prompt"], "answer": answer,
                   "elapsed_s": round(time.time()-start, 2), "timestamp": time.time()}
            out.write(json.dumps(row) + "\n"); out.flush()   # BEFORE scoring
            verdict = score(t, answer)
            out.write(json.dumps({"task_id": t["id"], "verdict": verdict}) + "\n"); out.flush()
            print(f"{t['id']}: {'PASS' if verdict.get('pass') else 'FAIL'}")
    print(f"\nWrote {run_file}")

if __name__ == "__main__":
    main()
