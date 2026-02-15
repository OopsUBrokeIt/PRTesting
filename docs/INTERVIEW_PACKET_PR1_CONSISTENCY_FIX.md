# PR 1 - Consistency Type Fix

## Summary
Fix consistency type values sent through the API.

## Change
- Replace invalid `WEAK` type usage with `EVENTUAL`
- Supported values are now `EVENTUAL` and `STRONG`
- Validate consistency at request boundaries
