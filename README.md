# PR Review Practice Repo

This repository contains timed PR-review practice exercises.

## Round Layout
- `main`: clean baseline implementation.
- Practice branches: intentionally imperfect changes for review.

## Baseline Service
The baseline app mirrors the Airbnb listing-status prompt and exposes:
- `POST /register_listing`
- `GET /get_status/{listing_id}`
- `POST /sync_listing/{listing_id}`
