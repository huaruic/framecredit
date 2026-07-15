# Changelog

## 0.1.1 - 2026-07-15

- `framecredit app` now explains that the port is busy and suggests
  `--port` instead of crashing with a traceback when the address is
  already in use.

## 0.1.0 - 2026-07-15

First public release, licensed under AGPL-3.0-or-later.

- `framecredit process`: burn a compact outlined `X · @handle` Creator Marker
  into a video from the command line. H.264/AAC MP4 output that keeps the
  source dimensions, duration, and audio.
- `framecredit app`: local drag-and-drop web interface on 127.0.0.1 with a
  saved X handle, a real first-frame marker preview, and one-click export.
  Footage never leaves the machine.
- The marker alternates between the two top corners every 30 seconds so no
  region of the video is permanently covered.
- X handle validation and normalization (optional leading `@`, 1-15 letters,
  numbers, or underscores) shared by the CLI and the app.
- Safe failure behavior: still images and unreadable files are rejected with
  actionable errors, existing outputs are never silently overwritten, and
  failed encodes never leave partial files behind.
