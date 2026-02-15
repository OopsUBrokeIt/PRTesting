# PR 5 - Bulk Status Fetch

## Summary
Add a bulk endpoint for fetching statuses for multiple listing IDs.

## Change
- Add `POST /get_statuses`
- Add request/response models for bulk status retrieval
- Add one API test for mixed found/missing IDs

## Suggested review focus
- Missing-ID handling semantics
- Input validation and max payload size
- Duplicate IDs and ordering behavior
- Test coverage gaps for edge cases
