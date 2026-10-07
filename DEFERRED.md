# Deferred work

Items not completed, and why. Kept visible so progress is honest.

## Agent

### Top-N limited to 3

`answer_a17` processes the first three expiring contracts for playbook
review and obligation checks (`top_n=3`). Extending to all 16 is a
parameter change, not new code.

### Dynamic planning

The agent uses a fixed plan. A dynamic planner (deciding the next step
based on state) was considered and rejected: the A17 request is
well-defined, and planning adds cost without changing the answer.

## Harness

### Keystone (US instance) not tested

The platform has two businesses — Suryodaya (India) and Keystone (US).
All harness tasks run against Suryodaya.

**Why:** Keystone requires a separate password for the same team account.
Not available for automated testing.

**To add:** a task that logs in to
`class.agentswitch.theschoolofai.in` and runs `Contract.list`.

### More coverage possible

12 tasks cover the main behavior classes. Additional candidates:

- Pagination boundary at `offset=999999`
- `Contract.get` with malformed UUID
- `tools.describe` on a foreign tool
- Obligation workflow transitions

None are required by the spec.

## Tests

18 hand-written tests covering all 9 filed bugs. No gaps.

## Notes on the platform

Two test deviations remain in `pending_approval` state. They cannot be
withdrawn from this seat — the withdraw tool only accepts `draft`.
Documented in `BUGS.md`.
