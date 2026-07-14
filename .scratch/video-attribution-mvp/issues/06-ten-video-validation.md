# Validate Attribution Survival on ten teaching videos

Status: ready-for-human

User stories: 31–36, 38–48

## What to build

Run the completed MVP against a Validation Set of ten representative teaching videos. For every Attributed Export, create the agreed Ordinary Repost renditions: a re-encoded copy, a lightly cropped copy, and a copy with an added caption overlay. Record Attribution Survival, five-second Creator recognition, active Creator interaction time, and whether the Source Signature materially obscures teaching content.

This is a product validation exercise, not an expansion of the rendering feature. Failures should become evidence for a narrowly scoped follow-up rather than being hidden by changing the target after the experiment.

## Acceptance criteria

- [ ] Ten representative teaching Source Videos are supplied and described.
- [ ] Every Source Video is processed through the same local workflow used by Creators.
- [ ] Re-encoded, lightly cropped, and caption-overlay renditions are generated for every Attributed Export.
- [ ] At least 80% of the agreed transformed renditions retain a clearly readable Creator Identity, or the MVP is explicitly recorded as failing this target.
- [ ] Human observers attempt to identify the Creator within five seconds from representative renditions.
- [ ] Human observers attempt to locate the likely Creator using the X handle.
- [ ] Active per-video Creator interaction time is recorded and compared with the thirty-second target.
- [ ] Visual obstruction is reviewed and recorded for every Source Video.
- [ ] Results, failures, and the resulting go/no-go decision are saved with the Validation Set report.

## Blocked by

- `02-local-drop-zone.md`
- `03-distributed-creator-marker.md`
- `04-compact-x-handle-marker.md`
- `05-safe-errors-and-outputs.md`

## Comments

- Audit 2026-07-14: not started as an experiment. Only one real Source Video
  (a 61:42 teaching video, plus a 65-second clip of it) has been validated end
  to end; the ten-video Validation Set, the transformed renditions, and the
  observer measurements have not begun. Remains blocked on Issues 04 and 05.
  User-story numbers refer to the pre-rewrite PRD.
