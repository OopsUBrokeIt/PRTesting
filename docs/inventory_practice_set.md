# System Pre-Read: FulFillNow Inventory Reservation Service

## Product Context
FulFillNow processes ecommerce orders across multiple warehouses. Checkout reliability depends on inventory reservations: items should be held for a short window before payment capture. If holds are stale or payment fails, inventory should be released.

## Business Requirements
- Reserve SKU quantities for an order at checkout.
- Confirm reservation after payment capture.
- Release reservation on timeout or explicit cancel.
- Reconcile stale reservations every 5 minutes.
- Notify downstream Warehouse Gateway on confirm/release.

## API Surface
- `POST /v1/reservations` create reservation for order lines.
- `POST /v1/reservations/{id}/confirm` confirm reservation after payment.
- `POST /v1/reservations/{id}/release` manually release reservation.
- `GET /v1/reservations/{id}` read reservation state.
- `POST /v1/workers/reconcile-stale` trigger stale reconciliation.

## External Dependencies
- Warehouse Gateway (`/v1/inventory/holds`) for physical hold updates.
- PostgreSQL-backed stock service (simulated repository in this exercise).
- Event bus publisher for analytics/auditing.

## Constraints
- Warehouse Gateway rate limit: 60 req/s.
- Reservation TTL: 15 minutes.
- Reconcile worker should be non-blocking for API trigger.
- Consistency: eventual between local state and warehouse updates.
- Idempotency expected for confirm/release endpoints.

---

# PR Description: Add Reservation Confirm/Release + Stale Reconciliation Worker

## Problem
We currently create reservations but rely on manual operations to clean stale holds and resolve payment failures. This causes oversell risk and delayed inventory recovery.

## Proposed Change
- Add confirm/release endpoints for reservation lifecycle.
- Add stale reconciliation worker with manual trigger endpoint.
- Emit reservation events (`created`, `confirmed`, `released`, `reconciled`).
- Persist retry metadata on warehouse sync attempts.

## Tradeoffs
- Implemented worker in API process for quicker rollout.
- Lifecycle events have minimal payload to avoid schema updates in analytics.
- Current reconciliation scans all reservations each run.

## Testing Notes
- Added initial tests for create + release paths.
- No load tests or end-to-end worker tests in this PR.

---

# Follow-up PR Description: Add Idempotent Reservation Creates + Limited Reconcile Trigger

## Problem
Operations reported duplicate reservations during checkout retries and reconcile runs taking too long under peak load.

## Proposed Change
- Add optional `idempotency_key` to create reservation endpoint.
- Add `source` and `release_reason` metadata to reservation model.
- Add `limit` and `dry_run` parameters to reconcile trigger.
- Add repository lookup by idempotency key.

## Tradeoffs
- Idempotency implemented in repository memory index for faster rollout.
- Reconcile limit is caller-provided to support ad-hoc operations.
- Dry-run path reuses same endpoint shape as production trigger.

## Testing Notes
- Added test for idempotent create behavior.
- Worker integration and concurrency tests are not included.
