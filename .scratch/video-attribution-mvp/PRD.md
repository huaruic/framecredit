# FrameCredit: Video Attribution MVP

Status: ready-for-agent

## Problem Statement

Video creators publish original teaching videos as native uploads on X. Other users can download those videos and upload them again as new posts without retaining the creator's name or enough information for viewers to find the original work. Ordinary platform reporting is slow and reactive, while manual evidence collection does not prevent the attribution from being lost in the first place.

Creators need a low-friction way to make their identity travel with the video itself. The goal is not to make copying technically impossible. The goal is to ensure that an ordinary download-and-reupload preserves a clear creator identity, and that removing the attribution requires deliberate cropping, covering, or damage to the video.

The first validation focuses on one creator workflow: a creator has a finished teaching video, publishes it as a native video on X, and may also have an existing YouTube version. The creator wants viewers of copied versions to identify the original X creator quickly and, when possible, find the original video using the creator identity and video title.

## Solution

FrameCredit is a local video-processing tool. A Creator configures their X display name and unique X handle once, then drops a Source Video into the application. FrameCredit produces an Attributed Export with a distributed Source Signature burned into the audiovisual content.

The Attributed Export keeps a compact Creator Marker visible throughout playback. The marker changes between safe positions at intervals instead of remaining in one crop-prone corner or moving continuously. A larger Source Card repeats at the beginning, middle, and end so that trimming either endpoint does not necessarily remove all attribution. The Source Card includes the Creator Identity and a human-readable Source Title that can help viewers find the original. An exact YouTube URL may be accepted as optional input, but exact-link display and QR codes are not required for the first validation.

All processing occurs on the creator's computer. FrameCredit does not upload the source video, depend on an X API, change the creator's native X upload workflow, or require a platform to preserve metadata. The core processing behavior is exposed through one end-to-end command so it can be tested independently and later consumed by a minimal drag-and-drop desktop interface.

The MVP succeeds when common download, re-encoding, light cropping, and caption-overlay workflows still leave the creator visibly identifiable in most tested outputs without materially obstructing the teaching content.

## User Stories

