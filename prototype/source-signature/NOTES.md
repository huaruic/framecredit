# Prototype Answer

Question: Does the simple Source Signature remain visibly attributable after ordinary re-encoding, light cropping, and a caption overlay?

Verdict: Passes the initial synthetic feasibility check.

## Observations

- The Attributed Export and all three transformed renditions remained playable H.264/AAC videos at 1280×720 and approximately 12 seconds.
- `小明 @xiaoming` remained readable at every sampled timestamp after heavy re-encoding.
- A 10% horizontal and 5% vertical crop pushed the edge marker close to the frame boundary, but the text remained readable; the centered marker and repeated Source Card provided spatial fallback.
- The added bottom caption bar did not obscure the top or centered Creator Marker.
- The repeated Source Card was clearly readable after every tested transformation.
- The Source Card is visually dominant, which is acceptable for its short 1.5-second windows but should be reviewed on real teaching footage.

## Decision

Proceed with the simple visible-attribution MVP: a persistent Creator Marker that switches between top-left, top-right, and centered positions, plus Source Cards at the beginning, middle, and end.

This prototype proves technical feasibility only. It does not satisfy the product validation target until ten representative teaching videos and the agreed transformations have been reviewed.

Keep only the validated decision from this prototype. Delete or absorb the throwaway code after the decision is recorded in the PRD or an ADR.
