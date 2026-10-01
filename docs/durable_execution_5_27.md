# Berkios 5.27 — Durable Execution, Approval & Live State

5.27 connects the persistence layer introduced in 5.26 to the execution runtime.

## Durable execution
`ExecutionController` now persists run snapshots and execution events.
On runtime startup, persisted execution runs are restored when their serialized
state is available.

## Durable approvals
`ApprovalManager` persists approval requests and decisions and restores them
when a runtime starts.

## Shared runtime services
`AgentRuntime` now caches:
- one persistence service
- one execution controller
- one approval center
- one live bridge

This prevents the previous problem where calling a factory repeatedly created
disconnected in-memory controllers.

## iBook live bridge
iBook continues to use the live bridge, but the bridge can now fall back to
durable event storage.

## API
- `POST /v1/persistence/runs`
- `POST /v1/persistence/events`

These are inspection endpoints; execution authorization remains controlled by
the normal Berkios approval/permission system.

## Limitation
Existing historical agent loops remain independent from the new execution
controller. This release makes the 5.x execution/approval/live path durable
without pretending that every legacy in-memory subsystem has been migrated.
