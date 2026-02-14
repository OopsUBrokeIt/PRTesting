# Round 2 - PR Review Exercise

PR theme: bulk listing sync + outgoing status normalization.

## Intent
- Add a batched sync endpoint for multiple listing IDs.
- Normalize status values before calling Atlantis.

## Suggested review scope (15-20 min)
- API behavior and error semantics
- Status mapping correctness
- Edge cases for missing/duplicate listing IDs
- Test coverage for newly introduced logic
