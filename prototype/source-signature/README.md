# PROTOTYPE — Source Signature

Run the interactive prototype:

```bash
python3 prototype/source-signature/prototype.py
```

## Question

Can a simple Source Signature — a persistent Creator Marker that changes position plus repeated Source Cards — keep `小明 @xiaoming` visibly attributable after ordinary re-encoding, light cropping, and a caption overlay?

This is throwaway code. It exists only to answer that question and must not become the production processing engine.

## What it generates

- a synthetic 12-second Source Video;
- an Attributed Export;
- a heavily re-encoded rendition;
- a lightly cropped rendition;
- a rendition with an added caption bar;
- a contact sheet comparing four timestamps across every rendition.

The prototype uses Python, the locally installed FFmpeg/FFprobe, and the already available Pillow package only to create temporary text overlays. No package manager or application framework is introduced.

For a non-interactive run:

```bash
python3 prototype/source-signature/prototype.py --generate --output /tmp/framecredit-prototype
```

## Controls

- `g` — generate all artifacts
- `n` — select the next rendition
- `o` — open the selected rendition
- `c` — open the contact sheet
- `q` — quit and delete temporary artifacts
