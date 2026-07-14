# FrameCredit

FrameCredit is a creator-side tool that burns visible attribution into a video
before it is uploaded to X. If the video is downloaded and reposted, the copied
video still shows who made it.

The MVP command adds a compact Creator Marker containing the Creator's X
display name and handle. The marker switches discretely every 12 seconds
between top-left, top-right, and upper-center positions so one part of the
Source Video is not permanently obscured:

```bash
python3 -m pip install -e .
framecredit process input.mp4 \
  --creator-name "小明" \
  --x-handle "@xiaoming" \
  --output attributed.mp4
```

FrameCredit requires `ffmpeg` and `ffprobe` on `PATH`.

For this first MVP, an Attributed Export keeps the source dimensions and audio
track, uses H.264 video with AAC audio for broad upload compatibility, and keeps
the duration within 150 milliseconds of the source.

## Local drag-and-drop app

Start the local interface after installing the package:

```bash
framecredit app
```

FrameCredit opens a browser window where the Creator can save their Creator
Identity, preview the Creator Marker, and drag in a Source Video. The interface
listens only on `127.0.0.1`; the Source Video is streamed to the FrameCredit
process on the same computer and is never sent to a remote service. Attributed
Exports are written to `~/Movies/FrameCredit` by default and can be opened from
the result panel.

Keep the terminal process running while using the interface. Press `Ctrl+C` to
stop it.
