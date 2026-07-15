# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

FrameCredit burns visible creator attribution into videos before upload to X, so reposted copies still show who made them. Local-only Python tool: a CLI (`framecredit process`) and a local drag-and-drop web app (`framecredit app`).

## Commands

```bash
python3 -m pip install -e .        # install (a .venv exists at repo root)
python3 -m unittest                 # run all tests (stdlib unittest, no pytest)
python3 -m unittest tests.test_marker_schedule                       # one module
python3 -m unittest tests.test_process_command.ProcessCommandTest    # one class
```

Requires `ffmpeg` and `ffprobe` on PATH — most tests skip without them.

Run the app: `framecredit app` (serves on 127.0.0.1:8765; `--no-browser` to skip opening a browser).

## Architecture

Source lives in `src/framecredit/` — three modules, stdlib + Pillow only (ffmpeg/ffprobe are external commands, never Python bindings):

- `cli.py` — argparse entry point (`process` and `app` subcommands).
- `processing.py` — the core pipeline: Pillow renders the Creator Marker as a PNG (auto-sizes font, wraps to two lines, then ellipsizes for narrow videos), then ffmpeg overlays it with a time-based position expression that moves the marker between three positions every `MARKER_INTERVAL_SECONDS` (12s). Output is always H.264/AAC MP4. User-facing failures raise `ProcessingError`.
- `local_app.py` — stdlib `http.server` app bound to 127.0.0.1 only (privacy guarantee: video never leaves the machine). Serves `static/index.html`, persists Creator Identity as JSON under a platform-specific app home (`FRAMECREDIT_HOME` env var overrides — tests use this). Exports default to `~/Movies/FrameCredit`.

`build/` is stale setuptools output — never edit it.

## Domain vocabulary

`CONTEXT.md` at the repo root defines the ubiquitous language (Creator, Creator Identity, Creator Marker, Source Signature, Attributed Export, Attribution Survival, …) plus Chinese UI translations. Use these exact terms in code, docs, and UI; each entry lists rejected synonyms (e.g. say "Creator Marker", never "watermark") — don't drift to them.

## Repo conventions (from AGENTS.md)

- Issues and PRDs are local Markdown under `.scratch/<feature-slug>/` (`PRD.md` + `issues/NN-slug.md` with a `Status:` line). External PRs are not a triage surface.
- Architectural decisions go in `docs/adr/`; flag conflicts with existing ADRs explicitly instead of silently overriding.
