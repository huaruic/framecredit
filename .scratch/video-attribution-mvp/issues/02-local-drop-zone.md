# Export through a local drop zone

Status: ready-for-agent

User stories: 1, 4, 5, 25, 26, 29, 30, 37, 40, 41

## What to build

Deliver the smallest local user journey around the existing processing command. A Creator configures their X display name and handle, previews that Creator Identity, drops a Source Video into the application, sees processing progress, and receives the Attributed Export location. Processing stays on the Creator's computer and invokes the same public processing seam as the command-line workflow.

This slice is functional rather than polished. It must not introduce accounts, cloud storage, uploads, billing, or a second rendering implementation.

## Acceptance criteria

- [ ] A Creator can configure and locally retain an X display name and handle for later sessions.
- [ ] The configured Creator Identity is shown for confirmation before processing.
- [ ] A Source Video can be selected through a minimal local drop-zone interaction.
- [ ] The application shows meaningful progress while processing is active.
- [ ] A successful run presents the Attributed Export location and makes the file easy to open.
- [ ] The user journey invokes the same processing boundary established by issue 01.
- [ ] No Source Video or Attributed Export is uploaded to a remote service.
- [ ] A smoke test verifies that the local interface can invoke processing and report its result.

## Blocked by

- `01-first-attributed-export.md`
