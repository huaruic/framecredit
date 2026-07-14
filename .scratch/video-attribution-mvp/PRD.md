# FrameCredit: Video Attribution MVP

Status: ready-for-agent

## Problem Statement

Video creators publish original teaching videos as native uploads on X. Other
people can download those videos and upload them again as new posts without
retaining enough information for viewers to find the Creator.

FrameCredit does not try to make copying impossible. It makes the Creator's X
identity travel with an Ordinary Repost while keeping the teaching content
useful. Determined Removal by cropping, covering, or reconstructing frames
remains possible and is outside the MVP promise.

## Solution

FrameCredit is a local video-processing tool. A Creator saves their unique X
handle once and drops in a Source Video. FrameCredit produces an Attributed
Export with a compact Creator Marker burned into the frames.

The marker reads `X · @handle` so viewers know both the platform and the
searchable account. It remains visible during normal playback, alternates
discretely between the top corners every 30 seconds, and uses transparent
outlined text instead of an opaque card. A normal native X video cannot carry a
Creator-defined clickable region, so clickable hotspots, QR codes, and exact
links are not part of this validation.

All processing occurs on the Creator's computer. FrameCredit does not upload
the Source Video, depend on an X API, change the native X publishing workflow,
or require a platform to preserve metadata.

The MVP succeeds when Ordinary Reposts retain a readable X identity without
materially obstructing teaching content.

## User Stories

1. As a Creator, I want to save my X handle once, so that I do not re-enter it for every Source Video.
2. As a Creator, I want the marker to identify X explicitly, so that viewers do not have to guess which platform the handle belongs to.
3. As a Creator, I want my unique X handle burned into rendered frames, so that metadata stripping does not remove it.
4. As a Creator, I want to drag a finished video into a local tool, so that attribution adds one simple publishing step.
5. As a Creator, I want processing to happen locally, so that unpublished footage is not sent to a remote service.
6. As a Creator, I want a normal MP4 Attributed Export, so that I can upload it to X exactly as I do today.
7. As a Creator, I want a compact marker visible throughout playback, so that an Ordinary Repost normally retains my identity.
8. As a Creator, I want discrete position changes, so that the marker does not move continuously or remain in one corner forever.
9. As a Creator, I want the marker to avoid the subtitle region, so that teaching captions remain useful.
10. As a Creator, I want outlined text that remains readable over light and dark footage without an opaque card.
11. As a Creator, I want the marker to occupy little visual space, so that it does not materially obscure the lesson.
12. As a Creator, I want original dimensions, duration, audio synchronization, and practical visual quality preserved.
13. As a Creator, I want clear progress, success, and error feedback during local processing.
14. As a Creator, I want existing output files handled safely, so that repeated processing does not destroy earlier exports.
15. As a Creator, I want to preview the exact X identity before processing, so that a typo is not burned into a long export.
16. As a viewer, I want to identify and search for the Creator within five seconds at normal social-video size.
17. As a product team, we want one end-to-end processing interface shared by the command and local app.
18. As a product team, we want the MVP to avoid accounts, cloud storage, platform integrations, Source Cards, and provenance infrastructure.
19. As a product team, we want to distinguish visible attribution from machine-verifiable provenance.
20. As a product team, we want visual obstruction and Attribution Survival measured on representative teaching videos.

## Implementation Decisions

- The product and repository name are `FrameCredit` and `framecredit`.
- Creator Identity consists of one unique X handle and is displayed as `X · @handle`.
- The UI is English-first for overseas X Creators.
- The Creator Marker is transparent outlined text with no opaque panel.
- The marker alternates between top-left and top-right every 30 seconds.
- The Creator Marker is burned into frames rather than stored as metadata.
- The Source Video's aspect ratio, duration, and synchronized audio are preserved.
- The output is a broadly uploadable MP4.
- The local interface and command consume the same processing seam.
- The public command is:

  `framecredit process <input> --x-handle <handle> --output <output>`

- The MVP promise is Attribution Survival under Ordinary Reposts, not prevention of every unauthorized copy.

## Testing Decisions

- The primary automated seam is the end-to-end `framecredit process` command.
- Tests inspect public output media rather than private FFmpeg command construction.
- Automated behavior checks cover output readability, dimensions, duration,
  audio, visible attribution, compact marker bounds, light/dark contrast, the
  30-second position schedule, and safe failure behavior.
- UI smoke tests confirm the English handle-only workflow invokes the same
  processing path and reports elapsed time and the output location.
- A short real-video sample is used before reprocessing a full-length Source Video.
- Human validation confirms that the X handle is recognizable within five
  seconds and the marker does not materially obstruct teaching content.

## Out of Scope

- Preventing screen recording, cropping, blurring, inpainting, or Determined Removal.
- Clickable regions inside native X video frames.
- Source Cards, Source Titles, end cards, exact-source links, or QR codes.
- X, YouTube, or other platform APIs.
- Cloud processing, remote storage, accounts, teams, billing, or subscriptions.
- Invisible watermarking, perceptual fingerprint databases, C2PA, or provenance repositories.
- Web-wide copied-video detection, legal complaints, or takedown automation.
- A public registry, browser extension, mobile app, or polished SaaS.

## Further Notes

- Product positioning: "When the video is casually copied, the Creator travels with it."
- `@handle` alone is compact but platform-ambiguous; the `X ·` prefix removes that ambiguity.
- A burnt-in marker is pixels, not a hyperlink. A mention becomes clickable only
  when it appears in X post text, which an independently re-uploaded file cannot preserve.
- Human-visible attribution and machine-verifiable provenance remain separate product layers.
