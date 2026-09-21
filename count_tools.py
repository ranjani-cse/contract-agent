"""Count and categorize the tools available to our agent."""

from agent.mcp_client import list_tools
from collections import Counter

tools = list_tools()['tools']
print(f"Total tools: {len(tools)}")
print()

# Group by prefix
prefixes = Counter(t['name'].split('.')[0] for t in tools)
print("Top entities by tool count:")
for name, count in sorted(prefixes.items(), key=lambda x: -x[1])[:20]:
    print(f"  {name}: {count}")

print()
print("Contract-related tools:")
contract_tools = [t['name'] for t in tools if 'ontract' in t['name']]
for t in contract_tools:
    print(f"  {t}")
