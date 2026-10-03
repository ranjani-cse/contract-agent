import os, sys, json, requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Authenticate
AS = "https://agentswitch.theschoolofai.in"
body = {"email": "team17@theschoolofai.in", "password": "hC1ivvROcB7MEKxX!aA1"}
resp = requests.post(f"{AS}/api/auth/login", json=body)
os.environ["TOKEN"] = resp.json()["token"]
os.environ["AS"] = AS

from agent.mcp_client import list_tools, call_tool, is_failure, failure_reason

tools_to_test = [
    "ContractPlaybook.list",
    "ContractPlaybook.get",
    "ContractPreferences.list",
    "ContractPreferences.get",
    "ContractPreferences.create",
    "ContractPreferences.update",
    "ContractAmendment.list",
    "ContractAmendment.get"
]

all_tools = list_tools()
tool_schemas = {t['name']: t for t in all_tools if t['name'] in tools_to_test}

results = {}

for t_name in tools_to_test:
    print(f"\n--- Testing {t_name} ---")
    if t_name not in tool_schemas:
        print(f"Tool {t_name} not found in list_tools()")
        continue
    
    # Try calling without required args to see the error, or with basic pagination
    args = {}
    if 'list' in t_name:
        args = {"limit": 1}
    elif 'get' in t_name or 'update' in t_name:
        args = {"id": "00000000-0000-0000-0000-000000000000"}
    
    if t_name == "ContractPreferences.create":
        args = {"key": "test_pref", "value": "test_val"}
        
    print(f"Calling with args: {args}")
    r = call_tool(t_name, args)
    
    print(f"Failed? {is_failure(r)}")
    if is_failure(r):
        print(f"Reason: {failure_reason(r)}")
    else:
        print(f"Success! Result: {str(r)[:200]}")
    results[t_name] = r

with open("probes_batch3_output.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nWrote full output to probes_batch3_output.json")
