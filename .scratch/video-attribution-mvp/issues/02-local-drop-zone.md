# Export through a local drop zone

Status: completed

User stories: 1, 4, 5, 25, 26, 29, 30, 37, 40, 41

## What to build

Deliver the smallest local user journey around the existing processing command. A Creator configures their X display name and handle, previews that Creator Identity, drops a Source Video into the application, sees processing progress, and receives the Attributed Export location. Processing stays on the Creator's computer and invokes the same public processing seam as the command-line workflow.

This slice is functional rather than polished. It must not introduce accounts, cloud storage, uploads, billing, or a second rendering implementation.

## Acceptance criteria

- [x] A Creator can configure and locally retain an X display name and handle for later sessions.
- [x] The configured Creator Identity is shown for confirmation before processing.
- [x] A Source Video can be selected through a minimal local drop-zone interaction.
- [x] The application shows meaningful progress while processing is active.
- [x] A successful run presents the Attributed Export location and makes the file easy to open.
- [x] The user journey invokes the same processing boundary established by issue 01.
- [x] No Source Video or Attributed Export is uploaded to a remote service.
- [x] A smoke test verifies that the local interface can invoke processing and report its result.

## Blocked by

- `01-first-attributed-export.md`

## Comments

- Audit 2026-07-14: delivered in `c3cbe06` and verified through the local-app
  and browser workflow tests, which now pass as part of a fully green suite.
  The X display name configured here was later removed intentionally by
  Issue 04: the saved Creator Identity is now only the X handle, and identity
  files from the earlier shape still load their handle cleanly. User-story
  numbers refer to the pre-rewrite PRD.
