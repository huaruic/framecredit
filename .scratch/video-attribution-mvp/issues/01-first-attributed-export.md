# Generate the first Attributed Export

Status: ready-for-agent

User stories: 2, 3, 6, 7, 8, 21–24, 26, 37

## What to build

Deliver the first complete path through FrameCredit's public processing seam. Given a valid Source Video, Creator display name, X handle, and output location, `framecredit process` produces a playable MP4 with a fixed, visible Creator Marker. The command is the product's primary behavior boundary and must be usable by later interfaces without a second rendering path.

Use the throwaway Source Signature prototype only as evidence that overlay rendering is feasible. Do not promote the prototype shell or its hard-coded media settings into production unchanged.

## Acceptance criteria

- [ ] A valid Source Video can be processed through the public `framecredit process` command.
- [ ] The command accepts a Creator display name, X handle, input path, and output path.
- [ ] A successful run produces a broadly uploadable, playable MP4 containing a visible Creator Marker.
- [ ] The Attributed Export preserves the Source Video's aspect ratio, synchronized audio when present, and duration within a documented tolerance.
- [ ] The command reports success and the final output location.
- [ ] One end-to-end test invokes the public command and verifies the observable output media behavior.
- [ ] Internal FFmpeg arguments, private functions, and filter construction are not used as test assertions.

## Blocked by

None - can start immediately.
