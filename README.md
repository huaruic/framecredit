# FrameCredit

FrameCredit is a creator-side tool that burns visible attribution into a video
before it is uploaded to X. If the video is downloaded and reposted, the copied
video still shows who made it.

The first MVP command adds a fixed Creator Marker containing the creator's X
display name and handle:

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
