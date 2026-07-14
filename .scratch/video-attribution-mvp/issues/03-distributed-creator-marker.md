# Distribute the Creator Marker across time and space

Status: ready-for-agent

User stories: 9–13, 31, 32, 34

## What to build

Extend the public processing path so the compact Creator Marker remains present throughout normal playback while switching discretely between top-left, top-right, and centered safe positions. The schedule must distribute the Creator Identity across time and space without continuously moving or routinely occupying the subtitle region.

The prototype validated this three-position shape on synthetic footage. Production behavior may replace its fixed four-second interval with a duration-aware schedule, but the externally visible result must remain deterministic and testable.

## Acceptance criteria

- [ ] The Creator Marker is visible throughout the Attributed Export outside explicitly documented transition boundaries.
- [ ] The marker uses at least top-left, top-right, and centered positions during a representative video.
- [ ] Position changes are discrete and do not animate continuously across the content.
- [ ] The normal schedule avoids the lower subtitle region.
- [ ] The Creator Identity remains readable over both light and dark sample backgrounds.
- [ ] Extracted output frames confirm different positions at representative timestamps through the public processing seam.
- [ ] The marker schedule is deterministic for the same duration and configuration.

## Blocked by

- `01-first-attributed-export.md`
