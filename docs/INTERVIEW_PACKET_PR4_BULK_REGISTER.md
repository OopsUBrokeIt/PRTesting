# PR 4 - Bulk Listing Registration

## Summary
Add support for batch listing registration in a single request.

## Change
- Add `POST /register_listings`
- Add bulk request/response models
- Add basic API test coverage for the bulk endpoint

## Suggested review scope
- Input validation and limits
- Duplicate listing behavior
- Error semantics for partial success
- Performance and idempotency concerns
