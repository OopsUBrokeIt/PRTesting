# System Pre-Read: StreamCart Subscription Service

## Product Context
StreamCart sells monthly and annual subscriptions to creators. Customers can pause, resume, and cancel plans from self-serve settings. Revenue reporting depends on accurate subscription status and payment retries.

## Business Requirements
- Create a subscription for a customer and charge the initial invoice.
- Support pause/resume by date range for temporary holds.
- Retry failed renewals up to 3 attempts before marking `past_due`.
- Expose an operations endpoint to trigger retry worker manually.
- Emit billing events to Analytics service for reporting.

## API Surface
- `POST /v1/subscriptions` create subscription and initial charge.
- `POST /v1/subscriptions/{id}/pause` pause an active subscription.
- `POST /v1/subscriptions/{id}/resume` resume a paused subscription.
- `POST /v1/workers/retry-failed-charges` force retry run.
- `GET /v1/subscriptions/{id}` fetch current state.

## External Dependencies
- `PayFlow` API for charge/renewal operations.
- PostgreSQL (simulated by repository module in this exercise).
- Internal Analytics collector (`/v1/events`) for lifecycle events.

## Constraints
- PayFlow rate limit: 40 requests/sec per key.
- Subscription status is eventually consistent with async retries.
- Retry worker runs every 10 minutes.
- Pause window max: 90 days.
- Manual worker trigger should return quickly and run work in background.

---

# PR Description: Add Pause/Resume + Failed Charge Retry Worker

## Problem
Customer support receives many tickets for temporary suspensions and failed renewals. Today, users can only cancel, and failed renewals are manually retried by operations.

## Proposed Change
- Add pause and resume endpoints.
- Add failed charge retry worker and manual trigger endpoint.
- Track retry metadata on subscriptions.
- Emit analytics events for pause/resume/retry outcomes.

## Tradeoffs
- Implemented worker logic in service process for faster delivery instead of separate worker deployment.
- Retry logic currently scans all subscriptions in memory/repository each run.
- Added minimal event payload to analytics to avoid schema migration in reporting.

## Testing Notes
- Added a small unit test file for pause flow and retry worker.
- Integration tests are not included in this PR.
