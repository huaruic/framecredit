# Security Policy

FrameCredit is a local-only tool: the web interface binds `127.0.0.1`, and
your footage never leaves your machine. Security reports that matter most to
this project:

- anything that makes the local app reachable from outside the machine
- path traversal or file disclosure through the local API
- command injection through file names, handles, or other user input

## Reporting a vulnerability

Please email ernestchen247@gmail.com instead of opening a public issue.
You will get an acknowledgement within a few days. Once a fix is released,
credit is yours if you want it.

## Supported versions

Only the latest release on `main` is supported.