1. As a video creator, I want to configure my X identity once, so that I do not re-enter it for every video.
2. As a video creator, I want my X display name included in the attribution, so that viewers recognize my public creator identity.
3. As a video creator, I want my unique X handle included in the attribution, so that viewers can search for the correct account even when display names are duplicated.
4. As a video creator, I want to drag a finished video into a local tool, so that protecting a video adds only one simple step to my publishing workflow.
5. As a video creator, I want processing to happen locally, so that I do not wait for a large upload or entrust unpublished footage to a remote service.
6. As a video creator, I want FrameCredit to export a normal MP4, so that I can upload it to X exactly as I upload videos today.
7. As a video creator, I want attribution burned into the rendered frames, so that ordinary metadata stripping does not remove it.
8. As a video creator, I want a compact creator marker visible throughout the video, so that a copied clip normally retains my identity.
9. As a video creator, I want the marker to switch positions periodically, so that cropping one corner does not erase the attribution from the entire video.
10. As a video creator, I want marker movement to happen as discrete position changes, so that it does not distract viewers like a continuously moving overlay.
11. As a video creator, I want the marker to avoid the usual subtitle region when possible, so that it does not obscure teaching captions.
12. As a video creator, I want the marker to remain legible over light and dark backgrounds, so that complex footage does not hide my name.
13. As a video creator, I want the marker to occupy little visual space, so that attribution does not materially reduce the usefulness of the lesson.
14. As a video creator, I want a stronger source card at the beginning, so that viewers immediately see who made the video.
15. As a video creator, I want the source card repeated around the middle, so that removing the introduction does not remove every source clue.
16. As a video creator, I want the source card repeated at the end, so that viewers who finish the lesson receive a clear attribution reminder.
17. As a video creator, I want to provide a human-readable video title, so that copied-video viewers can search for the original work.
18. As a video creator, I want the title display to remain concise, so that long titles do not overwhelm the frame.
19. As a video creator, I want to provide an optional YouTube source URL, so that the tool has enough information for later exact-source enhancements.
20. As a video creator, I want exact links and QR codes to remain optional, so that they do not add visual complexity to every video.
21. As a video creator, I want the original audio to remain audible and synchronized, so that attribution processing does not damage the lesson.
22. As a video creator, I want the output duration to remain effectively unchanged except for explicitly approved source-card treatment, so that publishing schedules and captions remain usable.
23. As a video creator, I want the original aspect ratio preserved, so that the tool does not unexpectedly crop my teaching content.
24. As a video creator, I want the output to retain practical visual quality, so that creator attribution does not introduce unacceptable compression artifacts.
25. As a video creator, I want clear progress feedback during processing, so that I know the application is working on long videos.
26. As a video creator, I want a clear success result with the exported file location, so that I can immediately upload the Attributed Export.
27. As a video creator, I want understandable errors for unreadable or unsupported inputs, so that I know what to fix without inspecting logs.
28. As a video creator, I want existing output files handled safely, so that processing does not silently destroy a previous export.
29. As a video creator, I want to preview the configured creator identity before processing, so that a typo is not burned into a finished export.
30. As a video creator, I want the same creator identity applied consistently across videos, so that copied works build a recognizable source pattern.
31. As a viewer, I want to identify the creator within five seconds, so that I can distinguish an original creator from a re-uploader.
32. As a viewer, I want the creator handle to be readable at normal social-video size, so that attribution does not require zooming.
33. As a viewer, I want enough title information to search for the original video, so that I can reach the source even when the rendered text is not clickable.
34. As a viewer, I want attribution to be present without dominating the lesson, so that source transparency and viewing quality coexist.
35. As a Creator testing FrameCredit, I want to compare the Attributed Export with re-encoded copies, so that I can judge its Attribution Survival under Ordinary Reposts.
36. As a creator testing FrameCredit, I want to compare horizontal and lightly cropped renditions, so that I can understand the limits of the current marker positions.
37. As a product team, we want one end-to-end processing interface, so that the command-line harness and future desktop drop zone exercise the same behavior.
38. As a product team, we want common Light Transformations represented in the Validation Set, so that success is measured against real reposting behavior rather than pristine files.
39. As a product team, we want failures recorded per transformation, so that later improvements target observed weaknesses rather than hypothetical attacks.
40. As a product team, we want the MVP to avoid platform integrations, so that its value can be tested without waiting for X or YouTube cooperation.
41. As a product team, we want the MVP to avoid accounts and cloud storage, so that the first experiment remains focused on attribution survival.
42. As a product team, we want to distinguish human-visible attribution from machine-verifiable provenance, so that the first release is not burdened by C2PA, fingerprint databases, or invisible watermark infrastructure.
43. As a product team, we want to state that determined removal remains possible, so that the product does not promise absolute prevention of copying.
44. As a product team, we want an explicit 80% survival target across the agreed common transformations, so that the MVP has a falsifiable outcome.
45. As a product team, we want human observers to identify the creator within five seconds, so that legibility is validated rather than assumed.
46. As a product team, we want the creator's extra per-video interaction to remain under thirty seconds, so that the workflow is sustainable.
47. As a product team, we want ten representative teaching videos in the initial experiment, so that the marker is evaluated against varied footage rather than one ideal sample.
48. As a product team, we want visual obstruction reviewed on each sample, so that robustness does not come at the cost of unusable educational content.

## Implementation Decisions

- The product name is FrameCredit and the repository name is `framecredit`.
- The first feature is called the Video Attribution MVP.
- The MVP is local-first and does not require a remote account, remote video storage, or a platform API.
- The creator continues to upload the processed MP4 natively in an X post.
- The creator identity consists of an X display name and an X handle. The handle is the unique, searchable component.
- Creator identity is configured once and reused for subsequent exports.
- Each video accepts a human-readable source title. An existing YouTube URL may be captured as optional information, but exact-link recovery is secondary to visible creator identity.
- Attribution is burned into rendered video frames rather than relying on MP4 metadata.
- The persistent creator marker remains visible throughout normal playback.
- The marker changes between a small set of safe positions at intervals. It does not continuously travel across the screen.
- The position schedule distributes attribution across time and space so that one simple crop is less likely to remove every instance.
- A larger source card overlays existing footage at the beginning, around the middle, and at the end; it does not append time to the video.
- The default source card emphasizes creator identity and a searchable title. QR codes are disabled by default and are not required for the MVP.
- The application must preserve the input aspect ratio and retain synchronized audio.
- The output must be a broadly uploadable MP4. The exact video and audio codec choices remain a prototype decision and will be recorded in an ADR after validation.
- The minimal user-facing shape is a local drag-and-drop tool with creator settings, per-video title input, processing progress, and a clear export result.
- The processing engine exposes one end-to-end public command:

  `framecredit process <input> --creator-name <name> --x-handle <handle> --source-title <title> --output <output>`

