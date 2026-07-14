# Repeat Source Cards with a searchable Source Title

Status: ready-for-agent

User stories: 14–20, 33

## What to build

Extend the end-to-end processing command with a Source Title and render a larger Source Card over existing footage near the beginning, midpoint, and end of the Attributed Export. Each card emphasizes the Creator Identity and concise Source Title so a viewer can search for the original publication even when rendered text is not clickable.

Exact URLs and QR codes remain optional future enhancements and must not be required by this slice.

## Acceptance criteria

- [ ] The public processing command accepts a Source Title.
- [ ] A Source Card containing the Creator Identity and Source Title appears near the beginning, midpoint, and end.
- [ ] Source Cards overlay existing footage and do not extend the output duration.
- [ ] The title is constrained or fitted so long text cannot overflow the visible card.
- [ ] The card remains readable over light and dark sample footage.
- [ ] Extracted output frames confirm all three card windows through the public processing seam.
- [ ] No QR code, short-link service, or platform API is required.

## Blocked by

- `01-first-attributed-export.md`
