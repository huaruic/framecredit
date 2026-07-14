# Minimize the Creator Marker around the X handle

Status: ready-for-agent

User stories: 2, 3, 13, 31, 32

## What to build

Replace the large bilingual Creator Marker with a compact, English-first marker
that carries the Creator's unique X handle. The rendered marker reads
`X · @handle` on one line, uses outlined text instead of an opaque card, and
switches discretely between the two top corners every 30 seconds.

The local interface is English and asks only for the X handle needed by the
Attributed Export. Display names, Source Cards, Source Titles, QR codes, links,
and clickable video regions are outside this MVP slice.

## Acceptance criteria

- [x] The public processing command requires an X handle but no display name.
- [x] The local interface stores and previews one X handle and is fully English.
- [x] The Creator Marker contains only `X · @handle` on one line.
- [x] The Creator Marker uses transparent outlined text without an opaque panel.
- [x] The visible marker remains compact on horizontal and small sample videos.
- [x] The marker remains readable on light and dark sample footage.
- [x] The marker alternates discretely between top-left and top-right every 30 seconds.
- [x] Extracted output frames confirm both positions through the public processing seam.
- [x] The Attributed Export keeps the Source Video's dimensions, duration, and audio.
- [x] No Source Card, Source Title, QR code, platform API, or clickable hotspot is added.

## Blocked by

- `01-first-attributed-export.md`
- `02-local-drop-zone.md`
- `03-distributed-creator-marker.md`

## Comments

- The prior Source Card proposal was replaced after real-video validation showed
  that the persistent two-line card obscured browser and teaching content.
- A burned-in marker is video pixels and cannot carry an X click target. The X
  handle remains human-readable and searchable after an ordinary repost.
- Automated verification passes 11 tests, including the required Playwright
  browser workflow and extracted-frame checks through the public command.
- A 65-second clip from the 1278×826 real Source Video processed in 4.59 seconds.
  The 8 MB Attributed Export retained H.264 video, AAC audio, dimensions, and
  duration. Frames at 3, 31, and 61 seconds confirmed left, right, left.
