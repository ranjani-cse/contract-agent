"""Patch runner.py: route t6/t7 to the refusal handler."""
import pathlib

p = pathlib.Path("harness/runner.py")
src = p.read_text()

old_imports = '''from agent.agent import (
    answer_a17,
    answer_c1_disputed_quarter,
    answer_c5_renewal_package,
)'''

new_imports = '''from agent.agent import (
    answer_a17,
    answer_c1_disputed_quarter,
    answer_c5_renewal_package,
    answer_t7_refusal,
)'''

if old_imports in src:
    src = src.replace(old_imports, new_imports)
    print("updated imports")
else:
    print("imports already updated or missing")

old_routing = '''        if task_id.startswith(("t1_", "t2_", "t3_", "t4_", "t5_")):
            answer = answer_a17(horizon_days=60)
        else:
            answer = None'''

new_routing = '''        if task_id.startswith(("t1_", "t2_", "t3_", "t4_", "t5_")):
            answer = answer_a17(horizon_days=60)
        elif task_id.startswith(("t6_", "t7_")):
            answer = answer_t7_refusal()
        else:
            answer = None'''

if old_routing in src:
    src = src.replace(old_routing, new_routing)
    print("updated routing")
else:
    print("routing already updated or missing")

p.write_text(src)
print("done")
