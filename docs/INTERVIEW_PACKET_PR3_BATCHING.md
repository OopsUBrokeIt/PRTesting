# PR 3 - Atlantis Batching via Queue

## Summary
Move Atlantis sync calls from immediate single-item requests to batched requests.

## Change
- Add internal job queue for registration and listing-sync events
- Flush queue when enough jobs are queued or jobs become old enough
- Call Atlantis batch endpoint without changing external API routes
