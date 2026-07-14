# Distribute the Creator Marker across time and space

Status: completed

User stories: 9–13, 31, 32, 34

## What to build

Extend the public processing path so the compact Creator Marker remains present throughout normal playback while switching discretely between top-left, top-right, and centered safe positions. The schedule must distribute the Creator Identity across time and space without continuously moving or routinely occupying the subtitle region.

The prototype validated this three-position shape on synthetic footage. Production behavior may replace its fixed four-second interval with a duration-aware schedule, but the externally visible result must remain deterministic and testable.

## Acceptance criteria

- [x] The Creator Marker is visible throughout the Attributed Export outside explicitly documented transition boundaries.
- [x] The marker uses at least top-left, top-right, and centered positions during a representative video.
- [x] Position changes are discrete and do not animate continuously across the content.
- [x] The normal schedule avoids the lower subtitle region.
- [x] The Creator Identity remains readable over both light and dark sample backgrounds.
- [x] Extracted output frames confirm different positions at representative timestamps through the public processing seam.
- [x] The marker schedule is deterministic for the same duration and configuration.

## Blocked by

- `01-first-attributed-export.md`

## Manual validation constraints

The first real-video validation used a 61:42, 1278×826, 30 fps Source Video of
about 400 MB. CPU encoding completed in about 4 minutes 15 seconds (roughly
12–14× real-time), while the fixed top-left Creator Marker obscured browser
content and a long Creator Identity expanded into a banner.

Issue 03 therefore also keeps a long Creator Marker within 35% of the frame
width, uses a 12-second discrete interval, and must not materially regress the
observed encoding speed. A full-length rerun remains a manual validation step;
automated tests use short representative videos.

A local before/after benchmark used the same 38-second, 960×540, 24 fps sample
for three alternating runs of each implementation. The fixed-position median
was 1.92 seconds and the distributed-position median was 1.91 seconds, so no
short-sample regression was measurable. This does not replace the full-length
manual rerun.

## Comments

- Audit 2026-07-14: delivered in `1b26136` and validated on the real 61:42
  Source Video described above. The three-position layout and 12-second
  interval verified here were later superseded by Issue 04's two-corner
  30-second schedule; the extracted-frame and determinism tests now assert
  that schedule and pass as part of a fully green suite. User-story numbers
  refer to the pre-rewrite PRD.