- The desktop interface will consume the same processing boundary rather than implementing a separate rendering path.
- The first implementation should prefer a small number of deep modules: creator configuration, processing orchestration, source-signature schedule, and export reporting.
- The MVP promise is increased Attribution Survival for Ordinary Reposts, not prevention of every unauthorized copy.
- The initial validation targets common download, re-encoding, light cropping, and caption-overlay transformations.
- Decisions about FFmpeg packaging, desktop framework, operating-system support, font fallback, and hardware acceleration are intentionally deferred to the prototype and subsequent ADRs.

## Testing Decisions

- The highest and primary automated test seam is the end-to-end `framecredit process` command.
- Tests verify observable behavior through input and output media files. They do not assert internal filter graphs, command construction, private functions, or implementation-specific module calls.
- The first tracer test processes a small fixture video and verifies that a playable output file is produced successfully.
- Media-level assertions inspect the output through standard media probing rather than internal state.
- Automated behavior checks should cover:
  - output file existence and readability;
  - preserved aspect ratio;
  - duration within an explicitly documented tolerance;
  - presence and synchronization of audio when the input contains audio;
  - creator attribution present at representative beginning, middle, and ending timestamps;
  - creator marker positions differing across the configured schedule;
  - safe handling of existing output paths;
  - clear failure for unreadable or unsupported inputs.
- Visual assertions should operate on extracted frames from the public output. The exact strategy for confirming text visibility may use deterministic render-region comparisons in automated tests and human legibility review in the MVP experiment; brittle OCR is not assumed as the sole test oracle.
- Robustness validation uses ten representative teaching videos and generates common transformed renditions, including re-encoding, light horizontal or vertical cropping, and added caption overlays.
- The target is for at least 80% of agreed transformed renditions to retain a clearly visible creator identity.
- Human validation asks observers to identify the creator from a rendition within five seconds and to locate the likely original using the X identity and video title.
- Creator-workflow validation measures active per-video interaction time, targeting less than thirty seconds excluding media-processing time.
- Visual-quality review records whether the marker or source card materially obscures teaching content.
- The repository is new and contains no prior test patterns. The first tracer test will establish the preferred end-to-end media fixture convention.
- UI tests are not the primary behavior seam. A minimal smoke test may confirm that the drag-and-drop interface invokes the same processing command and reports its final result.

## Out of Scope

- Preventing all copying, screen recording, cropping, blurring, inpainting, or determined removal of attribution.
- DMCA complaints, legal evidence collection, copyright registration, or takedown automation.
- X, YouTube, or other social-platform API integrations.
- Replacing native X video uploads with link-only posts or embedded YouTube players.
- Cloud video upload, cloud processing, remote storage, user accounts, teams, billing, or subscriptions.
- A public creator registry or source-resolution service.
- Browser extensions that identify copied videos while browsing X.
- Invisible watermark encoding or decoding.
- Perceptual video or audio fingerprint databases.
- C2PA Content Credentials, signing certificates, or provenance repositories.
- Blockchain, NFTs, or decentralized ownership records.
- Default QR-code generation or a mandatory short-link service.
- Automatic web-wide detection of copied videos.
- Revenue sharing, licensing negotiation, or attribution enforcement against re-uploaders.
- Mobile applications.
- Full support for every video container, codec, aspect ratio, writing system, and operating system in the first validation.
- A polished multi-creator SaaS experience.
- A public marketing website.

## Further Notes

- Product positioning: "When the video is casually copied, the creator travels with it."
- The primary threat model is ordinary download-and-reupload plus light modifications. The product deliberately does not claim to defeat a motivated editor who is willing to damage or reconstruct the content.
- Human-visible attribution and machine-verifiable provenance solve different problems. FrameCredit starts with the former because the immediate success criterion is that viewers know the creator's name.
- A static corner watermark is insufficient because one crop can remove it. The core design principle is redundant attribution across time and space.
- Audio attribution, exact-link cards, optional QR codes, invisible watermarking, fingerprints, C2PA, and source lookup remain candidate follow-on layers only after the visible-attribution MVP is validated.
- The FrameCredit name has received only a lightweight collision search. Formal trademark and domain clearance are outside this PRD.
- After the PRD, stable product vocabulary should be captured in `CONTEXT.md`. Prototype-validated technical choices should be captured as ADRs rather than copied into `AGENTS.md`.
- The throwaway Source Signature prototype passed its synthetic feasibility check: the Creator Identity remained readable after heavy re-encoding, light cropping, and a bottom caption overlay. This is not a substitute for the ten-video Validation Set.
