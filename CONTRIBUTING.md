# Contributing to FrameCredit

Thanks for helping creators keep credit for their work.

## Development setup

```bash
git clone https://github.com/huaruic/framecredit.git
cd framecredit
python3 -m venv .venv
.venv/bin/pip install -e .
```

Requirements: Python 3.11+, and `ffmpeg` / `ffprobe` on `PATH`
(`brew install ffmpeg` on macOS, `apt install ffmpeg` on Debian/Ubuntu).

## Running tests

```bash
python3 -m unittest                    # full suite (stdlib unittest, no pytest)
python3 -m unittest tests.test_process_command   # one module
```

Most tests skip without ffmpeg. The browser test additionally needs
`playwright-cli` on PATH and is skipped otherwise.

## Ground rules

- **Vocabulary matters.** `CONTEXT.md` defines the project language (Creator
  Marker, Attributed Export, Attribution Survival, ...). Use those exact terms
  in code, docs, and UI. Each entry lists rejected synonyms; do not drift to
  them.
- **Local-only is a promise.** The app binds 127.0.0.1 and never uploads
  footage. Changes that add network calls to the processing path will not be
  accepted.
- **Stdlib + Pillow only.** ffmpeg/ffprobe are invoked as external commands,
  never through Python bindings. Think twice before proposing a new
  dependency.
- **Honest scope.** FrameCredit is about Attribution Survival, not theft
  prevention. Features that promise more than a visible marker can deliver
  (QR codes, clickable regions, "unremovable" claims) are out of scope; see
  the PRD under `.scratch/video-attribution-mvp/`.
- Architectural decisions live in `docs/adr/`. If your change conflicts with
  an existing ADR, call it out explicitly.

## Pull requests

1. Fork, branch from `main`, keep the diff focused.
2. Add or update tests for any behavior change; run the full suite.
3. Use conventional commit messages (`feat:`, `fix:`, `docs:` ... lowercase).
4. CI must be green.

## Reporting bugs

Open a GitHub issue with the template. For anything security-related, see
[SECURITY.md](SECURITY.md).
