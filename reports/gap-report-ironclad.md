━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GAP REPORT — CONTRACTS SEAT (Team 17)
Product Compared: Ironclad (ironcladapp.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1: WHAT IRONCLAD DOES THAT WE DON'T

Ironclad has 34 features we lack:

• AI chat interface, prompt library, file upload to AI
• AI insight discovery, commercial context extraction
• Smart Import API (AI-powered document ingestion)
• Custom workflow builder with templates
• Pause/resume/cancel/revert workflows
• Turn history tracking, dynamic schemas
• Built-in e-signature (send, cancel, remind, update signers)
• Recipient URLs, scheduled signatures, BYOSP
• Email thread retrieval, attachment extraction
• Advanced reporting, analytics dashboard
• Compensation analysis, missing agreement reports
• Volume by type, Data Exports, data warehouse integration
• 30+ integrations (Salesforce, Jira, HubSpot, NetSuite,
  ServiceNow, Dynamics 365, Box, Google Sheets, MuleSoft)
• Public REST API with OAuth 2.0, 100+ endpoints
• OpenAPI spec, /llms.txt for AI agents
• Per-tenant encryption, HYOK for GCP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q2: WHICH GAPS CAN AN AGENT CLOSE TODAY?

PLATFORM GAPS (14 — need new tables/endpoints):
• Public REST API, OAuth 2.0
• Workflow templates, pause/resume, turn history
• Dynamic schemas, built-in signatures
• Email thread retrieval
• 30+ integrations, Smart Import API
• Data Exports, per-tenant encryption
• Data warehouse, AI chat UI

AGENT-BUILDABLE (19 — orchestration over existing MCP):
• Workflow orchestration, approval routing
• Expiration alerts, missing obligations
• Compliance checks, contract insights
• Risk surfacing, savings capture
• Financial term protection, compensation analysis
• Volume by type, missing agreement reports
• Advanced reporting, analytics dashboard
• Searchable repository, document analysis
• Contract summarization, playbook comparison
• Agent chat interface

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q3: WHAT CAN AN AGENT DO THAT IRONCLAD CANNOT?

Ironclad is a UI over a database. A human drives every step.

Our agent holds a goal across 20+ steps, re-reads changed
state, makes decisions, and acts via MCP tools.

EXAMPLE — "What expires in 60 days, review this draft against
our playbook, list missing obligations."

Ironclad: Human runs report, opens each contract, reads the
playbook, compares manually, checks obligations, writes up.
→ Human does all the work.

Our agent: Calls Contract.list (filter: end_date < 60 days),
Contract.get on each, propose-clause-deviation against the
playbook, obligation-evidence-pack for each. Returns:
"3 contracts expire. Two have unfavorable liability caps.
One is missing a governing-law clause. Three obligations
uncovered. Drafts attached."
→ Agent does all the work.

THE DIFFERENCE:
Ironclad makes a human faster.
Our agent replaces the human's clicks.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
