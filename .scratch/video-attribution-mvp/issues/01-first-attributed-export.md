# Generate the first Attributed Export

Status: completed

User stories: 2, 3, 6, 7, 8, 21–24, 26, 37

## What to build

Deliver the first complete path through FrameCredit's public processing seam. Given a valid Source Video, Creator display name, X handle, and output location, `framecredit process` produces a playable MP4 with a fixed, visible Creator Marker. The command is the product's primary behavior boundary and must be usable by later interfaces without a second rendering path.

Use the throwaway Source Signature prototype only as evidence that overlay rendering is feasible. Do not promote the prototype shell or its hard-coded media settings into production unchanged.

## Acceptance criteria

- [x] A valid Source Video can be processed through the public `framecredit process` command.
- [x] The command accepts a Creator display name, X handle, input path, and output path.
- [x] A successful run produces a broadly uploadable, playable MP4 containing a visible Creator Marker.
- [x] The Attributed Export preserves the Source Video's aspect ratio, synchronized audio when present, and duration within a documented tolerance.
- [x] The command reports success and the final output location.
- [x] One end-to-end test invokes the public command and verifies the observable output media behavior.
- [x] Internal FFmpeg arguments, private functions, and filter construction are not used as test assertions.

## Blocked by

None - can start immediately.

## Comments

- Audit 2026-07-14: delivered in `a84c38b` and verified through the
  end-to-end command test, which now passes as part of a fully green suite.
  Two details were later superseded by Issue 04: the command no longer
  accepts a Creator display name (the Creator Identity is one X handle), and
  the fixed marker position was replaced by the alternating 30-second
  two-corner schedule. User-story numbers refer to the pre-rewrite PRD.
