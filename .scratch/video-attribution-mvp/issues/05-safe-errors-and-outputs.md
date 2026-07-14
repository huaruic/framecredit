# Handle processing errors and output files safely

Status: ready-for-agent

User stories: 27, 28

## What to build

Make the complete local workflow safe enough for repeated MVP use. Unreadable or unsupported Source Videos produce understandable failures, processing failures propagate through the public boundary, and an existing output is never overwritten without an explicit user decision. The command and local drop zone must communicate the same failure meaning in forms appropriate to their interfaces.

## Acceptance criteria

- [ ] An unreadable input fails without creating a misleading successful output.
- [ ] An unsupported input produces an actionable message rather than raw internal diagnostics alone.
- [ ] The command exits unsuccessfully when processing fails.
- [ ] The local interface shows the failure and allows the Creator to try another Source Video.
- [ ] An existing output file is not silently overwritten.
- [ ] Temporary or partial outputs are not presented as completed Attributed Exports.
- [ ] End-to-end tests cover unreadable input, unsupported input, and an existing output path through public interfaces.

## Blocked by

- `02-local-drop-zone.md`
