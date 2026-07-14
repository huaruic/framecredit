# Handle processing errors and output files safely

Status: ready-for-agent

User stories: 27, 28

## What to build

Make the complete local workflow safe enough for repeated MVP use. Unreadable or unsupported Source Videos produce understandable failures, processing failures propagate through the public boundary, and an existing output is never overwritten without an explicit user decision. The command and local drop zone must communicate the same failure meaning in forms appropriate to their interfaces.

## Acceptance criteria

- [x] An unreadable input fails without creating a misleading successful output.
- [ ] An unsupported input produces an actionable message rather than raw internal diagnostics alone.
- [x] The command exits unsuccessfully when processing fails.
- [x] The local interface shows the failure and allows the Creator to try another Source Video.
- [ ] An existing output file is not silently overwritten.
- [ ] Temporary or partial outputs are not presented as completed Attributed Exports.
- [ ] End-to-end tests cover unreadable input, unsupported input, and an existing output path through public interfaces.

## Blocked by

- `02-local-drop-zone.md`

## Comments

- Audit 2026-07-14, verified against actual behavior:
  - Verified — unreadable input: a garbage `.mp4` fails before any output is
    written (`framecredit process` printed `could not read the source video`,
    exited 1, and created no output file; guard order in
    `src/framecredit/processing.py:32-36`, error mapping in
    `processing.py:75-93`).
  - Verified — command exits unsuccessfully: `ProcessingError` is caught and
    mapped to exit code 1 in `src/framecredit/cli.py:45-47`; confirmed by the
    run above and by `tests/test_process_command.py:36-63`.
  - Verified — local interface failure path: `POST /api/process` with an
    unreadable body returned HTTP 400 with the same error text and wrote
    nothing to the output directory (`src/framecredit/local_app.py:205-210`);
    the page shows `Processing failed: …` and re-enables the process button
    and drop zone for another Source Video
    (`src/framecredit/static/index.html:516-523`).
  - Not verified — unsupported input: a PNG image passed as input is accepted,
    exits 0, and produces a one-frame MP4 announced as a completed Attributed
    Export instead of an actionable failure (`_video_dimensions` only checks
    that ffprobe finds a video stream, `processing.py:75-93`).
  - Not verified — existing output: the local app avoids collisions with a
    numbered suffix (`local_app.py:263-272`, covered by
    `tests/test_local_app.py:262-284`), but the CLI passes `-y` to ffmpeg
    (`processing.py:212`) and silently overwrote a pre-existing output file
    with exit 0 in a real run.
  - Not verified — partial outputs: ffmpeg writes directly to the final output
    path with no temp-then-rename (`processing.py:245`), so a failed encode
    can leave a partial file at the completed-export name.
  - Not verified — test coverage: only the existing-output path through the
    local app is tested; no end-to-end tests exist for unreadable or
    unsupported input through either public interface.
- User-story numbers refer to the pre-rewrite PRD.
