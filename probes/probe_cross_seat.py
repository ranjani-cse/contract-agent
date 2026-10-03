"""Probe: can the Contracts seat reach tools it shouldn't?"""
from agent.mcp_client import call_tool, is_failure, failure_reason

foreign = [
    "SalarySlip.list", "SalarySlip.get",
    "Employee.list", "Employee.get",
    "Payroll.list", "Payslip.list",
    "WorkOrder.list", "StockEntry.list",
    "Ticket.list", "EsignDocument.list",
    "Mailbox.list", "FormSubmission.list",
    "Lead.list", "Deal.list",  # crm — should be allowed, check
]

for tool in foreign:
    r = call_tool(tool, {"limit": 1})
    status = "LEAK" if not is_failure(r) else "OK"
    print(f"{status:5} {tool:30} {failure_reason(r) or ''}")
