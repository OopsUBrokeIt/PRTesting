# Round 3 - PR Review Exercise

PR theme: sync retries + lightweight audit trail.

## Intent
- Add retry behavior for outbound listing sync calls.
- Persist sync attempts in an in-memory audit log.
- Expose a read endpoint for recent sync audits.

## Suggested review scope (15-20 min)
- Retry semantics and correctness
- Error handling and status reporting
- Audit data integrity
- Missing edge-case test coverage
